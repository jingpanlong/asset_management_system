from database import Database

class User:
    def __init__(self, user_id=None, username=None, password=None, role=None):
        self.id = user_id
        self.username = username
        self.password = password
        self.role = role
        self.db = Database()
    
    def login(self, username, password):
        """用户登录验证"""
        result = self.db.fetchone(
            "SELECT id, username, role FROM users WHERE username = ? AND password = ?",
            (username, password)
        )
        
        if result:
            self.id, self.username, self.role = result
            return True
        return False
    
    def register(self, username, password, role='user'):
        """用户注册"""
        # 检查用户名是否已存在
        if self.db.fetchone("SELECT id FROM users WHERE username = ?", (username,)):
            return False, "用户名已存在"
        
        # 创建新用户
        success = self.db.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, password, role)
        )
        
        if success:
            user_id = self.db.cursor.lastrowid
            self.id = user_id
            self.username = username
            self.role = role
            return True, "注册成功"
        return False, "注册失败"
    
    def get_all_users(self):
        """获取所有用户"""
        if self.role != 'admin':
            return []
        
        return self.db.fetchall("SELECT id, username, role, created_at FROM users")
    
    def update_user_role(self, user_id, new_role):
        """更新用户角色"""
        if self.role != 'admin':
            return False
        
        return self.db.execute(
            "UPDATE users SET role = ? WHERE id = ?",
            (new_role, user_id)
        )
    
    def delete_user(self, user_id):
        """删除用户"""
        if self.role != 'admin':
            return False
        
        # 不能删除自己
        if self.id == user_id:
            return False
        
        return self.db.execute("DELETE FROM users WHERE id = ?", (user_id,))
    
    def change_password(self, old_password, new_password):
        """修改密码"""
        # 验证旧密码
        result = self.db.fetchone(
            "SELECT id FROM users WHERE id = ? AND password = ?",
            (self.id, old_password)
        )
        
        if not result:
            return False, "旧密码不正确"
        
        # 更新密码
        success = self.db.execute(
            "UPDATE users SET password = ? WHERE id = ?",
            (new_password, self.id)
        )
        
        if success:
            self.password = new_password
            return True, "密码修改成功"
        return False, "密码修改失败"
