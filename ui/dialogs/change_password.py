from PyQt5.QtWidgets import (QDialog, QFormLayout, QLineEdit, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QLabel, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class ChangePasswordDialog(QDialog):
    def __init__(self, parent=None, user=None):
        super().__init__(parent)
        self.user = user
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("更改密码")
        self.setFixedSize(350, 250)
        
        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 30, 40, 20)
        main_layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("更改密码")
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
        
        # 旧密码输入
        self.old_password_edit = QLineEdit()
        self.old_password_edit.setEchoMode(QLineEdit.Password)
        self.old_password_edit.setPlaceholderText("请输入旧密码")
        form_layout.addRow("旧密码:", self.old_password_edit)
        
        # 新密码输入
        self.new_password_edit = QLineEdit()
        self.new_password_edit.setEchoMode(QLineEdit.Password)
        self.new_password_edit.setPlaceholderText("请输入新密码")
        form_layout.addRow("新密码:", self.new_password_edit)
        
        # 确认新密码输入
        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setEchoMode(QLineEdit.Password)
        self.confirm_password_edit.setPlaceholderText("请确认新密码")
        form_layout.addRow("确认新密码:", self.confirm_password_edit)
        
        main_layout.addLayout(form_layout)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # 取消按钮
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        cancel_button.setMinimumHeight(30)
        
        # 确认按钮
        self.confirm_button = QPushButton("确认修改")
        self.confirm_button.clicked.connect(self.change_password)
        self.confirm_button.setMinimumHeight(30)
        
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(self.confirm_button)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def change_password(self):
        """修改密码"""
        old_password = self.old_password_edit.text().strip()
        new_password = self.new_password_edit.text().strip()
        confirm_password = self.confirm_password_edit.text().strip()
        
        if not old_password or not new_password or not confirm_password:
            QMessageBox.warning(self, "警告", "所有字段不能为空")
            return
        
        if new_password != confirm_password:
            QMessageBox.warning(self, "警告", "两次输入的新密码不一致")
            return
        
        success, msg = self.user.change_password(old_password, new_password)
        
        if success:
            QMessageBox.information(self, "成功", msg)
            self.accept()
        else:
            QMessageBox.warning(self, "错误", msg)
