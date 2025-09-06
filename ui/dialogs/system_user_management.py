from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QTableWidget, QTableWidgetItem, QHeaderView,
                            QLabel, QMessageBox, QGroupBox, QFormLayout,
                            QLineEdit, QComboBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

class SystemUserManagementDialog(QDialog):
    def __init__(self, parent=None, current_user=None):
        super().__init__(parent)
        self.current_user = current_user  # 当前登录用户（管理员）
        self.init_ui()
        self.load_users()
    
    def init_ui(self):
        self.setWindowTitle("系统用户管理")
        self.resize(800, 600)
        
        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("系统用户管理")
        title_font = QFont("SimHei", 14, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 操作按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setAlignment(Qt.AlignLeft)
        
        # 添加用户按钮
        add_button = QPushButton("添加用户")
        add_button.clicked.connect(self.add_user)
        add_button.setMinimumHeight(30)
        button_layout.addWidget(add_button)
        
        # 修改角色按钮
        self.change_role_button = QPushButton("修改角色")
        self.change_role_button.clicked.connect(self.change_user_role)
        self.change_role_button.setMinimumHeight(30)
        self.change_role_button.setEnabled(False)
        button_layout.addWidget(self.change_role_button)
        
        # 删除用户按钮
        self.delete_button = QPushButton("删除用户")
        self.delete_button.clicked.connect(self.delete_user)
        self.delete_button.setMinimumHeight(30)
        self.delete_button.setEnabled(False)
        button_layout.addWidget(self.delete_button)
        
        main_layout.addLayout(button_layout)
        
        # 用户表格
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(4)
        self.user_table.setHorizontalHeaderLabels(["ID", "用户名", "角色", "创建时间"])
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.user_table.verticalHeader().setVisible(False)
        self.user_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.user_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.user_table.cellClicked.connect(self.on_cell_clicked)
        
        main_layout.addWidget(self.user_table)
        
        # 按钮布局
        close_layout = QHBoxLayout()
        close_layout.setAlignment(Qt.AlignRight)
        
        # 关闭按钮
        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.reject)
        close_button.setMinimumHeight(30)
        close_button.setMinimumWidth(80)
        
        close_layout.addWidget(close_button)
        main_layout.addLayout(close_layout)
        
        self.setLayout(main_layout)
    
    def load_users(self):
        """加载系统用户"""
        users = self.current_user.get_all_users()
        
        self.user_table.setRowCount(len(users))
        
        for row, user in enumerate(users):
            user_id, username, role, created_at = user
            
            # ID
            item0 = QTableWidgetItem(str(user_id))
            item0.setTextAlignment(Qt.AlignCenter)
            self.user_table.setItem(row, 0, item0)
            
            # 用户名
            item1 = QTableWidgetItem(username)
            item1.setTextAlignment(Qt.AlignCenter)
            # 当前登录用户高亮显示
            if username == self.current_user.username:
                item1.setBackground(QColor(220, 230, 242))
            self.user_table.setItem(row, 1, item1)
            
            # 角色
            item2 = QTableWidgetItem(role)
            item2.setTextAlignment(Qt.AlignCenter)
            if role == 'admin':
                item2.setForeground(QColor(255, 102, 0))  # 橙色
            self.user_table.setItem(row, 2, item2)
            
            # 创建时间
            item3 = QTableWidgetItem(created_at)
            item3.setTextAlignment(Qt.AlignCenter)
            self.user_table.setItem(row, 3, item3)
    
    def on_cell_clicked(self, row, column):
        """表格单元格点击事件"""
        # 获取选中用户
        user_id = int(self.user_table.item(row, 0).text())
        username = self.user_table.item(row, 1).text()
        
        # 不能修改或删除当前登录用户
        if username == self.current_user.username:
            self.change_role_button.setEnabled(False)
            self.delete_button.setEnabled(False)
        else:
            self.change_role_button.setEnabled(True)
            self.delete_button.setEnabled(True)
    
    def add_user(self):
        """添加新用户"""
        dialog = AddSystemUserDialog(self)
        if dialog.exec_():
            self.load_users()
    
    def change_user_role(self):
        """修改用户角色"""
        selected_rows = self.user_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "警告", "请先选择用户")
            return
        
        row = selected_rows[0].row()
        user_id = int(self.user_table.item(row, 0).text())
        username = self.user_table.item(row, 1).text()
        current_role = self.user_table.item(row, 2).text()
        
        # 确定新角色
        new_role = "user" if current_role == "admin" else "admin"
        
        # 确认修改
        reply = QMessageBox.question(
            self, "确认修改", f"确定要将用户 {username} 的角色从 {current_role} 改为 {new_role} 吗？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.current_user.update_user_role(user_id, new_role):
                QMessageBox.information(self, "成功", "用户角色已更新")
                self.load_users()
            else:
                QMessageBox.warning(self, "错误", "更新失败")
    
    def delete_user(self):
        """删除用户"""
        selected_rows = self.user_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "警告", "请先选择用户")
            return
        
        row = selected_rows[0].row()
        user_id = int(self.user_table.item(row, 0).text())
        username = self.user_table.item(row, 1).text()
        
        # 确认删除
        reply = QMessageBox.question(
            self, "确认删除", f"确定要删除用户 {username} 吗？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.current_user.delete_user(user_id):
                QMessageBox.information(self, "成功", "用户已删除")
                self.load_users()
            else:
                QMessageBox.warning(self, "错误", "删除失败")


class AddSystemUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("添加系统用户")
        self.resize(400, 300)
        
        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 30, 40, 20)
        main_layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("添加系统用户")
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
        
        # 角色选择
        self.role_combo = QComboBox()
        self.role_combo.addItems(["user", "admin"])
        form_layout.addRow("角色:", self.role_combo)
        
        main_layout.addLayout(form_layout)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # 取消按钮
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        cancel_button.setMinimumHeight(30)
        
        # 确定按钮
        self.confirm_button = QPushButton("确定")
        self.confirm_button.clicked.connect(self.add_user)
        self.confirm_button.setMinimumHeight(30)
        
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(self.confirm_button)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def add_user(self):
        """添加用户"""
        from models.user import User
        
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
