from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import RentalRequest, Review, User

# UserAdmin: https://docs.djangoproject.com/en/5.2/topics/auth/customizing/#custom-users-and-django-contrib-admin
admin.site.register(User, UserAdmin)
# Регистрация моделей: https://docs.djangoproject.com/en/5.2/ref/contrib/admin/#modeladmin-objects
admin.site.register(RentalRequest)
admin.site.register(Review)
