from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox, QAction, QMenu, QTextEdit, QProgressBar,
    QWidget, QToolTip, QButtonGroup, QGroupBox, QSizePolicy, QSizeGrip, QSlider, QScrollBar, QDial,
    QSpinBox, QDoubleSpinBox, QLCDNumber, QFrame, QScrollArea, QSplashScreen, QComboBox,QListWidget
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer
import sys
import sqlite3

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
                            Gender TEXT,  -- Added Gender column
                            FOREIGN KEY (UserID) REFERENCES User(UserID),
                            FOREIGN KEY (CaseID) REFERENCES Cases(CaseID)
                        )''')

            self.cur.execute('''CREATE TABLE IF NOT EXISTS Suspect (
                            SuspectID INTEGER PRIMARY KEY AUTOINCREMENT,
                            UserID INTEGER,
                            CaseID INTEGER,
                            Gender TEXT,
                            FOREIGN KEY (UserID) REFERENCES User(UserID),
                            FOREIGN KEY (CaseID) REFERENCES Cases(CaseID)
                        )''')

            self.cur.execute('''CREATE TABLE IF NOT EXISTS LawEnforcer (
                            EnforcerID INTEGER PRIMARY KEY AUTOINCREMENT,
                            UserID INTEGER,
                            CaseID INTEGER,
                            FOREIGN KEY (UserID) REFERENCES User(UserID),
                            FOREIGN KEY (CaseID) REFERENCES Cases(CaseID)
                        )''')

            self.cur.execute('''CREATE TABLE IF NOT EXISTS Admin (
                            AdminID INTEGER PRIMARY KEY AUTOINCREMENT,
                            UserID INTEGER,
                            FOREIGN KEY (UserID) REFERENCES User(UserID)
                        )''')

            self.cur.execute('''CREATE TABLE IF NOT EXISTS CaseProgress (
                            ProgressID INTEGER PRIMARY KEY AUTOINCREMENT,
                            CaseID INTEGER,
                            Progress TEXT,
                            FOREIGN KEY (CaseID) REFERENCES Cases(CaseID)
                        )''')

            self.conn.commit()


    def close_connection(self):
        self.conn.close()

class SignupWindow(QDialog):
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

        self.label_gender = QLabel("Gender:")
        self.combobox_gender = QComboBox()
        self.combobox_gender.addItems(["Male", "Female"])
        self.layout.addWidget(self.label_gender)
        self.layout.addWidget(self.combobox_gender)

        self.button_signup = QPushButton("Signup")
        self.button_signup.clicked.connect(self.signup)
        self.layout.addWidget(self.button_signup)

        self.button_login = QPushButton("Login")
        self.button_login.clicked.connect(self.login_callback)
        self.layout.addWidget(self.button_login)

        # Set alignment to center
        self.layout.setAlignment(Qt.AlignCenter)

        # Set a reasonable size
        self.resize(300, 250)

    def signup(self):
        firstname = self.lineedit_firstname.text().strip()
        lastname = self.lineedit_lastname.text().strip()
        email = self.lineedit_email.text().strip()
        password = self.lineedit_password.text().strip()
        gender = self.combobox_gender.currentText()

        if not firstname or not lastname or not email or not password:
            QMessageBox.warning(self, "Please fill in all fields.", "Warning")
            return

        # Check if email already exists
        self.db.cur.execute("SELECT Email FROM User WHERE Email = ?", (email,))
        existing_email = self.db.cur.fetchone()
        if existing_email:
            QMessageBox.warning(self, "Email already exists.", "Warning")
            return

        # Insert new user into the database
        try:
            self.db.cur.execute("INSERT INTO User (FirstName, LastName, Email, Password) VALUES (?, ?, ?, ?)",
                                (firstname, lastname, email, password))
            self.db.conn.commit()
            user_id = self.db.cur.lastrowid

            role_id = self.get_role_id("Witness")  # Default role for signup
            self.db.cur.execute("INSERT INTO Witness (UserID, Gender) VALUES (?, ?)", (user_id, gender))
            self.db.conn.commit()

            QMessageBox.information(self, "Signup successful.", "Success")
        except Exception as e:
            QMessageBox.warning(self, f"Error during signup: {str(e)}", "Error")

    def get_role_id(self, role_name):
        self.db.cur.execute("SELECT RoleID FROM Role WHERE RoleName = ?", (role_name,))
        role_id = self.db.cur.fetchone()
        return role_id[0] if role_id else None

class LoginWindow(QDialog):
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
            QMessageBox.information(self, "Login successful.", "Success")
            self.login_callback()
        else:
            QMessageBox.warning(self, "Invalid email or password.", "Error")

    def signup_callback(self):
        self.signup_window = SignupWindow(self.db, self.login_callback)
        self.signup_window.show()
        self.close()

class MainWindow(QMainWindow):
    def __init__(self, db, user_id):
        super().__init__()
        self.db = db
        self.user_id = user_id

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
        self.pending_cases_window = PendingCasesWindow(self.db, self.user_id)
        self.pending_cases_window.show()

class PendingCasesWindow(QDialog):
    def __init__(self, db, user_id):
        super().__init__()
        self.db = db
        self.user_id = user_id
        self.setWindowTitle("Pending Cases")

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label_cases = QLabel("Your Pending Cases:")
        self.layout.addWidget(self.label_cases)

        self.listwidget_cases = QListWidget()
        self.layout.addWidget(self.listwidget_cases)

        self.load_pending_cases()

    def load_pending_cases(self):
        self.listwidget_cases.clear()
        # Fetch and display pending cases for the user
        self.db.cur.execute("SELECT CaseID FROM Witness WHERE UserID = ?", (self.user_id,))
        pending_cases = self.db.cur.fetchall()
        for case_id in pending_cases:
            self.listwidget_cases.addItem(str(case_id[0]))

class Launcher(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.login_window = LoginWindow(self.db, self.show_main_window)
        self.setCentralWidget(self.login_window)

    def show_main_window(self):
        user_id = self.get_user_id()
        if user_id:
            self.main_window = MainWindow(self.db, user_id)
            self.setCentralWidget(self.main_window)

    def get_user_id(self):
        email = self.login_window.lineedit_email.text().strip()
        self.db.cur.execute("SELECT UserID FROM User WHERE Email = ?", (email,))
        user_id = self.db.cur.fetchone()
        return user_id[0] if user_id else None

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
