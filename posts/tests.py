import django.utils.timezone
from django.test import TestCase
from django.urls import reverse

from .models import Event


class EventModelTests(TestCase):
    def test_is_not_important(self):
        event = Event(title="*")
        self.assertIs(event.was_important(), False)

    def test_is_important(self):
        event = Event(title="not important")
        self.assertIs(event.was_important(), True)


def create_post(title):
    return Event.objects.create(title=title)


class IndexViewTests(TestCase):
    def test_no_posts(self):
        response = self.client.get(reverse("posts:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You have not made any posts yet.")

    def test_two_posts(self):
        create_post(title="*")
        create_post(title="I ate hamburgers")
        response = self.client.get(reverse("posts:index"))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context["latest_posts"],
            ["<Event: I ate hamburgers>", "<Event: *>"],
        )


class HistoryViewTests(TestCase):
    def test_view_sample_post(self):
        event = create_post("asdf")
        url = reverse("posts:history", args=(event.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, event.text)
