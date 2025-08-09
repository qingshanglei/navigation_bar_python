from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# 延迟导入避免循环导入
def get_db():
    from flask import current_app
    return current_app.extensions['sqlalchemy']

class User:
    """用户模型"""
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.username = kwargs.get('username')
        self.password = kwargs.get('password')
        self.created_at = kwargs.get('created_at', datetime.utcnow())
    
    @staticmethod
    def create_table():
        """创建用户表"""
        db = get_db()
        with db.engine.connect() as conn:
            conn.execute(db.text('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(128) NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            '''))
            conn.commit()
    
    @staticmethod
    def query():
        """返回查询对象"""
        return UserQuery()
    
    @staticmethod
    def get(user_id):
        """根据ID获取用户"""
        db = get_db()
        with db.engine.connect() as conn:
            result = conn.execute(db.text('SELECT * FROM users WHERE id = :id'), {'id': user_id})
            row = result.fetchone()
            if row:
                # 安全地解析时间字符串
                created_at = None
                if row[3]:
                    try:
                        created_at = datetime.fromisoformat(row[3])
                    except (ValueError, TypeError):
                        # 如果解析失败，使用当前时间
                        created_at = datetime.utcnow()
                return User(
                    id=row[0],
                    username=row[1],
                    password=row[2],
                    created_at=created_at
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
        with db.engine.connect() as conn:
            if self.id:
                # 更新
                conn.execute(db.text('''
                    UPDATE users SET username = :username, password = :password 
                    WHERE id = :id
                '''), {
                    'username': self.username,
                    'password': self.password,
                    'id': self.id
                })
            else:
                # 新增
                result = conn.execute(db.text('''
                    INSERT INTO users (username, password, created_at) 
                    VALUES (:username, :password, :created_at)
                '''), {
                    'username': self.username,
                    'password': self.password,
                    'created_at': self.created_at
                })
                self.id = result.lastrowid
            conn.commit()

class UserQuery:
    """用户查询类"""
    
    def filter_by(self, **kwargs):
        """按条件过滤"""
        self.filters = kwargs
        return self
    
    def first(self):
        """获取第一个结果"""
        db = get_db()
        with db.engine.connect() as conn:
            if 'username' in self.filters:
                result = conn.execute(
                    db.text('SELECT * FROM users WHERE username = :username'), 
                    {'username': self.filters['username']}
                )
                row = result.fetchone()
                if row:
                    # 安全地解析时间字符串
                    created_at = None
                    if row[3]:
                        try:
                            created_at = datetime.fromisoformat(row[3])
                        except (ValueError, TypeError):
                            # 如果解析失败，使用当前时间
                            created_at = datetime.utcnow()
                    return User(
                        id=row[0],
                        username=row[1],
                        password=row[2],
                        created_at=created_at
                    )
        return None
    
    def __repr__(self):
        return f'<UserQuery {id(self)}>'
    
    @staticmethod
    def create_user(username, password):
        """创建新用户"""
        user = User(username=username)
        user.set_password(password)
        return user
