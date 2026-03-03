from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from apps.users.models import User


class UserModelTest(TestCase):

    def test_create_user(self):
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="StrongPass123!"
        )
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("StrongPass123!"))
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_active)

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="AdminPass123!"
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_user_str(self):
        user = User.objects.create_user(username="john", password="Pass1234!")
        self.assertEqual(str(user), "john")
        

class UserRegisterViewTest(APITestCase):

    def test_register_success(self):
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "StrongPass123!",
            "password2": "StrongPass123!",
        }
        response = self.client.post("/api/auth/register/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_register_password_mismatch(self):
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "StrongPass123!",
            "password2": "WrongPass123!",
        }
        response = self.client.post("/api/auth/register/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_username(self):
        User.objects.create_user(username="existing", password="Pass1234!")
        data = {
            "username": "existing",
            "email": "e@example.com",
            "password": "StrongPass123!",
            "password2": "StrongPass123!",
        }
        response = self.client.post("/api/auth/register/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_fields(self):
        response = self.client.post("/api/auth/register/", {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLoginViewTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="loginuser",
            email="login@example.com",
            password="StrongPass123!"
        )

    def test_login_success(self):
        response = self.client.post("/api/auth/login/", {
            "username": "loginuser",
            "password": "StrongPass123!",
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_wrong_password(self):
        response = self.client.post("/api/auth/login/", {
            "username": "loginuser",
            "password": "WrongPassword!",
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_user(self):
        response = self.client.post("/api/auth/login/", {
            "username": "nobody",
            "password": "pass",
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserProfileViewTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="profileuser",
            email="profile@example.com",
            password="StrongPass123!"
        )
        login_response = self.client.post("/api/auth/login/", {
            "username": "profileuser",
            "password": "StrongPass123!",
        })
        self.token = login_response.data["access"]

    def test_get_profile_authenticated(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        response = self.client.get("/api/auth/profile/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "profileuser")

    def test_get_profile_unauthenticated(self):
        response = self.client.get("/api/auth/profile/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class LogoutViewTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="logoutuser",
            password="StrongPass123!"
        )
        login_response = self.client.post("/api/auth/login/", {
            "username": "logoutuser",
            "password": "StrongPass123!",
        })
        self.access = login_response.data["access"]
        self.refresh = login_response.data["refresh"]

    def test_logout_success(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access}")
        response = self.client.post("/api/auth/logout/", {"refresh": self.refresh})
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)

    def test_logout_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access}")
        response = self.client.post("/api/auth/logout/", {"refresh": "invalidtoken"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_unauthenticated(self):
        response = self.client.post("/api/auth/logout/", {"refresh": self.refresh})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)