from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import Event, RSVP, Review
from datetime import timedelta, datetime
from django.utils import timezone


class EventAPITest(APITestCase):
    def setUp(self):
        # create users
        self.organizer = User.objects.create_user(username='org', password='testpass')
        self.other = User.objects.create_user(username='other', password='testpass')
        self.invited = User.objects.create_user(username='invited', password='testpass')

        # public event
        now = timezone.now()
        self.public_event = Event.objects.create(
            title='Public', description='Public event', organizer=self.organizer,
            location='NY', start_time=now + timedelta(days=1), end_time=now + timedelta(days=1, hours=2), is_public=True
        )

        # private event
        self.private_event = Event.objects.create(
            title='Private', description='Private event', organizer=self.organizer,
            location='LA', start_time=now + timedelta(days=2), end_time=now + timedelta(days=2, hours=2), is_public=False
        )
        self.private_event.invited_users.add(self.invited)

    def obtain_token(self, username, password='testpass'):
        url = reverse('token_obtain_pair')
        resp = self.client.post(url, {'username': username, 'password': password}, format='json')
        from django.urls import reverse
        from rest_framework import status
        from rest_framework.test import APITestCase
        from django.contrib.auth.models import User
        from .models import Event, RSVP, Review
        from datetime import timedelta, datetime
        from django.utils import timezone


        class EventAPITest(APITestCase):
            def setUp(self):
                # create users
                self.organizer = User.objects.create_user(username='org', password='testpass')
                self.other = User.objects.create_user(username='other', password='testpass')
                self.invited = User.objects.create_user(username='invited', password='testpass')

                # public event
                now = timezone.now()
                self.public_event = Event.objects.create(
                    title='Public', description='Public event', organizer=self.organizer,
                    location='NY', start_time=now + timedelta(days=1), end_time=now + timedelta(days=1, hours=2), is_public=True
                )

                # private event
                self.private_event = Event.objects.create(
                    title='Private', description='Private event', organizer=self.organizer,
                    location='LA', start_time=now + timedelta(days=2), end_time=now + timedelta(days=2, hours=2), is_public=False
                )
                self.private_event.invited_users.add(self.invited)

            def obtain_token(self, username, password='testpass'):
                url = reverse('token_obtain_pair')
                resp = self.client.post(url, {'username': username, 'password': password}, format='json')
                return resp.data.get('access')

            def test_list_public_events_anonymous(self):
                url = reverse('event-list')
                resp = self.client.get(url)
                self.assertEqual(resp.status_code, status.HTTP_200_OK)
                # only public event should be visible to anonymous
                titles = [item['title'] for item in resp.data['results']]
                self.assertIn('Public', titles)
                self.assertNotIn('Private', titles)

            def test_private_event_visible_to_invited(self):
                token = self.obtain_token('invited')
                self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
                url = reverse('event-list')
                resp = self.client.get(url)
                titles = [item['title'] for item in resp.data['results']]
                self.assertIn('Private', titles)

            def test_create_event_authenticated(self):
                token = self.obtain_token('other')
                self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
                url = reverse('event-list')
                now = timezone.now()
                data = {
                    'title': 'New', 'description': 'desc', 'location': 'X',
                    'start_time': (now + timedelta(days=3)).isoformat(), 'end_time': (now + timedelta(days=3, hours=1)).isoformat(), 'is_public': True
                }
                resp = self.client.post(url, data, format='json')
                self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
                self.assertEqual(resp.data['organizer'], 'other')

            def test_organizer_can_edit_event(self):
                token = self.obtain_token('org')
                self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
                url = reverse('event-detail', args=[self.public_event.pk])
                resp = self.client.patch(url, {'title': 'Updated'}, format='json')
                self.assertEqual(resp.status_code, status.HTTP_200_OK)
                self.public_event.refresh_from_db()
                self.assertEqual(self.public_event.title, 'Updated')

            def test_non_organizer_cannot_edit(self):
                token = self.obtain_token('other')
                self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
                url = reverse('event-detail', args=[self.public_event.pk])
                resp = self.client.patch(url, {'title': 'Hacked'}, format='json')
                self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

            def test_rsvp_and_update(self):
                token = self.obtain_token('other')
                self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
                url = reverse('event-rsvp', args=[self.public_event.pk])
                resp = self.client.post(url, {'status': 'Going'}, format='json')
                self.assertEqual(resp.status_code, status.HTTP_200_OK)
                self.assertEqual(resp.data['status'], 'Going')

                # organizer updates other user's rsvp
                token2 = self.obtain_token('org')
                self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token2}')
                url2 = reverse('event-rsvp-update', args=[self.public_event.pk, self.other.pk])
                resp2 = self.client.patch(url2, {'status': 'Maybe'}, format='json')
                self.assertEqual(resp2.status_code, status.HTTP_200_OK)
                self.assertEqual(resp2.data['status'], 'Maybe')

            def test_review_create_and_list(self):
                token = self.obtain_token('other')
                self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
                url = reverse('event-reviews', args=[self.public_event.pk])
                resp = self.client.post(url, {'rating': 5, 'comment': 'Great!'}, format='json')
                self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
                # list reviews
                url2 = reverse('event-list_reviews', args=[self.public_event.pk])
                resp2 = self.client.get(url2)
                self.assertEqual(resp2.status_code, status.HTTP_200_OK)
                self.assertTrue(any(r['comment'] == 'Great!' for r in resp2.data['results']))