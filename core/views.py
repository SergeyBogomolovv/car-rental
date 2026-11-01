from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as BaseLoginView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, TemplateView

from .forms import LoginForm, RegisterForm, RentalRequestForm, ReviewForm
from .models import RentalRequest


# TemplateView: https://docs.djangoproject.com/en/5.2/ref/class-based-views/base/#django.views.generic.base.TemplateView
class HomeView(TemplateView):
    template_name = "home.html"
    extra_context = {
        "cars": [
            {
                "name": "LADA Vesta",
                "image": "img/Lada.webp",
                "description": "Практичный седан для ежедневных поездок по городу.",
            },
            {
                "name": "Hyundai Creta",
                "image": "img/Hyundai.webp",
                "description": "Удобный кроссовер для семейных планов и загородных маршрутов.",
            },
            {
                "name": "Toyota Camry",
                "image": "img/Toyota.webp",
                "description": "Комфортный седан для деловых встреч и дальних путешествий.",
            },
        ],
    }


# LoginView: https://docs.djangoproject.com/en/5.2/topics/auth/default/#django.contrib.auth.views.LoginView
class LoginView(BaseLoginView):
    template_name = "auth.html"
    authentication_form = LoginForm
    extra_context = {"title": "Вход", "button_text": "Войти"}


# CreateView: https://docs.djangoproject.com/en/5.2/ref/class-based-views/generic-editing/#django.views.generic.edit.CreateView
class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "auth.html"
    # reverse_lazy: https://docs.djangoproject.com/en/5.2/ref/urlresolvers/#reverse-lazy
    success_url = reverse_lazy("login")
    extra_context = {
        "title": "Регистрация",
        "button_text": "Зарегистрироваться",
        "is_registration": True,
    }


# ListView: https://docs.djangoproject.com/en/5.2/ref/class-based-views/generic-display/#django.views.generic.list.ListView
# LoginRequiredMixin: https://docs.djangoproject.com/en/5.2/topics/auth/default/#django.contrib.auth.mixins.LoginRequiredMixin
class RentalRequestListView(LoginRequiredMixin, ListView):
    template_name = "requests.html"
    context_object_name = "rental_requests"

    def get_queryset(self):
        # Чужие заявки не попадают в список. Отзыв загружаем тем же запросом.
        # filter: https://docs.djangoproject.com/en/5.2/ref/models/querysets/#filter
        # select_related: https://docs.djangoproject.com/en/5.2/ref/models/querysets/#select-related
        return RentalRequest.objects.filter(user=self.request.user).select_related(
            "review"
        )


class RentalRequestCreateView(LoginRequiredMixin, CreateView):
    form_class = RentalRequestForm
    template_name = "form.html"
    success_url = reverse_lazy("requests")
    extra_context = {"title": "Новая заявка", "button_text": "Отправить"}

    def form_valid(self, form):
        # Владелец и начальный статус не передаются пользователем в форме.
        # Пример form_valid: https://docs.djangoproject.com/en/5.2/topics/class-based-views/generic-editing/#models-and-request-user
        form.instance.user = self.request.user
        return super().form_valid(form)


# login_required: https://docs.djangoproject.com/en/5.2/topics/auth/default/#django.contrib.auth.decorators.login_required
@login_required
def review_create(request, pk):
    # get_object_or_404: https://docs.djangoproject.com/en/5.2/topics/http/shortcuts/#get-object-or-404
    rental_request = get_object_or_404(
        RentalRequest,
        pk=pk,
        user=request.user,
        status=RentalRequest.Status.COMPLETED,
        review__isnull=True,
    )
    form = ReviewForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        # save(commit=False): https://docs.djangoproject.com/en/5.2/topics/forms/modelforms/#the-save-method
        review = form.save(commit=False)
        review.rental_request = rental_request
        review.save()
        return redirect("requests")
    return render(
        request,
        "form.html",
        {
            "form": form,
            "title": f"Отзыв об аренде {rental_request.car}",
            "button_text": "Отправить отзыв",
        },
    )
