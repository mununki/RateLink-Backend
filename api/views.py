from account.models import MyUser, RateReader, MyUserProfile
from rate.models import Rate
from countrycity.models import Location, Liner
from rest_framework import viewsets, views
from api.serializers import UserSerializer, UserCreateSerializer, UserUpdateSerializer, ChangePasswordSerializer, ChangeProfileImageSerializer, RateReaderSerializer, RateUserSerializer, RateSerializer, LocationSerializer, LinerSerializer, RateInputpersonSerializer, RateAccountSerializer, RateLinerSerializer, RatePolSerializer, RatePodSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .permissions import UserPermission, UserCreatePermission, UserUpdatePermission, RatePermission, AjaxPermission
from dateutil.relativedelta import relativedelta
from django.utils import timezone
import dateutil.parser
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Avg
from rest_framework import permissions
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from resizeimage import resizeimage
from rest_framework.parsers import MultiPartParser

class RateReaderViewSet(viewsets.ModelViewSet):
    serializer_class = RateReaderSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('id', 'shower', 'reader',)

    def get_queryset(self):
        showerreader = RateReader.objects.none()

        showerreader = showerreader | RateReader.objects.filter(shower=self.request.user)
        showerreader = showerreader | RateReader.objects.filter(reader=self.request.user)

        return showerreader

    def perform_create(self, serializer):
        serializer.save(shower=self.request.user)


class RateReaderUserView(views.APIView):

    def get(self, request, *args, **kwargs):

        readers = RateReader.objects.filter(shower=self.request.user)
        users = MyUser.objects.filter(who_reads__in=readers)

        serializer = RateUserSerializer(users, many=True)

        return Response(serializer.data)


class RateShowerUserView(views.APIView):

    def get(self, request, *args, **kwargs):

        showers = RateReader.objects.filter(reader=self.request.user)
        users = MyUser.objects.filter(who_shows__in=showers)

        serializer = UserSerializer(users, many=True)

        return Response(serializer.data)


class UserSearchView(views.APIView):

    def get(self, request, *args, **kwargs):
        email_query = self.request.query_params.get('email', None)
        nickname_query = self.request.query_params.get('nickname', None)
        company_query = self.request.query_params.get('company', None)

        filter_args = {}
        if email_query:
            filter_args['email__exact'] = email_query
        if nickname_query:
            filter_args['nickname__exact'] = nickname_query
        if company_query:
            filter_args['profile__company__exact'] = company_query

        users = MyUser.objects.filter(**filter_args)

        if not email_query and not nickname_query and not company_query:
            users = MyUser.objects.none()

        serializer = UserSerializer(users, many=True)

        return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    queryset = MyUser.objects.all()
    serializer_class = UserSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('id', 'email', 'nickname', )
    permission_classes = (UserPermission,)

class UserCreateViewSet(viewsets.ModelViewSet):
    queryset = MyUser.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = (UserCreatePermission,)

class UserUpdateViewSet(viewsets.ModelViewSet):
    queryset = MyUser.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = (UserUpdatePermission,)

class UpdateProfileImage(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = (MultiPartParser,)

    def get_object(self, queryset=None):
        return MyUserProfile.objects.get(owner=self.request.user)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = ChangeProfileImageSerializer(data=request.data)

        if serializer.is_valid():
            img = serializer.validated_data["new_profile_image"]

            pil_image_obj = Image.open(img)
            new_image = resizeimage.resize_cover(pil_image_obj, [100, 100], validate=False)

            new_image_io = BytesIO()
            new_image.save(new_image_io, new_image.format)

            temp_name = img.name

            self.object.image.save(
                temp_name,
                content=ContentFile(new_image_io.getvalue())
            )

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdatePassword(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, queryset=None):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            old_password = serializer.data.get("old_password")
            if not self.object.check_password(old_password):
                return Response({"old_password": ["Wrong Password."]},
                                status=status.HTTP_400_BAD_REQUEST)
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        'user': UserSerializer(user, context={'request': request}).data
    }

