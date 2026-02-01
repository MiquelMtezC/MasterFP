from django.test import TestCase
from django.contrib.auth.models import User, Permission
from django.urls import reverse
from .models import Question, Choice


class StaffReadOnlyTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # 1️⃣ Crear superusuari
        cls.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )

        # 2️⃣ Crear usuari staff només lectura
        cls.staff_user = User.objects.create_user(
            username='staffuser',
            email='staff@test.com',
            password='staff123',
            is_staff=True
        )

        # Assignar permisos de lectura
        cls.staff_user.user_permissions.add(
            Permission.objects.get(codename='view_question'),
            Permission.objects.get(codename='view_choice')
        )

        # 3️⃣ Crear 2 Question amb 2 Choice cadascuna
        cls.q1 = Question.objects.create(question_text="Pregunta 1?")
        Choice.objects.create(question=cls.q1, choice_text="Opció 1A", votes=0)
        Choice.objects.create(question=cls.q1, choice_text="Opció 1B", votes=0)

        cls.q2 = Question.objects.create(question_text="Pregunta 2?")
        Choice.objects.create(question=cls.q2, choice_text="Opció 2A", votes=0)
        Choice.objects.create(question=cls.q2, choice_text="Opció 2B", votes=0)

    def test_staff_can_view_questions(self):
        self.client.login(username='staffuser', password='staff123')
        response = self.client.get(reverse('admin:polls_question_changelist'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pregunta 1?")
        self.assertContains(response, "Pregunta 2?")

    def test_staff_cannot_edit_question(self):
        self.client.login(username='staffuser', password='staff123')
        response = self.client.get(
            reverse('admin:polls_question_change', args=[self.q1.id])
        )

        self.assertEqual(response.status_code, 200)

        # No pot guardar canvis
        self.assertNotContains(response, 'name="_save"')
        self.assertNotContains(response, 'name="_continue"')

    def test_staff_cannot_add_question(self):
        self.client.login(username='staffuser', password='staff123')
        response = self.client.get(reverse('admin:polls_question_add'))
        self.assertEqual(response.status_code, 403)
