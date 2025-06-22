"""
Test cases for authentication and caching functionality
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.cache import cache
from django.urls import reverse
from django.conf import settings


class AuthenticationCachingTestCase(TestCase):
    """Test cases for authentication and caching behavior"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.test_username = "testuser"
        self.test_password = "testpass123"

        # Clear cache before each test
        cache.clear()

    def tearDown(self):
        """Clean up after each test"""
        # Clean up any test users
        User.objects.filter(username=self.test_username).delete()
        cache.clear()

    def test_homepage_access_without_authentication(self):
        """Test that homepage is accessible without authentication"""
        response = self.client.get(reverse("main:home-page"))
        self.assertEqual(response.status_code, 200)

        # Check that cache control headers are present
        self.assertIn("max-age", response.get("Cache-Control", ""))

    def test_protected_pages_redirect_to_login(self):
        """Test that protected pages redirect unauthenticated users to login"""
        protected_urls = [
            reverse("main:predict-aqi"),
            reverse("main:past-data"),
            reverse("main:download"),
        ]

        for url in protected_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertIn("/login/", response.url)

    def test_navbar_visibility_without_authentication(self):
        """Test that protected navigation items are hidden for unauthenticated users"""
        response = self.client.get(reverse("main:home-page"))
        self.assertEqual(response.status_code, 200)

        # Check that protected nav items are not visible
        content = response.content.decode()
        self.assertNotIn('href="' + reverse("main:predict-aqi") + '"', content)
        self.assertNotIn('href="' + reverse("main:past-data") + '"', content)

        # Check that public nav items are visible
        self.assertIn('href="' + reverse("main:home-page") + '"', content)
        self.assertIn('href="' + reverse("main:about-us") + '"', content)
        self.assertIn('href="' + reverse("main:signup") + '"', content)
        self.assertIn('href="' + reverse("main:login") + '"', content)

    def test_user_signup_with_cache_control(self):
        """Test user signup and proper cache control headers"""
        signup_data = {
            "Username": self.test_username,
            "Password": self.test_password,
            "Password1": self.test_password,
        }

        response = self.client.post(reverse("main:signup"), signup_data)

        # Should redirect after successful signup
        self.assertEqual(response.status_code, 302)

        # Check cache control headers
        cache_control = response.get("Cache-Control", "")
        self.assertIn("no-cache", cache_control)
        self.assertIn("no-store", cache_control)
        self.assertIn("must-revalidate", cache_control)

        # Verify user was created and logged in
        self.assertTrue(User.objects.filter(username=self.test_username).exists())

    def test_user_login_with_cache_control(self):
        """Test user login and proper cache control headers"""
        # Create a test user first
        User.objects.create_user(
            username=self.test_username, password=self.test_password
        )

        login_data = {
            "Username": self.test_username,
            "Password": self.test_password,
        }

        response = self.client.post(reverse("main:login"), login_data)

        # Should redirect after successful login
        self.assertEqual(response.status_code, 302)

        # Check cache control headers
        cache_control = response.get("Cache-Control", "")
        self.assertIn("no-cache", cache_control)
        self.assertIn("no-store", cache_control)
        self.assertIn("must-revalidate", cache_control)

    def test_navbar_visibility_with_authentication(self):
        """Test that protected navigation items are visible for authenticated users"""
        # Create and login user
        user = User.objects.create_user(
            username=self.test_username, password=self.test_password
        )
        self.client.force_login(user)

        response = self.client.get(reverse("main:home-page"))
        self.assertEqual(response.status_code, 200)

        content = response.content.decode()

        # Check that protected nav items are visible
        self.assertIn('href="' + reverse("main:predict-aqi") + '"', content)
        self.assertIn('href="' + reverse("main:past-data") + '"', content)

        # Check that login/signup links are not visible
        self.assertNotIn('href="' + reverse("main:signup") + '"', content)
        self.assertNotIn('href="' + reverse("main:login") + '"', content)

    def test_protected_pages_access_with_authentication(self):
        """Test that protected pages are accessible for authenticated users"""
        # Create and login user
        user = User.objects.create_user(
            username=self.test_username, password=self.test_password
        )
        self.client.force_login(user)

        protected_urls = [
            reverse("main:predict-aqi"),
            reverse("main:past-data"),
            reverse("main:download"),
        ]

        for url in protected_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                # Should be accessible (200) or should be a POST-only endpoint (405)
                self.assertIn(response.status_code, [200, 405])

    def test_user_logout_with_cache_control(self):
        """Test user logout and proper cache control headers"""
        # Create and login user
        user = User.objects.create_user(
            username=self.test_username, password=self.test_password
        )
        self.client.force_login(user)

        response = self.client.post(reverse("main:logout"))

        # Should redirect after logout
        self.assertEqual(response.status_code, 302)

        # Check cache control headers
        cache_control = response.get("Cache-Control", "")
        self.assertIn("no-cache", cache_control)
        self.assertIn("no-store", cache_control)
        self.assertIn("must-revalidate", cache_control)

    def test_protected_pages_after_logout(self):
        """Test that protected pages redirect to login after logout"""
        # Create and login user
        user = User.objects.create_user(
            username=self.test_username, password=self.test_password
        )
        self.client.force_login(user)

        # Verify access while logged in
        response = self.client.get(reverse("main:predict-aqi"))
        self.assertEqual(response.status_code, 200)

        # Logout
        self.client.post(reverse("main:logout"))

        # Verify redirect to login after logout
        response = self.client.get(reverse("main:predict-aqi"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_cache_varies_on_authentication_state(self):
        """Test that homepage cache varies based on authentication state"""
        # Test unauthenticated access
        response1 = self.client.get(reverse("main:home-page"))
        self.assertEqual(response1.status_code, 200)

        # Create and login user
        user = User.objects.create_user(
            username=self.test_username, password=self.test_password
        )
        self.client.force_login(user)

        # Test authenticated access
        response2 = self.client.get(reverse("main:home-page"))
        self.assertEqual(response2.status_code, 200)

        # Content should be different based on authentication state
        content1 = response1.content.decode()
        content2 = response2.content.decode()

        # Authenticated version should have logout button, unauthenticated should have login/signup
        self.assertIn("signup", content1.lower())
        self.assertIn("login", content1.lower())
        self.assertIn("logout", content2.lower())

    def test_login_redirect_parameter(self):
        """Test that login redirects to 'next' parameter if provided"""
        target_url = reverse("main:predict-aqi")
        login_url = f"{reverse('main:login')}?next={target_url}"

        # Try to access protected page, should redirect to login with next parameter
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)

        # Create user and login with next parameter
        User.objects.create_user(
            username=self.test_username, password=self.test_password
        )

        login_data = {
            "Username": self.test_username,
            "Password": self.test_password,
        }

        response = self.client.post(login_url, login_data)
        self.assertEqual(response.status_code, 302)
        # Should redirect to the target URL after login
        self.assertEqual(response.url, target_url)

    def test_invalid_login_attempt(self):
        """Test handling of invalid login credentials"""
        login_data = {
            "Username": "nonexistent",
            "Password": "wrongpassword",
        }

        response = self.client.post(reverse("main:login"), login_data)

        # Should return to login page with error
        self.assertEqual(response.status_code, 200)

        # Check for error message in Django messages framework
        messages = list(response.context["messages"])
        self.assertTrue(
            any("Invalid username or password" in str(message) for message in messages)
        )

    def test_signup_validation(self):
        """Test signup form validation"""
        # Test with mismatched passwords
        signup_data = {
            "Username": self.test_username,
            "Password": self.test_password,
            "Password1": "differentpassword",
        }

        response = self.client.post(reverse("main:signup"), signup_data)
        self.assertEqual(response.status_code, 200)

        # Check for error message in Django messages framework
        messages = list(response.context["messages"])
        self.assertTrue(
            any("Passwords do not match" in str(message) for message in messages)
        )

        # Verify user was not created
        self.assertFalse(User.objects.filter(username=self.test_username).exists())

    def test_duplicate_username_signup(self):
        """Test signup with existing username"""
        # Create existing user
        User.objects.create_user(
            username=self.test_username, password=self.test_password
        )

        # Try to signup with same username
        signup_data = {
            "Username": self.test_username,
            "Password": "newpassword123",
            "Password1": "newpassword123",
        }

        response = self.client.post(reverse("main:signup"), signup_data)
        self.assertEqual(response.status_code, 200)

        # Check for error message in Django messages framework
        messages = list(response.context["messages"])
        self.assertTrue(
            any("Username already exists" in str(message) for message in messages)
        )


class CachePerformanceTestCase(TestCase):
    """Test cases for caching performance and behavior"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        cache.clear()

    def test_homepage_caching_behavior(self):
        """Test that homepage implements proper caching"""
        # First request
        response1 = self.client.get(reverse("main:home-page"))
        self.assertEqual(response1.status_code, 200)

        # Check cache headers
        cache_control = response1.get("Cache-Control", "")
        self.assertIn("max-age", cache_control)

        # Second request should potentially be faster due to caching
        response2 = self.client.get(reverse("main:home-page"))
        self.assertEqual(response2.status_code, 200)

    def test_cache_control_meta_tags(self):
        """Test that pages include proper cache control meta tags"""
        response = self.client.get(reverse("main:home-page"))
        self.assertEqual(response.status_code, 200)

        content = response.content.decode()

        # Check for cache control meta tags
        self.assertIn('http-equiv="Cache-Control"', content)
        self.assertIn('http-equiv="Pragma"', content)
        self.assertIn('http-equiv="Expires"', content)
