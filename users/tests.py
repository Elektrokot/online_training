from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from courses.models import Lesson, Course
from users.models import Payment

User = get_user_model()


class UserTestCase(APITestCase):

    def setUp(self):
        # Создаём пользователей
        self.user = User.objects.create_user(
            email="user@example.com",
            password="password123",
            phone="+79001234567",
            city="Москва",
        )
        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="password123",
            phone="+79007654321",
            city="СПб",
        )
        self.admin = User.objects.create_superuser(
            email="admin@example.com",
            password="admin123",
            phone="+79001112233",
            city="Киров",
        )

    def test_register_user(self):
        """ Тестирование регистрации пользователя """
        data = {
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'phone': '+79001113344',
            'city': 'Новосибирск'
        }
        response = self.client.post('/register/', data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.json())
        self.assertIn('refresh', response.json())
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())

    def test_login_user(self):
        """Тестирование входа пользователя"""
        data = {"email": "user@example.com", "password": "password123"}
        response = self.client.post("/login/", data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.json())
        self.assertIn("refresh", response.json())

    def test_get_user_profile(self):
        """Тестирование просмотра профиля пользователя"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/users/{self.user.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["email"], "user@example.com")

    def test_update_own_profile(self):
        """Тестирование обновления собственного профиля"""
        self.client.force_authenticate(user=self.user)
        data = {"phone": "+79009998877", "city": "Воронеж"}
        response = self.client.patch(f"/users/{self.user.id}/", data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.phone, "+79009998877")

    def test_update_other_profile_fails(self):
        """Тестирование отказа в обновлении чужого профиля"""
        self.client.force_authenticate(user=self.user)
        data = {"phone": "+79009998877"}
        response = self.client.patch(f"/users/{self.other_user.id}/", data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_delete_user(self):
        """Тестирование удаления пользователя админом"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f"/users/delete/{self.user.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.user.id).exists())

    def test_user_cannot_delete_another_user(self):
        """Тестирование отказа в удалении чужого профиля не админом"""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f"/users/delete/{self.other_user.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(User.objects.filter(id=self.other_user.id).exists())

    def test_user_can_delete_own_profile(self):
        """Тестирование удаления собственного профиля (если разрешено)"""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f"/users/delete/{self.user.id}/")
        # В текущей реализации только админ может удалить
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class PaymentTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com',
            password='password123',
            phone='+79001234567',
            city='Москва'
        )
        self.course = Course.objects.create(
            title='Python Basics',
            description='...',
            owner=self.user
        )
        self.lesson = Lesson.objects.create(
            title='Variables',
            description='...',
            video_url='https://youtube.com/watch?v=test',
            course=self.course,
            owner=self.user
        )

    def test_filter_payments_by_course(self):
        """ Тестирование фильтрации платежей по курсу """
        self.client.force_authenticate(user=self.user)
        Payment.objects.create(
            user=self.user,
            paid_course=self.course,
            amount=1000.00,
            payment_method='transfer'
        )
        response = self.client.get(f'/payments/?paid_course={self.course.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем, что возвращается список (без пагинации)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)  # Один платеж

    def test_order_payments_by_date(self):
        """ Тестирование сортировки платежей по дате """
        self.client.force_authenticate(user=self.user)
        p1 = Payment.objects.create(
            user=self.user,
            paid_course=self.course,
            amount=1000.00,
            payment_method='transfer'
        )
        p2 = Payment.objects.create(
            user=self.user,
            paid_lesson=self.lesson,
            amount=500.00,
            payment_method='cash'
        )
        response = self.client.get('/payments/?ordering=payment_date')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertLessEqual(data[0]['payment_date'], data[1]['payment_date'])
