from datetime import datetime

# 延迟导入避免循环依赖

def get_db():
    from flask import current_app
    return current_app.extensions['sqlalchemy']


class Nav:
    """
    导航菜单模型（使用原生SQL，保持与 Category 一致的风格）
    表名：navs
    字段：id, category_id, title, url, description, icon, sort_order, is_public, created_at
    """

    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.category_id = kwargs.get('category_id')
        self.title = kwargs.get('title')
        self.url = kwargs.get('url')
        self.description = kwargs.get('description')
        self.icon = kwargs.get('icon')
        self.sort_order = kwargs.get('sort_order', 0)
        self.is_public = kwargs.get('is_public', True)
        self.created_at = kwargs.get('created_at', datetime.utcnow())

    @staticmethod
    def create_table():
        """创建导航菜单表（如不存在）"""
        db = get_db()
        with db.engine.connect() as conn:
            conn.execute(db.text('''
                CREATE TABLE IF NOT EXISTS navs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    description TEXT,
                    icon TEXT,
                    sort_order INTEGER DEFAULT 0,
                    is_public BOOLEAN DEFAULT TRUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES nav_categories(id)
                )
            '''))
            conn.commit()

    @staticmethod
    def get(nav_id: int):
        """根据ID获取导航项"""
        db = get_db()
        with db.engine.connect() as conn:
            res = conn.execute(db.text('SELECT * FROM navs WHERE id = :id'), {'id': nav_id})
            row = res.fetchone()
            if not row:
                return None
            return Nav(
                id=row[0],
                category_id=row[1],
                title=row[2],
                url=row[3],
                description=row[4],
                icon=row[5],
                sort_order=row[6],
                is_public=bool(row[7]),
                created_at=datetime.fromisoformat(row[8]) if row[8] else None
            )

    @staticmethod
    def search(filters=None, page: int = 1, size: int = 10, sort: str = 'sort_order'):
        """
        分页检索导航项
        支持过滤：is_public, keyword(匹配title/description), category_id
        返回 (list[Nav], total)
        """
        db = get_db()
        with db.engine.connect() as conn:
            sql = 'SELECT * FROM navs'
            count_sql = 'SELECT COUNT(*) FROM navs'
            params = {}
            conditions = []

            if filters:
                if 'is_public' in filters:
                    conditions.append('is_public = :is_public')
                    params['is_public'] = filters['is_public']
                if 'category_id' in filters and filters['category_id'] is not None:
                    conditions.append('category_id = :category_id')
                    params['category_id'] = filters['category_id']
                if 'keyword' in filters and filters['keyword']:
                    conditions.append('(title LIKE :kw OR description LIKE :kw)')
                    params['kw'] = f"%{filters['keyword']}%"

            if conditions:
                where_clause = ' WHERE ' + ' AND '.join(conditions)
                sql += where_clause
                count_sql += where_clause

            total = conn.execute(db.text(count_sql), params).fetchone()[0]

            if sort == 'created_at':
                sql += ' ORDER BY created_at DESC'
            else:
                sql += ' ORDER BY sort_order ASC, created_at ASC'

            if page and size:
                offset = (page - 1) * size
                sql += f' LIMIT {size} OFFSET {offset}'

            rows = conn.execute(db.text(sql), params)
            items = []
            for row in rows:
                items.append(Nav(
                    id=row[0],
                    category_id=row[1],
                    title=row[2],
                    url=row[3],
                    description=row[4],
                    icon=row[5],
                    sort_order=row[6],
                    is_public=bool(row[7]),
                    created_at=datetime.fromisoformat(row[8]) if row[8] else None
                ))
            return items, total

    def to_dict(self):
        return {
            'id': self.id,
            'category_id': self.category_id,
            'title': self.title,
            'url': self.url,
            'description': self.description,
            'icon': self.icon,
            'sort_order': self.sort_order,
            'is_public': self.is_public,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

    def save(self):
        """新增或更新"""
        db = get_db()
        with db.engine.connect() as conn:
            if self.id:
                conn.execute(db.text('''
                    UPDATE navs
                    SET category_id = :category_id,
                        title = :title,
                        url = :url,
                        description = :description,
                        icon = :icon,
                        sort_order = :sort_order,
                        is_public = :is_public
                    WHERE id = :id
                '''), {
                    'id': self.id,
                    'category_id': self.category_id,
                    'title': self.title,
                    'url': self.url,
                    'description': self.description,
                    'icon': self.icon,
                    'sort_order': self.sort_order,
                    'is_public': self.is_public,
                })
            else:
                result = conn.execute(db.text('''
                    INSERT INTO navs (category_id, title, url, description, icon, sort_order, is_public, created_at)
                    VALUES (:category_id, :title, :url, :description, :icon, :sort_order, :is_public, :created_at)
                '''), {
                    'category_id': self.category_id,
                    'title': self.title,
                    'url': self.url,
                    'description': self.description,
                    'icon': self.icon,
                    'sort_order': self.sort_order,
                    'is_public': self.is_public,
                    'created_at': self.created_at
                })
                self.id = result.lastrowid
            conn.commit()
            return self

    def delete(self):
        if not self.id:
            return False
        db = get_db()
        with db.engine.connect() as conn:
            conn.execute(db.text('DELETE FROM navs WHERE id = :id'), {'id': self.id})
            conn.commit()
            return True