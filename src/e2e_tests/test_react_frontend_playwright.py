"""
Test cases for the React frontend using pytest-playwright.

These tests verify that the React frontend loads correctly and can interact
with the backend. The tests use the AsyncReactPlaywrightTestCase base class
which handles building the React app and starting the Vite preview server.
"""
import time
import requests
from playwright.async_api import expect
from .react_test_case import AsyncReactPlaywrightTestCase
from unittest import mock
from compasui.tests.testcases import CompasTestCase
from adacs_sso_plugin.adacs_user import ADACSUser
from django.contrib.auth import get_user_model
from adacs_django_playwright.adacs_django_playwright import async_playwright_test

User = get_user_model()


def request_lookup_users_mock(*args, **kwargs):
    """Mock function for looking up users."""
    user = User.objects.first()
    if user:
        return True, [{"id": user.id, "name": "buffy summers"}]
    return False, []


class TestReactFrontend(AsyncReactPlaywrightTestCase):
    """
    Test cases for the React frontend.
    
    These tests verify that the React frontend loads and renders correctly.
    The tests wait for the backend to be ready before testing, ensuring
    that GraphQL queries can succeed.
    """

    async def asetUp(self):
        """Set up the test environment."""
        self.user = ADACSUser(**CompasTestCase.DEFAULT_USER)
        # Wait for backend to be ready before running tests
        self.wait_for_backend_ready()

    def wait_for_backend_ready(self, timeout=30):
        """
        Wait for the backend to be responsive.
        
        This ensures the React app can successfully mount and render
        when we navigate to it. We check multiple endpoints to ensure
        the backend is fully ready.
        """
        print(f"Waiting for backend to be ready at {self.live_server_url}...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Try to access the root endpoint first (should always work)
                response = requests.get(self.live_server_url, timeout=2)
                if response.status_code in [200, 301, 302, 404]:
                    # Backend is responding, try GraphQL
                    try:
                        graphql_url = f"{self.live_server_url}/graphql"
                        # POST with a simple introspection query
                        graphql_response = requests.post(
                            graphql_url,
                            json={"query": "{ __typename }"},
                            timeout=2
                        )
                        if graphql_response.status_code in [200, 400, 401, 403]:
                            # GraphQL is responding (400/401/403 are OK - means it's running)
                            print(f"✓ Backend is ready at {self.live_server_url} (took {time.time() - start_time:.1f}s)")
                            print(f"  GraphQL endpoint: {graphql_url} - Status: {graphql_response.status_code}")
                            return
                    except requests.exceptions.RequestException as graphql_err:
                        # GraphQL not ready yet, but backend is - keep waiting
                        print(f"  Backend responding, GraphQL not ready yet: {type(graphql_err).__name__}")
            except requests.exceptions.RequestException as e:
                print(f"  Backend not ready yet: {type(e).__name__}")
            
            # Wait a bit before retrying
            time.sleep(0.5)
        
        # If we get here, the backend didn't become ready in time
        raise TimeoutError(
            f"Backend did not become ready within {timeout} seconds at {self.live_server_url}. "
            f"The React app requires a working backend to mount properly."
        )

    async def wait_for_page_load(self, page):
        """
        Wait for a page to fully load after navigation.
        
        This ensures the React app has mounted and any loading spinners
        have disappeared. Call this after page.goto() or clicking links.
        
        Args:
            page: Playwright page object
        """
        # Wait for network to be idle
        await page.wait_for_load_state("networkidle")
        
        # Wait for React app container to be visible (not just attached)
        # This ensures the app has mounted and rendered
        print("Waiting for page to load...")
        await page.wait_for_selector("#root", state="visible", timeout=10000)
        
        # Wait for loading spinner to disappear if it exists
        try:
            await page.wait_for_selector("div[role='progressbar']", state="detached", timeout=5000)
            print("Loading spinner disappeared")
        except:
            print("No loading spinner found or timeout waiting for it")

    @async_playwright_test
    @mock.patch(
        "compasui.utils.auth.lookup_users.request_lookup_users",
        side_effect=request_lookup_users_mock,
    )
    async def test_homepage_loads(self, lookup):
        """
        Test that the homepage loads correctly.
        
        This test verifies:
        1. The page loads with the correct title
        2. The React app container (#root) is present
        3. The main heading and navigation buttons are visible
        """
        page = await self.browser_context.new_page()
        
        # Capture console messages for debugging
        console_messages = []
        page.on("console", lambda msg: console_messages.append(f"{msg.type}: {msg.text}"))
        page.on("pageerror", lambda err: console_messages.append(f"ERROR: {err}"))

        # Navigate to the frontend
        print(f"Navigating to {self.react_url}")
        await page.goto(self.react_url)
        await self.wait_for_page_load(page)
        
        # Take a screenshot for debugging
        await page.screenshot(path="test_homepage.png")
        print("Screenshot saved to test_homepage.png")
        
        # Print console messages for debugging
        if console_messages:
            print("Console messages:")
            for msg in console_messages[-20:]:  # Last 20 messages
                print(f"  {msg}")

        # Test that the page loads correctly
        await expect(page).to_have_title("GW Landscape")
        
        # Check that the root div exists (React app container)
        root_div = page.locator("#root")
        await expect(root_div).to_be_attached()
        
        # Wait for the heading to appear - this will fail if app didn't mount
        heading = page.get_by_text("Welcome to GWLandscape!")
        await expect(heading).to_be_visible(timeout=10000)
        
        # Check for navigation buttons
        await expect(page.get_by_role("link", name="Publications")).to_be_visible()
        await expect(page.get_by_role("link", name="Simulate Binary")).to_be_visible()
        await expect(
            page.get_by_role("link", name="Simulate Population")
        ).to_be_visible()

    @async_playwright_test
    @mock.patch(
        "compasui.utils.auth.lookup_users.request_lookup_users",
        side_effect=request_lookup_users_mock,
    )
    async def test_simulate_binary_page_loads(self, lookup):
        """
        Test that the simulate binary page loads correctly.
        
        This test verifies:
        1. Can navigate to the homepage
        2. Can click the "Simulate Binary" button
        3. The simulate binary page loads with expected content
        """
        page = await self.browser_context.new_page()

        # Navigate to the homepage
        print(f"Navigating to {self.react_url}")
        await page.goto(self.react_url)
        await self.wait_for_page_load(page)

        # Click on Simulate Binary button
        await page.get_by_role("link", name="Simulate Binary").click()
        await self.wait_for_page_load(page)
        
        # Check for simulate binary page content
        simulate_heading = page.get_by_text("Simulate the evolution of a binary")
        await expect(simulate_heading).to_be_visible(timeout=10000)

    @async_playwright_test
    @mock.patch(
        "compasui.utils.auth.lookup_users.request_lookup_users",
        side_effect=request_lookup_users_mock,
    )
    async def test_publications_page_loads(self, lookup):
        """
        Test that the publications page loads correctly.
        
        This test verifies:
        1. Can navigate to the homepage
        2. Can click the "Publications" button
        3. The publications page loads with the expected heading and search box
        """
        page = await self.browser_context.new_page()

        # Navigate to the homepage
        print(f"Navigating to {self.react_url}")
        await page.goto(self.react_url)
        await self.wait_for_page_load(page)

        # Click on Publications button
        await page.get_by_role("link", name="Publications").click()
        await self.wait_for_page_load(page)
        
        # Verify publications page content
        # Check for the page heading (h1) specifically, not just any text
        await expect(page.locator("h1")).to_contain_text("Published Datasets", timeout=10000)
        await expect(page.get_by_placeholder("Search by Author, Title, Keyword or Publication Date")).to_be_visible()
