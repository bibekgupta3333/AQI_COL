# Authentication and Caching Tests

This directory contains comprehensive test cases for the AQI application's authentication and caching functionality.

## Test Files

### `test_authentication_caching.py`

Contains test cases for:

- Authentication flow (login, logout, signup)
- Protected page access control
- Navigation bar visibility based on authentication state
- Cache control headers and behavior
- Redirect functionality
- Form validation

## Running the Tests

### Run All Tests

```bash
python manage.py test main.test_authentication_caching
```

### Run Specific Test Class

```bash
# Run authentication and caching tests
python manage.py test main.test_authentication_caching.AuthenticationCachingTestCase

# Run cache performance tests
python manage.py test main.test_authentication_caching.CachePerformanceTestCase
```

### Run Specific Test Method

```bash
python manage.py test main.test_authentication_caching.AuthenticationCachingTestCase.test_protected_pages_redirect_to_login
```

### Run Tests with Verbose Output

```bash
python manage.py test main.test_authentication_caching -v 2
```

### Run Tests with Coverage (if coverage.py is installed)

```bash
coverage run --source='.' manage.py test main.test_authentication_caching
coverage report
coverage html  # Generate HTML coverage report
```

## Test Coverage

The tests cover the following scenarios:

### Authentication Tests

- ✅ Homepage access without authentication
- ✅ Protected pages redirect to login when not authenticated
- ✅ Navigation bar visibility changes based on authentication state
- ✅ User signup with proper cache control
- ✅ User login with proper cache control
- ✅ Protected pages accessible when authenticated
- ✅ User logout with proper cache control
- ✅ Protected pages redirect after logout
- ✅ Login redirect with 'next' parameter
- ✅ Invalid login attempt handling
- ✅ Signup form validation
- ✅ Duplicate username handling

### Caching Tests

- ✅ Homepage caching behavior
- ✅ Cache varies on authentication state
- ✅ Cache control headers on authentication actions
- ✅ Cache control meta tags in HTML
- ✅ Cache clearing on login/logout

## Test Data

Tests use temporary test users that are automatically cleaned up after each test:

- Username: `testuser`
- Password: `testpass123`

## Expected Behavior

### For Unauthenticated Users:

- Can access: Homepage, About, Login, Signup
- Cannot access: Predict, Past Data, Download
- Redirected to login when accessing protected pages
- See Login/Signup links in navigation

### For Authenticated Users:

- Can access: All pages including Predict, Past Data, Download
- See Logout button in navigation
- No Login/Signup links visible
- Can logout and return to unauthenticated state

### Cache Behavior:

- Homepage has proper cache headers (`max-age=900`)
- Authentication state changes trigger cache invalidation
- Login/logout actions have no-cache headers
- Meta tags prevent browser caching of sensitive content

## Troubleshooting

### Common Issues:

1. **ALLOWED_HOSTS Error**: Make sure `testserver` is in ALLOWED_HOSTS setting
2. **Cache Issues**: Tests clear cache before/after each test automatically
3. **Database Issues**: Tests use Django's test database which is automatically created/destroyed

### Debug Mode:

Run tests with debug output:

```bash
python manage.py test main.test_authentication_caching --debug-mode --pdb
```

## Integration with CI/CD

These tests can be integrated into your CI/CD pipeline:

```yaml
# Example GitHub Actions workflow
- name: Run Authentication Tests
  run: python manage.py test main.test_authentication_caching --keepdb
```

## Performance Considerations

- Tests use Django's `TestCase` which uses database transactions for speed
- Cache is cleared before each test to ensure isolation
- Mock objects could be used for external API calls in future enhancements
