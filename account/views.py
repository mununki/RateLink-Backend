from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from .models import MyUser, MyUserProfile, RateReader, MessageBox
from django.core.mail import EmailMessage
from django.contrib import messages
import tempfile
from urllib.request import urlopen
from django.core.files import File
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from resizeimage import resizeimage
from .forms import SignupForm, LoginForm, ProfileUpdateForm, RateReaderForm, MessageSend
import re

def SignupRateManager(request):
    if not request.user.is_authenticated:

        form = SignupForm()

        if request.method == "POST":
            form = SignupForm(request.POST)
            if form.is_valid():
                new_user = form.save(commit=False)
                new_user.email = form.cleaned_data['email']
                new_user.is_active = False
                new_user.save()
                current_site = get_current_site(request)
                mail_subject = 'Activate your Rate Manager account.'
                message = render_to_string('acc_active_email.html', {
                    'new_user': new_user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(new_user.pk)).decode(),
                    'token': account_activation_token.make_token(new_user),
                })
                email = EmailMessage(
                    mail_subject, message, to=[new_user.email]
                )
                email.send()

                messages.add_message(request, messages.SUCCESS, '회원가입 인증 메일을 확인해주세요.')
                return redirect('login')

            else:

                return render(request, 'signup.html', {'form':form, })

        else:

            return render(request, 'signup.html', {'form': form })

    else:
        return redirect('main')

def validate_email(request):
    email = request.GET.get('email', None)
    data = {
        'is_taken': MyUser.objects.filter(email__iexact=email).exists()
    }
    return JsonResponse(data)

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        new_user = MyUser.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, MyUser.DoesNotExist):
        new_user = None

    if new_user is not None and account_activation_token.check_token(new_user, token):
        new_user.is_active = True
        new_user.save()
        login(request, new_user)
        return redirect('profileupdate')
    else:
        return HttpResponse('Activation link is invalid!')

def LoginRateManager(request):
    if not request.user.is_authenticated:
        if request.method == "POST":
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(email = email, password = password)
            if user is not None:
                login(request, user)
                messages.add_message(request, messages.SUCCESS, request.user.nickname + '님 환영합니다!')
                return redirect('rateSearch')
            else:
                messages.add_message(request, messages.WARNING, 'Email / Password를 다시 확인해주세요.')
                return redirect('login')
        else:
            form = LoginForm()
            return render(request, 'login.html', {'form': form })
    else:
        return redirect('main')

