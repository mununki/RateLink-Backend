import graphene
from graphene_django import DjangoObjectType
from account.models import MyUser, RateReader, MyUserProfile
from rate.models import Rate


class MyUserType(DjangoObjectType):
    class Meta:
        model = MyUser


class MyUserProfileType(DjangoObjectType):
    class Meta:
        model = MyUserProfile


class RateReaderType(DjangoObjectType):
    class Meta:
        model = RateReader


class Query(graphene.ObjectType):
    me = graphene.Field(MyUserType, userId=graphene.Int(), )
    inputpersons = graphene.List(MyUserType, userId=graphene.Int(), search=graphene.String(), )

    def resolve_me(self, info, userId, **kwargs):
        try:
            user = MyUser.objects.get(id=userId)
        except:
            raise Exception('Not registered!')

        return user

    def resolve_inputpersons(self, info, userId, search, **kwargs):
        try:
            user = MyUser.objects.get(id=userId)
        except:
            raise Exception('Not existing User!')

        rates = Rate.objects.filter(inputperson=user).order_by('-id')

        showers = RateReader.objects.filter(reader=user)
        showers = MyUser.objects.filter(who_shows__in=showers)
        for shower in showers:
            rates = rates | Rate.objects.filter(inputperson=shower)

        users = MyUser.objects.filter(inputperson__in=rates).distinct()

        users = users.filter(profile__profile_name__istartswith=search)

        return users.order_by('profile__profile_name')
