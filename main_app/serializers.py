from rest_framework import serializers, viewsets
from rest_framework.response import Response

from .models import Organization, User, Event


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'name', 'qrcode']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'firstname', 'lastname', 'organization', 'login', 'password']


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'user', 'organization', 'timestamp', 'is_entry']


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

    def create(self, request, *args, **kwargs):
        qr_data = request.data['qr_data']
        user_id = request.data['user_id']
        user = User.objects.get(id=user_id)
        org_id, is_entry_str = qr_data.split('-')
        is_entry = is_entry_str == 'entry'
        organization = Organization.objects.get(id=int(org_id))
        event = Event(user=user, organization=organization, is_entry=is_entry)
        event.save()
        serializer = EventSerializer(event)
        return Response(serializer.data)
