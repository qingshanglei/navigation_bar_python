from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.category import Category
import re

# 延迟导入模型避免循环导入
def get_user_model():
    from models.user_simple import User
    return User

categories_bp = Blueprint('categories', __name__)

# 用于存储已注销的token（简单实现，生产环境建议使用Redis）
blacklisted_tokens = set()

def success_response(data=None, msg="操作成功", code=1):
    """成功响应格式"""
    return jsonify({
        'code': code,
        'msg': msg,
        'data': data
    })

def error_response(msg="操作失败", code=0):
    """错误响应格式"""
    return jsonify({
        'code': code,
        'msg': msg,
        'data': None
    })

def validate_token():
    """验证token是否有效"""
    jti = get_jwt()['jti']
    if jti in blacklisted_tokens:
        return False, "Token已失效，请重新登录"
    
    User = get_user_model()
    user = User.get(get_jwt_identity())
    if not user:
        return False, "用户不存在"
    
    return True, user

@categories_bp.route('/', methods=['GET'])
@jwt_required()
def get_categories():
    """
    获取分类列表
    支持查询参数：
    - page: 页码，默认1
    - size: 每页数量，默认20
    - level: 分类层级筛选（1,2,3）
    - is_public: 公开状态筛选（1=公开，0=私有）
    - parent_id: 父分类ID筛选
    - sort: 排序字段（sort_order,created_at）
    """
    try:
        # 验证token
        is_valid, result = validate_token()
        if not is_valid:
            return error_response(result), 401
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        size = request.args.get('size', 20, type=int)
        parent_id = request.args.get('parent_id')
        level = request.args.get('level', type=int)
        is_public = request.args.get('is_public', type=int)
        sort = request.args.get('sort', 'sort_order')
        
        # 构建过滤条件
        filters = {}
        if parent_id is not None:
            if parent_id.lower() == 'null' or parent_id == '':
                filters['parent_id'] = None
            else:
                filters['parent_id'] = int(parent_id)
        if level is not None:
            filters['level'] = level
        if is_public is not None:
            filters['is_public'] = is_public
        
        # 获取所有符合条件的分类（用于构建树结构）
        all_categories, total = Category.get_all(filters, None, None, sort)
        
        # 构建树结构
        category_dict = {cat.id: cat for cat in all_categories}
        tree_data = []
        
        # 找出根分类并构建树
        for category in all_categories:
            if category.parent_id is None or category.parent_id not in category_dict:
                # 为根分类添加子分类
                category.children = []
                tree_data.append(category)
        
        # 为每个分类添加其子分类
        for category in all_categories:
            if category.parent_id is not None and category.parent_id in category_dict:
                parent = category_dict[category.parent_id]
                if not hasattr(parent, 'children'):
                    parent.children = []
                parent.children.append(category)
        
        # 递归设置所有分类的children属性
        def set_children(cat):
            if not hasattr(cat, 'children'):
                cat.children = []
            for child in cat.children:
                set_children(child)
        
        for cat in tree_data:
            set_children(cat)
        
        # 构建分页信息
        pages = (total + size - 1) // size if total > 0 else 0
        
        # 构建响应数据（按照新的接口规范）
        data = [{
            'list': [cat.to_dict(include_children=True) for cat in tree_data],
            'pagination': {
                'page': page,
                'size': size,
                'total': total,
                'pages': pages
            }
        }]
        
        return success_response(data, "获取分类树成功")
        
    except Exception as e:
        return error_response(f"获取分类列表失败: {str(e)}"), 500

@categories_bp.route('/<int:category_id>', methods=['GET'])
@jwt_required()
def get_category(category_id):
    """获取单个分类详情"""
    try:
        # 验证token
        is_valid, result = validate_token()
        if not is_valid:
            return error_response(result), 401
        
        # 获取分类
        category = Category.get(category_id)
        if not category:
            return error_response("分类不存在"), 404
        
        return success_response(category.to_dict(), "获取分类详情成功")
        
    except Exception as e:
        return error_response(f"获取分类详情失败: {str(e)}"), 500

