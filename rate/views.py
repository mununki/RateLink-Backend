from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from .models import Rate
from .forms import PostRateForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from dateutil.relativedelta import relativedelta
import dateutil.parser
from account.models import MyUser, RateReader
from countrycity.models import Liner
from django.contrib import messages
from account.models import MyUserProfile
from django.utils import timezone
import re


def rateSearchedList(request):
    if request.user.is_authenticated:

        MOBILE_AGENT_RE = re.compile(r'.*(iphone|mobile|androidtouch)',re.IGNORECASE)
        if MOBILE_AGENT_RE.match(request.META['HTTP_USER_AGENT']):
            is_mobile = True
        else:
            is_mobile = False

        # 로그인 유저에게 운임을 보여주는 Shower query
        showers = RateReader.objects.filter(reader=request.user).distinct()
        # Shower 한 명 씩 입력한 운임 정보를 rates 객체에 취합
        rates = Rate.objects.none()
        for shower in showers:
            userinstance = MyUser.objects.get(email=shower.shower.email)
            rates = rates | Rate.objects.filter(inputperson=userinstance)

        rates = rates | Rate.objects.filter(inputperson=request.user)

        if request.GET.get('pk'): # 수정 시도 후 취소한 경우
            pk = request.GET.get('pk')
            try:
                modifiedrate = rates.get(pk=pk)
            except:
                modifiedrate = Rate.objects.none()

            html = render_to_string('rateform_modify_ajax_done.html', {'modifiedrate': modifiedrate, 'is_mobile':is_mobile},)
            result = {'html': html}
            return JsonResponse(result)

        if request.GET.getlist('inputperson'):
            inputpersons = request.GET.getlist('inputperson')
            inputperson_list = []
            for inputperson in inputpersons:
                x = MyUser.objects.filter(profile__profile_name=inputperson)
                for y in x:
                    inputperson_list.append(y)

        else:
            inputperson_list = []

        account_list = request.GET.getlist('account')

        if request.GET.getlist('liner'):
            liners = request.GET.getlist('liner')
            liner_list = []
            for liner in liners:
                x = Liner.objects.filter(label=liner).values_list('name', flat=True)
                for y in x:
                    liner_list.append(y)

        else:
            liner_list = []

        pol_list = request.GET.getlist('pol')
        pod_list = request.GET.getlist('pod')
        sf = request.GET.get('search_from')
        st = request.GET.get('search_to')

        # 참조 전 최초 선언
        searchvalue_ip = []
        searchvalue_ac = []
        searchvalue_ln = []
        searchvalue_pl = []
        searchvalue_pd = []
        searchvalue_st = []

        filter_args = {}

        if inputperson_list != [] and inputperson_list != ['-']:
            filter_args['inputperson__in'] = inputperson_list
            searchvalue_ip = request.GET.getlist('inputperson')
        if account_list != [] and account_list != ['-']:
            filter_args['account__in'] = account_list
            searchvalue_ac = request.GET.getlist('account')
        if liner_list != [] and liner_list != ['-']:
            filter_args['liner__in'] = liner_list
            searchvalue_ln = request.GET.getlist('liner')
        if pol_list != [] and pol_list != ['-']:
            filter_args['pol__in'] = pol_list
            searchvalue_pl = request.GET.getlist('pol')
        if pod_list != [] and pod_list != ['-']:
            filter_args['pod__in'] = pod_list
            searchvalue_pd = request.GET.getlist('pod')
        if sf:
            searchvalue_sf = dateutil.parser.parse(sf).date()
            filter_args['effectiveDate__gte'] = searchvalue_sf
        else:
            searchvalue_sf = timezone.now().replace(day=1) + relativedelta(months=-1) # 전달 1일
            filter_args['effectiveDate__gte'] = searchvalue_sf
        if st:
            searchvalue_st = dateutil.parser.parse(st).date()
            filter_args['effectiveDate__lte'] = searchvalue_st
        # else:
        #     searchvalue_st = timezone.now().replace(day=1) + relativedelta(months=+1, days=-1) # 앞달 말일

        filtered_ordered_rates = rates.filter(**filter_args).order_by('-id').exclude(deleted=1)

        loginuser = request.user

        page = request.GET.get('page', 1)
        paginator = Paginator(filtered_ordered_rates, 20)
        try:
            rates_paginated = paginator.page(page)
        except PageNotAnInteger:
            rates_paginated = paginator.page(1)
        except EmptyPage:
            rates_paginated = paginator.page(paginator.num_pages)

        try:
            profile = MyUserProfile.objects.get(owner=request.user)
        except:
            profile = False

        inputperson_unique = filtered_ordered_rates.order_by('inputperson__profile__profile_name').values('inputperson__profile__profile_name').distinct()
        account_unique = filtered_ordered_rates.order_by('account').values('account').distinct()
        liner_filtered = filtered_ordered_rates.order_by('liner').values('liner').distinct()

        liner_args = {}
        liner_temp = []
        for liner in liner_filtered:
            liner_temp.append(liner['liner'])
        liner_args['name__in'] = liner_temp

        liner_unique = Liner.objects.filter(**liner_args).order_by('label').values('label')

        pol_unique = filtered_ordered_rates.order_by('pol').values('pol').distinct()
        pod_unique = filtered_ordered_rates.order_by('pod').values('pod').distinct()
        context = {
            'rates_paginated': rates_paginated,
            'inputperson_unique': inputperson_unique,
            'account_unique': account_unique,
            'liner_unique': liner_unique,
            'pol_unique': pol_unique,
            'pod_unique': pod_unique,
            'loginuser': loginuser,
            'searchvalue_ip': searchvalue_ip,
            'searchvalue_ac': searchvalue_ac,
            'searchvalue_ln': searchvalue_ln,
            'searchvalue_pl': searchvalue_pl,
            'searchvalue_pd': searchvalue_pd,
            'searchvalue_sf': searchvalue_sf,
            'searchvalue_st': searchvalue_st,
            'profile': profile,
            'is_mobile': is_mobile,
        }

        if (not request.GET.get('page') or request.GET.get('page') == '1') and not request.GET.get('handler') == 'search_ajax_wide' and not request.GET.get('handler') == 'search_ajax_narrow':

            return render(request, 'searchresult.html', context)

        else:

            if request.GET.get('handler') == 'search_ajax_narrow':

                html = render_to_string('searchresult_more_narrow.html', context)

                if int(page) < paginator.num_pages:
                    next_page = int(page) + 1
                else:
                    next_page = 'last_page'

                result = {
                    'html': html,
                    'page': next_page,
                    'searchvalue_ip': searchvalue_ip,
                    'searchvalue_ac': searchvalue_ac,
                    'searchvalue_ln': searchvalue_ln,
                    'searchvalue_pl': searchvalue_pl,
                    'searchvalue_pd': searchvalue_pd,
                    'searchvalue_sf': searchvalue_sf,
                    'searchvalue_st': searchvalue_st,
                    'is_mobile': is_mobile,
                }
                return JsonResponse(result)

            elif request.GET.get('handler') == 'search_ajax_wide':

                html = render_to_string('searchresult_more.html', context)

                if int(page) < paginator.num_pages:
                    next_page = int(page) + 1
                else:
                    next_page = 'last_page'

                result = {
                    'html': html,
                    'page': next_page,
                    'searchvalue_ip': searchvalue_ip,
                    'searchvalue_ac': searchvalue_ac,
                    'searchvalue_ln': searchvalue_ln,
                    'searchvalue_pl': searchvalue_pl,
                    'searchvalue_pd': searchvalue_pd,
                    'searchvalue_sf': searchvalue_sf,
                    'searchvalue_st': searchvalue_st,
                    'is_mobile': is_mobile,
                }
                return JsonResponse(result)

            elif request.GET.get('handler') == 'narrow':

                html = render_to_string('searchresult_more_narrow.html', context)

                if int(page) < paginator.num_pages:
                    next_page = int(page) + 1
                else:
                    next_page = 'last_page'

                result = {
                    'html': html,
                    'page': next_page,
                    'searchvalue_ip': searchvalue_ip,
                    'searchvalue_ac': searchvalue_ac,
                    'searchvalue_ln': searchvalue_ln,
                    'searchvalue_pl': searchvalue_pl,
                    'searchvalue_pd': searchvalue_pd,
                    'searchvalue_sf': searchvalue_sf,
                    'searchvalue_st': searchvalue_st,
                    'is_mobile': is_mobile,
                }
                return JsonResponse(result)

            else:

                html = render_to_string('searchresult_more.html', context)

                if int(page) < paginator.num_pages:
                    next_page = int(page) + 1
                else:
                    next_page = 'last_page'

                result = {
                    'html':html,
                    'page':next_page,
                    'searchvalue_ip':searchvalue_ip,
                    'searchvalue_ac':searchvalue_ac,
                    'searchvalue_ln': searchvalue_ln,
                    'searchvalue_pl': searchvalue_pl,
                    'searchvalue_pd': searchvalue_pd,
                    'searchvalue_sf': searchvalue_sf,
                    'searchvalue_st': searchvalue_st,
                    'is_mobile': is_mobile,
                }
                return JsonResponse(result)

    else:
        return redirect('login')

