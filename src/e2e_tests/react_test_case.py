import subprocess
import time
import os
import signal
import atexit
from adacs_django_playwright.adacs_django_playwright import (
    AsyncPlaywrightTestCase,
    PlaywrightTestCase,
)

# Module-level variables to store the Vite server process
vite_process = None
react_app_built = False
redis_process = None
celery_process = None

FRONTEND_PORT = 4173
BACKEND_PORT = 8000
REDIS_PORT = 6380  # Use non-standard port to avoid conflicts


def build_react_app():
    """Build the React app using npm run build."""
    global react_app_built

    if react_app_built:
        return

    print("Building React app...")
    # Path to the react directory
    react_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "react"
    )

    # Clean the dist folder first to ensure fresh build
    dist_path = os.path.join(react_dir, "dist")
    if os.path.exists(dist_path):
        import shutil
        shutil.rmtree(dist_path)
        print(f"Cleaned {dist_path}")

    result = subprocess.run(
        ["npm", "run", "build"],
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
        print(f"Error building React app: {result.stderr}")
        raise Exception(f"Failed to build React app: {result.stderr}")

    react_app_built = True
    print("React app built successfully")
    print(f"  Backend URL: http://localhost:{BACKEND_PORT}")
    print(f"  Frontend URL: http://localhost:{FRONTEND_PORT}")


def start_vite_preview():
    """Start the Vite preview server to serve the built React app."""
    global vite_process

    if vite_process is not None:
        return

    print("Starting Vite preview server...")
    # Path to the react directory
    react_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "react"
    )

    # Start vite preview server
    vite_process = subprocess.Popen(
        [
            "npm",
            "run",
            "preview",
            "--",
            "--port",
            "4173",
            "--strictPort",
        ],
        cwd=react_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid,  # Use process group for easier termination
    )

    # Wait for server to start (could be improved with actual readiness check)
    max_wait = 10  # seconds
    start_time = time.time()

    while time.time() - start_time < max_wait:
        # Check if process is still running
        if vite_process.poll() is not None:
            stderr = vite_process.stderr.read().decode("utf-8")
            raise Exception(f"Vite preview server failed to start: {stderr}")

        # Try to connect to the server
        try:
            import socket

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(("localhost", 4173))
            sock.close()

            if result == 0:
                print("Vite preview server started successfully")
                return
        except Exception as e:
            print(f"Error checking server: {e}")

        time.sleep(0.5)

    # If we get here, the server didn't start in time
    stop_vite_preview()
    raise Exception("Timed out waiting for Vite preview server to start")


def stop_vite_preview():
    """Stop the Vite preview server."""
    global vite_process

    if vite_process is not None:
        print("Stopping Vite preview server...")
        try:
            # Kill the process group
            os.killpg(os.getpgid(vite_process.pid), signal.SIGTERM)
            vite_process.wait(timeout=5)
        except Exception as e:
            print(f"Error stopping Vite preview server: {e}")
            # Try to force kill if normal termination fails
            try:
                os.killpg(os.getpgid(vite_process.pid), signal.SIGKILL)
            except:
                pass

        vite_process = None
        print("Vite preview server stopped")


# Register the stop_vite_preview function to be called when the Python interpreter exits
atexit.register(stop_vite_preview)


def start_redis():
    """Start Redis server for Celery."""
    global redis_process

    if redis_process is not None:
        return

    print("Starting Redis server...")
    redis_process = subprocess.Popen(
        ["redis-server", "--port", str(REDIS_PORT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid,
    )

    # Wait for Redis to start
    max_wait = 5
    start_time = time.time()

    while time.time() - start_time < max_wait:
        try:
            import socket

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(("localhost", REDIS_PORT))
            sock.close()

            if result == 0:
                print("Redis server started successfully")
                return
        except Exception as e:
            print(f"Error checking Redis: {e}")

        time.sleep(0.5)

    stop_redis()
    raise Exception("Timed out waiting for Redis to start")


def stop_redis():
    """Stop Redis server."""
    global redis_process

    if redis_process is not None:
        print("Stopping Redis server...")
        try:
            os.killpg(os.getpgid(redis_process.pid), signal.SIGTERM)
            redis_process.wait(timeout=5)
        except Exception as e:
            print(f"Error stopping Redis: {e}")
            try:
                os.killpg(os.getpgid(redis_process.pid), signal.SIGKILL)
            except:
                pass

        redis_process = None
        print("Redis server stopped")


def start_celery_worker():
    """Start Celery worker for processing tasks."""
    global celery_process

    if celery_process is not None:
        return

    print("Starting Celery worker...")
    celery_process = subprocess.Popen(
        ["celery", "-A", "gw_compas", "worker", "--loglevel=info"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid,
        env=dict(os.environ, DJANGO_SETTINGS_MODULE="gw_compas.development-settings"),
    )

    # Give Celery time to start
    time.sleep(3)
    print("Celery worker started")


def stop_celery_worker():
    """Stop Celery worker."""
    global celery_process

    if celery_process is not None:
        print("Stopping Celery worker...")
        try:
            os.killpg(os.getpgid(celery_process.pid), signal.SIGTERM)
            celery_process.wait(timeout=10)
        except Exception as e:
            print(f"Error stopping Celery: {e}")
            try:
                os.killpg(os.getpgid(celery_process.pid), signal.SIGKILL)
            except:
                pass

        celery_process = None
        print("Celery worker stopped")


# Register cleanup functions
atexit.register(stop_vite_preview)
atexit.register(stop_redis)
atexit.register(stop_celery_worker)


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
        # Start Redis for Celery
        start_redis()
        # Start Celery worker
        start_celery_worker()
        # Ensure React app is built and Vite server is running
        build_react_app()
        start_vite_preview()

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
        # Start Redis for Celery
        start_redis()
        # Start Celery worker
        start_celery_worker()
        # Ensure React app is built and Vite server is running
        build_react_app()
        start_vite_preview()

    @property
    def react_url(self):
        """Return the URL of the Vite preview server."""
        return f"http://localhost:{FRONTEND_PORT}"
