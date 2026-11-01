from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

# path и маршруты: https://docs.djangoproject.com/en/5.2/topics/http/urls/#example
urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    # LogoutView: https://docs.djangoproject.com/en/5.2/topics/auth/default/#django.contrib.auth.views.LogoutView
    path("logout/", LogoutView.as_view(), name="logout"),
    path("requests/", views.RentalRequestListView.as_view(), name="requests"),
    path(
        "requests/new/", views.RentalRequestCreateView.as_view(), name="request_create"
    ),
    path("requests/<int:pk>/review/", views.review_create, name="review_create"),
]
