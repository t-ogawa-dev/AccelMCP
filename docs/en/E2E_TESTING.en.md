[日本語](../E2E_TESTING.md) | English

# E2E Testing with Playwright

This project uses a dedicated container for E2E testing.

## Architecture

- **web**: Production application container (no Playwright required)
- **e2e**: Dedicated E2E test container (includes Playwright + Chromium)
- **db**: MySQL database

## How to Run E2E Tests

### Method 1: Run in dedicated container (recommended)

```bash
# Start the E2E container and run tests
docker compose --profile e2e run --rm e2e

# Run only a specific test file
docker compose --profile e2e run --rm e2e python -m pytest tests/e2e/test_login.py -v

# Run all tests (unit + integration + E2E)
docker compose --profile e2e run --rm e2e python -m pytest tests/ -v
```

### Method 2: Run in web container (during development)

The web container can also run non-E2E tests:

```bash
# Unit, integration, and API tests only
docker compose exec web python -m pytest tests/unit/ -v
```

## Why Separate Containers?

1. **Lightweight production image**: The web container does not include Playwright or Chromium, keeping the image size small.
2. **Security**: No unnecessary browser binaries in the production environment.
3. **Maintainability**: Clear separation between the test and production environments.
4. **Rails best practice**: Similar to how Rails separates the Chromium container.

## Technology Choices

### Why Playwright's built-in browser instead of Selenium Grid?

Rails uses containers like `seleniarm/standalone-chromium` for Selenium Grid, but this project uses Playwright's built-in Chromium.

**Reasons:**

- **Playwright's design philosophy**: Playwright manages its own browser binaries and is not compatible with Selenium Grid.
- **Simplicity**: No need to configure communication with an external browser container.
- **Lightweight**: The E2E container is self-contained; no additional browser container required.
- **Speed**: No communication overhead with a local browser.

**If you want to use Selenium Grid:**

- Use Selenium WebDriver instead of Playwright.
- Or consider Playwright's experimental Grid support only when parallel testing across multiple browsers is required.

**Advantages of the current architecture:**

```
e2e container = Python + pytest + Playwright + Chromium (all-in-one)
```

- Fully contained within `Dockerfile.e2e`
- Simple configuration
- Production web container remains completely clean

## Docker Compose Profiles

Using `profiles: [e2e]` means the E2E container does not start with a normal `docker compose up`. It only starts when `--profile e2e` is explicitly specified.

```bash
# Normal startup (web and db only)
docker compose up -d

# Start only for E2E testing
docker compose --profile e2e up -d
```
