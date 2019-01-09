from django.core.management.base import BaseCommand
from account.models import MyUser

class Command(BaseCommand):
    def handle(self, *args, **options):
        if not MyUser.objects.filter(email='woonki.moon@gmail.com').exists():
            MyUser.objects.create_superuser('woonki.moon@gmail.com','rladmin','goodluck0716$')
