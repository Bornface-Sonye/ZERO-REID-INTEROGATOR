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

class Database:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cur = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cur.execute('''CREATE TABLE IF NOT EXISTS Role (
                                RoleID INTEGER PRIMARY KEY AUTOINCREMENT,
                                RoleName TEXT NOT NULL
                            )''')

        self.cur.execute('''CREATE TABLE IF NOT EXISTS User (
                                UserID INTEGER PRIMARY KEY AUTOINCREMENT,
                                FirstName TEXT NOT NULL,
                                LastName TEXT NOT NULL,
                                Email TEXT UNIQUE NOT NULL,
                                Password TEXT NOT NULL,
                                RoleID INTEGER,
                                FOREIGN KEY (RoleID) REFERENCES Role(RoleID)
                            )''')

        self.cur.execute('''CREATE TABLE IF NOT EXISTS Cases (
                                CaseID INTEGER PRIMARY KEY AUTOINCREMENT,
                                CaseDescription TEXT
                            )''')

        self.cur.execute('''CREATE TABLE IF NOT EXISTS Witness (
                                WitnessID INTEGER PRIMARY KEY AUTOINCREMENT,
                                UserID INTEGER,
                                CaseID INTEGER,
                                FOREIGN KEY (UserID) REFERENCES User(UserID),
                                FOREIGN KEY (CaseID) REFERENCES Cases(CaseID)
                            )''')

        self.conn.commit()

    def close_connection(self):
        self.conn.close()

class SentimentAnalysis:
    def __init__(self):
        # Initialize NLTK Sentiment Intensity Analyzer
        self.sid = SentimentIntensityAnalyzer()
        # Initialize spaCy NLP model
        self.nlp = sp.load("en_core_web_sm")

    def is_obedient(self, text):
        # Sentiment analysis for obedience
        # You can define your own rules for determining obedience based on sentiment scores
        sentiment_scores = self.sid.polarity_scores(text)
        obedient_score = sentiment_scores['compound']
        if obedient_score >= 0:
            return 'Yes' # Obedient
        else:
            return 'No' # Not obedient

    def calculate_emotion_score(self, text):
        # Calculate emotion score
        sentiment_scores = self.sid.polarity_scores(text)
        emotion_score = sentiment_scores['compound']
        return emotion_score

    def calculate_consistency_score(self, text1, text2):
        # Calculate consistency score based on two sets of text
        doc1 = self.nlp(text1)
        doc2 = self.nlp(text2)
        # You can define your own logic to calculate consistency score
        # For example, you can measure the similarity between two text samples
        similarity = doc1.similarity(doc2)
        consistency_score = (similarity + 1) / 2 # Normalize to [0, 1]
        return consistency_score

    def calculate_confidence_score(self, emotion_score, consistency_score):
        # Calculate confidence score as an average of emotion and consistency scores
        confidence_score = (emotion_score + consistency_score) / 2
        return confidence_score

class SignupWindow(QWidget):
    def __init__(self, db, login_callback):
        super().__init__()
        self.db = db
        self.login_callback = login_callback
        self.setWindowTitle("Signup")

        # Create a form layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Add widgets to the layout
        self.label_firstname = QLabel("First Name:")
        self.lineedit_firstname = QLineEdit()
        self.layout.addWidget(self.label_firstname)
        self.layout.addWidget(self.lineedit_firstname)

        self.label_lastname = QLabel("Last Name:")
        self.lineedit_lastname = QLineEdit()
        self.layout.addWidget(self.label_lastname)
        self.layout.addWidget(self.lineedit_lastname)

        self.label_email = QLabel("Email:")
        self.lineedit_email = QLineEdit()
        self.layout.addWidget(self.label_email)
        self.layout.addWidget(self.lineedit_email)

        self.label_password = QLabel("Password:")
        self.lineedit_password = QLineEdit()
        self.lineedit_password.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.label_password)
        self.layout.addWidget(self.lineedit_password)

        self.button_signup = QPushButton("Signup")
        self.button_signup.clicked.connect(self.signup)
        self.layout.addWidget(self.button_signup)

        self.button_login = QPushButton("Login")
        self.button_login.clicked.connect(self.login_callback)
        self.layout.addWidget(self.button_login)

        # Set alignment to center
        self.layout.setAlignment(Qt.AlignCenter)

        # Set a reasonable size
        self.resize(300, 200)

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

