from PyQt5.QtWidgets import (QDialog, QFormLayout, QLineEdit, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QLabel, QMessageBox,
                            QComboBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from models.user import User

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.user = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("资产管理系统 - 登录")
        self.setFixedSize(400, 300)
        self.setWindowIcon(QIcon("assets/images/logo.ico"))
        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(50, 50, 50, 30)
        main_layout.setSpacing(20)
        # 标题
        title_label = QLabel("资产管理系统")
        title_font = QFont("SimHei", 16, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 表单布局
        form_layout = QFormLayout()
        form_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form_layout.setSpacing(15)
        
        # 用户名输入
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("请输入用户名")
        form_layout.addRow("用户名:", self.username_edit)
        
        # 密码输入
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("请输入密码")
        form_layout.addRow("密码:", self.password_edit)
        
        main_layout.addLayout(form_layout)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # 登录按钮
        self.login_button = QPushButton("登录")
        self.login_button.clicked.connect(self.login)
        self.login_button.setMinimumHeight(30)
        
        # 注册按钮
        self.register_button = QPushButton("注册")
        self.register_button.clicked.connect(self.show_register_dialog)
        self.register_button.setMinimumHeight(30)
        
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.register_button)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def login(self):
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "警告", "用户名和密码不能为空")
            return
        
        self.user = User()
        if self.user.login(username, password):
            QMessageBox.information(self, "成功", f"欢迎回来，{username}！")
            self.accept()
        else:
            QMessageBox.warning(self, "错误", "用户名或密码不正确")
    
    def show_register_dialog(self):
        register_dialog = RegisterDialog(self)
        if register_dialog.exec_():
            QMessageBox.information(self, "成功", "注册成功，请登录")


class RegisterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("注册")
        self.setFixedSize(350, 300)
        
        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 30, 40, 20)
        main_layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("用户注册")
        title_font = QFont("SimHei", 14, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 表单布局
        form_layout = QFormLayout()
        form_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form_layout.setSpacing(15)
        
        # 用户名输入
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("请设置用户名")
        form_layout.addRow("用户名:", self.username_edit)
        
        # 密码输入
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("请设置密码")
        form_layout.addRow("密码:", self.password_edit)
        
        # 确认密码输入
        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setEchoMode(QLineEdit.Password)
        self.confirm_password_edit.setPlaceholderText("请确认密码")
        form_layout.addRow("确认密码:", self.confirm_password_edit)
        
        # 角色选择（默认普通用户，管理员注册需要权限）
        self.role_combo = QComboBox()
        self.role_combo.addItems(["user"])  # 默认可注册普通用户
        form_layout.addRow("角色:", self.role_combo)
        
        main_layout.addLayout(form_layout)
        
        # 注册按钮
        self.register_button = QPushButton("注册")
        self.register_button.clicked.connect(self.register)
        self.register_button.setMinimumHeight(30)
        main_layout.addWidget(self.register_button)
        
        self.setLayout(main_layout)
    
    def register(self):
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()
        confirm_password = self.confirm_password_edit.text().strip()
        role = self.role_combo.currentText()
        
        if not username or not password or not confirm_password:
            QMessageBox.warning(self, "警告", "所有字段不能为空")
            return
        
        if password != confirm_password:
            QMessageBox.warning(self, "警告", "两次输入的密码不一致")
            return
        
        user = User()
        success, msg = user.register(username, password, role)
        
        if success:
            QMessageBox.information(self, "成功", msg)
            self.accept()
        else:
            QMessageBox.warning(self, "错误", msg)
