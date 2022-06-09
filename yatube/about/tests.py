from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus


class AboutUrlsTest(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_url_correct_names(self):
        list_reverse_urls = {
            reverse('about:author'): 'author/',
            reverse('about:tech'): 'tech/',
        }

        for reversed_name, url in list_reverse_urls.items():
            with self.subTest(url=url):
                self.assertEqual(url, reversed_name)

    def test_about_pages_exist_and_desired_location(self):
        pages_list = [
            reverse('about:author'),
            reverse('about:tech')
        ]
        for url in pages_list:
            response = self.guest_client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_correct_names(self):
        list_reverse_urls = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }

        for url, template in list_reverse_urls.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
