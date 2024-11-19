from django.test import TestCase

# Create your tests here.
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from api.models import CustomUser, Contact


class APITest(APITestCase):
    def setUp(self):
        """
        Set up initial data for testing.
        """
        # Create a test user
        self.user = CustomUser.objects.create_user(
            phone_number="1234567890",
            name="Test User",
            email="testuser@example.com",
            password="testpassword123"
        )
        self.client = APIClient()
        self.login_url = "/api/login/"  # Update with your actual login endpoint
        self.add_contact_url = "/api/contact/"  # Update with your actual add contact endpoint

        # Log in to obtain a valid JWT token
        response = self.client.post(self.login_url, {
            "phone_number": self.user.phone_number,
            "password": "testpassword123"
        })
        self.token = response.data.get("access")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_user_login(self):
        """
        Test the user login functionality.
        """
        response = self.client.post(self.login_url, {
            "phone_number": self.user.phone_number,
            "password": "testpassword123"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_add_contact(self):
        """
        Test adding a contact.
        """
        data = {
            "name": "New Contact",
            "phone_number": "9876543210"
        }
        response = self.client.post(self.add_contact_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Contact.objects.count(), 1)
        contact = Contact.objects.first()
        self.assertEqual(contact.name, data["name"])
        self.assertEqual(contact.phone_number, data["phone_number"])
        self.assertEqual(contact.user, self.user)

    def test_add_contact_invalid_phone_number(self):
        """
        Test adding a contact with an invalid phone number.
        """
        data = {
            "name": "Invalid Contact",
            "phone_number": "12345"  # Invalid length
        }
        response = self.client.post(self.add_contact_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("phone_number", response.data)

    def test_add_contact_duplicate(self):
        """
        Test adding a duplicate contact.
        """
        data = {
            "name": "Duplicate Contact",
            "phone_number": "9876543210"
        }
        self.client.post(self.add_contact_url, data)
        response = self.client.post(self.add_contact_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)

    def test_unauthenticated_access(self):
        """
        Test accessing the API without authentication.
        """
        self.client.credentials()  # Remove the authorization header
        data = {
            "name": "Unauthorized Contact",
            "phone_number": "9876543210"
        }
        response = self.client.post(self.add_contact_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
