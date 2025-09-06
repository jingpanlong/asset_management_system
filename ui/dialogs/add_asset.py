from PyQt5.QtWidgets import (QDialog, QFormLayout, QLineEdit, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QLabel, QMessageBox,
                            QComboBox, QTextEdit, QDateEdit, QSpinBox,
                            QFileDialog, QGroupBox, QGridLayout)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QPixmap, QFont
from models.asset import Asset
import os
import shutil

class AddAssetDialog(QDialog):
    def __init__(self, parent=None, asset_id=None, user_id=None):
        super().__init__(parent)
        self.asset = None
        self.asset_id = asset_id
        self.user_id = user_id
        self.image_path = ""
        self.init_ui()
        
        # 如果是编辑模式，加载资产信息
        if asset_id:
            self.load_asset_info(asset_id)
    
    def init_ui(self):
        self.setWindowTitle("添加资产" if not self.asset_id else "编辑资产")
        self.resize(600, 600)
        
        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # 标题
        title = "添加资产" if not self.asset_id else "编辑资产"
        title_label = QLabel(title)
        title_font = QFont("SimHei", 14, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 创建分组布局
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)
        
        # 左侧表单布局 - 基础信息
        basic_group = QGroupBox("基础信息")
        basic_layout = QFormLayout()
        basic_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)
        basic_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        basic_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        basic_layout.setSpacing(10)
        
        # 资产编号
        self.asset_id_edit = QLineEdit()
        self.asset_id_edit.setPlaceholderText("请输入资产编号")
        if self.asset_id:  # 编辑模式下资产编号不可修改
            self.asset_id_edit.setReadOnly(True)
        basic_layout.addRow("资产编号:", self.asset_id_edit)
        
        # 设备名称
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("请输入设备名称")
        basic_layout.addRow("设备名称:", self.name_edit)
        
        # 数量
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setValue(1)
        basic_layout.addRow("数量:", self.quantity_spin)
        
        # 类目
        self.category_combo = QComboBox()
        categories = Asset.get_categories()
        self.category_combo.addItems(categories)
        basic_layout.addRow("类目:", self.category_combo)
        
        # 品牌规格
        self.brand_edit = QLineEdit()
        self.brand_edit.setPlaceholderText("请输入品牌规格")
        basic_layout.addRow("品牌规格:", self.brand_edit)
        
        # 入库时间
        self.purchase_date_edit = QDateEdit()
        self.purchase_date_edit.setCalendarPopup(True)
        self.purchase_date_edit.setDate(QDate.currentDate())
        basic_layout.addRow("入库时间:", self.purchase_date_edit)
        
        basic_group.setLayout(basic_layout)
        
        # 右侧表单布局 - 其他信息
        other_group = QGroupBox("其他信息")
        other_layout = QFormLayout()
        other_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)
        other_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        other_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        other_layout.setSpacing(10)
        
        # 设备位置
        self.location_edit = QLineEdit()
        self.location_edit.setPlaceholderText("请输入设备位置")
        other_layout.addRow("设备位置:", self.location_edit)
        
        # 维修状态
        self.status_combo = QComboBox()
        self.status_combo.addItems(["正常", "维修中", "已报废"])
        other_layout.addRow("维修状态:", self.status_combo)
        
        # 资产图片
        self.image_label = QLabel("未选择图片")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumHeight(100)
        self.image_label.setStyleSheet("border: 1px solid #ccc;")
        
        self.upload_button = QPushButton("上传图片")
        self.upload_button.clicked.connect(self.upload_image)
        
        other_layout.addRow("资产图片:", self.image_label)
        other_layout.addRow("", self.upload_button)
        
        # 备注
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("请输入备注信息")
        self.notes_edit.setMinimumHeight(60)
        other_layout.addRow("备注:", self.notes_edit)
        
        other_group.setLayout(other_layout)
        
        # 将分组添加到网格布局
        grid_layout.addWidget(basic_group, 0, 0)
        grid_layout.addWidget(other_group, 0, 1)
        grid_layout.setColumnStretch(0, 1)
        grid_layout.setColumnStretch(1, 1)
        
        main_layout.addLayout(grid_layout)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setAlignment(Qt.AlignRight)
        
        # 取消按钮
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        cancel_button.setMinimumHeight(30)
        cancel_button.setMinimumWidth(80)
        
        # 保存按钮
        self.save_button = QPushButton("保存")
        self.save_button.clicked.connect(self.save_asset)
        self.save_button.setMinimumHeight(30)
        self.save_button.setMinimumWidth(80)
        
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(self.save_button)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def upload_image(self):
        """上传资产图片"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图片", "", "图片文件 (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if file_path:
            # 显示选中的图片
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                # 缩放图片以适应标签
                scaled_pixmap = pixmap.scaled(
                    self.image_label.width(), self.image_label.height(),
                    Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                self.image_label.setPixmap(scaled_pixmap)
                self.image_path = file_path
                self.image_label.setText("")
    
    def load_asset_info(self, asset_id):
        """加载资产信息到表单"""
        self.asset = Asset(asset_id)
        
        if self.asset.id:
            self.asset_id_edit.setText(self.asset.asset_id)
            self.name_edit.setText(self.asset.name)
            self.quantity_spin.setValue(self.asset.quantity)
            
            # 设置类目
            category_index = self.category_combo.findText(self.asset.category)
            if category_index >= 0:
                self.category_combo.setCurrentIndex(category_index)
            
            self.brand_edit.setText(self.asset.brand_spec)
            
            # 设置日期
            if self.asset.purchase_date:
                date_parts = self.asset.purchase_date.split('-')
                if len(date_parts) == 3:
                    try:
                        year, month, day = map(int, date_parts)
                        self.purchase_date_edit.setDate(QDate(year, month, day))
                    except:
                        pass
            
            self.location_edit.setText(self.asset.location)
            
            # 设置维修状态
            status_index = self.status_combo.findText(self.asset.maintenance_status)
            if status_index >= 0:
                self.status_combo.setCurrentIndex(status_index)
            
            # 显示图片
            if self.asset.image_path and os.path.exists(self.asset.image_path):
                pixmap = QPixmap(self.asset.image_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(
                        self.image_label.width(), self.image_label.height(),
                        Qt.KeepAspectRatio, Qt.SmoothTransformation
                    )
                    self.image_label.setPixmap(scaled_pixmap)
                    self.image_path = self.asset.image_path
                    self.image_label.setText("")
            
            self.notes_edit.setText(self.asset.notes)
    
    def save_asset(self):
        """保存资产信息"""
        asset_id = self.asset_id_edit.text().strip()
        name = self.name_edit.text().strip()
        quantity = self.quantity_spin.value()
        category = self.category_combo.currentText()
        brand_spec = self.brand_edit.text().strip()
        purchase_date = self.purchase_date_edit.date().toString("yyyy-MM-dd")
        location = self.location_edit.text().strip()
        maintenance_status = self.status_combo.currentText()
        notes = self.notes_edit.toPlainText().strip()
        
        # 验证必填字段
        if not asset_id:
            QMessageBox.warning(self, "警告", "资产编号不能为空")
            return
        
        if not name:
            QMessageBox.warning(self, "警告", "设备名称不能为空")
            return
        
        # 处理图片
        saved_image_path = ""
        if self.image_path and os.path.exists(self.image_path):
            # 确保assets/images目录存在
            if not os.path.exists("assets/images"):
                os.makedirs("assets/images")
            
            # 复制图片到项目目录
            file_ext = os.path.splitext(self.image_path)[1]
            new_file_name = f"{asset_id}{file_ext}"
            saved_image_path = os.path.join("assets/images", new_file_name)
            
            # 如果是新图片或图片已更改，才复制
            if not self.asset or self.asset.image_path != saved_image_path:
                shutil.copy2(self.image_path, saved_image_path)
        
        # 创建或更新资产
        if not self.asset:
            self.asset = Asset()
            self.asset.asset_id = asset_id
        
        self.asset.name = name
        self.asset.quantity = quantity
        self.asset.category = category
        self.asset.brand_spec = brand_spec
        self.asset.purchase_date = purchase_date
        self.asset.location = location
        self.asset.maintenance_status = maintenance_status
        self.asset.notes = notes
        
        # 如果有新图片，更新图片路径
        if saved_image_path:
            self.asset.image_path = saved_image_path
        
        # 保存资产
        success, msg = self.asset.save(self.user_id)
        if success:
            QMessageBox.information(self, "成功", msg)
            self.accept()
        else:
            QMessageBox.warning(self, "错误", msg)
