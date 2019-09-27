from typing import Dict, List

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework.reverse import reverse


User = get_user_model()


USER_PASSWORD = '123'

EMPTY_STATS = {
    'tally': {},
    'average': None,
}

SAMPLE_REQUEST_DATA = {
    'level': 3
}


class AuthMixin:
    def login(self, user):
        self.client.get(settings.LOGIN_URL)
        response = self.client.post(
            settings.LOGIN_URL, {'username': user.username, 'password': USER_PASSWORD}
        )
        # Assert correct post-login response
        self.assertEqual(response.status_code, 302)  # Should return "found" response
        self.assertEqual(response.get('location'), settings.LOGIN_REDIRECT_URL)

    def logout(self):
        self.client.get(settings.LOGOUT_URL)


class HappinessViewTests(TestCase, AuthMixin):
    def setUp(self):
        self.user = User.objects.create_user(username='user', password=USER_PASSWORD)

    def test_get_list_empty(self):
        response = self.client.get(reverse('happiness-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), EMPTY_STATS)

    def test_post(self):
        self.login(self.user)
        response = self.client.post(reverse('happiness-list'), SAMPLE_REQUEST_DATA)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), _get_stats_from_entries([SAMPLE_REQUEST_DATA]))

    def test_get_list_after_post(self):
        self.test_post()
        response = self.client.get(reverse('happiness-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), _get_stats_from_entries([SAMPLE_REQUEST_DATA]))

    def test_unauthenticated_get_list_after_post(self):
        self.test_post()
        self.logout()
        response = self.client.get(reverse('happiness-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), _get_stats_from_entries([SAMPLE_REQUEST_DATA]))

    def test_post_to_same_date_twice_should_fail(self):
        self.test_post()
        self.login(self.user)
        response = self.client.post(reverse('happiness-list'), {'level': 5})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            ['You have already submitted your happiness level for today.'],
        )

    def test_post_as_nonuser_should_fail(self):
        response = self.client.post(reverse('happiness-list'), SAMPLE_REQUEST_DATA)
        self.assertEqual(response.status_code, 403)

    def test_modify_as_nonuser_should_fail(self):
        self.test_post()
        record_id = 1
        modified_entry = {'level': 4}
        self.assertNotEqual(SAMPLE_REQUEST_DATA, modified_entry)

        self.logout()
        for method in ['put', 'patch', 'delete']:
            request = getattr(self.client, method)
            response = request(
                reverse('happiness-detail', [record_id]),
                modified_entry,
                content_type='application/json',
            )
            self.assertEqual(response.status_code, 403)

    def test_get(self):
        self.test_post()
        record_id = 1

        response = self.client.get(reverse('happiness-detail', [record_id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), SAMPLE_REQUEST_DATA)

    def test_put(self):
        self.test_post()
        record_id = 1
        modified_entry = {'level': 4}
        self.assertNotEqual(SAMPLE_REQUEST_DATA, modified_entry)

        response = self.client.put(
            reverse('happiness-detail', [record_id]),
            modified_entry,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), modified_entry)

    def test_patch(self):
        self.test_post()
        record_id = 1
        modified_entry = {'level': 4}
        self.assertNotEqual(SAMPLE_REQUEST_DATA, modified_entry)

        response = self.client.patch(
            reverse('happiness-detail', [record_id]),
            modified_entry,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), modified_entry)

    def test_delete(self):
        self.test_post()
        record_id = 1

        response = self.client.delete(reverse('happiness-detail', [record_id]))
        self.assertEqual(response.status_code, 204)

        response = self.client.get(reverse('happiness-detail', [record_id]))
        self.assertEqual(response.status_code, 404)

        response = self.client.get(reverse('happiness-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), EMPTY_STATS)


def _get_stats_from_entries(entries: List[Dict[str, int]]):
    tally = {}
    sum = 0
    count = 0

    for entry in entries:
        # count numbers to calculate average later
        level = entry['level']
        sum += level
        count += 1

        # update tally
        key = str(level)
        if key not in tally:
            tally[key] = 1
        else:
            tally[key] += 1

    return {
        'tally': tally,
        'average': (sum / count) if count else None,
    }
