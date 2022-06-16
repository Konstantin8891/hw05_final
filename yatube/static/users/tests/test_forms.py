from django.test import Client, TestCase
from django.urls import reverse

from ..forms import User


class PostCreateFormTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_create_new_user(self):
        users_count = User.objects.count()
        user_data = {
            'first_name': 'TestFirstName',
            'last_name': 'TestLastName',
            'username': 'TestUserName',
            'email': 'something@somewhere.com',
            'password1': 'testpass1,',
            'password2': 'testpass1,',
        }
        self.guest_client.post(
            reverse('users:signup'),
            data=user_data,
            follow=True
        )
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertTrue(User.objects.filter(username='TestUserName').exists())
