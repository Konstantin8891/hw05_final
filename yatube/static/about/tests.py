from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse


class AboutURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_urls(self):
        urls = [
            '/about/author/',
            '/about/tech/',
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_templates(self):
        template_url = {
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/',
        }
        for template, url in template_url.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_about_namespace(self):
        reverses_templates = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }
        for rev, template in reverses_templates.items():
            with self.subTest(rev=rev):
                response = self.guest_client.get(rev)
                self.assertTemplateUsed(response, template)
