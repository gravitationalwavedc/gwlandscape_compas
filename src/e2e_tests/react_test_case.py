import logging
import os
import signal
import socket
import subprocess
import tempfile
import time
from pathlib import Path

import requests
from adacs_django_playwright.adacs_django_playwright import (
    AsyncPlaywrightTestCase,
    PlaywrightTestCase,
)


class SharedServiceState:
    def __init__(self):
        self.vite_process = None
        self.react_app_built = False
        self.react_build_tempdir = None
        self.react_build_dir = None
        self.redis_process = None
        self.celery_process = None


state = SharedServiceState()

# Module logger
# logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

FRONTEND_PORT = 4173
BACKEND_PORT = 8000
REDIS_PORT = 6380  # Use non-standard port to avoid conflicts

os.environ["CELERY_BROKER_URL"] = f"redis://localhost:{REDIS_PORT}"
os.environ["CELERY_RESULT_BACKEND"] = f"redis://localhost:{REDIS_PORT}"


def wait_for_port(host: str, port: int, timeout: float = 10.0, interval: float = 0.5):
    """Wait until a TCP port is accepting connections."""
    deadline = time.monotonic() + timeout

    while True:
        try:
            with socket.create_connection((host, port), timeout=interval):
                return
        except OSError:
            if time.monotonic() >= deadline:
                raise TimeoutError(f"Timed out waiting for {host}:{port}")
            time.sleep(interval)


def wait_for_backend_ready(live_server_url, timeout=30):
    """
    Wait for the backend to be responsive.

    This ensures the React app can successfully mount and render
    when we navigate to it. We check multiple endpoints to ensure
    the backend is fully ready.
    """
    logger.info(f"Waiting for backend to be ready at {live_server_url}...")
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            # Try to access the root endpoint first (should always work)
            response = requests.get(live_server_url, timeout=2)
            if response.status_code in [200, 301, 302, 404]:
                # Backend is responding, try GraphQL
                try:
                    graphql_url = f"{live_server_url}/graphql"
                    # POST with a simple introspection query
                    graphql_response = requests.post(
                        graphql_url, json={"query": "{ __typename }"}, timeout=2
                    )
                    if graphql_response.status_code in [200, 400, 401, 403]:
                        # GraphQL is responding (400/401/403 are OK - means it's running)
                        logger.info(
                            f"✓ Backend is ready at {live_server_url} (took {time.time() - start_time:.1f}s)"
                        )
                        logger.info(
                            f"  GraphQL endpoint: {graphql_url} - Status: {graphql_response.status_code}"
                        )
                        return
                except requests.exceptions.RequestException as graphql_err:
                    # GraphQL not ready yet, but backend is - keep waiting
                    logger.info(
                        f"  Backend responding, GraphQL not ready yet: {type(graphql_err).__name__}"
                    )
        except requests.exceptions.RequestException as e:
            logger.info(f"  Backend not ready yet: {type(e).__name__}")

        # Wait a bit before retrying
        time.sleep(0.5)

    # If we get here, the backend didn't become ready in time
    raise TimeoutError(
        f"Backend did not become ready within {timeout} seconds at {live_server_url}. "
        f"The React app requires a working backend to mount properly."
    )


def build_react_app():
    """Build the React app using npm run build."""

    if state.react_app_built:
        return

    logger.info("Building React app...")

    # Path to the react directory
    react_dir = Path(__file__).resolve().parent.parent / "react"

    # Build into a temporary directory so we don't overwrite or remove any existing dist
    state.react_build_tempdir = tempfile.TemporaryDirectory()
    state.react_build_dir = state.react_build_tempdir.name

    result = subprocess.run(
        [
            "npm",
            "run",
            "build",
            "--",
            "--outDir",
            state.react_build_dir,
        ],
        cwd=react_dir,
        capture_output=True,
        text=True,
        env=dict(
            os.environ,
            VITE_FRONTEND_URL=f"http://localhost:{FRONTEND_PORT}",
            VITE_BACKEND_URL=f"http://localhost:{BACKEND_PORT}",
        ),
    )

    if result.returncode != 0:
        logger.error(f"Error building React app: {result.stderr}")
        raise Exception(f"Failed to build React app: {result.stderr}")

    state.react_app_built = True
    logger.info("React app built successfully")
    logger.info(f"  React build directory: {state.react_build_dir}")
    logger.info(f"  Backend URL: http://localhost:{BACKEND_PORT}")
    logger.info(f"  Frontend URL: http://localhost:{FRONTEND_PORT}")


def start_vite_preview():
    """Start the Vite preview server to serve the built React app."""

    if state.vite_process is not None:
        return

    logger.info("Starting Vite preview server...")
    # Path to the react directory
    react_dir = Path(__file__).resolve().parent.parent / "react"

    # Start vite preview server
    state.vite_process = subprocess.Popen(
        [
            "npm",
            "run",
            "preview",
            "--",
            "--outDir",
            state.react_build_dir,
            "--port",
            "4173",
            "--strictPort",
        ],
        cwd=react_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid,  # Use process group for easier termination
    )

    max_wait = 10  # seconds

    try:
        wait_for_port("localhost", FRONTEND_PORT, timeout=max_wait)
        logger.info("Vite preview server started successfully")
    except TimeoutError as exc:
        if state.vite_process.poll() is not None:
            stderr = state.vite_process.stderr.read().decode("utf-8")
            stop_vite_preview()
            raise Exception(f"Vite preview server failed to start: {stderr}") from exc

        stop_vite_preview()
        raise Exception("Timed out waiting for Vite preview server to start") from exc


