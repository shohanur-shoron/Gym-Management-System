from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from dotenv import load_dotenv
import os
load_dotenv()

class Command(BaseCommand):
    help = 'Creates a superuser.'

    def handle(self, *args, **options):
        User = get_user_model()
        if not User.objects.filter(email=os.getenv('SU_EMAIL')).exists():
            User.objects.create_superuser(
                email=os.getenv('SU_EMAIL'),
                password=os.getenv('SU_PASS')
            )
            print('Superuser has been created.')
