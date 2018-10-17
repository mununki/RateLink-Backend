import os
from django.db import models
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser)

class MyUserManager(BaseUserManager):
    def create_user(self, email, nickname, password=None):
        if not email:
            raise ValueError('User must have an email address')

        user = self.model (
            email = self.normalize_email(email),
            nickname = nickname,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nickname, password):
        user = self.create_user(
            email = email,
            nickname = nickname,
            password = password
        )
        user.is_admin = True
        user.save(using = self._db)
        return user

class MyUser(AbstractBaseUser):
    email = models.EmailField(
        verbose_name = 'email address',
        blank = False,
        max_length = 255,
        unique = True,
    )

    nickname = models.CharField(
        verbose_name = 'username',
        max_length = 20,
        blank = False,
        unique = False,
        default = ''
    )

    is_active = models.BooleanField(default = True)
    is_admin = models.BooleanField(default = False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname']

    def __str__(self):
        return self.email

    def get_nickname(self):
        return self.nickname

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

class RateReader(models.Model):
    shower = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='who_shows')
    reader = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='who_reads')
    relationship_date = models.DateTimeField(auto_now=True)

def image_file_path(instance, filename):

    try:
        image_instance = MyUserProfile.objects.get(pk=instance.pk)

        if image_instance.image:
            image = image_instance.image
            if image.file:
                if os.path.isfile(image.path):
                    image.file.close()
                    os.remove(image.path)
    except:
        pass

    from random import choice
    import string   # string.ascii_letters : ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz

    arr = [choice(string.ascii_letters) for _ in range(8)]
    pid = ''.join(arr)  # 8자리 임의의 문자를 만들어서 파일명으로 지정
    extension = filename.split('.')[-1] # 배열로 만들어 마지막 요소를 추출하여 확장자로 지정

    return 'profileimages/owner_{0}/{1}.{2}'.format(instance.owner.id, pid, extension)

class MyUserProfile(models.Model):
    LINER = '1'
    FORWARDER = '2'
    ETC = '3'
    JOB_CHOICE = (
        (LINER, '선사'),
        (FORWARDER, '포워더'),
        (ETC, '기타')
    )
    owner = models.OneToOneField(MyUser, on_delete=models.CASCADE, related_name='profile')
    profile_name = models.CharField(max_length=20, blank=True)
    job_boolean = models.CharField(choices=JOB_CHOICE, max_length=2, blank=True)
    company = models.CharField(max_length=10, blank=True)
    image = models.FileField(upload_to=image_file_path, blank=True)

    def __str__(self):
        return self.owner.nickname

class MessageBox(models.Model):
    sender = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='receiver')
    msg = models.TextField(max_length=256, default='')
    time = models.DateTimeField(auto_now=True)