@categories_bp.route('/<int:category_id>/children', methods=['GET'])
@jwt_required()
def get_category_children(category_id):
    """获取子分类列表"""
    try:
        # 验证token
        is_valid, result = validate_token()
        if not is_valid:
            return error_response(result), 401
        
        # 检查父分类是否存在
        parent = Category.get(category_id)
        if not parent:
            return error_response("父分类不存在"), 404
        
        # 获取子分类
        children = Category.get_children(category_id)
        data = [child.to_dict() for child in children]
        
        return success_response(data, "获取子分类列表成功")
        
    except Exception as e:
        return error_response(f"获取子分类列表失败: {str(e)}"), 500

@categories_bp.route('/', methods=['POST'])
@jwt_required()
def create_category():
    """创建新分类"""
    try:
        # 验证token
        is_valid, result = validate_token()
        if not is_valid:
            return error_response(result), 401
        
        # 获取请求数据
        data = request.get_json()
        if not data:
            return error_response("请求数据不能为空"), 400
        
        # 验证必填字段
        name = data.get('name', '').strip()
        if not name:
            return error_response("分类名称不能为空"), 400
        
        if len(name) > 50:
            return error_response("分类名称不能超过50个字符"), 400
        
        # 验证可选字段
        parent_id = data.get('parent_id')
        description = data.get('description', '').strip()
        sort_order = data.get('sort_order', 0)
        is_public = data.get('is_public', True)
        
        # 验证描述长度
        if description and len(description) > 200:
            return error_response("分类描述不能超过200个字符"), 400
        
        # 验证排序值
        if not isinstance(sort_order, int) or sort_order < 0:
            return error_response("排序值必须为非负整数"), 400
        
        # 计算分类层级
        level = 1
        if parent_id:
            parent = Category.get(parent_id)
            if not parent:
                return error_response("父分类不存在"), 400
            level = parent.level + 1
            
            # 限制层级深度
            if level > 5:
                return error_response("分类层级不能超过5级"), 400
        
        # 检查同级分类名称是否重复
        existing = Category.query().filter_by(parent_id=parent_id, name=name).first()
        if existing:
            return error_response("同级分类中已存在相同名称的分类"), 400
        
        # 创建分类
        category = Category(
            parent_id=parent_id,
            name=name,
            description=description,
            sort_order=sort_order,
            level=level,
            is_public=is_public
        )
        category.save()
        
        return success_response(category.to_dict(), "创建分类成功"), 201
        
    except Exception as e:
        return error_response(f"创建分类失败: {str(e)}"), 500

@categories_bp.route('/<int:category_id>', methods=['PUT'])
@jwt_required()
def update_category(category_id):
    """更新分类信息"""
    try:
        # 验证token
        is_valid, result = validate_token()
        if not is_valid:
            return error_response(result), 401
        
        # 获取分类
        category = Category.get(category_id)
        if not category:
            return error_response("分类不存在"), 404
        
        # 获取请求数据
        data = request.get_json()
        if not data:
            return error_response("请求数据不能为空"), 400
        
        # 更新字段
        if 'name' in data:
            name = data['name'].strip()
            if not name:
                return error_response("分类名称不能为空"), 400
            if len(name) > 50:
                return error_response("分类名称不能超过50个字符"), 400
            
            # 检查同级分类名称是否重复（排除自己）
            existing = Category.query().filter_by(parent_id=category.parent_id, name=name).first()
            if existing and existing.id != category.id:
                return error_response("同级分类中已存在相同名称的分类"), 400
            
            category.name = name
        
        if 'description' in data:
            description = data['description'].strip() if data['description'] else ''
            if len(description) > 200:
                return error_response("分类描述不能超过200个字符"), 400
            category.description = description
        
        if 'sort_order' in data:
            sort_order = data['sort_order']
            if not isinstance(sort_order, int) or sort_order < 0:
                return error_response("排序值必须为非负整数"), 400
            category.sort_order = sort_order
        
        if 'is_public' in data:
            category.is_public = bool(data['is_public'])
        
        # 处理父分类变更
        if 'parent_id' in data:
            new_parent_id = data['parent_id']
            if new_parent_id != category.parent_id:
                # 验证新父分类
                if new_parent_id:
                    new_parent = Category.get(new_parent_id)
                    if not new_parent:
                        return error_response("新父分类不存在"), 400
                    
                    # 检查是否会形成循环引用
                    if new_parent_id == category.id:
                        return error_response("不能将分类设置为自己的父分类"), 400
                    
                    # 检查新父分类是否是当前分类的子分类
                    def is_descendant(parent, child_id):
                        children = Category.get_children(parent.id)
                        for child in children:
                            if child.id == child_id:
                                return True
                            if is_descendant(child, child_id):
                                return True
                        return False
                    
                    if is_descendant(category, new_parent_id):
                        return error_response("不能将分类移动到其子分类下"), 400
                    
                    # 更新层级
                    category.level = new_parent.level + 1
                    if category.level > 5:
                        return error_response("分类层级不能超过5级"), 400
                else:
                    # 移动到根级
                    category.level = 1
                
                category.parent_id = new_parent_id
        
        # 保存更新
        category.save()
        
        return success_response(category.to_dict(), "更新分类成功")
        
    except Exception as e:
        return error_response(f"更新分类失败: {str(e)}"), 500

