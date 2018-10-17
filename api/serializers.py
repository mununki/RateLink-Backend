from account.models import MyUser, MyUserProfile, RateReader
from rate.models import Rate
from countrycity.models import Location, Liner
from rest_framework import serializers, status
from django.contrib.auth.password_validation import validate_password

class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MyUserProfile
        fields = ('id', 'profile_name', 'job_boolean', 'company', 'image')

class RateReaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = RateReader
        fields = ('id', 'shower', 'reader')

class RateUserSerializer(serializers.HyperlinkedModelSerializer):
    profile = ProfileSerializer(many=False)
    who_reads = RateReaderSerializer(many=True)

    class Meta:
        model = MyUser
        fields = ('id', 'email', 'nickname', 'profile', 'who_reads')

class UserSerializer(serializers.HyperlinkedModelSerializer):
    profile = ProfileSerializer(many=False)

    class Meta:
        model = MyUser
        fields = ('id', 'email', 'nickname', 'profile')

class UserCreateSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(many=False)

    class Meta:
        model = MyUser
        fields = ('id', 'email', 'nickname', 'password', 'profile')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        password = validated_data.pop('password')
        myuser = MyUser.objects.create(**validated_data)
        myuser.set_password(password)
        myuser.save()
        MyUserProfile.objects.create(owner=myuser, **profile_data)

        return myuser

class UserUpdateSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(many=False)

    class Meta:
        model = MyUser
        fields = ('id', 'profile')

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile')
        profile = instance.profile

        instance.email = validated_data.get('email', instance.email)
        instance.nickname = validated_data.get('nickname', instance.nickname)

        instance.save()

        profile.profile_name = profile_data.get(
            'profile_name',
            profile.profile_name
        )
        profile.company = profile_data.get(
            'company',
            profile.company
        )
        profile.job_boolean = profile_data.get(
            'job_boolean',
            profile.job_boolean
        )
        profile.save()

        return instance

class ChangeProfileImageSerializer(serializers.Serializer):
    new_profile_image = serializers.ImageField(use_url=True)

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value

class RateSerializer(serializers.ModelSerializer):
    inputperson = UserSerializer(read_only=True)

    class Meta:
        model = Rate
        fields = (
            'id',
            'inputperson',
            'account',
            'liner',
            'pol',
            'pod',
            'buying20',
            'selling20',
            'buying40',
            'selling40',
            'buying4H',
            'selling4H',
            'loadingFT',
            'dischargingFT',
            'effectiveDate',
            'offeredDate',
            'recordedDate',
            'remark',
            'deleted',
        )

class RateInputpersonSerializer(serializers.ModelSerializer):
    inputperson = serializers.CharField(source='inputperson.profile.profile_name')

    class Meta:
        model = Rate
        fields = (
            'inputperson',
        )

class RateAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rate
        fields = (
            'account',
        )

class RateLinerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Liner
        fields = (
            'label',
        )

class RatePolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rate
        fields = (
            'pol',
        )

class RatePodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rate
        fields = (
            'pod',
        )

class LinerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Liner
        fields = ('id', 'name', 'label')

class LocationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Location
        fields = ('id', 'name', 'country', 'label')