def stop_vite_preview():
    """Stop the Vite preview server."""

    if state.vite_process is not None:
        logger.info("Stopping Vite preview server...")
        try:
            # Kill the process group
            os.killpg(os.getpgid(state.vite_process.pid), signal.SIGTERM)
            state.vite_process.wait(timeout=5)
        except Exception as e:
            logger.error(f"Error stopping Vite preview server: {e}")
            # Try to force kill if normal termination fails
            try:
                os.killpg(os.getpgid(state.vite_process.pid), signal.SIGKILL)
            except:
                pass

        state.vite_process = None
        logger.info("Vite preview server stopped")


def start_redis():
    """Start Redis server for Celery."""

    if state.redis_process is not None:
        return

    logger.info("Starting Redis server...")
    state.redis_process = subprocess.Popen(
        ["redis-server", "--port", str(REDIS_PORT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid,
    )

    # Wait for Redis to start
    max_wait = 5

    try:
        wait_for_port("localhost", REDIS_PORT, timeout=max_wait)
        logger.info("Redis server started successfully")
    except TimeoutError as exc:
        stop_redis()
        raise Exception("Timed out waiting for Redis to start") from exc


def stop_redis():
    """Stop Redis server."""

    if state.redis_process is not None:
        logger.info("Stopping Redis server...")
        try:
            os.killpg(os.getpgid(state.redis_process.pid), signal.SIGTERM)
            state.redis_process.wait(timeout=5)
        except Exception as e:
            logger.error(f"Error stopping Redis: {e}")
            try:
                os.killpg(os.getpgid(state.redis_process.pid), signal.SIGKILL)
            except:
                pass

        state.redis_process = None
        logger.info("Redis server stopped")


def start_celery_worker():
    """Start Celery worker for processing tasks."""

    if state.celery_process is not None:
        return

    logger.info("Starting Celery worker...")
    # Get the path to the venv's celery executable
    venv_dir = Path(__file__).parent.parent / "venv"
    celery_executable = venv_dir / "bin" / "celery"

    # Don't capture stdout/stderr so we can see Celery logs in real-time
    state.celery_process = subprocess.Popen(
        [str(celery_executable), "-A", "gw_compas", "worker", "--loglevel=info"],
        preexec_fn=os.setsid,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=dict(
            os.environ,
            DJANGO_SETTINGS_MODULE="gw_compas.development-settings",
        ),
    )

    # Give Celery time to start
    time.sleep(3)
    logger.info("Celery worker started")


def stop_celery_worker():
    """Stop Celery worker."""

    if state.celery_process is not None:
        logger.info("Stopping Celery worker...")
        try:
            os.killpg(os.getpgid(state.celery_process.pid), signal.SIGTERM)
            state.celery_process.wait(timeout=10)
        except Exception as e:
            logger.error(f"Error stopping Celery: {e}")
            try:
                os.killpg(os.getpgid(state.celery_process.pid), signal.SIGKILL)
            except:
                pass

        state.celery_process = None
        logger.info("Celery worker stopped")


def start_shared_services():
    """Start all shared external services used by React Playwright tests."""
    start_redis()
    start_celery_worker()
    build_react_app()
    start_vite_preview()


def stop_shared_services():
    """Stop all shared external services used by React Playwright tests."""
    stop_vite_preview()
    stop_celery_worker()
    stop_redis()
    if state.react_build_tempdir is not None:
        try:
            state.react_build_tempdir.cleanup()
            logger.info("Cleaned temporary React build directory")
        except Exception as e:
            logger.error(f"Error cleaning temporary React build directory: {e}")


class ReactPlaywrightTestCase(PlaywrightTestCase):
    """
    A test case class that extends PlaywrightTestCase to add support for testing
    the React frontend served by Vite preview.
    """

    port = BACKEND_PORT

    @classmethod
    def setUpClass(cls):
        """Set up the test environment."""
        super().setUpClass()
        start_shared_services()

    @classmethod
    def tearDownClass(cls):
        """Tear down shared services after all tests in the class have run."""
        try:
            stop_shared_services()
        finally:
            super().tearDownClass()

    def setUp(self):
        """Set up before each test method."""
        super().setUp()
        wait_for_backend_ready(self.live_server_url)

    @property
    def react_url(self):
        """Return the URL of the Vite preview server."""
        return f"http://localhost:{FRONTEND_PORT}"


class AsyncReactPlaywrightTestCase(AsyncPlaywrightTestCase):
    """
    A test case class that extends PlaywrightTestCase to add support for testing
    the React frontend served by Vite preview.
    """

    port = BACKEND_PORT

    @classmethod
    def setUpClass(cls):
        """Set up the test environment."""
        super().setUpClass()
        start_shared_services()

    @classmethod
    def tearDownClass(cls):
        """Tear down shared services after all tests in the class have run."""
        try:
            stop_shared_services()
        finally:
            super().tearDownClass()

    def setUp(self):
        """Set up before each test method."""
        super().setUp()
        wait_for_backend_ready(self.live_server_url)

    @property
    def react_url(self):
        """Return the URL of the Vite preview server."""
        return f"http://localhost:{FRONTEND_PORT}"
