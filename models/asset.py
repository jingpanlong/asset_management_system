from database import Database
from datetime import datetime
import os

class Asset:
    def __init__(self, asset_id=None):
        self.id = None  # 数据库ID
        self.asset_id = asset_id  # 资产编号
        self.name = ""  # 设备名称
        self.quantity = 1  # 数量
        self.category = ""  # 类目
        self.brand_spec = ""  # 品牌规格
        self.purchase_date = None  # 入库时间
        self.image_path = ""  # 资产图片路径
        self.location = ""  # 设备位置
        self.notes = ""  # 备注
        self.maintenance_status = "正常"  # 维修状态
        
        self.users = []  # 使用人列表
        self.repair_records = []  # 维修记录列表
        
        self.db = Database()
        
        # 如果提供了资产编号，加载资产信息
        if asset_id:
            self.load_by_asset_id(asset_id)
    
    def load_by_asset_id(self, asset_id):
        """通过资产编号加载资产信息"""
        asset_data = self.db.fetchone(
            "SELECT * FROM assets WHERE asset_id = ?",
            (asset_id,)
        )
        
        if asset_data:
            self.id = asset_data[0]
            self.asset_id = asset_data[1]
            self.name = asset_data[2]
            self.quantity = asset_data[3]
            self.category = asset_data[4]
            self.brand_spec = asset_data[5]
            self.purchase_date = asset_data[6]
            self.image_path = asset_data[7]
            self.location = asset_data[8]
            self.notes = asset_data[9]
            self.maintenance_status = asset_data[10]
            
            # 加载使用人信息
            self.load_users()
            # 加载维修记录
            self.load_repair_records()
            return True
        return False
    
    def load_by_id(self, asset_id):
        """通过数据库ID加载资产信息"""
        asset_data = self.db.fetchone(
            "SELECT * FROM assets WHERE id = ?",
            (asset_id,)
        )
        
        if asset_data:
            self.id = asset_data[0]
            self.asset_id = asset_data[1]
            self.name = asset_data[2]
            self.quantity = asset_data[3]
            self.category = asset_data[4]
            self.brand_spec = asset_data[5]
            self.purchase_date = asset_data[6]
            self.image_path = asset_data[7]
            self.location = asset_data[8]
            self.notes = asset_data[9]
            self.maintenance_status = asset_data[10]
            
            # 加载使用人信息
            self.load_users()
            # 加载维修记录
            self.load_repair_records()
            return True
        return False
    
    def load_users(self):
        """加载资产使用人信息"""
        if self.id:
            self.users = self.db.fetchall(
                "SELECT id, user_name, start_date, end_date FROM asset_users WHERE asset_id = ?",
                (self.id,)
            )
    
    def load_repair_records(self):
        """加载资产维修记录"""
        if self.id:
            self.repair_records = self.db.fetchall(
                """SELECT id, repair_date, fault_cause, repair_result, created_at 
                   FROM repair_records WHERE asset_id = ? ORDER BY repair_date DESC""",
                (self.id,)
            )
    
    def save(self, user_id):
        """保存资产信息"""
        if self.id:
            # 更新现有资产
            success = self.db.execute("""
                UPDATE assets SET 
                    asset_id = ?, name = ?, quantity = ?, category = ?, 
                    brand_spec = ?, purchase_date = ?, image_path = ?, 
                    location = ?, notes = ?, maintenance_status = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                self.asset_id, self.name, self.quantity, self.category,
                self.brand_spec, self.purchase_date, self.image_path,
                self.location, self.notes, self.maintenance_status, self.id
            ))
            return success
        else:
            # 检查资产编号是否已存在
            if self.db.fetchone("SELECT id FROM assets WHERE asset_id = ?", (self.asset_id,)):
                return False, "资产编号已存在"
            
            # 创建新资产
            success = self.db.execute("""
                INSERT INTO assets (
                    asset_id, name, quantity, category, brand_spec, 
                    purchase_date, image_path, location, notes, 
                    maintenance_status, created_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.asset_id, self.name, self.quantity, self.category,
                self.brand_spec, self.purchase_date, self.image_path,
                self.location, self.notes, self.maintenance_status, user_id
            ))
            
            if success:
                self.id = self.db.cursor.lastrowid
                return True, "资产创建成功"
            return False, "资产创建失败"
    
    def add_user(self, user_name, start_date, end_date=None):
        """添加资产使用人"""
        if self.id:
            return self.db.execute("""
                INSERT INTO asset_users (asset_id, user_name, start_date, end_date)
                VALUES (?, ?, ?, ?)
            """, (self.id, user_name, start_date, end_date))
        return False
    
    def update_user(self, user_record_id, end_date):
        """更新使用人记录（主要是结束日期）"""
        return self.db.execute(
            "UPDATE asset_users SET end_date = ? WHERE id = ?",
            (end_date, user_record_id)
        )
    
    def add_repair_record(self, repair_date, fault_cause, repair_result, user_id):
        """添加维修记录"""
        if self.id:
            success = self.db.execute("""
                INSERT INTO repair_records (
                    asset_id, repair_date, fault_cause, repair_result, created_by
                ) VALUES (?, ?, ?, ?, ?)
            """, (self.id, repair_date, fault_cause, repair_result, user_id))
            
            # 更新资产维修状态
            if repair_result and "已修复" in repair_result:
                self.maintenance_status = "正常"
            else:
                self.maintenance_status = "维修中"
                
            self.db.execute(
                "UPDATE assets SET maintenance_status = ? WHERE id = ?",
                (self.maintenance_status, self.id)
            )
            
            return success
        return False
    
    def delete(self):
        """删除资产"""
        if self.id:
            return self.db.execute("DELETE FROM assets WHERE id = ?", (self.id,))
        return False
    
    @staticmethod
    def get_all_assets(filters=None):
        """获取所有资产，支持筛选"""
        db = Database()
        query = "SELECT * FROM assets"
        params = []
        
        if filters and isinstance(filters, dict):
            conditions = []
            for key, value in filters.items():
                if value:
                    conditions.append(f"{key} LIKE ?")
                    params.append(f"%{value}%")
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY asset_id"
        return db.fetchall(query, params)
    
    @staticmethod
    def get_categories():
        """获取所有资产类目"""
        return [
            "笔记本电脑", "插线板", "打印机及设备", "打印云盒", "电脑显示屏",
            "电脑主机", "读卡器", "翻页笔", "键盘", "麦克风", "内存条",
            "拍摄用品", "其他", "手机", "鼠标", "投影", "网络", "相机",
            "遥控器", "音响", "硬盘", "转接线"
        ]