class RateChartView(views.APIView):

    def get(self, request, *args, **kwargs):
        # 로그인 유저에게 운임을 보여주는 Shower query
        showers = RateReader.objects.filter(reader=self.request.user).distinct()
        # Shower 한 명 씩 입력한 운임 정보를 rates 객체에 취합
        rates = Rate.objects.none()
        for shower in showers:
            userinstance = MyUser.objects.get(email=shower.shower.email)
            rates = rates | Rate.objects.filter(inputperson=userinstance)

        rates = rates | Rate.objects.filter(inputperson=self.request.user)

        liner_list = []
        liner_query = self.request.query_params.get('liner', None)

        if liner_query:
            liners_list = liner_query.split('|')
            for liner in liners_list:
                x = Liner.objects.filter(name=liner).values_list('name', flat=True)
                for y in x:
                    liner_list.append(y)
        else:
            liner_list = []

        pol_list = []
        pol_query = self.request.query_params.get('pol', None)
        if pol_query:
            pol_list = pol_query.split('|')

        pod_list = []
        pod_query = self.request.query_params.get('pod', None)
        if pod_query:
            pod_list = pod_query.split('|')

        sf = self.request.query_params.get('search_from', None)
        st = self.request.query_params.get('search_to', None)

        filter_args = {}

        if liner_list != []:
            filter_args['liner__in'] = liner_list
        if pol_list != []:
            filter_args['pol__in'] = pol_list
        if pod_list != []:
            filter_args['pod__in'] = pod_list

        if sf:
            fullsf = sf + '-01'
            searchvalue_sf = dateutil.parser.parse(fullsf).date()
            filter_args['effectiveDate__gte'] = searchvalue_sf
        else:
            searchvalue_sf = timezone.now().replace(day=1) + relativedelta(months=-1)  # 전달 1일
            filter_args['effectiveDate__gte'] = searchvalue_sf
        if st:
            fullst = st + '-01'
            searchvalue_st = dateutil.parser.parse(fullst).date().replace(day=1) + relativedelta(months=1) - relativedelta(days=1)
            filter_args['effectiveDate__lte'] = searchvalue_st

        filtered_rates = rates.filter(**filter_args).exclude(deleted=1)

        query_type = self.request.query_params.get('type', None) # type : 20 -> buying20 , 40 -> buying40 , 4H -> buying4H
        liners = filtered_rates.values('liner').distinct()

        period_sf = sf.split('-')
        period_st = st.split('-')
        gap_year = int(period_st[0]) - int(period_sf[0])
        gap_month = int(period_st[1]) - int(period_sf[1])
        gap_total = gap_year * 12 + gap_month + 1

        context = {}
        context_liners = []
        liner_avg_rate = []
        for i in range(gap_total):
            item = {}
            temp_args = {}
            div = int((int(period_sf[1]) - 1 + i) / 12)
            if ((int(period_sf[1]) - 1 + i) % 12 + 1) < 10:
                t_sf = str(int(period_sf[0]) + div) + '0' + str((int(period_sf[1]) - 1 + i) % 12 + 1)
                temp_sf = str(int(period_sf[0]) + div) + '0' + str((int(period_sf[1]) - 1 + i) % 12 + 1) + '01'
                query_sf = dateutil.parser.parse(temp_sf).date()
                query_st = dateutil.parser.parse(temp_sf).date().replace(day=1) + relativedelta(months=1) - relativedelta(days=1)
            else:
                t_sf = str(int(period_sf[0]) + div) + str((int(period_sf[1]) - 1 + i) % 12 + 1)
                temp_sf = str(int(period_sf[0]) + div) + str((int(period_sf[1]) - 1 + i) % 12 + 1) + '01'
                query_sf = dateutil.parser.parse(temp_sf).date()
                query_st = dateutil.parser.parse(temp_sf).date().replace(day=1) + relativedelta(months=1) - relativedelta(days=1)

            temp_args['effectiveDate__gte'] = query_sf
            temp_args['effectiveDate__lte'] = query_st

            item['month'] = t_sf

            if query_type == '20':
                temp = filtered_rates.filter(**temp_args).exclude(buying20=0).aggregate(avg_rate=Avg('buying20'))['avg_rate']
                if temp:
                    item['Market'] = int(temp)
                else:
                    item['Market'] = temp

            elif query_type == '40':
                temp = filtered_rates.filter(**temp_args).exclude(buying40=0).aggregate(avg_rate=Avg('buying40'))['avg_rate']
                if temp:
                    item['Market'] = int(temp)
                else:
                    item['Market'] = temp

            elif query_type == '4H':
                temp = filtered_rates.filter(**temp_args).exclude(buying4H=0).aggregate(avg_rate=Avg('buying4H'))['avg_rate']
                if temp:
                    item['Market'] = int(temp)
                else:
                    item['Market'] = temp

            for liner in liners:
                temp_args['liner'] = liner['liner']

                if query_type == '20':
                    temp = filtered_rates.filter(**temp_args).exclude(buying20=0).aggregate(avg_rate=Avg('buying20'))['avg_rate']
                    if temp:
                        item[liner['liner']] = int(temp)
                    else:
                        item[liner['liner']] = temp

                elif query_type == '40':
                    temp = filtered_rates.filter(**temp_args).exclude(buying40=0).aggregate(avg_rate=Avg('buying40'))['avg_rate']
                    if temp:
                        item[liner['liner']] = int(temp)
                    else:
                        item[liner['liner']] = temp
                elif query_type == '4H':
                    temp = filtered_rates.filter(**temp_args).exclude(buying4H=0).aggregate(avg_rate=Avg('buying4H'))['avg_rate']
                    if temp:
                        item[liner['liner']] = int(temp)
                    else:
                        item[liner['liner']] = temp

            liner_avg_rate.append(item)

        context_liners.append('Market')
        for liner in liners:
            context_liners.append(liner['liner'])

        context['type'] = query_type
        context['pol'] = self.request.query_params.get('pol', None)
        context['pod'] = self.request.query_params.get('pod', None)
        context['liners'] = context_liners
        context['result'] = liner_avg_rate
        return Response(context)