def rateInput(request):
    if request.user.is_authenticated:

        MOBILE_AGENT_RE = re.compile(r'.*(iphone|mobile|androidtouch)', re.IGNORECASE)
        if MOBILE_AGENT_RE.match(request.META['HTTP_USER_AGENT']):
            is_mobile = True
        else:
            is_mobile = False

        if request.method == "POST":
            form = PostRateForm(request.POST)
            if form.is_valid():
                liner_list = request.POST.getlist('liner')
                pol_list = request.POST.getlist('pol')
                pod_list = request.POST.getlist('pod')

                saved_post_id = []
                for liner in liner_list:
                    for pol in pol_list:
                        for pod in pod_list:
                            form = PostRateForm(request.POST)
                            post = form.save(commit=False)
                            post.account = post.account.upper()
                            post.liner = liner
                            post.pol = pol
                            post.pod = pod
                            post.inputperson = request.user
                            post.deleted = 0
                            post.save()
                            saved_post_id.append(post.id)

                just_inputed_rates = Rate.objects.filter(pk__in=saved_post_id)
                html = render_to_string('rateform_input_ajax_done.html', {'just_inputed_rates': just_inputed_rates, 'is_mobile':is_mobile, })
                result = {'html': html, 'message':'운임 저장 완료!',}
                return JsonResponse(result)

            else:
                messages.add_message(request, messages.WARNING, '운임 저장 실패!')
                return redirect('rateSearch')
        else:
            form = PostRateForm()
            ed = timezone.now().replace(day=1) + relativedelta(months=+1, days=-1)
            od = timezone.now()
            ip = request.user.nickname
            try:
                profile = MyUserProfile.objects.get(owner=request.user)
            except:
                profile = False

            return render(request, 'rateform_input_ajax.html', {'form':form, 'ed':ed, 'od':od, 'ip':ip, 'profile':profile, 'is_mobile':is_mobile,})

    else:
        return redirect('login')

