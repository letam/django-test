from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework.reverse import reverse


User = get_user_model()


USER_PASSWORD = '123'

SAMPLE_ENTRY = {
    'date': '2019-09-27',
    'level': 3,
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
        self.assertEqual(response.json(), [])

    def test_post(self):
        self.login(self.user)
        response = self.client.post(reverse('happiness-list'), SAMPLE_ENTRY)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), SAMPLE_ENTRY)

    def test_get_list_after_post(self):
        self.test_post()
        response = self.client.get(reverse('happiness-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [SAMPLE_ENTRY])

    def test_post_to_same_date_twice_should_fail(self):
        self.test_post()
        self.login(self.user)
        try:
            response = self.client.post(
                reverse('happiness-list'), {'date': SAMPLE_ENTRY['date'], 'level': 5}
            )
        except Exception as e:
            self.assertEqual(e.__class__.__name__, 'IntegrityError')
            self.assertEqual(
                str(e),
                'UNIQUE constraint failed: happiness_happiness.user_id, happiness_happiness.date',
            )

    def test_post_as_nonuser_should_fail(self):
        response = self.client.post(reverse('happiness-list'), SAMPLE_ENTRY)
        self.assertEqual(response.status_code, 403)

    def test_modify_as_nonuser_should_fail(self):
        self.test_post()
        self.logout()
        record_id = 1

        modified_entry = {
            'date': SAMPLE_ENTRY['date'],
            'level': 4,
        }
        self.assertNotEqual(SAMPLE_ENTRY, modified_entry)

        for method in ['put', 'patch', 'delete']:
            request = getattr(self.client, method)
            response = request(
                reverse('happiness-detail', [record_id]),
                modified_entry,
                content_type='application/json',
            )
            self.assertEqual(response.status_code, 403)
