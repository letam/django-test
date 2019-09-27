from dateutil.parser import parse as parse_date

from django.db.utils import IntegrityError
from django.http import Http404
from django.utils import timezone

from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .models import Happiness
from .serializers import HappinessSerializer
from .services import get_stats


class HappinessViewSet(viewsets.ModelViewSet):
    """ List happiness level entries, and CRUD actions. """

    queryset = Happiness.objects.all()
    serializer_class = HappinessSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'date'

    def get_object(self):
        date = self.kwargs.get('date')
        if date:
            try:
                parse_date(date)
            except ValueError as e:
                raise ValidationError('Invalid date provided.')
        else:
            date = timezone.now().date()
        obj = Happiness.objects.filter(user=self.request.user, date=date).first()
        if not obj:
            if self.action == 'update':
                return Happiness(user=self.request.user, date=date)
            else:
                raise Http404
        return obj

    def list(self, request):
        """
        Return stats for today.
        """
        return Response(get_stats())

    def create(self, request):
        """
        Create entry for user's happiness level for today and return stats.
        """
        response = super().create(request)
        response.data = get_stats()
        return response

    def perform_create(self, serializer):
        today = timezone.now().date()
        try:
            serializer.save(user=self.request.user, date=today)
        except IntegrityError as e:
            raise ValidationError(
                'You have already submitted your happiness level for today.'
            )

    def retrieve(self, request, date):
        """
        Retrieve stats for the date.
        """
        try:
            parse_date(date)
        except ValueError as e:
            raise ValidationError('Invalid date provided.')
        return Response(get_stats(date))

    def update(self, request, date=None, *args, **kwargs):
        """
        Replace or partially update the user's entry for the date and return stats.
        """
        response = super().update(request, date, *args, **kwargs)
        response.data = get_stats(date)
        return response
