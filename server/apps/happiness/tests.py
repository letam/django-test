from typing import Dict, List

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.timezone import now, timedelta

from rest_framework.reverse import reverse

from apps.happiness.models import Team


User = get_user_model()


USER_PASSWORD = '123'

EMPTY_STATS = {
    'tally': {},
    'average': None,
}


class AuthMixin:
    def login(self, user=None):
        if not user:
            user = self.user
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
        self.team_a = Team.objects.create(name='Team A')
        self.team_b = Team.objects.create(name='Team B')

        self.entries_created_by_team_id = {
            self.team_a.id: [],
            self.team_b.id: [],
        }

        self.user1 = User.objects.create_user(username='user1', password=USER_PASSWORD)
        self.user1.userprofile.team = self.team_a
        self.user1.userprofile.save()

        self.user2 = User.objects.create_user(username='user2', password=USER_PASSWORD)
        self.user2.userprofile.team = self.team_a
        self.user2.userprofile.save()

        self.user3 = User.objects.create_user(username='user3', password=USER_PASSWORD)
        self.user3.userprofile.team = self.team_a
        self.user3.userprofile.save()

        self.user4 = User.objects.create_user(username='user4', password=USER_PASSWORD)
        self.user4.userprofile.team = self.team_b
        self.user4.userprofile.save()

        self.user5 = User.objects.create_user(username='user5', password=USER_PASSWORD)
        self.user5.userprofile.team = self.team_b
        self.user5.userprofile.save()

        self.user = self.user1

    def test_get_list_empty(self):
        response = self.client.get(reverse('happiness-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), EMPTY_STATS)

    def post(self, user=None, data=None):
        if not user:
            user = self.user
        if not data:
            data = {'level': 3}
        self.login(user)
        response = self.client.post(reverse('happiness-list'), data)
        entries_from_team = self.entries_created_by_team_id[user.userprofile.team_id]
        if response.status_code == 201:
            entries_from_team.append(data)
        self.assertEqual(response.json(), _get_stats_from_entries(entries_from_team))
        return response

    def test_post(self):
        response = self.post(data={'level': 3})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), _get_stats_from_entries([{'level': 3}]))
        return response

    def test_post_invalid_level_value_should_fail(self):
        self.login()
        response = self.client.post(reverse('happiness-list'), {'level': 0})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {'level': ['Happiness level must be between 1 and 5']},
        )
        response = self.client.post(reverse('happiness-list'), {'level': -1})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {'level': ['Happiness level must be between 1 and 5']},
        )
        response = self.client.post(reverse('happiness-list'), {'level': 6})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {'level': ['Happiness level must be between 1 and 5']},
        )

    def test_get_list_after_post(self):
        self.post(data={'level': 3})
        response = self.client.get(reverse('happiness-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), _get_stats_from_entries([{'level': 3}]))

    def test_unauthenticated_get_list_after_post(self):
        self.post(data={'level': 3})
        self.logout()
        response = self.client.get(reverse('happiness-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), _get_stats_from_entries([{'level': 3}]))

    def test_unauthenticated_get_list_after_posts_from_multiple_users(self):

        response = self.post(self.user1, {'level': 1})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), _get_stats_from_entries([{'level': 1}]))
        self.logout()

        response = self.post(self.user2, {'level': 2})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json(), _get_stats_from_entries([{'level': 1}, {'level': 2}])
        )
        self.logout()

        response = self.post(self.user3, {'level': 3})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json(),
            _get_stats_from_entries([{'level': 1}, {'level': 2}, {'level': 3}]),
        )
        self.logout()

        response = self.client.get(reverse('happiness-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            _get_stats_from_entries([{'level': 1}, {'level': 2}, {'level': 3}]),
        )

    def test_get_list_after_posts_from_users_on_different_teams(self):

        # Team A
        response = self.post(self.user1, {'level': 1})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), _get_stats_from_entries([{'level': 1}]))
        self.logout()

        response = self.post(self.user2, {'level': 2})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json(), _get_stats_from_entries([{'level': 1}, {'level': 2}])
        )
        self.logout()

        response = self.post(self.user3, {'level': 3})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json(),
            _get_stats_from_entries([{'level': 1}, {'level': 2}, {'level': 3}]),
        )
        self.logout()

        # Team B

        ## Confirm that TEAM B has empty stats
        self.login(self.user4)
        response = self.client.get(reverse('happiness-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), EMPTY_STATS)

        response = self.post(self.user4, {'level': 4})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json(),
            _get_stats_from_entries([{'level': 4}]),
        )
        self.logout()

        response = self.post(self.user5, {'level': 5})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json(),
            _get_stats_from_entries([{'level': 4}, {'level': 5}]),
        )
        self.logout()

        ## Confirm that TEAM A's stats stayed the same
        self.login(self.user1)
        response = self.client.get(reverse('happiness-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            _get_stats_from_entries([{'level': 1}, {'level': 2}, {'level': 3}]),
        )
        self.logout()

        ## Confirm that unauthenticated user sees stats combined from all teams
        response = self.client.get(reverse('happiness-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            _get_stats_from_entries(
                [{'level': 1}, {'level': 2}, {'level': 3}, {'level': 4}, {'level': 5}]
            ),
        )

    def test_post_to_same_date_twice_should_fail(self):
        self.post()
        response = self.client.post(reverse('happiness-list'), {'level': 5})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            ['You have already submitted your happiness level for today.'],
        )

    def test_post_as_nonuser_should_fail(self):
        response = self.client.post(reverse('happiness-list'), {'level': 3})
        self.assertEqual(response.status_code, 403)

    def put(self, user=None, data=None, date=None):
        if not user:
            user = self.user
        if not data:
            data = {'level': 3}
        if not date:
            date = now().date() - timedelta(days=1)
        self.login(user)
        response = self.client.put(
            reverse('happiness-detail', [date]), data, content_type='application/json'
        )
        return response

    def test_modify_as_nonuser_should_fail(self):
        yesterday = now().date() - timedelta(days=1)
        self.put(data={'level': 3}, date=yesterday)
        modified_entry = {'level': 4}
        self.assertNotEqual({'level': 3}, modified_entry)

        self.logout()
        for method in ['put', 'patch', 'delete']:
            request = getattr(self.client, method)
            response = request(
                reverse('happiness-detail', [yesterday]),
                modified_entry,
                content_type='application/json',
            )
            self.assertEqual(response.status_code, 403)

    def test_get_for_date_with_no_data(self):
        yesterday = now().date() - timedelta(days=1)
        response = self.client.get(reverse('happiness-detail', [yesterday]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), EMPTY_STATS)

    def test_get_for_date_after_post(self):
        yesterday = now().date() - timedelta(days=1)
        self.put(data={'level': 3}, date=yesterday)
        response = self.client.get(reverse('happiness-detail', [yesterday]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), _get_stats_from_entries([{'level': 3}]))

    def test_put_without_prior_entry_should_create(self):
        yesterday = now().date() - timedelta(days=1)
        response = self.client.get(reverse('happiness-detail', [yesterday]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), EMPTY_STATS)

        self.put(data={'level': 3})
        modified_entry = {'level': 4}
        self.assertNotEqual({'level': 3}, modified_entry)

        response = self.client.put(
            reverse('happiness-detail', [yesterday]),
            modified_entry,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), _get_stats_from_entries([{'level': 4}]))

    def test_put_with_prior_entry_should_update(self):
        self.login()
        yesterday = now().date() - timedelta(days=1)

        response = self.client.put(
            reverse('happiness-detail', [yesterday]),
            {'level': 3},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), _get_stats_from_entries([{'level': 3}]))

    def test_patch(self):
        yesterday = now().date() - timedelta(days=1)
        self.put(data={'level': 3}, date=yesterday)

        modified_entry = {'level': 4}
        self.assertNotEqual({'level': 3}, modified_entry)

        response = self.client.patch(
            reverse('happiness-detail', [yesterday]),
            modified_entry,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), _get_stats_from_entries([{'level': 4}]))

    def test_patch_without_prior_entry_should_404(self):
        yesterday = now().date() - timedelta(days=1)
        self.login()
        response = self.client.patch(
            reverse('happiness-detail', [yesterday]),
            {'level': 3},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {'detail': 'Not found.'})

    def test_delete(self):
        yesterday = now().date() - timedelta(days=1)
        self.put(data={'level': 3}, date=yesterday)

        response = self.client.delete(reverse('happiness-detail', [yesterday]))
        self.assertEqual(response.status_code, 204)

        response = self.client.get(reverse('happiness-detail', [yesterday]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), EMPTY_STATS)

    def test_delete_without_prior_entry_should_404(self):
        yesterday = now().date() - timedelta(days=1)
        self.login()
        response = self.client.delete(reverse('happiness-detail', [yesterday]))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {'detail': 'Not found.'})


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
