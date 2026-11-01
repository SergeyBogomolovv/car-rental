from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import RentalRequest, Review, User


class BootstrapMixin:
    # Поля экземпляра формы: https://docs.djangoproject.com/en/5.2/ref/forms/api/#django.forms.Form.fields
    fields: dict[str, forms.Field]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = (
                "form-select"
                if isinstance(field.widget, forms.Select)
                else "form-control"
            )


# UserCreationForm: https://docs.djangoproject.com/en/5.2/topics/auth/default/#django.contrib.auth.forms.UserCreationForm
class RegisterForm(BootstrapMixin, UserCreationForm):
    # RegexField: https://docs.djangoproject.com/en/5.2/ref/forms/fields/#regexfield
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


# AuthenticationForm: https://docs.djangoproject.com/en/5.2/topics/auth/default/#django.contrib.auth.forms.AuthenticationForm
class LoginForm(BootstrapMixin, AuthenticationForm):
    pass


# ModelForm и Meta: https://docs.djangoproject.com/en/5.2/topics/forms/modelforms/#modelform
class RentalRequestForm(BootstrapMixin, forms.ModelForm):
    # DateField и input_formats: https://docs.djangoproject.com/en/5.2/ref/forms/fields/#datefield
    # DateInput: https://docs.djangoproject.com/en/5.2/ref/forms/widgets/#django.forms.DateInput
    start_date = forms.DateField(
        label="Дата начала аренды",
        input_formats=["%d.%m.%Y"],
        widget=forms.DateInput(format="%d.%m.%Y", attrs={"placeholder": "ДД.ММ.ГГГГ"}),
    )

    class Meta:
        model = RentalRequest
        fields = ["car", "start_date", "payment"]


# Настройка виджетов: https://docs.djangoproject.com/en/5.2/topics/forms/modelforms/#overriding-the-default-fields
class ReviewForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Review
        fields = ["text"]
        widgets = {"text": forms.Textarea(attrs={"rows": 4})}
