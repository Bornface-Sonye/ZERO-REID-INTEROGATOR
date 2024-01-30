from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox, QAction, QMenu, QTextEdit, QProgressBar,
    QWidget, QToolTip, QButtonGroup, QGroupBox, QSizePolicy, QSizeGrip, QSlider, QScrollBar, QDial,
    QSpinBox, QDoubleSpinBox, QLCDNumber, QFrame, QScrollArea,QSplashScreen
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer
import sys
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import spacy as sp
import sqlite3
import time

class Launcher(QDialog):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.login_window = LoginWindow(self.db, self.show_main_window)
        
        # Set layout for the dialog
        layout = QVBoxLayout()
        layout.addWidget(self.login_window)
        self.setLayout(layout)

        self.setWindowTitle("Login or Sign Up")
        self.setFixedSize(300, 200)  # Set a fixed size for the dialog
        self.setModal(True)  # Make the dialog modal

    def show_main_window(self):
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()

class LoginWindow(QWidget):
    def __init__(self, db, login_callback):
        super().__init__()
        self.db = db
        self.login_callback = login_callback
        self.setWindowTitle("Login")

        # Create a form layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Add widgets to the layout
        self.label_email = QLabel("Email:")
        self.lineedit_email = QLineEdit()
        layout.addWidget(self.label_email)
        layout.addWidget(self.lineedit_email)

        self.label_password = QLabel("Password:")
        self.lineedit_password = QLineEdit()
        self.lineedit_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.label_password)
        layout.addWidget(self.lineedit_password)

        self.button_login = QPushButton("Login")
        self.button_login.clicked.connect(self.login)
        layout.addWidget(self.button_login)

        self.button_signup = QPushButton("Signup")
        self.button_signup.clicked.connect(self.signup_callback)
        layout.addWidget(self.button_signup)

        # Set alignment to center
        layout.setAlignment(Qt.AlignCenter)

    def login(self):
        email = self.lineedit_email.text().strip()
        password = self.lineedit_password.text().strip()

        if not email or not password:
            QMessageBox.warning(self, "Warning", "Please fill in all fields.")
            return

        # Check if email and password match
        self.db.cur.execute("SELECT UserID FROM User WHERE Email = ? AND Password = ?", (email, password))
        user_id = self.db.cur.fetchone()
        if user_id:
            QMessageBox.information(self, "Success", "Login successful.")
            self.login_callback()
        else:
            QMessageBox.warning(self, "Error", "Invalid email or password.")

    def signup_callback(self):
        self.signup_window = SignupWindow(self.db, self.login_callback)
        self.signup_window.exec_()

class SignupWindow(QDialog):
    def __init__(self, db, login_callback):
        super().__init__()
        self.db = db
        self.login_callback = login_callback
        self.setWindowTitle("Signup")

        # Create a form layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Add widgets to the layout
        self.label_firstname = QLabel("First Name:")
        self.lineedit_firstname = QLineEdit()
        layout.addWidget(self.label_firstname)
        layout.addWidget(self.lineedit_firstname)

        self.label_lastname = QLabel("Last Name:")
        self.lineedit_lastname = QLineEdit()
        layout.addWidget(self.label_lastname)
        layout.addWidget(self.lineedit_lastname)

        self.label_email = QLabel("Email:")
        self.lineedit_email = QLineEdit()
        layout.addWidget(self.label_email)
        layout.addWidget(self.lineedit_email)

        self.label_password = QLabel("Password:")
        self.lineedit_password = QLineEdit()
        self.lineedit_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.label_password)
        layout.addWidget(self.lineedit_password)

        self.button_signup = QPushButton("Signup")
        self.button_signup.clicked.connect(self.signup)
        layout.addWidget(self.button_signup)

        self.button_login = QPushButton("Login")
        self.button_login.clicked.connect(self.login_callback)
        layout.addWidget(self.button_login)

        # Set alignment to center
        layout.setAlignment(Qt.AlignCenter)

    def signup(self):
        firstname = self.lineedit_firstname.text().strip()
        lastname = self.lineedit_lastname.text().strip()
        email = self.lineedit_email.text().strip()
        password = self.lineedit_password.text().strip()

        if not firstname or not lastname or not email or not password:
            QMessageBox.warning(self, "Warning", "Please fill in all fields.")
            return

        # Check if email already exists
        self.db.cur.execute("SELECT Email FROM User WHERE Email = ?", (email,))
        existing_email = self.db.cur.fetchone()
        if existing_email:
            QMessageBox.warning(self, "Warning", "Email already exists. Please use a different email.")
            return

        # Insert new user into the database
        try:
            self.db.cur.execute("INSERT INTO User (FirstName, LastName, Email, Password) VALUES (?, ?, ?, ?)",
                                (firstname, lastname, email, password))
            self.db.conn.commit()
            QMessageBox.information(self, "Success", "Signup successful.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error during signup: {str(e)}")

class MainWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Witness Submission System")
        self.setFixedSize(400, 200)

        # Add your UI elements here

if __name__ == "__main__":
    app = QApplication([])
    app.setStyleSheet(
        "QDialog { background-color: #00CED1 }"
        "QLabel { color: white; font-size: 16px }"
        "QLineEdit { background-color: white; }"
        "QPushButton { background-color: #4CAF50; color: white; font-weight: bold; border: none; padding: 10px; border-radius: 5px }"
        "QPushButton:hover { background-color: #45a049 }"
    )

    # Initialize Database
    db = Database('witness_submission.db')

    # Create launcher
    window = Launcher(db)
    window.exec_()
    sys.exit(app.exec_())
