from rest_framework import serializers

from .models import CustomUser, Organization, Event


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'name', 'qrcode']


class CustomUserSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer()

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'password', 'firstname', 'lastname', 'organization']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        org_data = validated_data.pop('organization')
        org_name = org_data.get('name', None)
        if org_name:
            org = Organization.objects.get(name=org_name)
        else:
            raise serializers.ValidationError("Missing organization id")
        user = CustomUser.objects.create(
            firstname=validated_data['firstname'],
            lastname=validated_data['lastname'],
            email=validated_data['email'],
            password=validated_data['password'],
            organization=org
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'user', 'qr_data', 'timestamp', 'is_entry']
