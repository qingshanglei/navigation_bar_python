from app import db

class Navigation(db.Model):
    __tablename__ = 'navigations'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    description = db.Column(db.String(500))
    icon = db.Column(db.String(100))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    click_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    # 关联关系
    category = db.relationship('Category', backref=db.backref('navigations', lazy=True))