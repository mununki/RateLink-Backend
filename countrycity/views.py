from .models import Location, Liner
from account.models import MyUser, MyUserProfile
from rate.models import CNTRtype, Client
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
import json
import csv
from io import StringIO
from rate.models import Rate
from account.models import MyUser
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.request import urlopen
import re


def search_location(request):
    if request.GET.get('term'):
        cities = Location.objects.filter(name__istartswith=request.GET['term'])[:10]
        id_text = []
        results = {}
        for city in cities:
            city_json = {}
            city_json['id'] = city.name
            city_json['text'] = city.name + ', ' + city.country + ' ' + city.label
            id_text.append(city_json)
        results['results'] = id_text
        data = json.dumps(results)
        mimetype = 'application/json'
        return HttpResponse(data, mimetype)

    else:
        results = {}
        results['results'] = ''
        data = json.dumps(results)
        mimetype = 'application/json'
        return HttpResponse(data, mimetype)


def search_liner(request):
    if request.GET.get('term'):
        liners = Liner.objects.filter(name__istartswith=request.GET['term'])[:10]
        id_text = []
        results = {}
        for liner in liners:
            liner_json = {}
            liner_json['id'] = liner.name
            liner_json['text'] = '[' + liner.name + '] ' + liner.label
            id_text.append(liner_json)
        results['results'] = id_text
        data = json.dumps(results)
        mimetype = 'application/json'
        return HttpResponse(data, mimetype)

    else:
        results = {}
        results['results'] = ''
        data = json.dumps(results)
        mimetype = 'application/json'
        return HttpResponse(data, mimetype)


def upload_location(request):
    if request.POST and request.FILES:
        csvfile = request.FILES['location']
        fields = ['name', 'country', 'label']
        f = StringIO(csvfile.read().decode())
        for row in csv.reader(f, delimiter='|'):
            Location.objects.create(**dict(zip(fields, row)))

        return HttpResponse('업로드 완료!')

    else:
        return render(request, 'upload_location.html')


def upload_liner(request):
    if request.POST and request.FILES:
        csvfile = request.FILES['liner']
        fields = ['name', 'label']
        f = StringIO(csvfile.read().decode())
        for row in csv.reader(f, delimiter=','):
            Liner.objects.create(**dict(zip(fields, row)))

        return HttpResponse('업로드 완료!')

    else:
        return render(request, 'upload_liner.html')


def upload_client(request):
    if request.POST and request.FILES:
        csvfile = request.FILES['client']
        fields = ['name', 'salesman', 'remarks']
        f = StringIO(csvfile.read().decode())
        for row in csv.reader(f, delimiter='|'):
            dict_row = dict(zip(fields, row))

            name = dict_row['name']
            salesman = MyUser.objects.get(email=dict_row['salesman'])
            remarks = dict_row['remarks']

            client = Client(
                name=name,
                salesman=salesman,
                remarks=remarks
            )
            client.save()

        return HttpResponse('업로드 완료!')

    else:
        return render(request, 'upload_client.html')


def upload_rates(request):
    if request.POST and request.FILES:
        csvfile = request.FILES['rates']
        fields = ['inputperson', 'account', 'liner', 'pol', 'pod', 'type', 'buying20', 'buying40', 'buying4H', 'selling20', 'selling40', 'selling4H', 'loadingFT', 'dischargingFT', 'offeredDate', 'effectiveDate', 'recordedDate', 'remark', 'deleted']
        f = StringIO(csvfile.read().decode())

        for row in csv.reader(f, delimiter='\t'):
            dict_row = dict(zip(fields, row))

            ip = MyUser.objects.get(email=dict_row['inputperson'])
            ac = Client.objects.get(name=dict_row['account'])
            ln = Liner.objects.get(name=dict_row['liner'])
            pl = Location.objects.get(name=dict_row['pol'])
            pd = Location.objects.get(name=dict_row['pod'])
            ty = CNTRtype.objects.get(name=dict_row['type'])
            b20 = dict_row['buying20']
            s20 = dict_row['selling20']
            b40 = dict_row['buying40']
            s40 = dict_row['selling40']
            b4H = dict_row['buying4H']
            s4H = dict_row['selling4H']
            lFT = dict_row['loadingFT']
            dFT = dict_row['dischargingFT']
            od = datetime.strptime(dict_row['offeredDate'], "%Y-%m-%d").date()
            ed = datetime.strptime(dict_row['effectiveDate'], "%Y-%m-%d").date()
            rd = datetime.strptime(dict_row['recordedDate'], "%Y-%m-%d").date()
            rmk = dict_row['remark']
            dt = dict_row['deleted']
            new_rate = Rate(
                inputperson=ip,
                account=ac,
                liner=ln,
                pol=pl,
                pod=pd,
                type=ty,
                buying20=b20,
                selling20=s20,
                buying40=b40,
                selling40=s40,
                buying4H=b4H,
                selling4H=s4H,
                loadingFT=lFT,
                dischargingFT=dFT,
                offeredDate=od,
                effectiveDate=ed,
                recordedDate=rd,
                remark=rmk,
                deleted=dt
            )
            new_rate.save()

        return HttpResponse('업로드 완료!')

    else:
        return render(request, 'upload_rates.html')


