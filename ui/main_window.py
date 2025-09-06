from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QTableWidget, QTableWidgetItem,
                            QHeaderView, QLabel, QLineEdit, QComboBox,
                            QMessageBox, QFileDialog, QAction, QMenuBar,
                            QMenu, QStatusBar, QSplitter, QGroupBox, QFormLayout)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon, QPixmap
from models.asset import Asset
from models.user import User
from ui.dialogs.add_asset import AddAssetDialog
from ui.dialogs.repair_record import RepairRecordDialog
from ui.dialogs.user_management import AssetUserManagementDialog
from utils.import_export import ImportExport
import os

class MainWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user  # 当前登录用户
        self.init_ui()
        self.load_assets()
    
    def init_ui(self):
        self.setWindowTitle(f"资产管理系统 - {self.user.username} ({self.user.role})")
        self.resize(1200, 800)
        self.setWindowIcon(QIcon("assets/images/logo.ico"))
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        # 标题
        title_label = QLabel("资产清单")
        title_font = QFont("SimHei", 16, QFont.Bold)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)
        
        # 搜索和筛选区域
        filter_group = QGroupBox("搜索和筛选")
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)
        
        # 搜索框
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("搜索资产编号、名称...")
        self.search_edit.returnPressed.connect(self.search_assets)
        filter_layout.addWidget(self.search_edit)
        
        # 类目筛选
        self.category_combo = QComboBox()
        self.category_combo.addItem("所有类目")
        categories = Asset.get_categories()
        self.category_combo.addItems(categories)
        self.category_combo.currentIndexChanged.connect(self.filter_assets)
        filter_layout.addWidget(self.category_combo)
        
        # 状态筛选
        self.status_combo = QComboBox()
        self.status_combo.addItems(["所有状态", "正常", "维修中", "已报废"])
        self.status_combo.currentIndexChanged.connect(self.filter_assets)
        filter_layout.addWidget(self.status_combo)
        
        # 搜索按钮
        search_button = QPushButton("搜索")
        search_button.clicked.connect(self.search_assets)
        filter_layout.addWidget(search_button)
        
        # 重置按钮
        reset_button = QPushButton("重置")
        reset_button.clicked.connect(self.reset_filters)
        filter_layout.addWidget(reset_button)
        
        filter_group.setLayout(filter_layout)
        main_layout.addWidget(filter_group)
        
        # 操作按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setAlignment(Qt.AlignLeft)
        
        # 添加资产按钮
        add_button = QPushButton("添加资产")
        add_button.clicked.connect(self.add_asset)
        add_button.setMinimumHeight(35)
        add_button.setMinimumWidth(100)
        button_layout.addWidget(add_button)
        
        # 编辑资产按钮
        self.edit_button = QPushButton("编辑资产")
        self.edit_button.clicked.connect(self.edit_asset)
        self.edit_button.setMinimumHeight(35)
        self.edit_button.setMinimumWidth(100)
        self.edit_button.setEnabled(False)
        button_layout.addWidget(self.edit_button)
        
        # 删除资产按钮
        self.delete_button = QPushButton("删除资产")
        self.delete_button.clicked.connect(self.delete_asset)
        self.delete_button.setMinimumHeight(35)
        self.delete_button.setMinimumWidth(100)
        self.delete_button.setEnabled(False)
        # 只有管理员可以删除
        if self.user.role != 'admin':
            self.delete_button.setEnabled(False)
            self.delete_button.setVisible(False)
        
        button_layout.addWidget(self.delete_button)
        
        # 使用人管理按钮
        self.user_button = QPushButton("使用人管理")
        self.user_button.clicked.connect(self.manage_users)
        self.user_button.setMinimumHeight(35)
        self.user_button.setMinimumWidth(100)
        self.user_button.setEnabled(False)
        button_layout.addWidget(self.user_button)
        
        # 维修记录按钮
        self.repair_button = QPushButton("维修记录")
        self.repair_button.clicked.connect(self.manage_repairs)
        self.repair_button.setMinimumHeight(35)
        self.repair_button.setMinimumWidth(100)
        self.repair_button.setEnabled(False)
        button_layout.addWidget(self.repair_button)
        
        # 导入按钮
        import_button = QPushButton("导入资产")
        import_button.clicked.connect(self.import_assets)
        import_button.setMinimumHeight(35)
        import_button.setMinimumWidth(100)
        button_layout.addWidget(import_button)
        
        # 导出按钮
        export_button = QPushButton("导出资产")
        export_button.clicked.connect(self.export_assets)
        export_button.setMinimumHeight(35)
        export_button.setMinimumWidth(100)
        button_layout.addWidget(export_button)
        
        main_layout.addLayout(button_layout)
        
        # 资产表格
        self.asset_table = QTableWidget()
        self.asset_table.setColumnCount(10)
        self.asset_table.setHorizontalHeaderLabels([
            "资产编号", "设备名称", "数量", "类目", "品牌规格",
            "入库时间", "设备位置", "使用人", "维修状态", "备注"
        ])
        self.asset_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.asset_table.verticalHeader().setVisible(False)
        self.asset_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.asset_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.asset_table.cellClicked.connect(self.on_cell_clicked)
        self.asset_table.setMinimumHeight(500)
        
        main_layout.addWidget(self.asset_table)
        
        # 状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("就绪")
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件")
        
        # 导入动作
        import_action = QAction("导入资产", self)
        import_action.triggered.connect(self.import_assets)
        file_menu.addAction(import_action)
        
        # 导出动作
        export_action = QAction("导出资产", self)
        export_action.triggered.connect(self.export_assets)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        # 退出动作
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 资产菜单
        asset_menu = menubar.addMenu("资产")
        
        # 添加资产动作
        add_asset_action = QAction("添加资产", self)
        add_asset_action.triggered.connect(self.add_asset)
        asset_menu.addAction(add_asset_action)
        
        # 编辑资产动作
        edit_asset_action = QAction("编辑资产", self)
        edit_asset_action.triggered.connect(self.edit_asset)
        asset_menu.addAction(edit_asset_action)
        
        # 删除资产动作
        delete_asset_action = QAction("删除资产", self)
        delete_asset_action.triggered.connect(self.delete_asset)
        if self.user.role == 'admin':
            asset_menu.addAction(delete_asset_action)
        
        # 用户菜单
        user_menu = menubar.addMenu("用户")
        
        # 更改密码动作
        change_pwd_action = QAction("更改密码", self)
        change_pwd_action.triggered.connect(self.change_password)
        user_menu.addAction(change_pwd_action)
        
        # 用户管理（仅管理员可见）
        if self.user.role == 'admin':
            user_manage_action = QAction("用户管理", self)
            user_manage_action.triggered.connect(self.manage_users_system)
            user_menu.addAction(user_manage_action)
        
        user_menu.addSeparator()
        
        # 退出登录动作
        logout_action = QAction("退出登录", self)
        logout_action.triggered.connect(self.logout)
        user_menu.addAction(logout_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助")
        
        # 关于动作
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def load_assets(self, filters=None):
        """加载资产数据到表格"""
        assets = Asset.get_all_assets(filters)
        
        self.asset_table.setRowCount(len(assets))
        
        for row, asset in enumerate(assets):
            # 资产ID（数据库ID，不显示，用于后续操作）
            asset_db_id = asset[0]
            
            # 资产编号
            item0 = QTableWidgetItem(asset[1])
            item0.setTextAlignment(Qt.AlignCenter)
            item0.setData(Qt.UserRole, asset_db_id)  # 存储数据库ID
            self.asset_table.setItem(row, 0, item0)
            
            # 设备名称
            item1 = QTableWidgetItem(asset[2])
            item1.setTextAlignment(Qt.AlignCenter)
            self.asset_table.setItem(row, 1, item1)
            
            # 数量
            item2 = QTableWidgetItem(str(asset[3]))
            item2.setTextAlignment(Qt.AlignCenter)
            self.asset_table.setItem(row, 2, item2)
            
            # 类目
            item3 = QTableWidgetItem(asset[4])
            item3.setTextAlignment(Qt.AlignCenter)
            self.asset_table.setItem(row, 3, item3)
            
            # 品牌规格
            item4 = QTableWidgetItem(asset[5])
            item4.setTextAlignment(Qt.AlignCenter)
            self.asset_table.setItem(row, 4, item4)
            
            # 入库时间
            item5 = QTableWidgetItem(asset[6])
            item5.setTextAlignment(Qt.AlignCenter)
            self.asset_table.setItem(row, 5, item5)
            
            # 设备位置
            item6 = QTableWidgetItem(asset[8])
            item6.setTextAlignment(Qt.AlignCenter)
            self.asset_table.setItem(row, 6, item6)
            
            # 使用人（需要查询）
            asset_obj = Asset()
            asset_obj.load_by_id(asset_db_id)
            users_text = ", ".join([user[1] for user in asset_obj.users if not user[3]])  # 只显示当前使用人
            item7 = QTableWidgetItem(users_text)
            item7.setTextAlignment(Qt.AlignCenter)
            self.asset_table.setItem(row, 7, item7)
            
            # 维修状态
            item8 = QTableWidgetItem(asset[10])
            item8.setTextAlignment(Qt.AlignCenter)
            # 根据状态设置颜色
            if asset[10] == "正常":
                item8.setForeground(Qt.green)
            elif asset[10] == "维修中":
                item8.setForeground(Qt.yellow)
            elif asset[10] == "已报废":
                item8.setForeground(Qt.red)
            self.asset_table.setItem(row, 8, item8)
            
            # 备注
            item9 = QTableWidgetItem(asset[9])
            item9.setTextAlignment(Qt.AlignCenter)
            self.asset_table.setItem(row, 9, item9)
        
        self.statusBar.showMessage(f"共加载 {len(assets)} 条资产记录")
    
    def on_cell_clicked(self, row, column):
        """表格单元格点击事件"""
        # 启用操作按钮
        self.edit_button.setEnabled(True)
        self.delete_button.setEnabled(True if self.user.role == 'admin' else False)
        self.user_button.setEnabled(True)
        self.repair_button.setEnabled(True)
    
    def add_asset(self):
        """添加新资产"""
        dialog = AddAssetDialog(self, user_id=self.user.id)
        if dialog.exec_():
            self.load_assets()
    
    def edit_asset(self):
        """编辑选中的资产"""
        selected_rows = self.asset_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "警告", "请先选择要编辑的资产")
            return
        
        # 获取选中资产的编号
        asset_id = self.asset_table.item(selected_rows[0].row(), 0).text()
        dialog = AddAssetDialog(self, asset_id=asset_id, user_id=self.user.id)
        if dialog.exec_():
            self.load_assets()
    
    def delete_asset(self):
        """删除选中的资产"""
        selected_rows = self.asset_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "警告", "请先选择要删除的资产")
            return
        
        # 获取选中资产的数据库ID和编号
        row = selected_rows[0].row()
        asset_db_id = self.asset_table.item(row, 0).data(Qt.UserRole)
        asset_id = self.asset_table.item(row, 0).text()
        
        # 确认删除
        reply = QMessageBox.question(
            self, "确认删除", f"确定要删除资产 {asset_id} 吗？\n此操作不可恢复！",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            asset = Asset()
            asset.load_by_id(asset_db_id)
            if asset.delete():
                QMessageBox.information(self, "成功", "资产已删除")
                self.load_assets()
            else:
                QMessageBox.warning(self, "错误", "删除失败")
    
    def manage_users(self):
        """管理资产使用人"""
        selected_rows = self.asset_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "警告", "请先选择资产")
            return
        
        # 获取选中资产的数据库ID
        asset_db_id = self.asset_table.item(selected_rows[0].row(), 0).data(Qt.UserRole)
        
        dialog = AssetUserManagementDialog(self, asset_id=asset_db_id)
        dialog.exec_()
        # 刷新表格中的使用人信息
        self.load_assets()
    
    def manage_repairs(self):
        """管理资产维修记录"""
        selected_rows = self.asset_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "警告", "请先选择资产")
            return
        
        # 获取选中资产的数据库ID
        asset_db_id = self.asset_table.item(selected_rows[0].row(), 0).data(Qt.UserRole)
        
        dialog = RepairRecordDialog(self, asset_id=asset_db_id, user_id=self.user.id)
        dialog.exec_()
        # 刷新表格中的维修状态信息
        self.load_assets()
    
    def search_assets(self):
        """搜索资产"""
        search_text = self.search_edit.text().strip()
        category = self.category_combo.currentText()
        status = self.status_combo.currentText()
        
        filters = {}
        
        if search_text:
            filters["(asset_id || name || brand_spec || location)"] = search_text
        
        if category != "所有类目":
            filters["category"] = category
        
        if status != "所有状态":
            filters["maintenance_status"] = status
        
        self.load_assets(filters)
    
    def filter_assets(self):
        """筛选资产"""
        self.search_assets()
    
    def reset_filters(self):
        """重置筛选条件"""
        self.search_edit.clear()
        self.category_combo.setCurrentIndex(0)
        self.status_combo.setCurrentIndex(0)
        self.load_assets()
    
    def import_assets(self):
        """导入资产数据"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择Excel文件", "", "Excel文件 (*.xlsx *.xls)"
        )
        
        if file_path:
            success, msg = ImportExport.import_assets(file_path, self.user.id)
            if success:
                QMessageBox.information(self, "成功", msg)
                self.load_assets()
            else:
                QMessageBox.warning(self, "错误", msg)
    
    def export_assets(self):
        """导出资产数据"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存Excel文件", "", "Excel文件 (*.xlsx)"
        )
        
        if file_path:
            # 确保文件扩展名正确
            if not file_path.endswith(".xlsx"):
                file_path += ".xlsx"
            
            # 获取当前筛选条件
            search_text = self.search_edit.text().strip()
            category = self.category_combo.currentText()
            status = self.status_combo.currentText()
            
            filters = {}
            
            if search_text:
                filters["(asset_id || name || brand_spec || location)"] = search_text
            
            if category != "所有类目":
                filters["category"] = category
            
            if status != "所有状态":
                filters["maintenance_status"] = status
            
            success, msg = ImportExport.export_assets(file_path, filters)
            if success:
                QMessageBox.information(self, "成功", msg)
            else:
                QMessageBox.warning(self, "错误", msg)
    
    def change_password(self):
        """更改密码"""
        from ui.dialogs.change_password import ChangePasswordDialog
        dialog = ChangePasswordDialog(self, self.user)
        dialog.exec_()
    
    def manage_users_system(self):
        """系统用户管理（仅管理员）"""
        from ui.dialogs.system_user_management import SystemUserManagementDialog
        dialog = SystemUserManagementDialog(self, self.user)
        dialog.exec_()
    
    def logout(self):
        """退出登录"""
        self.close()
    
    def show_about(self):
        """显示关于信息"""
        QMessageBox.about(
            self, "关于资产管理系统",
            "资产管理系统 v1.0\n\n用于公司资产的全生命周期管理，\n包括资产入库、使用登记、维修记录等功能。"
        )
