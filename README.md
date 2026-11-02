# «Ключ.на.старт»: пишем сайт по рабочим этапам

Гайд для повторения варианта 3 с нуля: Django 5.2, PostgreSQL, локальный Bootstrap **5.0.2**. Имена проекта и приложения: `project` и `core`. Все пути указаны от папки с `manage.py`.

В существующем готовом проекте ничего повторно создавать и удалять не нужно. Для тренировки используй отдельную папку и отдельную пустую базу.

Двигаемся так:

1. Запускаем главную страницу и подключаем оформление.
2. Добавляем слайдер и карточки автомобилей.
3. Делаем регистрацию, вход и выход.
4. Добавляем создание и просмотр своих заявок, смену статуса в админке.
5. Добавляем отзывы после завершённой аренды.
6. Доводим стиль и добавляем маленький JS.

**Каждый этап заканчивается проверкой работающего сайта.** Внутри этапа сначала дописываем перечисленные файлы и только потом проверяем. Пока редактируешь несколько связанных файлов, autoreload может временно показывать ошибку.

Код с подписью «создать» или «заменить» — полное содержимое файла. «Добавить» означает сохранить уже написанный код. В импортируемые списки добавляй новые имена, не удаляя старые.

## Этап 1. Главная страница уже открывается

### 1.1. Создать проект и приложение

Если проект и приложение уже выданы и настроены, пропусти их создание.

В активированном виртуальном окружении с установленными Django и драйвером PostgreSQL:

```powershell
django-admin startproject project .
python manage.py startapp core
```

Создай папки `templates`, `static/css`, `static/js`. Скопируй выданные Bootstrap, картинки и шрифты:

```text
static/
    bootstrap/css/bootstrap.min.css
    bootstrap/js/bootstrap.bundle.min.js
    css/style.css
    js/main.js
    img/...
    fonts/Montserrat/...
templates/
```

Пока `style.css` и `main.js` могут быть пустыми. Нужен именно `bootstrap.bundle.min.js`: он обеспечивает работу меню и слайдера.

Если нужен новый репозиторий, выполни `git init`. В `.gitignore` добавь `.venv/`, `__pycache__/`, `*.pyc`. Коммиты в начале и конце модулей делай по требованиям экзамена.

### 1.2. Подключить приложение, шаблоны и статику

В `project/settings.py`:

- В существующий `INSTALLED_APPS` добавь `"core"`. Стандартные приложения оставь.
- В существующем словаре внутри `TEMPLATES` замени только `DIRS`:

```python
"DIRS": [BASE_DIR / "templates"],
```

Настройки языка и статики:

```python
LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "Europe/Moscow"

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
```

Стандартные middleware, context processors и `AUTH_PASSWORD_VALIDATORS` оставь: авторизация, админка и проверка пароля их используют.

### 1.3. Сразу объявить своего пользователя

Это маленькое исключение из порядка «сначала главная, потом авторизация». Своего пользователя нужно подключить **до первого `migrate`**. Формы регистрации и входа сделаем позже, сейчас только подготовим модель.

Документация: [своя модель пользователя в новом проекте](https://docs.djangoproject.com/en/5.2/topics/auth/customizing/#using-a-custom-user-model-when-starting-a-project).

**`core/models.py` — заменить:**

```python
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    full_name = models.CharField("ФИО", max_length=150)
    phone = models.CharField("Телефон", max_length=15)
    REQUIRED_FIELDS = ["email", "full_name", "phone"]
```

В `project/settings.py` добавь:

```python
AUTH_USER_MODEL = "core.User"
```

`AbstractUser` уже даёт логин, email, пароль, флаги администратора. Мы добавили только ФИО и телефон. Проверки их формата появятся в форме регистрации.

**`core/admin.py` — заменить:**

```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User

admin.site.register(User, UserAdmin)
```

### 1.4. Подключить базу и применить первые миграции

В pgAdmin создай **пустую** базу, например `django-cars-training`. В `project/settings.py` замени `DATABASES`, указав свои данные:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "django-cars-training",
        "USER": "postgres",
        "PASSWORD": "свой_пароль",
        "HOST": "localhost",
        "PORT": "5432",
    }
}
```

```powershell
python manage.py makemigrations
python manage.py migrate
```

### 1.5. Сделать view и маршруты главной страницы

Документация: [TemplateView](https://docs.djangoproject.com/en/5.2/ref/class-based-views/base/#django.views.generic.base.TemplateView).

**`core/views.py` — заменить:**

```python
from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = "home.html"
```

**`core/urls.py` — создать:**

```python
from django.urls import path

