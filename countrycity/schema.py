import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth import get_user_model
from account.models import RateReader
from countrycity.models import Location, Liner
from rate.models import Rate


class LocationType(DjangoObjectType):
    class Meta:
        model = Location


class LinerType(DjangoObjectType):
    class Meta:
        model = Liner


class Query(graphene.ObjectType):
    # handler : 'pol' or 'pod' with userId will get user and shower's pol or pod Location queryset
    locations = graphene.List(LocationType, search=graphene.String(), userId=graphene.Int(), handler=graphene.String(), )
    liners = graphene.List(LinerType, search=graphene.String(), userId=graphene.Int(), )

    def resolve_locations(self, info, search=None, userId=None, handler=None, **kwargs):
        qs = Location.objects.all()

        if not userId == None:
            try:
                user = get_user_model().objects.get(id=userId)
            except:
                raise Exception('Not existing User!')

            rates = Rate.objects.filter(inputperson=user).order_by('-id')

            showers = RateReader.objects.filter(reader=user)
            showers = get_user_model().objects.filter(who_shows__in=showers)
            for shower in showers:
                rates = rates | Rate.objects.filter(inputperson=shower)

            if handler == 'pol':
                qs = qs.filter(ratepol__in=rates).distinct()
            elif handler == 'pod':
                qs = qs.filter(ratepod__in=rates).distinct()

        if not search == None:
            qs = qs.filter(name__istartswith=search)

        return qs.order_by('name')

    def resolve_liners(self, info, search=None, userId=None, **kwargs):
        qs = Liner.objects.all()

        if not userId == None:
            try:
                user = get_user_model().objects.get(id=userId)
            except:
                raise Exception('Not existing User!')

            rates = Rate.objects.filter(inputperson=user).order_by('-id')

            showers = RateReader.objects.filter(reader=user)
            showers = get_user_model().objects.filter(who_shows__in=showers)
            for shower in showers:
                rates = rates | Rate.objects.filter(inputperson=shower)

            qs = qs.filter(rate__in=rates).distinct()

        if not search == None:
            qs = qs.filter(name__istartswith=search) | qs.filter(label__istartswith=search)

        return qs.order_by('label')
