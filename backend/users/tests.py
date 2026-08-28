from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status

from .models import User

from django.test import override_settings


# Create your tests here.
class UserAuthTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="StrongPassword@123"
        )    

    def test_register_user(self):
        url = reverse("register")

        data = {
            "username" : "newuser",
            "email" : "newuser@example.com",
            "password" : "StrongPassword@123",
            "confirm_password" : "StrongPassword@123",
            "first_name" : "New",
            "last_name" : "User",
            "display_name" : "NewUser"
        }

        response = self.client.post(
            url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertTrue(
            User.objects.filter(
                username="newuser"
            ).exists()
        )

    def test_login_user(self):
        url = reverse("login")

        data = {
            "username" : "testuser",
            "password" : "StrongPassword@123",
        }

        response = self.client.post(
            url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "access",
            response.data
        )

        self.assertIn(
            "refresh",
            response.data
        )

    def test_login_with_wrong_password(self):
        url = reverse("login")

        data = {
            "username" : "testuser",
            "password" : "wrong-password"
        }

        response = self.client.post(
            url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )


    def test_login_with_wrong_username(self):
        url = reverse("login")

        data = {
            "username" : "wrong-username",
            "password" : "StrongPassword@123",
        }

        response = self.client.post(
            url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )


    def authenticate(self):
        login_url = reverse("login")

        data = {
            "username" : "testuser",
            "password" : "StrongPassword@123"
        }

        response = self.client.post(
            login_url,
            data,
            format="json"
        )

        access_token = response.data["access"]

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )


    def test_get_current_user(self):
        self.authenticate()

        url = reverse("profile")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["username"],
            "testuser"
        )

    def test_update_profile(self):
        self.authenticate()

        url = reverse("profile")

        data = {
            "first_name" : "Test",
            "last_name" : "User",
            "display_name" : "Tester"
        }

        response = self.client.patch(
            url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.user.refresh_from_db()

        self.assertEqual(
            self.user.display_name,
            "Tester",
        )

    def test_change_password(self):
        self.authenticate()

        url = reverse("change-password")

        data = {
            "current_password" : "StrongPassword@123",
            "new_password" : "NewStrongPassword@123",
            "confirm_password" : "NewStrongPassword@123"
        }

        response = self.client.post(
            url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(
                "NewStrongPassword@123"
            )
        )


    def test_profile_requires_authentication(self):
        url = reverse("profile")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )


    def test_change_password_with_wrong_current_password(self):
        self.authenticate()

        url = reverse("change-password")

        data = {
            "current_password" : "wrongcurrentpassword",
            "new_password" : "NewStrongPassword@123",
            "confirm_password" : "NewStrongPassword@123"
        }

        response = self.client.post(
            url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    @override_settings(
    MAILERS={
        "default": {
            "BACKEND": "django.core.mail.backends.locmem.EmailBackend",
        }
        }
    )   
    def test_forgot_password(self):
        url = reverse("forgot-password")

        data = {
            "email" : "test@example.com"
        }

        response = self.client.post(
            url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_reset_password(self):
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.encoding import force_bytes
        from django.utils.http import urlsafe_base64_encode

        uid = urlsafe_base64_encode(
            force_bytes(self.user.pk)
        )

        token = default_token_generator.make_token(
            self.user
        )

        url = reverse("reset-password")

        data = {
            "uid" : uid,
            "token" : token,
            "new_password" : "ResetPassword@123",
            "confirm_password" : "ResetPassword@123"
        }

        response = self.client.post(
            url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(
                "ResetPassword@123"
            )
        )


    def test_reset_password_with_invalid_token(self):
        from django.utils.encoding import force_bytes
        from django.utils.http import urlsafe_base64_encode

        uid = urlsafe_base64_encode(
            force_bytes(self.user.pk)
        )

        url = reverse("reset-password")

        data = {
            "uid" : uid,
            "token" : "invalid-token",
            "new_password" : "ResetPassword@123",
            "confirm_password" : "ResetPassword@123"
        }

        response = self.client.post(
            url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_logout(self):
        login_url = reverse("login")

        login_data = {
            "username" : "testuser",
            "password" : "StrongPassword@123"
        }

        login_response = self.client.post(
            login_url,
            login_data,
            format="json"
        )

        access_token = login_response.data["access"]
        refresh_token = login_response.data["refresh"]

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )

        logout_url = reverse("logout")

        response = self.client.post(
            logout_url,
            {
                "refresh" : refresh_token
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_refresh_token_cannot_be_used_after_logout(self):
        login_url = reverse("login")

        login_response = self.client.post(
            login_url,
            {
                "username" : "testuser",
                "password" : "StrongPassword@123"
            },

            format="json"
        )

        access_token = login_response.data["access"]
        refresh_token = login_response.data["refresh"]

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )

        self.client.post(
            reverse("logout"),
            {
                "refresh" : refresh_token
            },
            format="json"
        )

        self.client.credentials()

        refresh_response = self.client.post(
            reverse("token-refresh"),
            {
                "refresh" : refresh_token
            },

            format="json"
        )

        self.assertEqual(
            refresh_response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )




