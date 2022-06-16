from django.test import Client, TestCase


class NotFoundTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        self.guest_client = Client()

    def test_404(self):
        response = self.guest_client.get('/anypage.html')
        self.assertTemplateUsed(response, 'core/404.html')
