from django.test import TestCase
from .models import Question, Choice

class PollsModelsTest(TestCase):
    def test_creacio_question(self):
        # Creem una pregunta de prova
        q = Question.objects.create(question_text="Pregunta de prova?")
        self.assertEqual(q.question_text, "Pregunta de prova?")

    def test_creacio_choice(self):
        q = Question.objects.create(question_text="Pregunta 2?")
        c = Choice.objects.create(question=q, choice_text="Opció 1", votes=0)
        self.assertEqual(c.choice_text, "Opció 1")
        self.assertEqual(c.votes, 0)
