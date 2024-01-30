from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox, QAction, QMenu, QTextEdit, QProgressBar,
    QWidget, QToolTip, QButtonGroup, QGroupBox, QSizePolicy, QSizeGrip, QSlider, QScrollBar, QDial,
    QSpinBox, QDoubleSpinBox, QLCDNumber, QFrame, QScrollArea, QSplashScreen, QComboBox, QListWidget, QAction
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
                                Gender TEXT,
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
                                Gender TEXT,
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

        self.label_role = QLabel("Role:")
        self.combobox_role = QComboBox()
        self.populate_roles()  # Populate roles in the combobox
        self.layout.addWidget(self.label_role)
        self.layout.addWidget(self.combobox_role)

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

    def populate_roles(self):
        self.db.cur.execute("SELECT RoleName FROM Role")
        roles = self.db.cur.fetchall()
        for role in roles:
            self.combobox_role.addItem(role[0])

    def signup(self):
        firstname = self.lineedit_firstname.text().strip()
        lastname = self.lineedit_lastname.text().strip()
        email = self.lineedit_email.text().strip()
        password = self.lineedit_password.text().strip()
        gender = self.combobox_gender.currentText()
        role_name = self.combobox_role.currentText()

        if not firstname or not lastname or not email or not password:
            QMessageBox.warning(self, "Please fill in all fields.", "Warning")
            return

        # Check if email already exists
        self.db.cur.execute("SELECT Email FROM User WHERE Email = ?", (email,))
        existing_email = self.db.cur.fetchone()
        if existing_email:
            QMessageBox.warning(self, "Email already exists.", "Warning")
            return

        role_id = self.get_role_id(role_name)
        if role_id is None:
            QMessageBox.warning(self, "Role not found.", "Warning")
            return

        # Insert new user into the database
        try:
            self.db.cur.execute("INSERT INTO User (FirstName, LastName, Email, Password, RoleID) VALUES (?, ?, ?, ?, ?)",
                                (firstname, lastname, email, password, role_id))
            self.db.conn.commit()
            user_id = self.db.cur.lastrowid

            table_name = role_name.replace(" ", "")
            self.db.cur.execute(f"INSERT INTO {table_name} (UserID, Gender) VALUES (?, ?)", (user_id, gender))
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

        self.db.cur.execute("SELECT UserID, RoleID FROM User WHERE Email = ? AND Password = ?", (email, password))
        user_info = self.db.cur.fetchone()
        if user_info:
            user_id, role_id = user_info
            role_name = self.get_role_name(role_id)
            if role_name is None:
                QMessageBox.warning(self, "Role not found.", "Error")
                return

            QMessageBox.information(self, "Login successful.", "Success")
            self.login_callback(user_id, role_name)
        else:
            QMessageBox.warning(self, "Invalid email or password.", "Error")

    def signup_callback(self):
        self.signup_window = SignupWindow(self.db, self.login_callback)
        self.signup_window.show()
        self.close()

    def get_role_name(self, role_id):
        self.db.cur.execute("SELECT RoleName FROM Role WHERE RoleID = ?", (role_id,))
        role_name = self.db.cur.fetchone()
        return role_name[0] if role_name else None

