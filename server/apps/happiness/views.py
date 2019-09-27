from django.db.utils import IntegrityError
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

    def list(self, request):
        return Response(get_stats())

    def create(self, request):
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