def rateModify(request, pk, str):

    MOBILE_AGENT_RE = re.compile(r'.*(iphone|mobile|androidtouch)', re.IGNORECASE)
    if MOBILE_AGENT_RE.match(request.META['HTTP_USER_AGENT']):
        is_mobile = True
    else:
        is_mobile = False

    if request.method == "POST":
        previousrate = Rate.objects.get(pk=pk)
        form = PostRateForm(request.POST, instance=previousrate)
        loginuser = request.user.email
        # modify POST 저장 전에 로그인 유저와 작성자가 같은 지 체크
        if form.is_valid() and previousrate.inputperson.email == loginuser:

            post = form.save(commit=False)
            post.account = post.account.upper()
            post.save()

            modifiedrate = Rate.objects.get(pk=pk)
            html = render_to_string('rateform_modify_ajax_done.html', {'modifiedrate':modifiedrate, 'is_mobile': is_mobile,})
            result = {'html':html, 'message':'수정 성공!',}
            return JsonResponse(result)

        else:
            modifiedrate = Rate.objects.get(pk=pk)
            html = render_to_string('rateform_modify_ajax_done.html', {'modifiedrate':modifiedrate, })
            result = {'html':html, 'message':'수정 성공!',}
            return JsonResponse(result)
    else:
        previousrate = Rate.objects.get(pk=pk)
        loginuser = request.user.email
        if request.user.is_authenticated and previousrate.inputperson.email == loginuser:
            previousrate = Rate.objects.get(pk=pk)
            form = PostRateForm(instance=previousrate)
            ac = getattr(previousrate, 'account')
            ln = getattr(previousrate, 'liner')
            pl = getattr(previousrate, 'pol')
            pd = getattr(previousrate, 'pod')
            br20 = getattr(previousrate, 'buying20')
            sl20 = getattr(previousrate, 'selling20')
            br40 = getattr(previousrate, 'buying40')
            sl40 = getattr(previousrate, 'selling40')
            br4H = getattr(previousrate, 'buying4H')
            sl4H = getattr(previousrate, 'selling4H')
            lft = getattr(previousrate, 'loadingFT')
            dft = getattr(previousrate, 'dischargingFT')
            ed = getattr(previousrate, 'effectiveDate')
            od = getattr(previousrate, 'offeredDate')
            rmk = getattr(previousrate, 'remark')
            ip = request.user

            html = render_to_string('rateform_modify_ajax.html', {
                'pk' : pk,
                'form': form,
                'ac': ac,
                'ln': ln,
                'pl': pl,
                'pd': pd,
                'br20': br20,
                'sl20': sl20,
                'br40': br40,
                'sl40': sl40,
                'br4H': br4H,
                'sl4H': sl4H,
                'lft': lft,
                'dft': dft,
                'ed': ed,
                'od': od,
                'rmk': rmk,
                'ip': ip,
                'is_mobile': is_mobile,
                })
            result = {'html':html}
            return JsonResponse(result)

        # 로그인은 되어있지만, 기존 입력자와 다를 경우
        elif request.user.is_authenticated and previousrate.inputperson.email != loginuser:

            result = {'not_inputperson': '입력자만 수정할 수 있습니다.', 'message':'입력자만 수정할 수 있습니다.'}
            return JsonResponse(result)

        else:
            return redirect('login')

