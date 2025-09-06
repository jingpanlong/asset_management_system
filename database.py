import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self, db_name="assets.db"):
        # 确保data目录存在
        if not os.path.exists("data"):
            os.makedirs("data")
        
        self.db_path = os.path.join("data", db_name)
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """连接到数据库"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            # 启用外键约束
            self.cursor.execute("PRAGMA foreign_keys = ON")
            return True
        except Exception as e:
            print(f"数据库连接错误: {e}")
            return False
    
    def create_tables(self):
        """创建数据库表"""
        # 用户表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',  -- admin 或 user
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 资产表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_id TEXT UNIQUE NOT NULL,  -- 资产编号
            name TEXT NOT NULL,  -- 设备名称
            quantity INTEGER NOT NULL DEFAULT 1,  -- 数量
            category TEXT NOT NULL,  -- 类目
            brand_spec TEXT,  -- 品牌规格
            purchase_date DATE,  -- 入库时间
            image_path TEXT,  -- 资产图片路径
            location TEXT,  -- 设备位置
            notes TEXT,  -- 备注
            maintenance_status TEXT DEFAULT '正常',  -- 维修状态
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
        ''')
        
        # 资产使用人表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS asset_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_id INTEGER NOT NULL,
            user_name TEXT NOT NULL,  -- 使用人姓名
            start_date DATE NOT NULL,  -- 开始使用时间
            end_date DATE,  -- 结束使用时间
            FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE
        )
        ''')
        
        # 维修记录表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS repair_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_id INTEGER NOT NULL,
            repair_date DATE NOT NULL,  -- 维修时间
            fault_cause TEXT,  -- 故障原因
            repair_result TEXT,  -- 维修结果
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE,
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
        ''')
        
        # 添加默认管理员用户
        self.cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        if not self.cursor.fetchone():
            self.cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                ('admin', 'admin123', 'admin')
            )
        
        self.conn.commit()
    
    def execute(self, query, params=()):
        """执行SQL语句"""
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"SQL执行错误: {e}")
            self.conn.rollback()
            return False
    
    def fetchall(self, query, params=()):
        """获取所有查询结果"""
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"查询错误: {e}")
            return []
    
    def fetchone(self, query, params=()):
        """获取单个查询结果"""
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchone()
        except Exception as e:
            print(f"查询错误: {e}")
            return None
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