def ProfileUpdate(request):
    if request.user.is_authenticated:

        MOBILE_AGENT_RE = re.compile(r'.*(iphone|mobile|androidtouch)', re.IGNORECASE)
        if MOBILE_AGENT_RE.match(request.META['HTTP_USER_AGENT']):
            is_mobile = True
        else:
            is_mobile = False

        try:
            currentprofile = MyUserProfile.objects.get(owner=request.user)
        except:
            form = ProfileUpdateForm()
            post = form.save(commit=False)
            post.owner = request.user
            post.profile_name = request.user.nickname

            blank_image_url = request.build_absolute_uri('/static/account/profileimages/blank.png')
            img_temp = tempfile.NamedTemporaryFile()
            img_temp.write(urlopen(blank_image_url).read())
            img_temp.flush()
            post.image.save('blank.png', File(img_temp))
            post.save()

            currentprofile = MyUserProfile.objects.get(owner=request.user)

        if request.method == "POST":
            form = ProfileUpdateForm(request.POST, request.FILES, instance=currentprofile)
            if form.is_valid():
                post = form.save(commit=False)
                post.owner = request.user

                if request.FILES.get('image', False):
                    pil_image_obj = Image.open(post.image)
                    new_image = resizeimage.resize_cover(pil_image_obj, [100, 100], validate=False)

                    new_image_io = BytesIO()
                    new_image.save(new_image_io, new_image.format)

                    temp_name = request.FILES['image'].name
                    post.image.delete(save=False)

                    post.image.save(
                        temp_name,
                        content=ContentFile(new_image_io.getvalue()),
                        save=False
                    )
                elif request.POST.get('select'):
                    # 샘플 프로필 이미지 주소 이곳에 기입
                    sample_image1_url = request.build_absolute_uri('/static/account/profileimages/sample_profile_1.png')
                    sample_image2_url = request.build_absolute_uri('/static/account/profileimages/sample_profile_2.png')
                    sample_image3_url = request.build_absolute_uri('/static/account/profileimages/sample_profile_3.png')
                    sample_image4_url = request.build_absolute_uri('/static/account/profileimages/sample_profile_4.png')
                    sample_image5_url = request.build_absolute_uri('/static/account/profileimages/sample_profile_5.png')
                    select = request.POST.get('select')
                    if select == '1':
                        img_temp = tempfile.NamedTemporaryFile()
                        img_temp.write(urlopen(sample_image1_url).read())
                        img_temp.flush()
                        post.image.save('sample_profile_1.png', File(img_temp))
                    elif select == '2':
                        img_temp = tempfile.NamedTemporaryFile()
                        img_temp.write(urlopen(sample_image2_url).read())
                        img_temp.flush()
                        post.image.save('sample_profile_2.png', File(img_temp))
                    elif select == '3':
                        img_temp = tempfile.NamedTemporaryFile()
                        img_temp.write(urlopen(sample_image3_url).read())
                        img_temp.flush()
                        post.image.save('sample_profile_3.png', File(img_temp))
                    elif select == '4':
                        img_temp = tempfile.NamedTemporaryFile()
                        img_temp.write(urlopen(sample_image4_url).read())
                        img_temp.flush()
                        post.image.save('sample_profile_4.png', File(img_temp))
                    elif select == '5':
                        img_temp = tempfile.NamedTemporaryFile()
                        img_temp.write(urlopen(sample_image5_url).read())
                        img_temp.flush()
                        post.image.save('sample_profile_5.png', File(img_temp))

                post.save()
                messages.add_message(request, messages.SUCCESS, '저장 완료!')

                return redirect('profileupdate')
        else:

            form = ProfileUpdateForm(instance=currentprofile)

            showers = RateReader.objects.filter(reader=request.user).order_by('-relationship_date').distinct()
            readers = RateReader.objects.filter(shower=request.user).order_by('-relationship_date').distinct()

            return render(request, 'profileupdate.html', { 'form':form, 'showers':showers, 'readers':readers, 'is_mobile':is_mobile, 'loginuser':request.user, 'profile':currentprofile })

    else:
        return redirect('login')

def ReaderUpdate(request):

    MOBILE_AGENT_RE = re.compile(r'.*(iphone|mobile|androidtouch)', re.IGNORECASE)
    if MOBILE_AGENT_RE.match(request.META['HTTP_USER_AGENT']):
        is_mobile = True
    else:
        is_mobile = False

    if request.method == "POST":
        # 친구 찾기
        friendname = request.POST['friendname']
        friendemail = request.POST['friendemail']
        friendcompany = request.POST['friendcompany']

        temp = MyUser.objects.filter(nickname = friendname) | MyUser.objects.filter(email = friendemail) | MyUser.objects.filter(profile__company = friendcompany).exclude(profile__company='')
        friends = temp.exclude(email=request.user)

        showers = RateReader.objects.filter(reader=request.user).order_by('-relationship_date').distinct()
        readers = RateReader.objects.filter(shower=request.user).order_by('-relationship_date').distinct()

        readers_list = []
        for reader in readers:
            readers_list.append(reader.reader.email)

        try:
            profile = MyUserProfile.objects.get(owner=request.user)
        except:
            profile = False

        return render(request, 'friendupdate.html', { 'friends': friends, 'showers':showers, 'readers':readers, 'readers_list':readers_list, 'profile':profile, 'is_mobile':is_mobile,})
    else:
        if request.user.is_authenticated:
            try:
                profile = MyUserProfile.objects.get(owner=request.user)
            except:
                profile = False

            showers = RateReader.objects.filter(reader=request.user).order_by('-relationship_date').distinct()
            readers = RateReader.objects.filter(shower=request.user).order_by('-relationship_date').distinct()
            readers_list = []
            for reader in readers:
                readers_list.append(reader.reader.email)

            return render(request, 'friendupdate.html', { 'showers':showers, 'readers':readers, 'readers_list':readers_list, 'loginuser':request.user, 'profile':profile, 'is_mobile':is_mobile, })