class RateViewSet(viewsets.ModelViewSet):
    serializer_class = RateSerializer
    permission_classes = (RatePermission,)

    def get_queryset(self):
        # 로그인 유저에게 운임을 보여주는 Shower query
        showers = RateReader.objects.filter(reader=self.request.user).distinct()
        # Shower 한 명 씩 입력한 운임 정보를 rates 객체에 취합
        rates = Rate.objects.none()
        for shower in showers:
            userinstance = MyUser.objects.get(email=shower.shower.email)
            rates = rates | Rate.objects.filter(inputperson=userinstance)

        rates = rates | Rate.objects.filter(inputperson=self.request.user)

        inputperson_list = []
        inputpersons = self.request.query_params.get('inputperson', None)
        if inputpersons:
            inputpersons_list = inputpersons.split('|')
            for inputperson in inputpersons_list:
                x = MyUser.objects.get(profile__profile_name=inputperson)
                inputperson_list.append(x)
        else:
            inputperson_list = []

        account_list = []
        accounts = self.request.query_params.get('account', None)
        if accounts:
            account_list = accounts.split('|')


        liner_list = []
        liner_query = self.request.query_params.get('liner', None)
        if liner_query:
            liners_list = liner_query.split('|')
            for liner in liners_list:
                x = Liner.objects.filter(label=liner).values_list('name', flat=True)
                for y in x:
                    liner_list.append(y)
        else:
            liner_list = []

        pol_list = []
        pol_query = self.request.query_params.get('pol', None)
        if pol_query:
            pol_list = pol_query.split('|')

        pod_list = []
        pod_query = self.request.query_params.get('pod', None)
        if pod_query:
            pod_list = pod_query.split('|')

        sf = self.request.query_params.get('search_from', None)
        st = self.request.query_params.get('search_to', None)

        filter_args = {}

        if inputperson_list != []:
            filter_args['inputperson__in'] = inputperson_list
        if account_list != []:
            filter_args['account__in'] = account_list
        if liner_list != []:
            filter_args['liner__in'] = liner_list
        if pol_list != []:
            filter_args['pol__in'] = pol_list
        if pod_list != []:
            filter_args['pod__in'] = pod_list

        if sf:
            searchvalue_sf = dateutil.parser.parse(sf).date()
            filter_args['effectiveDate__gte'] = searchvalue_sf

        if st:
            searchvalue_st = dateutil.parser.parse(st).date()
            filter_args['effectiveDate__lte'] = searchvalue_st

        queryset = rates.filter(**filter_args).order_by('-id').exclude(deleted=1)

        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data.get("items") if 'items' in request.data else request.data
        many = isinstance(data, list)
        serializer = self.get_serializer(data=data, many=many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(inputperson=self.request.user)

class RateInputpersonViewSet(viewsets.ModelViewSet):
    serializer_class = RateInputpersonSerializer
    pagination_class = None
    permission_classes = (AjaxPermission,)

    def get_queryset(self):
        # 로그인 유저에게 운임을 보여주는 Shower query
        showers = RateReader.objects.filter(reader=self.request.user).distinct()
        # Shower 한 명 씩 입력한 운임 정보를 rates 객체에 취합
        rates = Rate.objects.none()
        for shower in showers:
            userinstance = MyUser.objects.get(email=shower.shower.email)
            rates = rates | Rate.objects.filter(inputperson=userinstance).exclude(deleted=1)

        rates = rates | Rate.objects.filter(inputperson=self.request.user).exclude(deleted=1)

        queryset = rates.distinct('inputperson')

        return queryset


class RateAccountViewSet(viewsets.ModelViewSet):
    serializer_class = RateAccountSerializer
    pagination_class = None
    permission_classes = (AjaxPermission,)

    def get_queryset(self):
        # 로그인 유저에게 운임을 보여주는 Shower query
        showers = RateReader.objects.filter(reader=self.request.user).distinct()
        # Shower 한 명 씩 입력한 운임 정보를 rates 객체에 취합
        rates = Rate.objects.none()
        for shower in showers:
            userinstance = MyUser.objects.get(email=shower.shower.email)
            rates = rates | Rate.objects.filter(inputperson=userinstance).exclude(deleted=1)

        rates = rates | Rate.objects.filter(inputperson=self.request.user).exclude(deleted=1)

        queryset = rates.values('account').distinct().order_by('account')

        return queryset


class RateLinerViewSet(viewsets.ModelViewSet):
    serializer_class = RateLinerSerializer
    pagination_class = None
    permission_classes = (AjaxPermission,)

    def get_queryset(self):
        # 로그인 유저에게 운임을 보여주는 Shower query
        showers = RateReader.objects.filter(reader=self.request.user).distinct()
        # Shower 한 명 씩 입력한 운임 정보를 rates 객체에 취합
        rates = Rate.objects.none()
        for shower in showers:
            userinstance = MyUser.objects.get(email=shower.shower.email)
            rates = rates | Rate.objects.filter(inputperson=userinstance).exclude(deleted=1)

        rates = rates | Rate.objects.filter(inputperson=self.request.user).exclude(deleted=1)

        liner_filtered = rates.values('liner').distinct()

        liner_args = {}
        liner_temp = []
        for liner in liner_filtered:
            liner_temp.append(liner['liner'])
        liner_args['name__in'] = liner_temp

        queryset = Liner.objects.filter(**liner_args).values('label').order_by('label')

        return queryset


class RatePolViewSet(viewsets.ModelViewSet):
    serializer_class = RatePolSerializer
    pagination_class = None
    permission_classes = (AjaxPermission,)

    def get_queryset(self):
        # 로그인 유저에게 운임을 보여주는 Shower query
        showers = RateReader.objects.filter(reader=self.request.user).distinct()
        # Shower 한 명 씩 입력한 운임 정보를 rates 객체에 취합
        rates = Rate.objects.none()
        for shower in showers:
            userinstance = MyUser.objects.get(email=shower.shower.email)
            rates = rates | Rate.objects.filter(inputperson=userinstance).exclude(deleted=1)

        rates = rates | Rate.objects.filter(inputperson=self.request.user).exclude(deleted=1)

        queryset = rates.values('pol').distinct().order_by('pol')

        return queryset


class RatePodViewSet(viewsets.ModelViewSet):
    serializer_class = RatePodSerializer
    pagination_class = None
    permission_classes = (AjaxPermission,)

    def get_queryset(self):
        # 로그인 유저에게 운임을 보여주는 Shower query
        showers = RateReader.objects.filter(reader=self.request.user).distinct()
        # Shower 한 명 씩 입력한 운임 정보를 rates 객체에 취합
        rates = Rate.objects.none()
        for shower in showers:
            userinstance = MyUser.objects.get(email=shower.shower.email)
            rates = rates | Rate.objects.filter(inputperson=userinstance).exclude(deleted=1)

        rates = rates | Rate.objects.filter(inputperson=self.request.user).exclude(deleted=1)

        queryset = rates.values('pod').distinct().order_by('pod')

        return queryset

class RateHeaderView(views.APIView):

    def get(self, request, *args, **kwargs):
        # 로그인 유저에게 운임을 보여주는 Shower query
        showers = RateReader.objects.filter(reader=self.request.user).distinct()
        # Shower 한 명 씩 입력한 운임 정보를 rates 객체에 취합
        rates = Rate.objects.none()
        for shower in showers:
            userinstance = MyUser.objects.get(email=shower.shower.email)
            rates = rates | Rate.objects.filter(inputperson=userinstance)

        rates = rates | Rate.objects.filter(inputperson=self.request.user)

        handler = self.request.query_params.get('handler', None)
        searchkw = self.request.query_params.get('searchkw', None)

        results = []

        if handler == "inputperson":
            ips = rates.values('inputperson__profile__profile_name').distinct().order_by('inputperson__profile__profile_name')
            
            for ip in ips:
                items = {}
                items['label'] = ip['inputperson__profile__profile_name']
                items['value'] = ip['inputperson__profile__profile_name']
                results.append(items)

        if handler == "account":
            acs = rates.values('account').distinct().order_by('account')
            for ac in acs:
                items = {}
                items['label'] = ac['account']
                items['value'] = ac['account']
                results.append(items)

        if handler == "liner":
            liner_filtered = rates.values('liner').distinct()

            liner_args = {}
            liner_temp = []
            for liner in liner_filtered:
                liner_temp.append(liner['liner'])
            liner_args['name__in'] = liner_temp

            lns = Liner.objects.filter(**liner_args).values('label').order_by('label')
            for ln in lns:
                items = {}
                items['label'] = ln['label']
                items['value'] = ln['label']
                results.append(items)

        if handler == "linerinput":
            liner_filtered = Liner.objects.all().order_by('label')

            for ln in liner_filtered:
                items = {}
                items['label'] = ln.label
                items['value'] = ln.name
                results.append(items)

        if handler == "pol":
            pols = rates.values('pol').distinct().order_by('pol')
            for pol in pols:
                items = {}
                items['label'] = pol['pol']
                items['value'] = pol['pol']
                results.append(items)

        if handler == "pod":
            pods = rates.values('pod').distinct().order_by('pod')
            for pod in pods:
                items = {}
                items['label'] = pod['pod']
                items['value'] = pod['pod']
                results.append(items)

        if handler == "locationinput":

            if searchkw:
                location_args = {}
                location_args['name__istartswith'] = searchkw
                queryset = Location.objects.filter(**location_args).order_by('label')

            else:
                queryset = Location.objects.none()

            for lc in queryset:
                items = {}
                items['label'] = lc.name
                items['value'] = lc.name
                results.append(items)

        return Response(results)


class LinerViewSet(viewsets.ModelViewSet):
    queryset = Liner.objects.all()
    serializer_class = LinerSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('id', 'name', 'label', )
    permission_classes = (AjaxPermission,)

class LocationViewSet(viewsets.ModelViewSet):
    serializer_class = LocationSerializer
    pagination_class = None
    permission_classes = (AjaxPermission,)

    def get_queryset(self):
        location_query = self.request.query_params.get('location', None)
        if location_query:
            location_args = {}
            location_args['name__istartswith'] = location_query
            queryset = Location.objects.filter(**location_args)

            return queryset

        else:
            queryset = Location.objects.none()

            return queryset