@categories_bp.route('/<int:category_id>', methods=['DELETE'])
@jwt_required()
def delete_category(category_id):
    """删除分类"""
    try:
        # 验证token
        is_valid, result = validate_token()
        if not is_valid:
            return error_response(result), 401
        
        # 获取查询参数
        cascade = request.args.get('cascade', 'false').lower() == 'true'
        
        # 获取分类
        category = Category.get(category_id)
        if not category:
            return error_response("分类不存在"), 404
        
        # 检查子分类
        children = Category.get_children(category_id)
        if children and not cascade:
            return error_response("分类下存在子分类，无法删除", 0), 400
        
        # 删除分类
        try:
            if cascade and children:
                # 级联删除子分类
                for child in children:
                    child.delete()
            
            category.delete()
            return success_response(None, "分类删除成功")
        except ValueError as e:
            return error_response(str(e)), 400
        
    except Exception as e:
        return error_response(f"删除分类失败: {str(e)}"), 500

@categories_bp.route('/categoriesRoot', methods=['GET'])
@jwt_required()
def get_root_categories():
    """
    获取所有顶级分类列表
    返回所有parent_id为null的分类
    """
    try:
        # 验证token
        is_valid, result = validate_token()
        if not is_valid:
            return error_response(result), 401
        
        # 获取所有顶级分类（parent_id为null）
        root_categories, _ = Category.get_all({'parent_id': None}, None, None, 'sort_order')
        
        # 转换为字典格式
        data = [cat.to_dict() for cat in root_categories]
        
        return success_response(data, "获取顶级分类成功")
        
    except Exception as e:
        return error_response(f"获取顶级分类失败: {str(e)}"), 500

# 公共接口（不需要认证）
@categories_bp.route('/public', methods=['GET'])
def get_public_categories():
    """获取公开分类列表"""
    try:
        # 获取查询参数
        tree = request.args.get('tree', 'false').lower() == 'true'
        
        if tree:
            # 返回公开分类的树结构
            all_categories, _ = Category.get_all({'is_public': True})
            category_dict = {cat.id: cat for cat in all_categories}
            
            tree_data = []
            for category in all_categories:
                if category.parent_id is None:
                    tree_data.append(category)
                else:
                    parent = category_dict.get(category.parent_id)
                    if parent:
                        if not hasattr(parent, 'children'):
                            parent.children = []
                        parent.children.append(category)
            
            data = [cat.to_dict(include_children=True) for cat in tree_data]
        else:
            # 返回公开分类列表
            categories, _ = Category.get_all({'is_public': True})
            data = [cat.to_dict() for cat in categories]
        
        return success_response(data, "获取公开分类成功")
        
    except Exception as e:
        return error_response(f"获取公开分类失败: {str(e)}"), 500
