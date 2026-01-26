from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
from courses.models import Course, Lesson, Subscription
from users.models import User, Payment

User = get_user_model()


class LessonTestCase(APITestCase):

    def setUp(self):
        # Создаём пользователей
        self.user = User.objects.create_user(
            email="user@example.com",
            password="password123",
            phone="+79001234567",
            city="Москва",
        )
        self.moderator = User.objects.create_user(
            email="moderator@example.com",
            password="password123",
            phone="+79007654321",
            city="СПб",
        )
        self.admin = User.objects.create_superuser(
            email="admin@example.com",
            password="admin123",
            phone="+79001112233",
            city="Киев",
        )

        # Создаём группу модераторов
        self.moderator_group, created = Group.objects.get_or_create(name="Модераторы")
        self.moderator.groups.add(self.moderator_group)

        # Создаём курс
        self.course = Course.objects.create(
            title="Python Basics", description="...", owner=self.user
        )

        # Создаём урок
        self.lesson = Lesson.objects.create(
            title="Variables",
            description="...",
            video_url="https://youtube.com/watch?v=test",
            course=self.course,
            owner=self.user,
        )

    def test_create_lesson_with_valid_youtube_url(self):
        """Тестирование создания урока с корректной YouTube-ссылкой"""
        self.client.force_authenticate(user=self.user)
        data = {
            "title": "New Lesson",
            "description": "...",
            "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "course": self.course.id,
            "owner": self.user.id,
        }
        response = self.client.post("/lessons/create/", data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_lesson_with_invalid_video_url(self):
        """Тестирование создания урока с некорректной ссылкой (не YouTube)"""
        self.client.force_authenticate(user=self.user)
        data = {
            "title": "Bad Lesson",
            "description": "...",
            "video_url": "https://vimeo.com/test",
            "course": self.course.id,
            "owner": self.user.id,
        }
        response = self.client.post("/lessons/create/", data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.json())
        error_message = response.json()["non_field_errors"][0]
        self.assertIn("Ссылка может вести только на YouTube.", error_message)

    def test_create_lesson_with_youtube_short_url(self):
        """Тестирование создания урока с короткой YouTube-ссылкой"""
        self.client.force_authenticate(user=self.user)
        data = {
            "title": "Short URL Lesson",
            "description": "...",
            "video_url": "https://youtu.be/dQw4w9WgXcQ",
            "course": self.course.id,
            "owner": self.user.id,
        }
        response = self.client.post("/lessons/create/", data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_lesson(self):
        """Тестирование создания урока (только авторизованным пользователем)"""
        self.client.force_authenticate(user=self.user)
        data = {
            "title": "New Lesson",
            "description": "...",
            "video_url": "https://youtube.com/watch?v=new",
            "course": self.course.id,
            "owner": self.user.id,
        }
        response = self.client.post("/lessons/create/", data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["title"], "New Lesson")

    def test_list_lesson(self):
        """Тестирование вывода списка уроков (доступно только модераторам)"""
        self.client.force_authenticate(user=self.moderator)
        response = self.client.get("/lessons/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_lesson(self):
        """Тестирование просмотра урока (доступно только модераторам)"""
        self.client.force_authenticate(user=self.moderator)
        response = self.client.get(f"/lessons/{self.lesson.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_lesson_by_owner(self):
        """Тестирование обновления урока владельцем"""
        self.client.force_authenticate(user=self.user)
        data = {
            "title": "Updated Lesson",
            "description": "Updated description",
            "video_url": "https://youtube.com/watch?v=updated",
            "course": self.course.id,
            "owner": self.user.id,
        }
        response = self.client.put(f"/lessons/update/{self.lesson.id}/", data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["title"], "Updated Lesson")

    def test_update_lesson_by_moderator(self):
        """Тестирование обновления урока модератором"""
        self.client.force_authenticate(user=self.moderator)
        data = {
            "title": "Moderator Updated",
            "description": "...",
            "video_url": "https://youtube.com/watch?v=moderated",
            "course": self.course.id,
            "owner": self.user.id,
        }
        response = self.client.put(f"/lessons/update/{self.lesson.id}/", data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["title"], "Moderator Updated")

    def test_delete_lesson_by_owner(self):
        """Тестирование удаления урока владельцем"""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f"/lessons/delete/{self.lesson.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lesson.objects.filter(id=self.lesson.id).exists())

    def test_delete_lesson_by_non_owner(self):
        """Тестирование отказа в удалении урока не владельцем"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f"/lessons/delete/{self.lesson.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class SubscriptionTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="user@example.com",
            password="password123",
            phone="+79001234567",
            city="Москва",
        )
        self.course = Course.objects.create(
            title="Python Basics", description="...", owner=self.user
        )

    def test_subscribe_to_course(self):
        """Тестирование подписки на курс"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f"/courses/{self.course.id}/subscription/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["message"], "Подписка добавлена")
        self.assertTrue(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

    def test_unsubscribe_from_course(self):
        """Тестирование отписки от курса"""
        Subscription.objects.create(user=self.user, course=self.course)
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f"/courses/{self.course.id}/subscription/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["message"], "Подписка удалена")
        self.assertFalse(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )


class PaginatorTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="user@example.com",
            password="password123",
            phone="+79001234567",
            city="Москва",
        )
        self.course = Course.objects.create(
            title="Python Basics", description="...", owner=self.user
        )
        for i in range(12):
            Lesson.objects.create(
                title=f"Lesson {i}",
                description="...",
                video_url="https://youtube.com/watch?v=test",
                course=self.course,
                owner=self.user,
            )

    def test_lesson_pagination(self):
        """Тестирование пагинации уроков"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/lessons/?page_size=10")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 10)  # 10 уроков на странице
        self.assertIn("next", response.json())  # Следующая страница должна быть

    def test_course_pagination(self):
        """Тестирование пагинации курсов"""
        for i in range(6):
            Course.objects.create(
                title=f"Test Course {i}", description="...", owner=self.user
            )
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/courses/?page_size=5")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 5)  # 5 курсов на странице
        self.assertIn("next", response.json())  # Следующая страница должна быть


class PaymentCreateTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="user@example.com",
            password="password123",
            phone="+79001234567",
            city="Москва",
        )
        self.course = Course.objects.create(
            title="Python Basics", description="...", owner=self.user
        )

    @patch("courses.views.create_stripe_product")
    @patch("courses.views.create_stripe_price")
    @patch("courses.views.create_checkout_session")
    def test_create_payment_and_get_stripe_session_url(
        self, mock_session, mock_price, mock_product
    ):
        """Тестирование создания платежа и получения ссылки на оплату"""
        mock_product.return_value = "prod_test123"
        mock_price.return_value = "price_test123"
        mock_session.return_value = (
            "cs_test123",
            "https://checkout.stripe.com/pay/cs_test...",
        )

        self.client.force_authenticate(user=self.user)
        data = {
            "paid_course": self.course.id,
            "amount": "1000.00",
            "payment_method": "transfer",
        }
        response = self.client.post("/payments/create/", data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("session_url", response.json())
        self.assertTrue(
            Payment.objects.filter(user=self.user, paid_course=self.course).exists()
        )

    @patch("courses.views.get_checkout_session_status")
    def test_get_payment_status(self, mock_status):
        """Тестирование получения статуса платежа"""
        mock_status.return_value = "paid"

        from users.models import Payment
        Payment.objects.create(
            user=self.user,
            paid_course=self.course,
            amount="100.00",
            payment_method="transfer",
            stripe_session_id="cs_test123",
            stripe_session_url="https://checkout.stripe.com/pay/cs_test...",
            stripe_status="paid"
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get("/payments/status/cs_test123/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["status"], "paid")
