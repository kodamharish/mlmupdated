from rest_framework import serializers
from .models import *

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    roles = RoleSerializer(many=True, read_only=True)  # For response
    role_ids = serializers.PrimaryKeyRelatedField(     # For creating/updating
        queryset=Role.objects.all(), write_only=True, many=True, source="roles"
    )
    referral_id = serializers.CharField(read_only=True)  # Include in response, not required from input
    #referred_by = serializers.CharField(read_only=True)  # Include in response, not required from input
    level_no = serializers.CharField(read_only=True)  # Include in response, not required from input


    class Meta:
        model = User
        fields = '__all__'



class MeetingRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingRequest
        fields = '__all__'

class ScheduledMeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduledMeeting
        fields = '__all__'



class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = '__all__'


class CarouselItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarouselItem
        fields = '__all__'


class TrainingMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingMaterial
        fields = '__all__'


class PhonenumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Phonenumber
        fields = '__all__'


class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = '__all__'