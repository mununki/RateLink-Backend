import os
import graphene
import json
from django.contrib.auth import get_user_model
from django.db.models import Q
from graphene_django import DjangoObjectType
from graphene_file_upload.scalars import Upload
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from rate.models import CNTRtype, Client, Rate
from account.models import RateReader
from countrycity.models import Liner, Location
from django.db.models import Min

RATE_PER_PAGE = 20


class CNTRtypeType(DjangoObjectType):
    class Meta:
        model = CNTRtype


class ClientType(DjangoObjectType):
    class Meta:
        model = Client


class RateType(DjangoObjectType):
    class Meta:
        model = Rate


class Query(graphene.ObjectType):
    cntrtypes = graphene.List(CNTRtypeType, userId=graphene.Int(), search=graphene.String(), )
    clients = graphene.List(ClientType, userId=graphene.Int(), search=graphene.String(), handler=graphene.String(), )
    rates = graphene.List(RateType, userId=graphene.Int(), queryParams=graphene.String(), cursor=graphene.Int(), )
    startDate = graphene.String(userId=graphene.Int(), )
    charts = graphene.List(RateType, userId=graphene.Int(), queryParams=graphene.String(), )

    def resolve_startDate(self, info, userId, **kwargs):
        try:
            user = get_user_model().objects.get(id=userId)
        except:
            raise Exception('Not existing User!')

        rates = Rate.objects.all().exclude(deleted=1)

        qs = rates.filter(inputperson=user)

        showers = RateReader.objects.filter(reader=user)
        showers = get_user_model().objects.filter(who_shows__in=showers)
        qs = qs | rates.filter(inputperson__in=showers)

        startDate = qs.aggregate(Min('effectiveDate'))

        return startDate['effectiveDate__min']

    def resolve_charts(self, info, userId, queryParams, **kwargs):
        try:
            user = get_user_model().objects.get(id=userId)
        except:
            raise Exception('Not existing User!')

        # {"selectedIp":[],"selectedAc":[],"selectedLn":[],"selectedPl":[],"selectedPd":[],"selectedTy":[],"initialSF":"2018-08-31T15:00:00.000Z","initialST":"2018-11-30T14:59:59.999Z"}
        queryParams = json.loads(queryParams)

        if queryParams['selectedPl'] == "" or queryParams['selectedPd'] == "" or queryParams['selectedTy'] == "":

            rates = Rate.objects.none()

            return rates

        else:
            rates = Rate.objects.filter(effectiveDate__gte=parse(queryParams['initialSF']))
            rates = rates.filter(effectiveDate__lte=parse(queryParams['initialST']))

            qs = rates.filter(inputperson=user).order_by('-id')

            showers = RateReader.objects.filter(reader=user)
            showers = get_user_model().objects.filter(who_shows__in=showers)
            qs = qs | rates.filter(inputperson__in=showers)

            qs = qs.exclude(deleted=1)

            pol = Location.objects.get(id=queryParams['selectedPl']['value'])
            pod = Location.objects.get(id=queryParams['selectedPd']['value'])
            type = CNTRtype.objects.get(id=queryParams['selectedTy']['value'])

            filter_args = {}

            filter_args['pol'] = pol
            filter_args['pod'] = pod
            filter_args['type'] = type

            qs = qs.filter(**filter_args)

            return qs

    def resolve_rates(self, info, userId, queryParams, cursor=None, **kwargs):
        try:
            user = get_user_model().objects.get(id=userId)
        except:
            raise Exception('Not existing User!')

        # {"selectedIp":[],"selectedAc":[],"selectedLn":[],"selectedPl":[],"selectedPd":[],"selectedTy":[],"initialSF":"2018-08-31T15:00:00.000Z","initialST":"2018-11-30T14:59:59.999Z"}
        queryParams = json.loads(queryParams)

        rates = Rate.objects.filter(effectiveDate__gte=parse(queryParams['initialSF']))
        rates = rates.filter(effectiveDate__lte=parse(queryParams['initialST']))

        qs = rates.filter(inputperson=user).order_by('-id')

        showers = RateReader.objects.filter(reader=user)
        showers = get_user_model().objects.filter(who_shows__in=showers)
        qs = qs | rates.filter(inputperson__in=showers)

        qs = qs.exclude(deleted=1)

        if len(queryParams['selectedTy']) > 0:
            querysetTy = CNTRtype.objects.none()
            for ty in queryParams['selectedTy']:
                querysetTy = querysetTy | CNTRtype.objects.filter(id=ty['value'])

            qs = qs.filter(type__in=querysetTy)

        if len(queryParams['selectedIp']) > 0:
            querysetIp = get_user_model().objects.none()
            for ip in queryParams['selectedIp']:
                querysetIp = querysetIp | get_user_model().objects.filter(id=ip['value'])

            qs = qs.filter(inputperson__in=querysetIp)

        if len(queryParams['selectedCt']) > 0:
            querysetCt = Client.objects.none()
            for ct in queryParams['selectedCt']:
                querysetCt = querysetCt | Client.objects.filter(id=ct['value'])

            qs = qs.filter(account__in=querysetCt)

        if len(queryParams['selectedLn']) > 0:
            querysetLn = Liner.objects.none()
            for ln in queryParams['selectedLn']:
                querysetLn = querysetLn | Liner.objects.filter(id=ln['value'])

            qs = qs.filter(liner__in=querysetLn)

        if len(queryParams['selectedPl']) > 0:
            querysetPl = Location.objects.none()
            for pl in queryParams['selectedPl']:
                querysetPl = querysetPl | Location.objects.filter(id=pl['value'])

            qs = qs.filter(pol__in=querysetPl)

        if len(queryParams['selectedPd']) > 0:
            querysetPd = Location.objects.none()
            for pd in queryParams['selectedPd']:
                querysetPd = querysetPd | Location.objects.filter(id=pd['value'])

            qs = qs.filter(pod__in=querysetPd)

        qs = qs.order_by('-id')

        if not cursor == None:
            qs = qs.filter(id__lt=cursor)

        qs = qs[:RATE_PER_PAGE]

        return qs

    def resolve_clients(self, info, userId, search, handler=None, **kwargs):

        try:
            user = get_user_model().objects.get(id=userId)
        except:
            raise Exception('Not existing User!')

        if handler == None:
            rates = Rate.objects.filter(inputperson=user)

            showers = RateReader.objects.filter(reader=user)
            showers = get_user_model().objects.filter(who_shows__in=showers)
            rates = rates | Rate.objects.filter(inputperson__in=showers)

            clients = Client.objects.filter(rate__in=rates).distinct()

        if not handler == None:
            clients = Client.objects.filter(salesman=user) | Client.objects.filter(salesman__isnull=True)
            clients = clients.distinct()

        clients = clients.filter(name__istartswith=search).order_by('name')

        return clients

    def resolve_cntrtypes(self, info, search, userId=None, **kwargs):
        types = CNTRtype.objects.all()

        if not userId == None:
            try:
                user = get_user_model().objects.get(id=userId)
            except:
                raise Exception('Not existing User!')

            rates = Rate.objects.filter(inputperson=user)

            showers = RateReader.objects.filter(reader=user)
            showers = get_user_model().objects.filter(who_shows__in=showers)
            rates = rates | Rate.objects.filter(inputperson__in=showers)

            types = CNTRtype.objects.filter(rate__in=rates).distinct().order_by('name')

        types = types.filter(name__istartswith=search)

        return types.order_by('name')


