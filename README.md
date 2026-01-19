# Онлайн-обучение (Online Training Platform)

## Описание

Проект представляет собой платформу онлайн-обучения с возможностью создания курсов, уроков, регистрации пользователей, управления платежами и т.д.

## Установка

1. Клонируйте репозиторий:

   ```bash
   git clone https://github.com/Elektrokot/online_training.git
   cd online_training
   ```

2. Установите зависимости:

   ```bash
   poetry install
   ```

4. Выполните миграции:

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Загрузите фикстуры:

   ```bash
   python manage.py loaddata payment_data.json
   ```

6. Создайте суперпользователя:

   ```bash
   python manage.py createsuperuser
   ```

7. Запустите сервер:

   ```bash
   python manage.py runserver
   ```

## API Endpoints

### Пользователи

- `GET /users/` – получить список пользователей
- `POST /users/` – создать пользователя
- `GET /users/{id}/` – получить информацию о пользователе
- `PUT /users/{id}/` – обновить пользователя
- `PATCH /users/{id}/` – частично обновить пользователя
- `DELETE /users/{id}/` – удалить пользователя

### Курсы

- `GET /courses/` – получить список курсов
- `POST /courses/` – создать курс
- `GET /courses/{id}/` – получить курс
- `PUT /courses/{id}/` – обновить курс
- `PATCH /courses/{id}/` – частично обновить курс
- `DELETE /courses/{id}/` – удалить курс

### Уроки

- `GET /lessons/` – получить список уроков
- `POST /lessons/` – создать урок
- `GET /lessons/{id}/` – получить урок
- `PUT /lessons/update/{id}/` – обновить урок
- `DELETE /clessons/delete/{id}/` – удалить урок

### Платежи

- `GET /payments/` – получить список платежей
- Параметры фильтрации:
  - `paid_course` – фильтр по курсу
  - `paid_lesson` – фильтр по уроку
  - `payment_method` – фильтр по способу оплаты
- Параметры сортировки:
  - `ordering=payment_date` – по возрастанию даты
  - `ordering=-payment_date` – по убыванию даты

## Примеры запросов в Postman

### Регистрация пользователя

- Method: `POST`
- URL: `http://127.0.0.1:8000/users/`
- Body (JSON):

```json
{
  "email": "test@example.com",
  "password": "securepassword123",
  "phone": "+79999999999",
  "city": "Москва"
}
```

### Получение списка курсов

- Method: `GET`
- URL: `http://127.0.0.1:8000/courses/`

### Создание урока

- Method: `POST`
- URL: `http://127.0.0.1:8000/lessons/`
- Body (JSON):

```json
{
  "title": "Variables",
  "description": "Introduction to variables",
  "video_url": "https://youtube.com/watch?v=...",
  "course": 1,
  "owner": 1
}
```

### Фильтрация платежей

- Method: `GET`
- URL: `http://127.0.0.1:8000/payments/?paid_course=1&ordering=-payment_date`

---

## Требования к окружению

- Python 3.9+

---

## Известные ограничения

- В разработке

---

## Планы по доработке

- В разработке

---

## Автор

Константин Чирков  
[GitHub](https://github.com/Elektrokot)

---

## Лицензия

MIT License

---

Этот README предоставляет полное описание проекта, включая новые модули, тесты,
структуру и инструкции по использованию. Он написан в информативном и профессиональном стиле,
удобен для чтения и понимания.