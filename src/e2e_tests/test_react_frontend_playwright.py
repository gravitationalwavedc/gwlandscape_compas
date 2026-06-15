"""
Test cases for the React frontend using pytest-playwright.

These tests verify that the React frontend loads correctly and can interact
with the backend. The tests use the AsyncReactPlaywrightTestCase base class
which handles building the React app and starting the Vite preview server.
"""

import logging
import os
import tempfile
import time
from unittest import mock

import requests
from adacs_django_playwright.adacs_django_playwright import \
    async_playwright_test
from adacs_sso_plugin.adacs_user import ADACSUser
from django.contrib.auth import get_user_model
from django.test import override_settings
from playwright.async_api import expect

from compasui.tests.testcases import CompasTestCase

from .react_test_case import REDIS_PORT, AsyncReactPlaywrightTestCase

logger = logging.getLogger(__name__)

User = get_user_model()

temp_output_dir = tempfile.TemporaryDirectory()


def request_lookup_users_mock(*args, **kwargs):
    """Mock function for looking up users."""
    user = User.objects.first()
    if user:
        return True, [{"id": user.id, "name": "buffy summers"}]
    return False, []


@override_settings(
    COMPAS_IO_PATH=temp_output_dir.name,
)
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
        logger.info("Waiting for page to load...")
        await page.wait_for_selector("#root", state="visible", timeout=10000)

        # Wait for loading spinner to disappear if it exists
        try:
            await page.wait_for_selector(
                "div[role='progressbar']", state="detached", timeout=5000
            )
            logger.info("Loading spinner disappeared")
        except:
            logger.debug("No loading spinner found or timeout waiting for it")

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
        page.on(
            "console", lambda msg: console_messages.append(f"{msg.type}: {msg.text}")
        )
        page.on("pageerror", lambda err: console_messages.append(f"ERROR: {err}"))

        # Navigate to the frontend
        logger.info(f"Navigating to {self.react_url}")
        await page.goto(self.react_url)
        await self.wait_for_page_load(page)

        # Take a screenshot for debugging
        await page.screenshot(path="test_homepage.png")
        logger.info("Screenshot saved to test_homepage.png")

        # Print console messages for debugging
        if console_messages:
            logger.info("Console messages:")
            for msg in console_messages[-20:]:  # Last 20 messages
                logger.info(f"  {msg}")

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
        logger.info(f"Navigating to {self.react_url}")
        await page.goto(self.react_url)
        await self.wait_for_page_load(page)

        # Click on Publications button
        await page.get_by_role("link", name="Publications").click()
        await self.wait_for_page_load(page)

        # Verify publications page content
        # Check for the page heading (h1) specifically, not just any text
        await expect(page.locator("h1")).to_contain_text(
            "Published Datasets", timeout=10000
        )
        await expect(
            page.get_by_placeholder(
                "Search by Author, Title, Keyword or Publication Date"
            )
        ).to_be_visible()

    @async_playwright_test
    @mock.patch(
        "compasui.utils.auth.lookup_users.request_lookup_users",
        side_effect=request_lookup_users_mock,
    )
    async def test_single_binary_page_loads(self, lookup):
        """
        Test that the single binary simulation page loads correctly.

        This test verifies:
        1. Can navigate to the homepage
        2. Can click the "Simulate Binary" button
        3. The single binary page loads with the expected form
        """
        page = await self.browser_context.new_page()

        # Navigate to the homepage
        logger.info(f"Navigating to {self.react_url}")
        await page.goto(self.react_url)
        await self.wait_for_page_load(page)

        # Click on Simulate Binary button
        await page.get_by_role("link", name="Simulate Binary").click()
        await self.wait_for_page_load(page)

        # Verify single binary page content
        # Check for the page heading
        await expect(page.locator("h1")).to_contain_text(
            "Simulate the evolution of a binary", timeout=10000
        )

        # Check that the form is present (look for key form fields)
        # The form should have fields for metallicity, mass, etc.
        await expect(page.get_by_label("Metallicity (Z)")).to_be_visible(timeout=5000)
        await expect(page.get_by_label("Mass 1 (M☉)")).to_be_visible()

    @async_playwright_test
    @mock.patch(
        "compasui.utils.auth.lookup_users.request_lookup_users",
        side_effect=request_lookup_users_mock,
    )
    async def test_single_binary_form_submission(self, lookup):
        """
        Test that the single binary form can be submitted and generates results.

        This test verifies:
        1. Can navigate to the single binary page
        2. Can fill out and submit the form
        3. Celery processes the job
        4. Results are displayed

        Note: This test requires Redis and Celery worker to be running.
        """
        page = await self.browser_context.new_page()

        # Navigate to the homepage
        logger.info(f"Navigating to {self.react_url}")
        await page.goto(self.react_url)
        await self.wait_for_page_load(page)

        # Click on Simulate Binary button
        await page.get_by_role("link", name="Simulate Binary").click()
        await self.wait_for_page_load(page)

        # Verify form is present
        await expect(page.locator("h1")).to_contain_text(
            "Simulate the evolution of a binary", timeout=10000
        )

        # Fill out the form with minimal test values
        # Metallicity (required field)
        await page.get_by_label("Metallicity (Z)").fill("0.01")

        # Mass 1 (required field)
        await page.get_by_label("Mass 1 (M").fill("20")

        # Mass 2 (required field)
        await page.get_by_label("Mass 2 (M").fill("10")

        # Find and click the submit button
        # The submit button has text "Start Simulation"
        submit_button = page.get_by_role("button", name="Start Simulation")

        logger.info("Submitting single binary simulation form...")
        await submit_button.click()

        # Wait for the page to navigate to results
        await self.wait_for_page_load(page)

        # Wait for the download link to appear as the signal that results are ready
        logger.info("Waiting for single binary results to become available...")
        output_link = page.get_by_test_id("download-link")

        try:
            await output_link.wait_for(state="visible", timeout=30000)
            logger.info("Download link is visible, results have loaded")
        except Exception:
            await page.screenshot(path="test_single_binary_timeout.png")
            raise AssertionError(
                "Single binary results did not load within timeout period"
            )

        # Also fail fast if the frontend shows a visible error alert
        error_message = page.get_by_test_id("error-message")
        if await error_message.count() > 0 and await error_message.is_visible():
            await page.screenshot(path="test_single_binary_error.png")
            raise AssertionError("Job submission failed - error message displayed")

        # Confirm COMPAS output image files are displayed
        output_images = page.locator("img[src*='/compas/static/assets/']")
        if await output_images.count() == 0:
            await page.screenshot(path="test_single_binary_no_output_images.png")
            raise AssertionError(
                "Expected COMPAS output images to be displayed after job completion"
            )
        await expect(output_images.first).to_be_visible(timeout=10000)

        # Confirm chart plots are rendered as SVG elements
        chart_svgs = page.locator("svg")
        if await chart_svgs.count() == 0:
            await page.screenshot(path="test_single_binary_no_svg_plots.png")
            raise AssertionError(
                "Expected chart plots to be rendered after job completion"
            )
        await expect(chart_svgs.first).to_be_visible(timeout=10000)

        logger.info("Single binary job submission test completed successfully")