from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
]
```

**`project/urls.py` — заменить:**

```python
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
]
```

### 1.6. Сделать базовый шаблон и простую главную

Пока в меню только главная. Ссылок на регистрацию и заявки ещё нет: соответствующие маршруты мы пока не написали.

Bootstrap: [navbar и бургер](https://getbootstrap.com/docs/5.0/components/navbar/#toggler).

**`templates/base.html` — создать:**

```html
{% load static %}
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}Ключ.на.старт{% endblock %}</title>
  <link rel="icon" href="{% static 'img/logo_icon.png' %}">
  <link rel="stylesheet" href="{% static 'bootstrap/css/bootstrap.min.css' %}">
  <link rel="stylesheet" href="{% static 'css/style.css' %}">
</head>
<body class="d-flex flex-column min-vh-100 bg-light">
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container">
      <a class="navbar-brand" href="{% url 'home' %}">Ключ.на.старт</a>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse"
              data-bs-target="#navigation" aria-controls="navigation"
              aria-expanded="false" aria-label="Открыть меню">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navigation">
        <div class="navbar-nav ms-auto align-items-lg-center gap-lg-2">
          <a class="nav-link" href="{% url 'home' %}">Автомобили</a>
        </div>
      </div>
    </div>
  </nav>

  <main class="container py-4 flex-grow-1">
    {% block content %}{% endblock %}
  </main>

  <footer class="bg-dark text-white-50 py-4 mt-3">
    <div class="container">
      © <span id="current-year">{% now 'Y' %}</span> Ключ.на.старт
    </div>
  </footer>
  <script src="{% static 'bootstrap/js/bootstrap.bundle.min.js' %}"></script>
  <script src="{% static 'js/main.js' %}"></script>
</body>
</html>
```

**`templates/home.html` — создать:**

```html
{% extends 'base.html' %}
{% block content %}
  <h1>Ключ к вашим путешествиям</h1>
  <p>Выберите автомобиль для своей поездки.</p>
{% endblock %}
```

### Проверка этапа 1

```powershell
python manage.py runserver
```

Открой `http://127.0.0.1:8000/`: видны меню, заголовок и подвал. На узком экране кнопка меню раскрывает навигацию. Если Bootstrap не работает, сначала проверь пути к его CSS и JS.

**Уже есть:** работающая главная страница, шаблоны, статика и подготовленная база.

## Этап 2. Главная со слайдером и автомобилями

### 2.1. Передать список карточек

В `core/views.py` **замени только класс `HomeView`**:

```python
class HomeView(TemplateView):
    template_name = "home.html"
    extra_context = {
        "cars": [
            {
                "name": "LADA Vesta",
                "image": "img/Lada.webp",
                "description": "Практичный седан для городских поездок.",
            },
            {
                "name": "Hyundai Creta",
                "image": "img/Hyundai.webp",
                "description": "Удобный автомобиль для семейных путешествий.",
            },
            {
                "name": "Toyota Camry",
                "image": "img/Toyota.webp",
                "description": "Комфортный седан для дальних маршрутов.",
            },
        ]
    }
```

Для этих карточек не нужны модель, форма и миграции.

### 2.2. Сверстать слайдер и карточки

