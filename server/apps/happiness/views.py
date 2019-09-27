from rest_framework import viewsets

from .models import Happiness
from .serializers import HappinessSerializer


class HappinessViewSet(viewsets.ModelViewSet):
    """ List happiness level entries, and CRUD actions. """
    queryset = Happiness.objects.all()
    serializer_class = HappinessSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
