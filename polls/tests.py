from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType

class RobustAdminSeleniumTest(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        opts = Options()
        # opts.add_argument("--headless")  # comentar per veure el navegador
        cls.selenium = WebDriver(options=opts)
        cls.selenium.implicitly_wait(5)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        # Crear superusuari admin
        User.objects.create_superuser(username="admin", password="admin123", email="admin@test.com")

    def login(self, username, password):
        self.selenium.get(f"{self.live_server_url}/admin/login/?next=/admin/")
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        self.selenium.find_element(By.NAME, "username").clear()
        self.selenium.find_element(By.NAME, "username").send_keys(username)
        self.selenium.find_element(By.NAME, "password").clear()
        self.selenium.find_element(By.NAME, "password").send_keys(password)
        self.selenium.find_element(By.XPATH, '//input[@value="Log in"]').click()

    def logout(self):
        self.selenium.delete_all_cookies()
        self.selenium.get(f"{self.live_server_url}/admin/login/?next=/admin/")

    def test_full_admin_flow_with_staff(self):
        wait = WebDriverWait(self.selenium, 10)

        # 1️⃣ Login admin
        self.login("admin", "admin123")

        # 2️⃣ Crear 2 Questions
        for i in range(1, 3):
            self.selenium.get(f"{self.live_server_url}/admin/polls/question/add/")
            q_input = wait.until(EC.presence_of_element_located((By.ID, "id_question_text")))
            q_input.clear()
            q_input.send_keys(f"Question {i}")
            self.selenium.find_element(By.NAME, "_save").click()

        # 3️⃣ Crear 2 Choices per Question
        for i in range(1, 3):
            for j in range(1, 3):
                self.selenium.get(f"{self.live_server_url}/admin/polls/choice/add/")
                question_select = wait.until(EC.presence_of_element_located((By.ID, "id_question")))
                question_select.find_element(By.XPATH, f'//option[text()="Question {i}"]').click()
                choice_input = self.selenium.find_element(By.ID, "id_choice_text")
                choice_input.clear()
                choice_input.send_keys(f"Choice {i}.{j}")
                self.selenium.find_element(By.NAME, "_save").click()

        # 4️⃣ Crear usuari miquel/miquel123
        self.selenium.get(f"{self.live_server_url}/admin/auth/user/add/")
        username_input = wait.until(EC.presence_of_element_located((By.ID, "id_username")))
        username_input.send_keys("miquel")
        self.selenium.find_element(By.ID, "id_password1").send_keys("miquel123")
        self.selenium.find_element(By.ID, "id_password2").send_keys("miquel123")
        self.selenium.find_element(By.NAME, "_save").click()

        # 5️⃣ Assignar permisos de només lectura via ORM
        user = User.objects.get(username="miquel")
        user.is_staff = True  # perquè pugui entrar a admin
        user.save()

        # Assignar permisos "view" de Question i Choice
        for model in ["question", "choice"]:
            ct = ContentType.objects.get(app_label="polls", model=model)
            perm = Permission.objects.get(content_type=ct, codename=f"view_{model}")
            user.user_permissions.add(perm)
        user.save()

        # 6️⃣ Logout admin
        self.logout()

        # 7️⃣ Login com miquel
        self.login("miquel", "miquel123")

        # 8️⃣ Comprovar lectura Questions
        self.selenium.get(f"{self.live_server_url}/admin/polls/question/")
        page = self.selenium.page_source
        assert "Question 1" in page
        assert "Question 2" in page
        assert "Add question" not in page  # només lectura

        # 9️⃣ Comprovar lectura Choices
        self.selenium.get(f"{self.live_server_url}/admin/polls/choice/")
        page = self.selenium.page_source
        assert "Choice 1.1" in page
        assert "Choice 2.2" in page
        assert "Add choice" not in page  # només lectura
