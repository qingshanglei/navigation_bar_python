from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# 延迟导入避免循环导入
def get_db():
    from app import db
    return db

class User:
    """用户模型 - 使用SQLAlchemy"""
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.username = kwargs.get('username')
        self.password = kwargs.get('password')
        self.created_at = kwargs.get('created_at', datetime.utcnow())
    
    @staticmethod
    def create_table():
        """创建用户表"""
        db = get_db()
        db.execute_sql('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(128) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    @staticmethod
    def query_by_username(username):
        """根据用户名查询用户"""
        db = get_db()
        result = db.execute_sql('SELECT * FROM users WHERE username = ?', (username,))
        row = result.fetchone()
        if row:
            return User(
                id=row[0],
                username=row[1],
                password=row[2],
                created_at=datetime.fromisoformat(row[3]) if row[3] else None
            )
        return None
    
    @staticmethod
    def query_by_id(user_id):
        """根据ID查询用户"""
        db = get_db()
        result = db.execute_sql('SELECT * FROM users WHERE id = ?', (user_id,))
        row = result.fetchone()
        if row:
            return User(
                id=row[0],
                username=row[1],
                password=row[2],
                created_at=datetime.fromisoformat(row[3]) if row[3] else None
            )
        return None
    
    def set_password(self, password):
        """设置密码哈希"""
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password, password)
    
    def to_dict(self):
        """用户信息序列化"""
        return {
            'id': self.id,
            'username': self.username,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
    
    def save(self):
        """保存用户到数据库"""
        db = get_db()
        if self.id:
            # 更新
            db.execute_sql(
                'UPDATE users SET username=?, password=? WHERE id=?',
                (self.username, self.password, self.id)
            )
        else:
            # 新增
            cursor = db.execute_sql(
                'INSERT INTO users (username, password, created_at) VALUES (?, ?, ?)',
                (self.username, self.password, self.created_at)
            )
            self.id = cursor.lastrowid
        db.commit()
    
    @classmethod
    def query_by_username(cls, username):
        """根据用户名查询用户"""
        db = get_db()
        cursor = db.execute_sql(
            'SELECT id, username, password, created_at FROM users WHERE username=?',
            (username,)
        )
        row = cursor.fetchone()
        if row:
            return cls(
                id=row[0],
                username=row[1],
                password=row[2],
                created_at=datetime.fromisoformat(row[3]) if row[3] else None
            )
        return None
    
    @classmethod
    def query_by_id(cls, user_id):
        """根据ID查询用户"""
        db = get_db()
        cursor = db.execute_sql(
            'SELECT id, username, password, created_at FROM users WHERE id=?',
            (user_id,)
        )
        row = cursor.fetchone()
        if row:
            return cls(
                id=row[0],
                username=row[1],
                password=row[2],
                created_at=datetime.fromisoformat(row[3]) if row[3] else None
            )
        return None
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    @staticmethod
    def create_user(username, password):
        """创建新用户"""
        user = User(username=username)
        user.set_password(password)
        return user