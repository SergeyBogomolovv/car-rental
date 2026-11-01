Проект «Ключ.на.старт», вариант 3. PostgreSQL подключается в `project/settings.py`.

```powershell
.\.venv\Scripts\Activate.ps1
python manage.py migrate
python manage.py runserver
```

Администратор уже создан: `Admin` / `StartNET`, вход на `/admin/`.
В новой базе: `python manage.py createsuperuser --username Admin` (для пароля `StartNET` подтверди предупреждение о длине).