Bootstrap: [слайдер](https://getbootstrap.com/docs/5.0/components/carousel/#with-controls), [интервал слайдера](https://getbootstrap.com/docs/5.0/components/carousel/#options), [карточка](https://getbootstrap.com/docs/5.0/components/card/#example), [сетка](https://getbootstrap.com/docs/5.0/layout/grid/).

**`templates/home.html` — заменить:**

```html
{% extends 'base.html' %}
{% load static %}
{% block content %}
  <h1>Ключ к вашим путешествиям</h1>
  <p class="text-secondary">Выберите автомобиль для своей поездки.</p>

  <div id="car-slider" class="carousel slide rounded overflow-hidden mb-4"
       data-bs-ride="carousel" data-bs-interval="3000">
    <div class="carousel-inner">
      <div class="carousel-item active">
        <img src="{% static 'img/slide1.jpg' %}" class="d-block w-100" alt="Автомобиль для путешествия">
      </div>
      <div class="carousel-item">
        <img src="{% static 'img/slide2.webp' %}" class="d-block w-100" alt="Новые маршруты">
      </div>
      <div class="carousel-item">
        <img src="{% static 'img/slide3.jpg' %}" class="d-block w-100" alt="Свобода передвижения">
      </div>
      <div class="carousel-item">
        <img src="{% static 'img/Toyota.webp' %}" class="d-block w-100" alt="Toyota Camry">
      </div>
    </div>
    <button class="carousel-control-prev" type="button"
            data-bs-target="#car-slider" data-bs-slide="prev">
      <span class="carousel-control-prev-icon" aria-hidden="true"></span>
      <span class="visually-hidden">Назад</span>
    </button>
    <button class="carousel-control-next" type="button"
            data-bs-target="#car-slider" data-bs-slide="next">
      <span class="carousel-control-next-icon" aria-hidden="true"></span>
      <span class="visually-hidden">Вперёд</span>
    </button>
  </div>

  <h2 class="mb-4">Наши автомобили</h2>
  <div class="row g-4">
    {% for car in cars %}
      <div class="col-md-4">
        <article class="card car-card h-100 border-0 shadow-sm">
          <img src="{% static car.image %}" class="card-img-top" alt="{{ car.name }}" loading="lazy">
          <div class="card-body">
            <h3>{{ car.name }}</h3>
            <p class="text-secondary mb-0">{{ car.description }}</p>
          </div>
        </article>
      </div>
    {% endfor %}
  </div>
{% endblock %}
```

У первого слайда обязательно `active`. Имена `#car-slider` в кнопках и `id` слайдера должны совпадать.

**`static/css/style.css` — добавить:**

```css
.carousel-item img {
  height: 380px;
  object-fit: cover;
}

.car-card img {
  aspect-ratio: 4 / 3;
  object-fit: cover;
}

@media (max-width: 575.98px) {
  .carousel-item img { height: 220px; }
}
```

### Проверка этапа 2

Обнови главную. Есть четыре слайда, кнопки назад/вперёд, автоматическая смена каждые три секунды. Высота слайдера не скачет. На широком экране карточки стоят в три колонки, на телефоне — в одну.

**Уже есть:** готовая публичная главная. Регистрация и заявки пока не мешают ей работать.

## Этап 3. Регистрация, вход и выход

Модель пользователя уже существует. Теперь делаем весь сценарий авторизации: формы → views → шаблоны → маршруты → меню.

### 3.1. Формы и BootstrapMixin

Документация: [UserCreationForm и AuthenticationForm](https://docs.djangoproject.com/en/5.2/topics/auth/default/#built-in-auth-forms), [RegexField](https://docs.djangoproject.com/en/5.2/ref/forms/fields/#regexfield).

**`core/forms.py` — создать:**

```python
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import User


class BootstrapMixin:
    fields: dict[str, forms.Field]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = (
                "form-select"
                if isinstance(field.widget, forms.Select)
                else "form-control"
            )


class RegisterForm(BootstrapMixin, UserCreationForm):
    username = forms.RegexField(
        label="Логин",
        regex=r"\A[a-zA-Z0-9]+\Z",
        min_length=6,
        max_length=150,
    )
    full_name = forms.RegexField(
        label="ФИО",
        regex=r"\A[А-Яа-яЁё]+(?: [А-Яа-яЁё]+)*\Z",
        max_length=150,
    )
    phone = forms.RegexField(
        label="Телефон",
        regex=r"\A8\([0-9]{3}\)[0-9]{3}-[0-9]{2}-[0-9]{2}\Z",
        widget=forms.TextInput(attrs={"placeholder": "8(999)999-99-99"}),
    )
    email = forms.EmailField(label="Электронная почта")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["username", "full_name", "phone", "email"]


class LoginForm(BootstrapMixin, AuthenticationForm):
    pass
```

`UserCreationForm` сама добавляет два поля пароля, проверяет их совпадение и сохраняет хеш. Минимум восемь символов проверяет стандартный `MinimumLengthValidator` из настроек. Уникальность логина уже задана в `AbstractUser`.

### 3.2. Views регистрации и входа

Документация: [LoginView](https://docs.djangoproject.com/en/5.2/topics/auth/default/#django.contrib.auth.views.LoginView), [CreateView](https://docs.djangoproject.com/en/5.2/ref/class-based-views/generic-editing/#django.views.generic.edit.CreateView).

В `core/views.py` добавь импорты. Существующий импорт `TemplateView` расширь до `CreateView, TemplateView`:

```python
from django.contrib.auth.views import LoginView as BaseLoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from .forms import LoginForm, RegisterForm
```

После `HomeView` добавь:

```python
class LoginView(BaseLoginView):
    template_name = "auth.html"
    authentication_form = LoginForm
    extra_context = {"title": "Вход", "button_text": "Войти"}


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "auth.html"
    success_url = reverse_lazy("login")
    extra_context = {
        "title": "Регистрация",
        "button_text": "Зарегистрироваться",
        "is_registration": True,
    }
```

В `project/settings.py` добавь:

```python
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "login"
```

### 3.3. Общий вывод полей и ошибок

Bootstrap: [поля формы](https://getbootstrap.com/docs/5.0/forms/form-control/), [select](https://getbootstrap.com/docs/5.0/forms/select/), [ошибки в alert](https://getbootstrap.com/docs/5.0/components/alerts/).

**`templates/fields.html` — создать рядом с остальными шаблонами:**

```html
{% for error in form.non_field_errors %}
  <div class="alert alert-danger" role="alert">{{ error }}</div>
{% endfor %}

{% for field in form %}
  <div class="mb-3">
    <label class="form-label" for="{{ field.id_for_label }}">{{ field.label }}</label>
    {{ field }}
    {% if field.help_text %}
      <div class="form-text">{{ field.help_text|safe }}</div>
    {% endif %}
    {% for error in field.errors %}
      <div class="text-danger small mt-1">{{ error }}</div>
    {% endfor %}
  </div>
{% endfor %}
```

`non_field_errors` нужны, например, для ошибки неверного логина или пароля. `field.errors` показывают ошибки конкретного поля.

### 3.4. Один шаблон для регистрации и входа

**`templates/auth.html` — создать:**

```html
{% extends 'base.html' %}
{% block title %}{{ title }} — Ключ.на.старт{% endblock %}
{% block content %}
  <div class="row justify-content-center">
    <div class="col-md-8 col-lg-6">
      <div class="card border-0 shadow-sm">
        <div class="card-body p-4">
          <h1 class="mb-4">{{ title }}</h1>
          <form method="post">
            {% csrf_token %}
            {% include 'fields.html' %}
            {% if next %}
              <input type="hidden" name="next" value="{{ next }}">
            {% endif %}
            <button class="btn btn-primary w-100">{{ button_text }}</button>
          </form>
          <p class="mt-3 mb-0 text-center">
            {% if is_registration %}
              Уже зарегистрированы? <a href="{% url 'login' %}">Войти</a>
            {% else %}
              Ещё не зарегистрированы? <a href="{% url 'register' %}">Регистрация</a>
            {% endif %}
          </p>
        </div>
      </div>
    </div>
  </div>
{% endblock %}
```

`next` пригодится позже: если гость откроет защищённую страницу, после входа его вернут на неё.

### 3.5. Подключить маршруты и обновить меню

В `core/urls.py` добавь импорт:

```python
from django.contrib.auth.views import LogoutView
```

Внутрь `urlpatterns` после главной добавь:

```python
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
```

В `base.html` **внутри** `div.navbar-nav`, после ссылки «Автомобили», добавь:

```html
{% if user.is_authenticated %}
  {% if user.is_staff %}
    <a class="nav-link" href="{% url 'admin:index' %}">Админка</a>
  {% endif %}
  <form method="post" action="{% url 'logout' %}" class="my-2 my-lg-0">
    {% csrf_token %}
    <button class="btn btn-outline-light btn-sm">Выйти</button>
  </form>
{% else %}
  <a class="nav-link" href="{% url 'login' %}">Вход</a>
  <a class="nav-link" href="{% url 'register' %}">Регистрация</a>
{% endif %}
```

Выход сделан POST-формой с CSRF, как требуется для `LogoutView` в Django 5. Миграции на этом этапе не нужны: модели не менялись.

### Проверка этапа 3

Зарегистрируй пользователя, например:

```text
Логин: driver123
ФИО: Иванов Иван Иванович
Телефон: 8(999)123-45-67
Email: driver@example.com
Пароль: Travel2026!pass
```

После регистрации откроется вход. Проверь неверный пароль, успешный вход и выход. Попробуй повторно зарегистрировать тот же логин, короткий логин, неверный телефон и латиницу в ФИО — должны появляться ошибки.

**Уже есть:** главная и полностью работающая авторизация.

## Этап 4. Пользователь создаёт заявки, администратор меняет статус

Делаем сразу весь сценарий заявок. Отзывы пока не импортируем и не проверяем: их модели ещё нет.

### 4.1. Модель заявки

В `core/models.py` добавь импорт:

```python
from django.conf import settings
```

После `User` добавь:

```python
class RentalRequest(models.Model):
    CAR_CHOICES = [
        ("LADA Vesta", "LADA Vesta"),
        ("Hyundai Creta", "Hyundai Creta"),
        ("Toyota Camry", "Toyota Camry"),
    ]

    class Payment(models.TextChoices):
        CASH = "cash", "Наличными"
        TRANSFER = "transfer", "Переводом по номеру телефона"

    class Status(models.TextChoices):
        NEW = "new", "Новая"
        RENTING = "renting", "Идет аренда"
        COMPLETED = "completed", "Аренда завершена"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="rental_requests",
        verbose_name="Пользователь",
    )
    car = models.CharField("Автомобиль", max_length=50, choices=CAR_CHOICES)
    start_date = models.DateField("Дата начала аренды")
    payment = models.CharField("Способ оплаты", max_length=10, choices=Payment.choices)
    status = models.CharField(
        "Статус", max_length=10, choices=Status.choices, default=Status.NEW
    )
    created_at = models.DateTimeField("Создана", auto_now_add=True)
```

Машина хранится обычным текстом. `choices` создаёт выпадающий список в форме. Статус по умолчанию задаётся в модели.

В `core/admin.py` добавь `RentalRequest` к импорту моделей и зарегистрируй:

```python
admin.site.register(RentalRequest)
```

```powershell
python manage.py makemigrations
python manage.py migrate
```

### 4.2. Форма заявки

В `core/forms.py` добавь `RentalRequest` к импорту моделей. После существующих форм добавь:

```python
class RentalRequestForm(BootstrapMixin, forms.ModelForm):
    start_date = forms.DateField(
        label="Дата начала аренды",
        input_formats=["%d.%m.%Y"],
        widget=forms.DateInput(format="%d.%m.%Y", attrs={"placeholder": "ДД.ММ.ГГГГ"}),
    )

    class Meta:
        model = RentalRequest
        fields = ["car", "start_date", "payment"]
```

Пользователя и статус в форму не включаем. Дата отображается текстовым полем; `input_formats` задаёт ввод `25.12.2026`. Проверку существования даты выполняет Django.

Документация: [ModelForm](https://docs.djangoproject.com/en/5.2/topics/forms/modelforms/), [DateField](https://docs.djangoproject.com/en/5.2/ref/forms/fields/#datefield).

### 4.3. Просмотр своих заявок и создание новой

В `core/views.py` добавь импорты:

```python
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import RentalRequest
```

В существующий импорт generic views добавь `ListView`, в импорт форм — `RentalRequestForm`. После существующих классов добавь:

```python
class RentalRequestListView(LoginRequiredMixin, ListView):
    template_name = "requests.html"
    context_object_name = "rental_requests"

    def get_queryset(self):
        return RentalRequest.objects.filter(user=self.request.user)


class RentalRequestCreateView(LoginRequiredMixin, CreateView):
    form_class = RentalRequestForm
    template_name = "form.html"
    success_url = reverse_lazy("requests")
    extra_context = {"title": "Новая заявка", "button_text": "Отправить"}

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
```

`LoginRequiredMixin` ставим первым. `filter` ограничивает список текущим пользователем. В `form_valid` назначаем владельца перед стандартным сохранением формы.

Документация: [ListView](https://docs.djangoproject.com/en/5.2/ref/class-based-views/generic-display/#django.views.generic.list.ListView), [LoginRequiredMixin](https://docs.djangoproject.com/en/5.2/topics/auth/default/#the-loginrequiredmixin-mixin), [назначение пользователя в form_valid](https://docs.djangoproject.com/en/5.2/topics/class-based-views/generic-editing/#models-and-request-user).

### 4.4. Шаблон формы заявки

**`templates/form.html` — создать:**

```html
{% extends 'base.html' %}
{% block title %}{{ title }} — Ключ.на.старт{% endblock %}
{% block content %}
  <div class="row justify-content-center">
    <div class="col-md-8 col-lg-6">
      <div class="card border-0 shadow-sm">
        <div class="card-body p-4">
          <h1 class="mb-4">{{ title }}</h1>
          <form method="post">
            {% csrf_token %}
            {% include 'fields.html' %}
            <div class="d-flex flex-wrap gap-2">
              <button class="btn btn-primary">{{ button_text }}</button>
              <a class="btn btn-outline-secondary" href="{% url 'requests' %}">К моим заявкам</a>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
{% endblock %}
```

Этот же шаблон потом используем для отзыва.

### 4.5. Список заявок — пока без отзывов

**`templates/requests.html` — создать:**

```html
{% extends 'base.html' %}
{% block title %}Мои заявки — Ключ.на.старт{% endblock %}
{% block content %}
  <div class="d-flex flex-wrap align-items-center justify-content-between gap-3 mb-4">
    <h1 class="mb-0">Мои заявки</h1>
    <a class="btn btn-primary" href="{% url 'request_create' %}">Новая заявка</a>
  </div>
  {% for rental in rental_requests %}
    <article class="card border-0 shadow-sm mb-3">
      <div class="card-body p-4">
        <div class="d-flex flex-wrap align-items-center justify-content-between gap-2 mb-3">
          <h2 class="mb-0">{{ rental.car }} · №{{ rental.pk }}</h2>
          {% if rental.status == 'new' %}
            <span class="badge bg-secondary">{{ rental.get_status_display }}</span>
          {% elif rental.status == 'renting' %}
            <span class="badge bg-primary">{{ rental.get_status_display }}</span>
          {% else %}
            <span class="badge bg-dark">{{ rental.get_status_display }}</span>
          {% endif %}
        </div>
        <p class="mb-1">Начало аренды: {{ rental.start_date|date:'d.m.Y' }}</p>
        <p class="mb-1">Оплата: {{ rental.get_payment_display }}</p>
        <p class="text-secondary small">Создана: {{ rental.created_at|date:'d.m.Y H:i' }}</p>
      </div>
    </article>
  {% empty %}
    <div class="alert alert-light border">У вас пока нет заявок.</div>
  {% endfor %}
{% endblock %}
```

`get_status_display` и `get_payment_display` выводят русские подписи из `choices`, а не значения `new` и `cash`.

### 4.6. Подключить страницы к сайту

В `core/urls.py` внутрь `urlpatterns` добавь:

```python
    path("requests/", views.RentalRequestListView.as_view(), name="requests"),
    path("requests/new/", views.RentalRequestCreateView.as_view(), name="request_create"),
```

В `base.html` сразу после **внешнего** `{% if user.is_authenticated %}` добавь:

```html
<a class="nav-link" href="{% url 'requests' %}">Мои заявки</a>
<a class="nav-link" href="{% url 'request_create' %}">Новая заявка</a>
```

Теперь в `home.html` под вводным абзацем добавь:

```html
<p><a class="btn btn-primary" href="{% url 'request_create' %}">Оформить аренду</a></p>
```

И в каждой карточке **внутри цикла**, после описания машины, добавь:

```html
<a class="btn btn-outline-primary mt-3" href="{% url 'request_create' %}">Оформить заявку</a>
```

Ссылка одинаковая для всех машин: выбор делается в форме. Передавать машину из карточки по заданию не требуется.

### 4.7. Создать администратора

Если администратора ещё нет:

```powershell
python manage.py createsuperuser --username Admin
```

Введи email, ФИО, телефон и пароль из задания: `StartNET`. Это учебный пароль из семи символов; команда предупредит о длине. Подтверди создание, ответив `y`. Валидаторы в настройках оставь — в регистрации пользователя по-прежнему нужен минимум восемь символов.

В `/admin/` открой заявку и измени её статус. Собственные классы админки не нужны: зарегистрированная модель уже имеет список, форму редактирования и пагинацию.

### Проверка этапа 4

1. Выйди и открой `/requests/new/`: должно перенаправить на вход.
2. Войди: благодаря `next` откроется форма заявки.
3. Проверь три автомобиля в select, два способа оплаты, дату `25.12.2026`.
4. Введи `31.02.2026`: должна появиться ошибка. Исправь и отправь форму.
5. После сохранения откроются свои заявки. У новой заявки статус «Новая».
6. В админке смени статус на «Идет аренда», затем «Аренда завершена». Проверь отображение в личном списке.
7. Войди вторым обычным пользователем: он не должен видеть заявки первого.

**Уже есть:** основной рабочий портал аренды с управлением статусами. Если дальше не успеть, этот сценарий уже работает.

## Этап 5. Отзыв после завершённой аренды

### 5.1. Модель отзыва

В конец `core/models.py` добавь:

```python
class Review(models.Model):
    rental_request = models.OneToOneField(
        RentalRequest,
        on_delete=models.CASCADE,
        related_name="review",
        verbose_name="Заявка",
    )
    text = models.TextField("Отзыв о качестве услуг проката")
```

`OneToOneField` означает один отзыв на одну заявку. Автор определяется через `review.rental_request.user`, отдельное поле пользователя не нужно.

В `core/admin.py` добавь `Review` к импорту моделей и зарегистрируй:

```python
admin.site.register(Review)
```

```powershell
python manage.py makemigrations
python manage.py migrate
```

### 5.2. Форма отзыва

В `core/forms.py` добавь `Review` к импорту моделей. В конец файла добавь:

```python
class ReviewForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Review
        fields = ["text"]
        widgets = {"text": forms.Textarea(attrs={"rows": 4})}
```

### 5.3. Обработчик отзыва

В `core/views.py` добавь импорты:

```python
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
```

В существующий импорт форм добавь `ReviewForm`. В конец файла добавь:

```python
@login_required
def review_create(request, pk):
    rental_request = get_object_or_404(
        RentalRequest,
        pk=pk,
        user=request.user,
        status=RentalRequest.Status.COMPLETED,
        review__isnull=True,
    )
    form = ReviewForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
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
```

Здесь оставляем функцию, как в текущем проекте. Она использует уже готовые `ReviewForm`, `form.html` и `fields.html`.

Проверяем право на отзыв **на сервере**, а не только прячем кнопку: заявка своя, аренда завершена, отзыва ещё нет. Иначе вернётся 404.

Документация: [get_object_or_404](https://docs.djangoproject.com/en/5.2/topics/http/shortcuts/#get-object-or-404), [save(commit=False)](https://docs.djangoproject.com/en/5.2/topics/forms/modelforms/#the-save-method).

### 5.4. Маршрут и вывод в списке заявок

В `core/urls.py` внутрь `urlpatterns` добавь:

```python
    path("requests/<int:pk>/review/", views.review_create, name="review_create"),
```

В `requests.html` внутри карточки, сразу **после абзаца «Создана»**, добавь:

```html
{% if rental.review %}
  <div class="bg-light rounded p-3">
    <h3>Ваш отзыв</h3>
    <div class="review-text">{{ rental.review.text|linebreaksbr }}</div>
  </div>
{% elif rental.status == 'completed' %}
  <a class="btn btn-outline-primary btn-sm" href="{% url 'review_create' rental.pk %}">Оставить отзыв</a>
{% else %}
  <p class="text-secondary small mb-0">Оставить отзыв можно после завершения аренды.</p>
{% endif %}
```

Теперь при желании в `RentalRequestListView.get_queryset` можно заменить `return` на:

```python
        return RentalRequest.objects.filter(user=self.request.user).select_related("review")
```

Это только сокращает количество SQL-запросов при выводе отзывов. Для работоспособности обычного `filter` достаточно. **До создания `Review` этот `select_related` добавлять нельзя.**

### Проверка этапа 5

У новой заявки и заявки в аренде кнопки отзыва нет. После завершения появляется. Пустой отзыв не сохраняется. После отправки текст показывается в карточке, кнопка исчезает. Повторное открытие адреса `/requests/ID/review/` возвращает 404; для чужой заявки — тоже.

**Уже есть:** весь пользовательский сценарий, включая отзывы.

## Этап 6. Цвета, шрифты, небольшая анимация и JS

Основной функционал уже закончен. Теперь дописываем оформление по выданному руководству. Bootstrap остаётся версии 5.0.2.

### 6.1. Дополнить CSS

В `static/css/style.css` сохрани правила изображений из этапа 2 и добавь:

```css
@font-face {
  font-family: "Montserrat";
  src: url("../fonts/Montserrat/Montserrat-Regular.ttf") format("truetype");
  font-weight: 400;
  font-style: normal;
  font-display: swap;
}

@font-face {
  font-family: "Montserrat";
  src: url("../fonts/Montserrat/Montserrat-Bold.ttf") format("truetype");
  font-weight: 700;
  font-style: normal;
  font-display: swap;
}

@font-face {
  font-family: "Montserrat";
  src: url("../fonts/Montserrat/Montserrat-Italic.ttf") format("truetype");
  font-weight: 400;
  font-style: italic;
  font-display: swap;
}

body {
  font-family: "Montserrat", sans-serif;
  font-size: 16px;
  color: #212b36;
  background-color: #f8f9fa;
}

h1, h2, h3 { font-weight: 700; }
h1 { font-size: 36px; }
h2 { font-size: 24px; }
h3 { font-size: 18px; }

small, .small, .form-text, footer {
  font-size: 12px;
  font-style: italic;
}

.bg-dark { background-color: #212b36 !important; }

.btn-primary, .btn-outline-primary, .bg-primary {
  background-color: #d9480f !important;
  border-color: #d9480f !important;
  color: #fff !important;
}

a, a:hover { color: #d9480f; }
.card-body, .review-text { overflow-wrap: anywhere; }

.btn { transition: transform 0.2s; }
.btn:active { transform: scale(0.98); }

@media (prefers-reduced-motion: reduce) {
  .btn { transition: none; }
}
```

Это короткий вариант оформления. Кнопки обоих видов будут оранжевыми с белым текстом. Маленькое уменьшение кнопки при нажатии даёт микроанимацию из задания. Другие эффекты для выполнения этого пункта добавлять не обязательно.

### 6.2. Год в подвале и счётчик символов

**`static/js/main.js` — заменить:**

```javascript
const year = document.getElementById("current-year");
if (year) year.textContent = new Date().getFullYear();

const review = document.getElementById("id_text");
if (review) {
  const counter = document.createElement("div");
  counter.className = "form-text";
  review.after(counter);

  function updateCounter() {
    counter.textContent = `Символов: ${review.value.length}`;
  }
  review.addEventListener("input", updateCounter);
  updateCounter();
}
```

Скрипт уже подключён в `base.html`. Проверки `if` позволяют подключать его на всех страницах, даже когда поля отзыва нет.

### Проверка этапа 6 и всего сайта

```powershell
python manage.py check
```

В браузере открой **каждую** страницу при ширине **390** и высоте **844**: главная, регистрация, вход, заявки, новая заявка, отзыв. Проверь меню, отсутствие горизонтальной прокрутки и видимость ошибок. Если CSS закешировался, обнови через `Ctrl+F5`.

Шрифт должен загружаться локально, кнопки — быть оранжевыми, счётчик отзыва — обновляться при вводе. Перепроверь цепочку: регистрация → вход → заявка → смена статуса администратором → отзыв.

## Что ещё сдать по заданию

Этапы выше покрывают код портала. Отдельно не забудь:

- Построить ER-диаграмму **средствами СУБД**, когда готовы все три модели. Для PostgreSQL можно использовать ERD Tool в pgAdmin.
- Оптимизировать копии выданных изображений под отображаемый размер: CSS обрезает картинку, но не уменьшает размер скачиваемого файла. После обработки проверь качество и пути в шаблонах.
- Делать коммиты в начале и конце модулей и отправить результат в экзаменационный репозиторий.
- Отдельный модуль с прототипом «Группа Таймыр» выполнять отдельно: этот гайд посвящён Django-порталу аренды.

Если времени мало, сначала заканчивай очередной рабочий этап и проверяй его. Стиль и JS можно дописать после основного сценария; незаконченные ссылки и импорты следующих этапов заранее не добавляй.
