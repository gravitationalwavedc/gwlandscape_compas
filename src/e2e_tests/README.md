# React Frontend Playwright Tests

This directory contains end-to-end tests for the React frontend using Playwright.

## Running the Tests

Use Django's test runner to execute the tests:

```bash
cd src/
source venv/bin/activate
python development-manage.py test e2e_tests.test_react_frontend_playwright --verbosity=2
```

To run a specific test:

```bash
python development-manage.py test e2e_tests.test_react_frontend_playwright.TestReactFrontend.test_homepage_loads --verbosity=2
```

## Test Infrastructure

The tests use the `AsyncReactPlaywrightTestCase` base class from `react_test_case.py`, which:

1. Waits for the backend GraphQL API to be ready before running tests
2. Builds the React app using `npm run build`
3. Starts a Vite preview server to serve the built app
4. Provides a Playwright browser context for testing
5. Handles cleanup when tests complete

## Test Behavior

The tests verify that the React frontend properly loads and renders by:

1. **Waiting for backend readiness** - Tests wait for GraphQL endpoint to respond before starting
2. **Smart waiting** - Uses Playwright's built-in waiting mechanisms instead of fixed timeouts
3. **Waiting for React to mount** - Checks for `#root` element to be visible (not just attached)
4. **Waiting for loading spinners** - Waits for loading indicators to disappear
5. **Verifying actual content** - Checks for specific headings, buttons, and page elements

This approach ensures tests:
- Run faster (no unnecessary fixed delays)
- Are more reliable (wait for actual conditions)
- Catch real rendering issues
- Work consistently across all test scenarios

## Debugging

When tests run, they save screenshots (e.g., `test_homepage.png`) in the src directory. This can help diagnose rendering issues.

The tests also print diagnostic information:
- Backend readiness status
- Navigation URLs
- Loading spinner status
- Console messages and errors

## Adding New Tests

To add new tests:

1. Create a new test method in `TestReactFrontend` class
2. Use the `@async_playwright_test` decorator
3. Use `page = await self.browser_context.new_page()` to get a new page
4. Navigate with `await page.goto(url)` followed by `await self.wait_for_page_load(page)`
5. Use Playwright's `expect` for assertions

Example:

```python
@async_playwright_test
@mock.patch(
    "compasui.utils.auth.lookup_users.request_lookup_users",
    side_effect=request_lookup_users_mock,
)
async def test_new_feature(self, lookup):
    """Test a new feature."""
    page = await self.browser_context.new_page()
    
    # Navigate and wait for page to load
    await page.goto(self.react_url)
    await self.wait_for_page_load(page)
    
    # Click a link and wait for navigation
    await page.get_by_role("link", name="Some Link").click()
    await self.wait_for_page_load(page)
    
    # Verify content
    await expect(page.locator("h1")).to_contain_text("Expected Heading")
    await expect(page.get_by_placeholder("Search")).to_be_visible()
```

## Dependencies

The tests require:
- `playwright` - Browser automation library
- `adacs_django_playwright` - Django integration for Playwright
- Node.js and npm - For building the React app
- Chromium browser - Installed automatically by Playwright

Install dependencies with:

```bash
source venv/bin/activate
pip install -r requirements.txt
playwright install
```

## CORS Configuration

The tests run the frontend on `http://localhost:4173` (Vite preview). Make sure this origin is allowed in your Django CORS configuration:

```python
# development-settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Development
    "http://localhost:4173",  # Testing
]
```