class MainWindow(QMainWindow):
    def __init__(self, db, user_id, role_name):
        super().__init__()
        self.db = db
        self.user_id = user_id
        self.role_name = role_name

        self.setWindowTitle("Witness Submission System")
        self.setGeometry(100, 100, QApplication.desktop().screenGeometry().width(), QApplication.desktop().screenGeometry().height())

        # Create actions for toolbar
        file_menu = self.menuBar().addMenu("&File")

        save_action = QAction("&Save", self)
        save_action.triggered.connect(self.save)
        file_menu.addAction(save_action)

        exit_action = QAction("&Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        if self.role_name == "Admin":
            # Add admin-specific actions to the menu
            admin_action = QAction("&Admin Action", self)
            admin_action.triggered.connect(self.admin_action)
            file_menu.addAction(admin_action)

        self.toolbar = self.addToolBar("Main Toolbar")
        self.toolbar.addAction(save_action)
        self.toolbar.addAction(exit_action)
        if self.role_name == "Admin":
            self.toolbar.addAction(admin_action)

    def save(self):
        QMessageBox.information(self, "Save", "Save functionality to be implemented.")

    def admin_action(self):
        # Implement admin action dialog here
        self.admin_dialog = AdminActionDialog(self.db)
        self.admin_dialog.exec_()

class AdminActionDialog(QDialog):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setWindowTitle("Admin Actions")
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)

        self.label_case_description = QLabel("Case Description:")
        self.lineedit_case_description = QLineEdit()
        self.layout.addWidget(self.label_case_description)
        self.layout.addWidget(self.lineedit_case_description)

        self.label_witnesses = QLabel("Witnesses:")
        self.lineedit_witnesses = QLineEdit()
        self.layout.addWidget(self.label_witnesses)
        self.layout.addWidget(self.lineedit_witnesses)

        self.label_suspects = QLabel("Suspects:")
        self.lineedit_suspects = QLineEdit()
        self.layout.addWidget(self.label_suspects)
        self.layout.addWidget(self.lineedit_suspects)

        self.label_law_enforcers = QLabel("Law Enforcers:")
        self.lineedit_law_enforcers = QLineEdit()
        self.layout.addWidget(self.label_law_enforcers)
        self.layout.addWidget(self.lineedit_law_enforcers)

        self.button_add_case = QPushButton("Add Case", clicked=self.add_case)
        self.layout.addWidget(self.button_add_case)

        self.layout.setAlignment(Qt.AlignCenter)
        self.resize(400, 300)

    def add_case(self):
        case_description = self.lineedit_case_description.text().strip()
        if not case_description:
            QMessageBox.warning(self, "Please provide case description.", "Warning")
            return

        witnesses = self.lineedit_witnesses.text().strip()
        suspects = self.lineedit_suspects.text().strip()
        law_enforcers = self.lineedit_law_enforcers.text().strip()

        # Split the input by comma and strip extra spaces
        witnesses = [w.strip() for w in witnesses.split(',') if w.strip()]
        suspects = [s.strip() for s in suspects.split(',') if s.strip()]
        law_enforcers = [le.strip() for le in law_enforcers.split(',') if le.strip()]

        # Add case to the database
        try:
            self.db.cur.execute("INSERT INTO Cases (CaseDescription) VALUES (?)", (case_description,))
            case_id = self.db.cur.lastrowid
            self.db.conn.commit()

            # Add witnesses
            for witness_name in witnesses:
                self.add_person("Witness", witness_name, case_id)

            # Add suspects
            for suspect_name in suspects:
                self.add_person("Suspect", suspect_name, case_id)

            # Add law enforcers
            for enforcer_name in law_enforcers:
                self.add_person("LawEnforcer", enforcer_name, case_id)

            QMessageBox.information(self, "Case added successfully.", "Success")
        except Exception as e:
            QMessageBox.warning(self, f"Error adding case: {str(e)}", "Error")

    def add_person(self, role, name, case_id):
        try:
            # Check if the person already exists
            self.db.cur.execute(f"SELECT UserID FROM User WHERE FirstName || ' ' || LastName = ?", (name,))
            user_id = self.db.cur.fetchone()
            if user_id:
                user_id = user_id[0]
            else:
                QMessageBox.warning(self, f"{name} not found in database.", "Error")
                return

            # Insert into appropriate role table
            self.db.cur.execute(f"INSERT INTO {role} (UserID, CaseID) VALUES (?, ?)", (user_id, case_id))
            self.db.conn.commit()
        except Exception as e:
            QMessageBox.warning(self, f"Error adding {role}: {str(e)}", "Error")

class AdminMainWindow(MainWindow):
    def __init__(self, db, user_id, role_name):
        super().__init__(db, user_id, role_name)
        self.setWindowTitle("Admin Window")
        # Add admin-specific widgets and functionalities here

class WitnessMainWindow(MainWindow):
    def __init__(self, db, user_id, role_name):
        super().__init__(db, user_id, role_name)
        self.setWindowTitle("Witness Window")
        # Add witness-specific widgets and functionalities here

class SuspectMainWindow(MainWindow):
    def __init__(self, db, user_id, role_name):
        super().__init__(db, user_id, role_name)
        self.setWindowTitle("Suspect Window")
        # Add suspect-specific widgets and functionalities here

class LawEnforcerMainWindow(MainWindow):
    def __init__(self, db, user_id, role_name):
        super().__init__(db, user_id, role_name)
        self.setWindowTitle("Law Enforcer Window")
        # Add law enforcer-specific widgets and functionalities here
class Launcher(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.login_window = LoginWindow(self.db, self.show_main_window)
        self.setCentralWidget(self.login_window)

    def show_main_window(self, user_id, role_name):
        if role_name == "Admin":
            self.main_window = AdminMainWindow(self.db, user_id, role_name)
        elif role_name == "Witness":
            self.main_window = WitnessMainWindow(self.db, user_id, role_name)
        elif role_name == "Suspect":
            self.main_window = SuspectMainWindow(self.db, user_id, role_name)
        elif role_name == "Law Enforcer":
            self.main_window = LawEnforcerMainWindow(self.db, user_id, role_name)

        self.setCentralWidget(self.main_window)

if __name__ == "__main__":
    app = QApplication([])
    app.setStyleSheet(
        "QMainWindow { background-color: #00CED1 }"
        "QLabel { color: white; font-size: 16px }"
        "QPushButton { background-color: #4CAF50; color: white; font-weight: bold; border: none; padding: 10px; border-radius: 5px }"
        "QPushButton:hover { background-color: #45a049 }"
    )

    # Initialize Database
    db = Database('witness_submission.db')

    # Populate roles
    roles = ["Admin", "Witness", "Suspect", "Law Enforcer"]
    for role in roles:
        db.cur.execute("INSERT INTO Role (RoleName) VALUES (?)", (role,))
    db.conn.commit()

    # Create launcher
    window = Launcher(db)
    window.show()

    sys.exit(app.exec_())