def find_location_code(request):
    if request.user.is_authenticated:

        MOBILE_AGENT_RE = re.compile(r'.*(iphone|mobile|androidtouch)', re.IGNORECASE)
        if MOBILE_AGENT_RE.match(request.META['HTTP_USER_AGENT']):
            is_mobile = True
        else:
            is_mobile = False

        # url = 'http://www.unece.org/cefact/locode/service/location'
        url = request.build_absolute_uri('/static/countrycity/countrylist_un.html')
        html = urlopen(url)
        source = html.read()
        html.close()

        soup = BeautifulSoup(source, 'html5lib')

        countries = soup.find_all(width="65%")

        if request.GET.get('location'):
            search_country = request.GET.get('country')
            search_location = request.GET.get('location')
            if 'United States' in search_country:
                temp = search_location.split(', ')
                search_location = temp[0]
                search_state = temp[1]

            # country_names = [search_country] # AJAX로 구현하지 않는 경우 사용
            # location_names = [search_location] # AJAX로 구현하지 않는 경우 사용
            for country in countries:
                name = country.get_text()

                if name == search_country:

                    local_link = country.a.get('href')
                    # absolute_link = 'http://www.unece.org' + local_link
                    absolute_link = local_link

                    absolute_link = absolute_link.replace('/..', '')

                    sub_html = urlopen(absolute_link)
                    sub_source = sub_html.read()
                    sub_html.close()

                    soup = BeautifulSoup(sub_source, 'html5lib')

                    locations = soup.find_all('tr')

                    for location in locations:
                        try:
                            location_name = location.find_all('td', {'width': '19%'})[1].get_text().encode('utf-8')
                            location_state = location.find_all('td', {'width': '3%'})[0].get_text().encode('utf-8')
                            location_name = location_name.replace(b'\xc2', b'').replace(b'\xa0', b'')
                            location_state = location_state.replace(b'\xc2', b'').replace(b'\xa0', b'')

                            if 'United States' in search_country:
                                if location_name == search_location.encode('utf-8') and location_state == search_state.encode('utf-8'):
                                    location_code = location.find('td', {'width': '8%'}).get_text().encode('utf-8')
                                    location_code = location_code.replace(b'\xc2', b'').replace(b'\xa0', b'')

                                    location_coordinates = location.find('td', {'width': '17%'}).get_text().encode('utf-8')
                                    location_coordinates = location_coordinates.replace(b'\xc2', b'').replace(b'\xa0', b'')
                                    location_coordinates_list = location_coordinates.split()
                                    location_coordinates_list[0] = location_coordinates_list[0].decode('utf-8')
                                    location_coordinates_list[1] = location_coordinates_list[1].decode('utf-8')
                                    lat_deg, lat_min, lat_dir = location_coordinates_list[0][:-3], location_coordinates_list[0][-3:-1], location_coordinates_list[0][-1]
                                    lng_deg, lng_min, lng_dir = location_coordinates_list[1][:-3], location_coordinates_list[1][-3:-1], location_coordinates_list[1][-1]
                                    if lat_dir == 'N':
                                        lat_temp = int(lat_deg) + (int(lat_min) / 60)
                                        lat = round(lat_temp, 3)
                                    elif lat_dir == 'S':
                                        lat_temp = (int(lat_deg) + (int(lat_min) / 60)) * -1
                                        lat = round(lat_temp, 3)

                                    if lng_dir == 'E':
                                        lng_temp = int(lng_deg) + (int(lng_min) / 60)
                                        lng = round(lng_temp, 3)
                                    elif lng_dir == 'W':
                                        lng_temp = (int(lng_deg) + (int(lng_min) / 60)) * -1
                                        lng = round(lng_temp, 3)

                                    result = {
                                        'code': location_code.decode('utf-8'),
                                        'lat': lat,
                                        'lng': lng,
                                        'is_mobile': is_mobile,
                                    }

                                    return JsonResponse(result)

                            else:
                                if location_name == search_location.encode('utf-8'):
                                    location_code = location.find('td', {'width': '8%'}).get_text().encode('utf-8')
                                    location_code = location_code.replace(b'\xc2', b'').replace(b'\xa0', b'')

                                    location_coordinates = location.find('td', {'width': '17%'}).get_text().encode('utf-8')
                                    location_coordinates = location_coordinates.replace(b'\xc2', b'').replace(b'\xa0', b'')
                                    location_coordinates_list = location_coordinates.split()
                                    location_coordinates_list[0] = location_coordinates_list[0].decode('utf-8')
                                    location_coordinates_list[1] = location_coordinates_list[1].decode('utf-8')
                                    lat_deg, lat_min, lat_dir = location_coordinates_list[0][:-3], location_coordinates_list[0][-3:-1], location_coordinates_list[0][-1]
                                    lng_deg, lng_min, lng_dir = location_coordinates_list[1][:-3], location_coordinates_list[1][-3:-1], location_coordinates_list[1][-1]
                                    if lat_dir == 'N':
                                        lat_temp = int(lat_deg) + (int(lat_min)/60)
                                        lat = round(lat_temp, 3)
                                    elif lat_dir == 'S':
                                        lat_temp = (int(lat_deg) + (int(lat_min)/60)) * -1
                                        lat = round(lat_temp, 3)

                                    if lng_dir == 'E':
                                        lng_temp = int(lng_deg) + (int(lng_min)/60)
                                        lng = round(lng_temp, 3)
                                    elif lng_dir == 'W':
                                        lng_temp = (int(lng_deg) + (int(lng_min)/60)) * -1
                                        lng = round(lng_temp, 3)

                                    result = {
                                        'code': location_code.decode('utf-8'),
                                        'lat': lat,
                                        'lng': lng,
                                        'is_mobile': is_mobile,
                                    }

                                    # AJAX로 구현하지 않는 경우 사용
                                    # return render(request, 'find_location_code.html', {'result': result, 'country_names': country_names, 'location_names': location_names,})
                                    return JsonResponse(result)

                        except:
                            pass

                    result = {'data': '결과 없음'}
                    return JsonResponse(result)

        else:

            loginuser = request.user
            try:
                profile = MyUserProfile.objects.get(owner=request.user)
            except:
                profile = False

            if request.GET.get('country'):
                search_country = request.GET.get('country')
                for country in countries:
                    name = country.get_text()
                    if name == search_country:

                        country_names = [search_country]

                        local_link = country.a.get('href')
                        # absolute_link = 'http://www.unece.org' + local_link
                        absolute_link = local_link

                        absolute_link = absolute_link.replace('/..', '')

                        sub_html = urlopen(absolute_link)
                        sub_source = sub_html.read()
                        sub_html.close()

                        soup = BeautifulSoup(sub_source, 'html5lib')

                        locations = soup.find_all('tr')

                        location_names = []
                        for location in locations:
                            try:
                                location_name = location.find_all('td', {'width': '19%'})[1].get_text().encode('utf-8')
                                location_state = location.find_all('td', {'width': '3%'})[0].get_text().encode('utf-8')
                                location_name = location_name.replace(b'\xc2', b'').replace(b'\xa0', b'')
                                location_state = location_state.replace(b'\xc2', b'').replace(b'\xa0', b'')
                                if location_name != 'NameWoDiacritics'.encode('utf-8'):
                                    if 'United States' in search_country:
                                        location_names.append(location_name.decode('utf-8') + ', ' + location_state.decode('utf-8'))
                                    else:
                                        location_names.append(location_name.decode('utf-8'))
                            except:
                                pass

                        # AJAX로 구현하지 않을 경우에 사용
                        # return render(request, 'find_location_code.html', {'country_names': country_names, 'location_names': location_names, })
                        return render(request, 'partof_location_code.html', {'location_names': location_names, 'loginuser': loginuser, 'profile': profile, })

            else:
                country_names = []
                for country in countries:
                    country_names.append(country.get_text())

                return render(request, 'find_location_code.html', {'country_names': country_names, 'is_mobile': is_mobile, 'loginuser': loginuser, 'profile': profile, })

    else:
        return redirect('login')