class LoginWindow(QWidget):
    def __init__(self, db, login_callback):
        super().__init__()
        self.db = db
        self.login_callback = login_callback
        self.setWindowTitle("Login")

        # Create a form layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Add widgets to the layout
        self.label_email = QLabel("Email:")
        self.lineedit_email = QLineEdit()
        self.layout.addWidget(self.label_email)
        self.layout.addWidget(self.lineedit_email)

        self.label_password = QLabel("Password:")
        self.lineedit_password = QLineEdit()
        self.lineedit_password.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.label_password)
        self.layout.addWidget(self.lineedit_password)

        self.button_login = QPushButton("Login")
        self.button_login.clicked.connect(self.login)
        self.layout.addWidget(self.button_login)

        self.button_signup = QPushButton("Signup")
        self.button_signup.clicked.connect(self.signup_callback)
        self.layout.addWidget(self.button_signup)

        # Set alignment to center
        self.layout.setAlignment(Qt.AlignCenter)

        # Set a reasonable size
        self.resize(300, 150)

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
        self.signup_window.show()
        self.close()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Witness Submission System")
        self.setGeometry(100, 100, QApplication.desktop().screenGeometry().width(), QApplication.desktop().screenGeometry().height())

        # Create actions for toolbar
        file_menu = self.menuBar().addMenu("&File")
        cases_menu = self.menuBar().addMenu("&Cases")

        save_action = QAction("&Save", self)
        save_action.triggered.connect(self.save)
        file_menu.addAction(save_action)

        exit_action = QAction("&Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        pending_cases_action = QAction("&Pending Cases", self)
        pending_cases_action.triggered.connect(self.show_pending_cases)
        cases_menu.addAction(pending_cases_action)

        self.toolbar = self.addToolBar("Main Toolbar")
        self.toolbar.addAction(save_action)
        self.toolbar.addAction(exit_action)
        self.toolbar.addAction(pending_cases_action)

    def save(self):
        QMessageBox.information(self, "Save", "Save functionality to be implemented.")

    def show_pending_cases(self):
        self.pending_cases_window = WitnessSubmissionWindow()
        self.pending_cases_window.show()
        
class Launcher(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.login_window = LoginWindow(self.db, self.show_main_window)
        self.setCentralWidget(self.login_window)

    def show_main_window(self):
        self.main_window = MainWindow()
        self.setCentralWidget(self.main_window)

class WitnessSubmissionWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Witness Submission")
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)
        self.setGeometry(0, 0, QApplication.desktop().screenGeometry().width(), QApplication.desktop().screenGeometry().height())

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.label_question = QLabel("Question:")
        self.layout.addWidget(self.label_question)

        self.lineedit_answer = QLineEdit()
        self.layout.addWidget(self.lineedit_answer)

        self.progress_bar = QProgressBar()
        self.layout.addWidget(self.progress_bar)

        self.button_next = QPushButton("Next")
        self.button_next.clicked.connect(self.next_question)
        self.layout.addWidget(self.button_next)

        # Add ToolTip
        QToolTip.setFont(QFont('SansSerif', 10))
        self.button_next.setToolTip('Click to proceed to the next question')

        self.current_question_index = 0
        self.questions = [
            "What did you witness?",
            "Where did the incident occur?",
            "When did it happen?",
            "Who else was present?",
            "Did you see any suspicious activities before or after the incident?"
        ]
        self.total_questions = len(self.questions)
        self.progress_bar.setMaximum(self.total_questions)

        self.show_next_question()

    def show_next_question(self):
        if self.current_question_index < self.total_questions:
            self.label_question.setText(self.questions[self.current_question_index])
            self.lineedit_answer.clear()
            self.current_question_index += 1
            self.progress_bar.setValue(self.current_question_index)
        else:
            QMessageBox.information(self, "Congratulations", "Thank you for your submission!")

    def next_question(self):
        if self.current_question_index < self.total_questions:
            self.show_next_question()
        else:
            QMessageBox.warning(self, "End of Questions", "No more questions to display.")

if __name__ == "__main__":
    app = QApplication([])
    app.setStyleSheet(
        "QMainWindow { background-color: #00CED1 }"
        "QLabel { color: white; font-size: 16px }"
        "QPushButton { background-color: #4CAF50; color: white; font-weight: bold; border: none; padding: 10px; border-radius: 5px }"
        "QPushButton:hover { background-color: #45a049 }"
        "QProgressBar { color: white; background-color: #20B2AA; border-radius: 5px; padding: 1px }"
    )

    # Initialize Database
    db = Database('witness_submission.db')

    # Create launcher
    window = Launcher(db)
    window.show()

    sys.exit(app.exec_())
