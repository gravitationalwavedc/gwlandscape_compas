# React Frontend Playwright Tests

This directory contains end-to-end tests for the React frontend using Playwright with a Django, GraphQL, Redis, and Celery backend.

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

To run all e2e tests:

```bash
python development-manage.py test e2e_tests --verbosity=2
```

## Test Infrastructure

The tests use the `AsyncReactPlaywrightTestCase` base class from `react_test_case.py`, which:

1. **Sets up Celery configuration** - Environment variables configure Celery to use Redis on port 6380
2. **Starts Redis server** - Launches Redis on port 6380 for Celery broker
3. **Starts Celery worker** - Launches Celery worker to process background tasks
4. **Builds the React app** - Uses `npm run build` to create production build
5. **Starts Vite preview server** - Serves the built app on port 4173
6. **Waits for backend readiness** - Checks both Django and GraphQL endpoints before running tests
7. **Provides Playwright browser context** - Sets up browser for testing
8. **Handles cleanup** - Stops all services when tests complete

## Test Architecture

### Environment Configuration

Celery broker URLs are set as environment variables at module load time (before Django imports):

```python
os.environ["CELERY_BROKER_URL"] = "redis://localhost:6380"
os.environ["CELERY_RESULT_BACKEND"] = "redis://localhost:6380"
```

This ensures both Django and the Celery worker use the same Redis instance.

### Service Management

The test infrastructure manages all required services:

- **Redis** - Started via `subprocess.Popen` on port 6380
- **Celery worker** - Started via `subprocess.Popen`, inherits environment variables
- **Vite preview** - Serves the React build on port 4173

All services are started in `setUpClass()` and stopped in `tearDownClass()` using process groups for clean termination.

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

When tests run, they save screenshots (e.g., `test_homepage.png`, `test_single_binary_timeout.png`) in the src directory. This can help diagnose rendering issues.

The tests also print diagnostic information:
- Backend readiness status
- Navigation URLs
- Loading spinner status
- Console messages and errors
- Celery task execution logs

### Common Issues

**Tests failing intermittently:**
- Check for stale Redis/Celery processes: `ps aux | grep -E "redis|celery" | grep 6380`
- Kill any stale processes and re-run tests
- Ensure port 6380 is available

**Celery tasks not executing:**
- Verify Redis is running on port 6380
- Check Celery worker logs for connection errors
- Ensure `CELERY_BROKER_URL` environment variable is set correctly

**Timeouts waiting for results:**
- Check if Celery worker is processing tasks
- Verify COMPAS executable path is correct
- Look for error messages in Celery worker output

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

### Testing Celery-Dependent Features

For tests that submit tasks to Celery (like job submission):

1. Fill out and submit forms as normal
2. Wait for results using `wait_for()` with appropriate timeout
3. Check for success indicators (download links, result content)
4. Check for error messages if task fails

Example:

```python
# Submit form that triggers Celery task
await submit_button.click()
await self.wait_for_page_load(page)

# Wait for results (with timeout)
output_link = page.get_by_test_id("download-link")
await output_link.wait_for(state="visible", timeout=60000)

# Verify results are displayed
await expect(output_link).to_be_visible()
```

## Dependencies

The tests require:
- `playwright` - Browser automation library
- `adacs_django_playwright` - Django integration for Playwright
- `redis-server` - Started automatically by tests
- Node.js and npm - For building the React app
- Chromium browser - Installed automatically by Playwright

Install Python dependencies with:

```bash
pip install -r requirements.txt
```

Install Playwright browsers:

```bash
playwright install
```

## CI/CD

The e2e tests run in GitLab CI using the Playwright Docker image. See `.gitlab-ci.yml` for configuration. The tests:

- Run separately from Django unit tests
- Use the Playwright Docker image with browsers pre-installed
- Start their own Redis and Celery worker
- Generate JUnit reports and screenshots as artifacts

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
