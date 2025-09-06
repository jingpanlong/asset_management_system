from PyQt5.QtWidgets import (QDialog, QFormLayout, QLineEdit, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QLabel, QMessageBox,
                            QDateEdit, QTableWidget, QTableWidgetItem,
                            QHeaderView, QGroupBox, QGridLayout)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor
from models.asset import Asset

class AssetUserManagementDialog(QDialog):
    def __init__(self, parent=None, asset_id=None):
        super().__init__(parent)
        self.asset_id = asset_id  # 资产数据库ID
        self.asset = None
        self.init_ui()
        self.load_asset_info()
        self.load_user_records()
    
    def init_ui(self):
        self.setWindowTitle("资产使用人管理")
        self.resize(800, 600)
        
        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("资产使用人管理")
        title_font = QFont("SimHei", 14, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 资产信息
        self.asset_info_label = QLabel()
        self.asset_info_label.setStyleSheet("background-color: #f0f0f0; padding: 10px; border-radius: 5px;")
        main_layout.addWidget(self.asset_info_label)
        
        # 添加使用人区域
        add_group = QGroupBox("添加使用人")
        add_layout = QGridLayout()
        add_layout.setSpacing(10)
        
        # 使用人姓名
        add_layout.addWidget(QLabel("使用人姓名:"), 0, 0)
        self.user_name_edit = QLineEdit()
        add_layout.addWidget(self.user_name_edit, 0, 1)
        
        # 开始时间
        add_layout.addWidget(QLabel("开始使用时间:"), 0, 2)
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate())
        add_layout.addWidget(self.start_date_edit, 0, 3)
        
        # 添加按钮
        add_button = QPushButton("添加使用人")
        add_button.clicked.connect(self.add_user)
        add_button.setMinimumHeight(30)
        add_layout.addWidget(add_button, 0, 4)
        
        add_group.setLayout(add_layout)
        main_layout.addWidget(add_group)
        
        # 使用记录表格
        records_group = QGroupBox("使用记录")
        records_layout = QVBoxLayout()
        
        self.records_table = QTableWidget()
        self.records_table.setColumnCount(5)
        self.records_table.setHorizontalHeaderLabels(["使用人", "开始时间", "结束时间", "状态", "操作"])
        self.records_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.records_table.verticalHeader().setVisible(False)
        
        records_layout.addWidget(self.records_table)
        records_group.setLayout(records_layout)
        main_layout.addWidget(records_group)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setAlignment(Qt.AlignRight)
        
        # 关闭按钮
        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.reject)
        close_button.setMinimumHeight(30)
        close_button.setMinimumWidth(80)
        
        button_layout.addWidget(close_button)
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def load_asset_info(self):
        """加载资产基本信息"""
        if self.asset_id:
            self.asset = Asset()
            self.asset.load_by_id(self.asset_id)
            
            if self.asset.id:
                info_text = f"""
                <table>
                    <tr><td><b>资产编号:</b></td><td>{self.asset.asset_id}</td>
                    <td><b>设备名称:</b></td><td>{self.asset.name}</td></tr>
                    <tr><td><b>类目:</b></td><td>{self.asset.category}</td>
                    <td><b>位置:</b></td><td>{self.asset.location}</td></tr>
                </table>
                """
                self.asset_info_label.setText(info_text)
    
    def load_user_records(self):
        """加载使用人记录"""
        if self.asset and self.asset.users:
            self.records_table.setRowCount(len(self.asset.users))
            
            for row, user in enumerate(self.asset.users):
                record_id, user_name, start_date, end_date = user
                
                # 使用人姓名
                item1 = QTableWidgetItem(user_name)
                item1.setTextAlignment(Qt.AlignCenter)
                self.records_table.setItem(row, 0, item1)
                
                # 开始时间
                item2 = QTableWidgetItem(start_date)
                item2.setTextAlignment(Qt.AlignCenter)
                self.records_table.setItem(row, 1, item2)
                
                # 结束时间
                item3 = QTableWidgetItem(end_date if end_date else "")
                item3.setTextAlignment(Qt.AlignCenter)
                self.records_table.setItem(row, 2, item3)
                
                # 状态
                status = "在用" if not end_date else "已归还"
                item4 = QTableWidgetItem(status)
                item4.setTextAlignment(Qt.AlignCenter)
                if status == "在用":
                    item4.setForeground(QColor("green"))
                else:
                    item4.setForeground(QColor("gray"))
                self.records_table.setItem(row, 3, item4)
                
                # 操作按钮
                if not end_date:  # 如果未结束，显示"结束使用"按钮
                    end_button = QPushButton("结束使用")
                    end_button.setMinimumHeight(25)
                    end_button.clicked.connect(lambda checked, rid=record_id, r=row: self.end_use(rid, r))
                    self.records_table.setCellWidget(row, 4, end_button)
                else:
                    item5 = QTableWidgetItem("")
                    self.records_table.setItem(row, 4, item5)
    
    def add_user(self):
        """添加使用人"""
        if not self.asset:
            QMessageBox.warning(self, "错误", "未找到资产信息")
            return
        
        user_name = self.user_name_edit.text().strip()
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        
        if not user_name:
            QMessageBox.warning(self, "警告", "使用人姓名不能为空")
            return
        
        success = self.asset.add_user(user_name, start_date)
        
        if success:
            QMessageBox.information(self, "成功", "使用人添加成功")
            # 刷新记录列表
            self.asset.load_users()
            self.load_user_records()
            # 清空表单
            self.user_name_edit.clear()
        else:
            QMessageBox.warning(self, "错误", "使用人添加失败")
    
    def end_use(self, record_id, row):
        """结束使用"""
        end_date = QDate.currentDate().toString("yyyy-MM-dd")
        
        success = self.asset.update_user(record_id, end_date)
        
        if success:
            # 更新表格显示
            item3 = QTableWidgetItem(end_date)
            item3.setTextAlignment(Qt.AlignCenter)
            self.records_table.setItem(row, 2, item3)
            
            item4 = QTableWidgetItem("已归还")
            item4.setTextAlignment(Qt.AlignCenter)
            item4.setForeground(QColor("gray"))
            self.records_table.setItem(row, 3, item4)
            
            # 移除按钮
            self.records_table.setCellWidget(row, 4, None)
            
            QMessageBox.information(self, "成功", "已记录结束使用时间")
        else:
            QMessageBox.warning(self, "错误", "操作失败")
