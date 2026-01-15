from django.contrib import admin
from .models import EmailVerificationCode, User

admin.site.register(EmailVerificationCode)
admin.site.register(User)