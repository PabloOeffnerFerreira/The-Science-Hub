import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel,
    QTabWidget, QFormLayout
)
from PyQt6.QtCore import Qt
from supabase import create_client, Client

# Your Supabase credentials (replace with your real values)
SUPABASE_URL = "https://suigibyknaqxbbkilzos.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN1aWdpYnlrbmFxeGJia2lsem9zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDc3NDk0MTcsImV4cCI6MjA2MzMyNTQxN30.Y26UuBdRrrFCrAWGf6g41tnPKktqI9kvgZAPazCD8lA"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def login_user(email: str, password: str):
    try:
        user = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        if user.user:
            return user.user
        else:
            return None
    except Exception as e:
        return str(e)

def sign_up_user(email: str, password: str):
    try:
        user = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        if user.user:
            return user.user
        else:
            return None
    except Exception as e:
        return str(e)

def create_profile(username: str, email: str, preferences: dict = None):
    if preferences is None:
        preferences = {}
    data = {
        "username": username,
        "email": email,
        "preferences": preferences
    }
    try:
        response = supabase.table("profiles").insert(data).execute()
        if response.data:
            return response.data[0]
        else:
            return None
    except Exception as e:
        return str(e)

def get_profile_by_email(email: str):
    response = supabase.table("profiles").select("*").eq("email", email).execute()
    if response.data:
        return response.data[0]
    else:
        return None

def update_profile(email: str, new_data: dict):
    response = supabase.table("profiles").update(new_data).eq("email", email).execute()
    if response.data:
        return response.data[0]
    else:
        return None

class AuthWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Science Hub - User Authentication")
        self.setFixedSize(350, 270)

        self.tabs = QTabWidget()
        self.login_tab = QWidget()
        self.signup_tab = QWidget()
        self.tabs.addTab(self.login_tab, "Login")
        self.tabs.addTab(self.signup_tab, "Sign Up")

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)

        self.init_login_tab()
        self.init_signup_tab()

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        layout.addWidget(self.status_label)
        self.setLayout(layout)

    def init_login_tab(self):
        layout = QFormLayout()
        self.login_email = QLineEdit()
        self.login_password = QLineEdit()
        self.login_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.login_button = QPushButton("Log In")
        self.login_button.clicked.connect(self.handle_login)

        layout.addRow("Email:", self.login_email)
        layout.addRow("Password:", self.login_password)
        layout.addRow(self.login_button)
        self.login_tab.setLayout(layout)

    def init_signup_tab(self):
        layout = QFormLayout()
        self.signup_username = QLineEdit()
        self.signup_email = QLineEdit()
        self.signup_password = QLineEdit()
        self.signup_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.signup_button = QPushButton("Sign Up")
        self.signup_button.clicked.connect(self.handle_signup)

        layout.addRow("Username:", self.signup_username)
        layout.addRow("Email:", self.signup_email)
        layout.addRow("Password:", self.signup_password)
        layout.addRow(self.signup_button)
        self.signup_tab.setLayout(layout)

    def handle_login(self):
        email = self.login_email.text().strip()
        password = self.login_password.text().strip()
        if not email or not password:
            self.status_label.setText("Please enter both email and password.")
            return

        self.status_label.setText("Logging in...")
        user = login_user(email, password)
        if isinstance(user, str):
            # error message
            self.status_label.setText(f"Login failed: {user}")
        elif user is None:
            self.status_label.setText("Login failed: Invalid credentials.")
        else:
            profile = get_profile_by_email(user.email)
            if profile is None:
                self.status_label.setText("No profile found, creating one...")
                profile = create_profile(username=user.email.split('@')[0], email=user.email)
                if isinstance(profile, str):
                    self.status_label.setText(f"Error creating profile: {profile}")
                    return
            self.status_label.setText(f"Logged in as {user.email}.\nWelcome, {profile['username']}!")

    def handle_signup(self):
        username = self.signup_username.text().strip()
        email = self.signup_email.text().strip()
        password = self.signup_password.text().strip()
        if not username or not email or not password:
            self.status_label.setText("Please fill in all fields.")
            return

        self.status_label.setText("Signing up...")
        user = sign_up_user(email, password)
        if isinstance(user, str):
            self.status_label.setText(f"Sign up failed: {user}")
        elif user is None:
            self.status_label.setText("Sign up failed: Could not create user.")
        else:
            profile = create_profile(username, user.email)
            if isinstance(profile, str):
                self.status_label.setText(f"Error creating profile: {profile}")
                return
            self.status_label.setText(f"User created and logged in as {user.email}.\nWelcome, {username}!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AuthWindow()
    window.show()
    sys.exit(app.exec())
