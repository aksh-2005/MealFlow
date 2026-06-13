import datetime
from unittest.mock import patch

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from myapp.models import UserProfile, ReportIssue, MenuItem, MealReview


class MealFlowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123',
            first_name='Test User'
        )
        self.profile, _ = UserProfile.objects.update_or_create(
            user=self.user,
            defaults={
                'first_name': 'Test User',
                'email': 'test@example.com',
                'phone': '9876543210',
                'address': '123 Test St',
                'pincode': '600001',
                'meal_preference': 'Veg'
            }
        )

    def test_registration_success(self):
        response = self.client.post(reverse('register'), {
            'full_name': 'New User',
            'username': 'newuser',
            'email': 'new@example.com',
            'phone': '1234567890',
            'address': '456 New St',
            'pincode': '600002',
            'meal_preference': 'Non-Veg',
            'password': 'newpassword123'
        })
        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertTrue(UserProfile.objects.filter(user__username='newuser').exists())

    def test_registration_long_name_success(self):
        # Issue 1: Test user registration with a long name (> 15 chars) succeeds now
        long_name = 'Akash Sundararajan Long Name'
        response = self.client.post(reverse('register'), {
            'full_name': long_name,
            'username': 'longnameuser',
            'email': 'long@example.com',
            'phone': '1234567890',
            'address': '456 New St',
            'pincode': '600002',
            'meal_preference': 'Veg',
            'password': 'newpassword123'
        })
        self.assertRedirects(response, reverse('dashboard'))
        profile = UserProfile.objects.get(user__username='longnameuser')
        self.assertEqual(profile.first_name, long_name)

    def test_registration_invalid_pincode_preserves_form_inputs(self):
        # Issue 8: Invalid pincode keeps user details in context
        response = self.client.post(reverse('register'), {
            'full_name': 'Invalid Pin User',
            'username': 'badpinuser',
            'email': 'badpin@example.com',
            'phone': '1234567890',
            'address': '789 Bad Pin St',
            'pincode': '12345',  # Not 6 digits
            'meal_preference': 'Veg',
            'password': 'newpassword123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('error', response.context)
        self.assertEqual(response.context['error'], 'Enter a valid 6-digit pincode.')
        self.assertEqual(response.context['full_name'], 'Invalid Pin User')
        self.assertEqual(response.context['username'], 'badpinuser')
        self.assertEqual(response.context['address'], '789 Bad Pin St')

    def test_registration_duplicate_username_preserves_form_inputs(self):
        # Issue 8: Duplicate username keeps user details in context
        response = self.client.post(reverse('register'), {
            'full_name': 'Duplicate User',
            'username': 'testuser',  # Already exists
            'email': 'duplicate@example.com',
            'phone': '1234567890',
            'address': '789 Duplicate St',
            'pincode': '600003',
            'meal_preference': 'Veg',
            'password': 'newpassword123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('error', response.context)
        self.assertEqual(response.context['error'], 'Username already exists')
        self.assertEqual(response.context['full_name'], 'Duplicate User')

    def test_report_issue_valid_selection(self):
        # Issue 2: Verify validation on issue reporting
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.post(reverse('report_issue'), {
            'issue': 'wrong_meal',
            'description': 'Received Non-Veg instead of Veg.'
        })
        self.assertRedirects(response, reverse('report_issue'))
        self.assertTrue(ReportIssue.objects.filter(user=self.user, issue='wrong_meal').exists())

    def test_report_issue_invalid_selection_redirects_error(self):
        # Issue 2: Empty or invalid issue choice redirects/renders error instead of crashing
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.post(reverse('report_issue'), {
            'issue': '',
            'description': 'Empty issue description.'
        })
        self.assertRedirects(response, reverse('report_issue'))
        self.assertFalse(ReportIssue.objects.filter(user=self.user).exists())

    @patch('stripe.checkout.Session.retrieve')
    def test_payment_success_unpaid_bypass_fails(self, mock_retrieve):
        # Issue 3: Verify security status validation on success redirect
        self.client.login(username='testuser', password='testpassword123')

        class MockSession:
            payment_status = 'unpaid'
            metadata = {'user_id': 1, 'plan_id': 'weekly'}

        MockSession.metadata['user_id'] = self.user.id
        mock_retrieve.return_value = MockSession()

        response = self.client.get(reverse('payment_success') + '?session_id=cs_test_unpaid')
        self.assertRedirects(response, reverse('plans'))

        self.profile.refresh_from_db()
        self.assertFalse(self.profile.subscription_active)
        self.assertEqual(self.profile.plan_name, "No Active Plan")

    @patch('stripe.checkout.Session.retrieve')
    def test_payment_success_paid_activates_subscription(self, mock_retrieve):
        # Issue 3: Verify subscription gets activated when status is 'paid'
        self.client.login(username='testuser', password='testpassword123')

        class MockSession:
            payment_status = 'paid'
            metadata = {'user_id': 1, 'plan_id': 'weekly'}

        MockSession.metadata['user_id'] = self.user.id
        mock_retrieve.return_value = MockSession()

        response = self.client.get(reverse('payment_success') + '?session_id=cs_test_paid')
        self.assertEqual(response.status_code, 200)

        self.profile.refresh_from_db()
        self.assertTrue(self.profile.subscription_active)
        self.assertEqual(self.profile.plan_name, "7-Day Value Plan")

    def test_superuser_profile_auto_creation_and_safe_access(self):
        # Create a superuser (simulating createsuperuser cli command)
        admin_user = User.objects.create_superuser(
            username='adminuser',
            email='admin@example.com',
            password='adminpassword123'
        )

        # Verify signal created profile
        self.assertTrue(UserProfile.objects.filter(user=admin_user).exists())

        # Verify safe profile fetching on views
        self.client.login(username='adminuser', password='adminpassword123')
        response = self.client.get(reverse('edit_address'))
        self.assertEqual(response.status_code, 200)

        # Edit preference redirects, check status code is 302
        response = self.client.get(reverse('edit_meal_preference'))
        self.assertEqual(response.status_code, 302)
