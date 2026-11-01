from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


# AbstractUser: https://docs.djangoproject.com/en/5.2/topics/auth/customizing/#django.contrib.auth.models.AbstractUser
class User(AbstractUser):
    full_name = models.CharField("ФИО", max_length=150)
    phone = models.CharField("Телефон", max_length=15)
    REQUIRED_FIELDS = ["email", "full_name", "phone"]


# Поля модели: https://docs.djangoproject.com/en/5.2/ref/models/fields/
class RentalRequest(models.Model):
    # Название машины хранится текстом, отдельная таблица не нужна.
    CAR_CHOICES = [
        ("LADA Vesta", "LADA Vesta"),
        ("Hyundai Creta", "Hyundai Creta"),
        ("Toyota Camry", "Toyota Camry"),
    ]

    # TextChoices: https://docs.djangoproject.com/en/5.2/ref/models/fields/#enumeration-types
    class Payment(models.TextChoices):
        CASH = "cash", "Наличными"
        TRANSFER = "transfer", "Переводом по номеру телефона"

    class Status(models.TextChoices):
        NEW = "new", "Новая"
        RENTING = "renting", "Идет аренда"
        COMPLETED = "completed", "Аренда завершена"

    # ForeignKey: https://docs.djangoproject.com/en/5.2/ref/models/fields/#django.db.models.ForeignKey
    # AUTH_USER_MODEL: https://docs.djangoproject.com/en/5.2/topics/auth/customizing/#referencing-the-user-model
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


class Review(models.Model):
    # OneToOneField: https://docs.djangoproject.com/en/5.2/ref/models/fields/#django.db.models.OneToOneField
    rental_request = models.OneToOneField(
        RentalRequest,
        on_delete=models.CASCADE,
        related_name="review",
        verbose_name="Заявка",
    )
    text = models.TextField("Отзыв о качестве услуг проката")