def ReaderAdd(request, pk):
    if request.user.is_authenticated:
        form = RateReaderForm()
        post = form.save(commit=False)
        post.reader = MyUser.objects.get(pk=pk)
        crs = RateReader.objects.filter(shower=request.user).distinct()
        current_readers = []
        for cr in crs:
            current_readers.append(cr.reader.email)
        current_readers.append(request.user.email)

        if post.reader.email in current_readers:
            messages.add_message(request, messages.INFO, '이미 등록한 사용자 입니다.')
            return redirect('readerupdate')
        else:
            post.shower = request.user
            post.save()
            messages.add_message(request, messages.SUCCESS, 'Reader 등록 완료!')
            return redirect('readerupdate')
    else:
        return redirect('login')

def ReaderDelete(request, pk):
    if request.user.is_authenticated:
        current_reader = RateReader.objects.get(pk=pk)
        current_reader.delete()

        messages.add_message(request, messages.INFO, '등록해제 완료!')
        return redirect('readerupdate')
    else:
        return redirect('login')

def FindID(request):
    if request.method == "POST":
        friendname = request.POST['friendname']
        friendemail = request.POST['friendemail']

        friends = MyUser.objects.filter(nickname = friendname) & MyUser.objects.filter(email = friendemail)

        if friends:
           pass
        else:
            messages.add_message(request, messages.WARNING, '결과를 찾을 수 없습니다.')

        return render(request, 'findid.html', { 'friends': friends })
    else:

        return render(request, 'findid.html')

def ChangePassword(request):

    MOBILE_AGENT_RE = re.compile(r'.*(iphone|mobile|androidtouch)', re.IGNORECASE)
    if MOBILE_AGENT_RE.match(request.META['HTTP_USER_AGENT']):
        is_mobile = True
    else:
        is_mobile = False

    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)

            return redirect('profileupdate')
        else:
            try:
                profile = MyUserProfile.objects.get(owner=request.user)
            except:
                profile = False

            messages.add_message(request, messages.WARNING, '패스워드를 다시 확인해주세요.')
            return render(request, 'changepassword.html', {'form': form, 'profile': profile, 'is_mobile':is_mobile,})
    else:
        try:
            profile = MyUserProfile.objects.get(owner=request.user)
        except:
            profile = False

        form = PasswordChangeForm(request.user)

    return render(request, 'changepassword.html', {'form': form, 'profile':profile, 'is_mobile': is_mobile,})

def LogoutRateManager(request):
    logout(request)
    return redirect('main')

def MessageList(request):
    if request.user.is_authenticated:

        received_messages = MessageBox.objects.filter(receiver=request.user)
        sent_messages = MessageBox.objects.filter(sender=request.user)

        if request.method == "POST":
            form = MessageSend(request.POST)

            post = form.save(commit=False)
            r = request.POST['receiver']
            rr = MyUser.objects.get(email = r)
            post.receiver = rr
            post.sender = request.user
            post.save()

            return redirect('messageList')

        else:
            form = MessageSend()

            # 수신자는 showers + readers
            receivers = MyUser.objects.none()
            showers = RateReader.objects.filter(reader=request.user)
            for shower in showers:
                receivers = receivers | MyUser.objects.filter(nickname=shower.shower.nickname)
            readers = RateReader.objects.filter(shower=request.user)
            for reader in readers:
                receivers = receivers | MyUser.objects.filter(nickname=reader.reader.nickname)

            return render(request, 'messagelist.html', { 'form': form, 'receivers': receivers, 'received_messages': received_messages, 'sent_messages': sent_messages})
    else:
        return redirect('login')