class CUDRate(graphene.Mutation):
    rate = graphene.Field(RateType)

    class Arguments:
        newRate = graphene.String()
        handler = graphene.String()
        rateId = graphene.Int()
        userId = graphene.Int()

    def mutate(self, info, handler, newRate=None, rateId=None, userId=None, **kwargs):

        if handler == "add":
            newRate = json.loads(newRate)

            user = get_user_model().objects.get(id=newRate['selectedIp'][0]['value'])

            for ct in newRate['selectedCt']:
                client = Client.objects.get(id=ct['value'])

                for ln in newRate['selectedLn']:
                    liner = Liner.objects.get(id=ln['value'])

                    for pl in newRate['selectedPl']:
                        pol = Location.objects.get(id=pl['value'])

                        for pd in newRate['selectedPd']:
                            pod = Location.objects.get(id=pd['value'])

                            for ty in newRate['selectedTy']:
                                type = CNTRtype.objects.get(id=ty['value'])

                                rate = Rate(
                                    inputperson=user,
                                    account=client,
                                    liner=liner,
                                    pol=pol,
                                    pod=pod,
                                    type=type,
                                    buying20=newRate['buying20'],
                                    buying40=newRate['buying40'],
                                    buying4H=newRate['buying4H'],
                                    selling20=newRate['selling20'],
                                    selling40=newRate['selling40'],
                                    selling4H=newRate['selling4H'],
                                    loadingFT=newRate['loadingFT'],
                                    dischargingFT=newRate['dischargingFT'],
                                    offeredDate=parse(newRate['initialod']),
                                    effectiveDate=parse(newRate['initialed']),
                                    remark=newRate['remark']
                                )
                                rate.save()

        elif handler == "modify":
            newRate = json.loads(newRate)

            rate = Rate.objects.get(id=rateId)
            user = get_user_model().objects.get(id=newRate['selectedIp'][0]['value'])

            if rate.inputperson == user:
                client = Client.objects.get(id=newRate['selectedCt']['value'])
                liner = Liner.objects.get(id=newRate['selectedLn']['value'])
                pol = Location.objects.get(id=newRate['selectedPl']['value'])
                pod = Location.objects.get(id=newRate['selectedPd']['value'])
                type = CNTRtype.objects.get(id=newRate['selectedTy']['value'])

                rate.account = client
                rate.liner = liner
                rate.pol = pol
                rate.pod = pod
                rate.type = type
                rate.buying20 = newRate['buying20']
                rate.buying40 = newRate['buying40']
                rate.buying4H = newRate['buying4H']
                rate.selling20 = newRate['selling20']
                rate.selling40 = newRate['selling40']
                rate.selling4H = newRate['selling4H']
                rate.loadingFT = newRate['loadingFT']
                rate.dischargingFT = newRate['dischargingFT']
                rate.offeredDate = parse(newRate['initialod'])
                rate.effectiveDate = parse(newRate['initialed'])
                rate.remark = newRate['remark']

                rate.save()
            else:
                raise Exception('Not Authorized!')

        elif handler == "delete":
            rate = Rate.objects.get(id=rateId)
            user = get_user_model().objects.get(id=userId)

            if rate.inputperson == user:
                rate.deleted = 1

                rate.save()
            else:
                raise Exception('Not Authorized!')

        elif handler == "duplicate":
            originRate = Rate.objects.get(id=rateId)
            user = get_user_model().objects.get(id=userId)

            rate = Rate(
                inputperson=user,
                account=originRate.account,
                liner=originRate.liner,
                pol=originRate.pol,
                pod=originRate.pod,
                type=originRate.type,
                buying20=originRate.buying20,
                buying40=originRate.buying40,
                buying4H=originRate.buying4H,
                selling20=originRate.selling20,
                selling40=originRate.selling40,
                selling4H=originRate.selling4H,
                loadingFT=originRate.loadingFT,
                dischargingFT=originRate.dischargingFT,
                offeredDate=originRate.offeredDate,
                effectiveDate=originRate.effectiveDate,
                remark=originRate.remark
            )

            rate.save()

        return CUDRate(rate=rate)


class Mutation(graphene.ObjectType):
    cud_rate = CUDRate.Field()
