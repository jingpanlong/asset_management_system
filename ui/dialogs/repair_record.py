from PyQt5.QtWidgets import (QDialog, QFormLayout, QLineEdit, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QLabel, QMessageBox,
                            QDateEdit, QTextEdit, QTableWidget, QTableWidgetItem,
                            QHeaderView, QGroupBox, QScrollArea, QWidget)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from models.asset import Asset

class RepairRecordDialog(QDialog):
    def __init__(self, parent=None, asset_id=None, user_id=None):
        super().__init__(parent)
        self.asset_id = asset_id  # 资产数据库ID
        self.user_id = user_id
        self.asset = None
        self.init_ui()
        self.load_asset_info()
        self.load_repair_records()
    
    def init_ui(self):
        self.setWindowTitle("资产维修记录")
        self.resize(800, 600)
        
        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("资产维修记录")
        title_font = QFont("SimHei", 14, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 资产信息
        self.asset_info_label = QLabel()
        self.asset_info_label.setStyleSheet("background-color: #f0f0f0; padding: 10px; border-radius: 5px;")
        main_layout.addWidget(self.asset_info_label)
        
        # 添加维修记录区域
        add_group = QGroupBox("添加新维修记录")
        add_layout = QFormLayout()
        add_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)
        add_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        add_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        add_layout.setSpacing(10)
        
        # 维修时间
        self.repair_date_edit = QDateEdit()
        self.repair_date_edit.setCalendarPopup(True)
        self.repair_date_edit.setDate(QDate.currentDate())
        add_layout.addRow("维修时间:", self.repair_date_edit)
        
        # 故障原因
        self.fault_cause_edit = QTextEdit()
        self.fault_cause_edit.setMinimumHeight(60)
        add_layout.addRow("故障原因:", self.fault_cause_edit)
        
        # 维修结果
        self.repair_result_edit = QTextEdit()
        self.repair_result_edit.setMinimumHeight(60)
        add_layout.addRow("维修结果:", self.repair_result_edit)
        
        # 添加按钮
        add_button = QPushButton("添加维修记录")
        add_button.clicked.connect(self.add_repair_record)
        add_button.setMinimumHeight(30)
        add_layout.addRow("", add_button)
        
        add_group.setLayout(add_layout)
        main_layout.addWidget(add_group)
        
        # 维修记录表格
        records_group = QGroupBox("历史维修记录")
        records_layout = QVBoxLayout()
        
        self.records_table = QTableWidget()
        self.records_table.setColumnCount(4)
        self.records_table.setHorizontalHeaderLabels(["维修时间", "故障原因", "维修结果", "记录时间"])
        self.records_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.records_table.verticalHeader().setVisible(False)
        self.records_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
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
                    <td><b>当前状态:</b></td><td>{self.asset.maintenance_status}</td></tr>
                </table>
                """
                self.asset_info_label.setText(info_text)
    
    def load_repair_records(self):
        """加载维修记录"""
        if self.asset and self.asset.repair_records:
            self.records_table.setRowCount(len(self.asset.repair_records))
            
            for row, record in enumerate(self.asset.repair_records):
                record_id, repair_date, fault_cause, repair_result, created_at = record
                
                # 维修时间
                item1 = QTableWidgetItem(repair_date)
                item1.setTextAlignment(Qt.AlignCenter)
                self.records_table.setItem(row, 0, item1)
                
                # 故障原因
                item2 = QTableWidgetItem(fault_cause)
                item2.setTextAlignment(Qt.AlignCenter)
                self.records_table.setItem(row, 1, item2)
                
                # 维修结果
                item3 = QTableWidgetItem(repair_result)
                item3.setTextAlignment(Qt.AlignCenter)
                self.records_table.setItem(row, 2, item3)
                
                # 记录时间
                item4 = QTableWidgetItem(created_at)
                item4.setTextAlignment(Qt.AlignCenter)
                self.records_table.setItem(row, 3, item4)
    
    def add_repair_record(self):
        """添加新的维修记录"""
        if not self.asset:
            QMessageBox.warning(self, "错误", "未找到资产信息")
            return
        
        repair_date = self.repair_date_edit.date().toString("yyyy-MM-dd")
        fault_cause = self.fault_cause_edit.toPlainText().strip()
        repair_result = self.repair_result_edit.toPlainText().strip()
        
        if not fault_cause:
            QMessageBox.warning(self, "警告", "故障原因不能为空")
            return
        
        success = self.asset.add_repair_record(repair_date, fault_cause, repair_result, self.user_id)
        
        if success:
            QMessageBox.information(self, "成功", "维修记录添加成功")
            # 刷新记录列表
            self.asset.load_repair_records()
            self.load_repair_records()
            # 清空表单
            self.fault_cause_edit.clear()
            self.repair_result_edit.clear()
        else:
            QMessageBox.warning(self, "错误", "维修记录添加失败")