def rateDelete(request, pk, str):
    if request.user.is_authenticated:
        currentrate = Rate.objects.get(pk=pk)
        loginuser = request.user.email
        if currentrate.inputperson.email == loginuser:
            form = PostRateForm(instance=currentrate)
            post = form.save(commit=False)
            post.inputperson = request.user
            post.deleted = 1
            post.save()

            result = {'pk':post.id, 'message':'삭제 완료!'}
            return JsonResponse(result)

        else:
            result = {'message':'입력자만 삭제할 수 있습니다.'}
            return JsonResponse(result)

    else:
        return redirect('login')

def rateDuplicate(request, pk):
    if request.user.is_authenticated:

        MOBILE_AGENT_RE = re.compile(r'.*(iphone|mobile|androidtouch)', re.IGNORECASE)
        if MOBILE_AGENT_RE.match(request.META['HTTP_USER_AGENT']):
            is_mobile = True
        else:
            is_mobile = False

        previousrate = Rate.objects.get(pk=pk)
        loginuser = request.user.email

        # modify POST 저장 전에 로그인 유저와 작성자가 같은 지 체크
        if previousrate.inputperson.email == loginuser:
            previousrate.pk = None
            previousrate.effectiveDate = timezone.now().replace(day=1) + relativedelta(months=+1, days=-1)
            previousrate.offeredDate = timezone.now()
            previousrate.save()

            just_inputed_rates = Rate.objects.filter(pk=previousrate.id)
            html = render_to_string('rateform_input_ajax_done.html', {'just_inputed_rates': just_inputed_rates, 'is_mobile':is_mobile, })
            result = {'html': html, 'message':'운임 복제 완료!',}
            return JsonResponse(result)

        else:
            result = {'message':'입력자만 복제할 수 있습니다.'}
            return JsonResponse(result)

    else:
        return redirect('login')

def main(request):

    return render(request, 'main.html')

def rates_json(request):
    if request.user.is_authenticated:
        rates = Rate.objects.all()
        id_text = []
        results = {}
        for rate in rates:
            rate_json = {}
            rate_json['inputperson'] = rate.inputperson
            rate_json['account'] = rate.account
            rate_json['liner'] = rate.liner
            rate_json['pol'] = rate.pol
            rate_json['pod'] = rate.pod
            rate_json['buying20'] = rate.buying20
            rate_json['selling20'] = rate.selling20
            rate_json['buying40'] = rate.buying40
            rate_json['selling40'] = rate.selling40
            rate_json['buying4H'] = rate.buying4H
            rate_json['selling4H'] = rate.selling4H
            rate_json['loadingFT'] = rate.loadingFT
            rate_json['dischargingFT'] = rate.dischargingFT
            rate_json['effectiveDate'] = rate.effectiveDate
            rate_json['offeredDate'] = rate.offeredDate
            rate_json['recordedDate'] = rate.recordedDate
            rate_json['remark'] = rate.remark
            rate_json['deleted'] = rate.deleted
            id_text.append(rate_json)
        results['results'] = id_text
        return render(request, 'download.html', {'rates':rates})

    else:
        return redirect('login')

def rateCharts(request):
    if request.user.is_authenticated:

        loginuser = request.user
        try:
            profile = MyUserProfile.objects.get(owner=request.user)
        except:
            profile = False

        MOBILE_AGENT_RE = re.compile(r'.*(iphone|mobile|androidtouch)', re.IGNORECASE)
        if MOBILE_AGENT_RE.match(request.META['HTTP_USER_AGENT']):
            is_mobile = True
        else:
            is_mobile = False

        return render(request, 'charts.html', {'is_mobile':is_mobile, 'loginuser':loginuser, 'profile':profile, })
    else:
        return redirect('login')