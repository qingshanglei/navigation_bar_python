from datetime import datetime

# 延迟导入避免循环导入
def get_db():
    from flask import current_app
    return current_app.extensions['sqlalchemy']

class Category:
    """
    导航分类模型
    支持层级结构的分类管理
    """
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.parent_id = kwargs.get('parent_id')
        self.name = kwargs.get('name')
        self.description = kwargs.get('description')
        self.sort_order = kwargs.get('sort_order', 0)
        self.level = kwargs.get('level', 1)
        self.is_public = kwargs.get('is_public', True)
        self.created_at = kwargs.get('created_at', datetime.utcnow())
    
    @staticmethod
    def create_table():
        """创建导航分类表"""
        db = get_db()
        with db.engine.connect() as conn:
            conn.execute(db.text('''
                CREATE TABLE IF NOT EXISTS nav_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    parent_id INTEGER DEFAULT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    sort_order INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 1,
                    is_public BOOLEAN DEFAULT TRUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (parent_id) REFERENCES nav_categories(id)
                )
            '''))
            conn.commit()
    
    @staticmethod
    def query():
        """返回查询对象"""
        return CategoryQuery()
    
    @staticmethod
    def get(category_id):
        """根据ID获取分类"""
        db = get_db()
        with db.engine.connect() as conn:
            result = conn.execute(
                db.text('SELECT * FROM nav_categories WHERE id = :id'), 
                {'id': category_id}
            )
            row = result.fetchone()
            if row:
                return Category(
                    id=row[0],
                    parent_id=row[1],
                    name=row[2],
                    description=row[3],
                    sort_order=row[4],
                    level=row[5],
                    is_public=bool(row[6]),
                    created_at=datetime.fromisoformat(row[7]) if row[7] else None
                )
        return None
    
    @staticmethod
    def get_all(filters=None, page=None, size=None, sort='sort_order'):
        """获取所有分类，支持分页和排序"""
        db = get_db()
        with db.engine.connect() as conn:
            # 构建基础查询
            sql = 'SELECT * FROM nav_categories'
            count_sql = 'SELECT COUNT(*) FROM nav_categories'
            params = {}
            
            # 构建过滤条件
            if filters:
                conditions = []
                if 'is_public' in filters:
                    conditions.append('is_public = :is_public')
                    params['is_public'] = filters['is_public']
                if 'parent_id' in filters:
                    if filters['parent_id'] is None:
                        conditions.append('parent_id IS NULL')
                    else:
                        conditions.append('parent_id = :parent_id')
                        params['parent_id'] = filters['parent_id']
                if 'level' in filters:
                    conditions.append('level = :level')
                    params['level'] = filters['level']
                
                if conditions:
                    where_clause = ' WHERE ' + ' AND '.join(conditions)
                    sql += where_clause
                    count_sql += where_clause
            
            # 获取总数
            total_result = conn.execute(db.text(count_sql), params)
            total = total_result.fetchone()[0]
            
            # 构建排序
            if sort == 'created_at':
                sql += ' ORDER BY created_at DESC'
            else:
                sql += ' ORDER BY sort_order ASC, created_at ASC'
            
            # 添加分页
            if page is not None and size is not None:
                offset = (page - 1) * size
                sql += f' LIMIT {size} OFFSET {offset}'
            
            result = conn.execute(db.text(sql), params)
            categories = []
            for row in result:
                categories.append(Category(
                    id=row[0],
                    parent_id=row[1],
                    name=row[2],
                    description=row[3],
                    sort_order=row[4],
                    level=row[5],
                    is_public=bool(row[6]),
                    created_at=datetime.fromisoformat(row[7]) if row[7] else None
                ))
            
            return categories, total
    
    @staticmethod
    def get_children(parent_id):
        """获取子分类"""
        children, _ = Category.get_all({'parent_id': parent_id})
        return children
    
    @staticmethod
    def get_tree():
        """获取分类树结构"""
        # 获取所有分类
        all_categories, _ = Category.get_all()
        
        # 构建分类字典
        category_dict = {cat.id: cat for cat in all_categories}
        
        # 构建树结构
        tree = []
        for category in all_categories:
            if category.parent_id is None:
                # 根分类
                tree.append(category)
            else:
                # 子分类，添加到父分类的children中
                parent = category_dict.get(category.parent_id)
                if parent:
                    if not hasattr(parent, 'children'):
                        parent.children = []
                    parent.children.append(category)
        
        return tree
    
    def to_dict(self, include_children=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'parent_id': self.parent_id,
            'name': self.name,
            'description': self.description,
            'sort_order': self.sort_order,
            'level': self.level,
            'is_public': self.is_public,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
        
        if include_children:
            if hasattr(self, 'children'):
                data['children'] = [child.to_dict(include_children=True) for child in self.children]
            else:
                data['children'] = []
        
        return data
    
    def save(self):
        """保存分类到数据库"""
        db = get_db()
        with db.engine.connect() as conn:
            if self.id:
                # 更新
                conn.execute(db.text('''
                    UPDATE nav_categories 
                    SET name = :name, description = :description, 
                        sort_order = :sort_order, level = :level, 
                        is_public = :is_public, parent_id = :parent_id
                    WHERE id = :id
                '''), {
                    'id': self.id,
                    'name': self.name,
                    'description': self.description,
                    'sort_order': self.sort_order,
                    'level': self.level,
                    'is_public': self.is_public,
                    'parent_id': self.parent_id
                })
            else:
                # 新增
                result = conn.execute(db.text('''
                    INSERT INTO nav_categories (parent_id, name, description, sort_order, level, is_public, created_at) 
                    VALUES (:parent_id, :name, :description, :sort_order, :level, :is_public, :created_at)
                '''), {
                    'parent_id': self.parent_id,
                    'name': self.name,
                    'description': self.description,
                    'sort_order': self.sort_order,
                    'level': self.level,
                    'is_public': self.is_public,
                    'created_at': self.created_at
                })
                self.id = result.lastrowid
            conn.commit()
    
    def delete(self):
        """删除分类"""
        if not self.id:
            return False
        
        db = get_db()
        with db.engine.connect() as conn:
            # 检查是否有子分类
            children = conn.execute(
                db.text('SELECT COUNT(*) FROM nav_categories WHERE parent_id = :id'),
                {'id': self.id}
            ).fetchone()[0]
            
            if children > 0:
                raise ValueError('不能删除有子分类的分类')
            
            # 删除分类
            conn.execute(
                db.text('DELETE FROM nav_categories WHERE id = :id'),
                {'id': self.id}
            )
            conn.commit()
            return True
    
    def __repr__(self):
        return f'<Category {self.name}>'

class CategoryQuery:
    """分类查询类"""
    
    def __init__(self):
        self.filters = {}
    
    def filter_by(self, **kwargs):
        """按条件过滤"""
        self.filters.update(kwargs)
        return self
    
    def all(self):
        """获取所有结果"""
        categories, _ = Category.get_all(self.filters)
        return categories
    
    def first(self):
        """获取第一个结果"""
        results = self.all()
        return results[0] if results else None