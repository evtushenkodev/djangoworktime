from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Organization, User, Event
from .serializers import OrganizationSerializer, UserSerializer, EventSerializer


class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        instance.generate_qr_code()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    @action(detail=False, methods=['post'])
    def create_from_qr(self, request):
        qr_data = request.data.get('qr_data')
        user = request.user
        org_id, is_entry_str = qr_data.split('-')
        is_entry = is_entry_str == 'entry'
        organization = Organization.objects.get(id=int(org_id))
        event = Event.objects.create(user=user, organization=organization, is_entry=is_entry)
        serializer = self.serializer_class(event)
        return Response(serializer.data)
