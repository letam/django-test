from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import Happiness
from .serializers import HappinessSerializer


class HappinessViewSet(viewsets.ModelViewSet):
    """ List happiness level entries, and CRUD actions. """
    queryset = Happiness.objects.all()
    serializer_class = HappinessSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
