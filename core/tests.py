from django.test import TestCase
from django.urls import reverse

from .forms import RegisterForm, RentalRequestForm
from .models import RentalRequest, Review, User


class RentalFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="driver1", password="Travel2026!pass"
        )
        self.other = User.objects.create_user(
            username="driver2", password="Travel2026!pass"
        )
        self.data = {"car": "LADA Vesta", "start_date": "25.12.2026", "payment": "cash"}
        self.rental = RentalRequest.objects.create(
            user=self.user,
            car="LADA Vesta",
            start_date="2026-12-25",
            payment="cash",
        )

    def test_public_pages_and_login_required(self):
        for name in ["home", "login", "register"]:
            with self.subTest(page=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)
        for name in ["requests", "request_create"]:
            with self.subTest(page=name):
                self.assertRedirects(
                    self.client.get(reverse(name)), f"/login/?next={reverse(name)}"
                )

    def test_registration_login_and_logout(self):
        data = {
            "username": "newdriver",
            "full_name": "Иванов Иван Иванович",
            "phone": "8(999)123-45-67",
            "email": "driver@example.com",
            "password1": "Travel2026!pass",
            "password2": "Travel2026!pass",
        }
        self.assertRedirects(
            self.client.post(reverse("register"), data), reverse("login")
        )
        user = User.objects.get(username="newdriver")
        self.assertTrue(user.check_password(data["password1"]))
        self.assertFalse(RegisterForm(data).is_valid())  # Повторный логин.
        response = self.client.post(
            reverse("login"), {"username": "newdriver", "password": "wrong"}
        )
        self.assertContains(response, "Пожалуйста, введите правильные")
        self.assertRedirects(
            self.client.post(
                reverse("login"),
                {
                    "username": "newdriver",
                    "password": data["password1"],
                },
            ),
            reverse("home"),
        )
        self.assertRedirects(self.client.post(reverse("logout")), reverse("login"))

    def test_registration_validation(self):
        valid = {
            "username": "newdriver",
            "full_name": "Иванов Иван",
            "phone": "8(999)123-45-67",
            "email": "driver@example.com",
            "password1": "Travel2026!pass",
            "password2": "Travel2026!pass",
        }
        for field, value in [
            ("username", "short"),
            ("username", "водитель"),
            ("username", "driver@1"),
            ("full_name", "Ivan Ivanov"),
            ("phone", "89991234567"),
            ("email", "wrong"),
            ("password2", "different"),
            ("full_name", ""),
            ("phone", ""),
            ("email", ""),
        ]:
            with self.subTest(field=field, value=value):
                form = RegisterForm({**valid, field: value})
                self.assertFalse(form.is_valid())
                self.assertIn(field, form.errors)
        form = RegisterForm({**valid, "password1": "abc", "password2": "abc"})
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_request_owner_status_and_date(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("request_create"),
            {
                **self.data,
                "user": self.other.pk,
                "status": "completed",
            },
        )
        self.assertRedirects(response, reverse("requests"))
        rental = RentalRequest.objects.exclude(pk=self.rental.pk).get()
        self.assertEqual(rental.user, self.user)
        self.assertEqual(rental.status, RentalRequest.Status.NEW)
        self.assertEqual(rental.start_date.isoformat(), "2026-12-25")
        for field, value in [
            ("car", "Unknown"),
            ("payment", "card"),
            ("start_date", "31.02.2026"),
            ("start_date", "2026-12-25"),
        ]:
            with self.subTest(field=field, value=value):
                form = RentalRequestForm({**self.data, field: value})
                self.assertFalse(form.is_valid())
                self.assertIn(field, form.errors)

    def test_only_own_requests_are_listed(self):
        foreign = RentalRequest.objects.create(
            user=self.other,
            car="Toyota Camry",
            start_date="2026-12-25",
            payment="cash",
        )
        self.client.force_login(self.user)
        response = self.client.get(reverse("requests"))
        self.assertEqual(list(response.context["rental_requests"]), [self.rental])
        self.assertNotContains(response, foreign.car)

    def test_review_requires_completed_own_request_and_is_unique(self):
        self.client.force_login(self.user)
        url = reverse("review_create", args=[self.rental.pk])
        for status in [RentalRequest.Status.NEW, RentalRequest.Status.RENTING]:
            self.rental.status = status
            self.rental.save()
            self.assertEqual(self.client.post(url, {"text": "Отзыв"}).status_code, 404)
        self.rental.status = RentalRequest.Status.COMPLETED
        self.rental.save()
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(url).status_code, 404)
        self.assertEqual(
            self.client.post(url, {"text": "Чужой отзыв"}).status_code, 404
        )
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertEqual(self.client.post(url, {"text": ""}).status_code, 200)
        self.assertFalse(Review.objects.exists())
        self.assertRedirects(
            self.client.post(url, {"text": "Все понравилось"}), reverse("requests")
        )
        self.assertContains(self.client.get(reverse("requests")), "Все понравилось")
        self.assertEqual(self.client.post(url, {"text": "Еще один"}).status_code, 404)
        self.assertEqual(Review.objects.count(), 1)

    def test_admin_can_change_status(self):
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        self.client.force_login(self.user)
        self.assertEqual(
            self.client.get(reverse("admin:core_rentalrequest_changelist")).status_code,
            200,
        )
        response = self.client.post(
            reverse("admin:core_rentalrequest_change", args=[self.rental.pk]),
            {
                "user": self.user.pk,
                "car": "LADA Vesta",
                "start_date": "25.12.2026",
                "payment": "cash",
                "status": "completed",
                "_save": "Сохранить",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.rental.refresh_from_db()
        self.assertEqual(self.rental.status, RentalRequest.Status.COMPLETED)
