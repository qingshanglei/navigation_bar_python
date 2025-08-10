from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from models.category import Category
import re
import json

from utils.responses import success_response, error_response
from utils.auth import validate_token

categories_bp = Blueprint('categories', __name__)

# 统一响应与鉴权由 utils 提供

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
        
        return success_response(data, "success")
        
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
        
        return success_response(category.to_dict(), "success")
        
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
        
        return success_response(data, "success")
        
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
        
        # 获取原始请求数据并解析为JSON，避免 get_json 触发 BadRequest
        raw_text = request.get_data(as_text=True)
        print("========创建新分类raw========")
        print(raw_text)
        try:
            data = json.loads(raw_text) if raw_text else None
        except Exception:
            return error_response("请求数据不是有效的JSON"), 400

        if data is None:
            return error_response("请求数据不能为空"), 400
        
        # 调试：打印接收到的数据
        print(f"接收到的创建分类数据: {data}")
        
        # 验证必填字段
        name = data.get('name', '').strip()
        if not name:
            return error_response("分类名称不能为空"), 400
        
        if len(name) > 50:
            return error_response("分类名称不能超过50个字符"), 400
        
        # 验证可选字段
        parent_id = data.get('parent_id')
        description = data.get('description', '').strip() if data.get('description') else ''
        sort_order = data.get('sort_order', 0)
        is_public_raw = data.get('is_public', 1)
        
        # 处理 is_public 字段（支持数字和布尔值）
        if isinstance(is_public_raw, bool):
            is_public = is_public_raw
        elif isinstance(is_public_raw, (int, float)):
            is_public = bool(int(is_public_raw))
        else:
            is_public = True  # 默认公开
        
        # 验证描述长度
        if description and len(description) > 200:
            return error_response("分类描述不能超过200个字符"), 400
        
        # 验证排序值
        try:
            sort_order = int(sort_order)
            if sort_order < 0:
                return error_response("排序值必须为非负整数"), 400
        except (ValueError, TypeError):
            return error_response("排序值必须为非负整数"), 400
        
        # 计算分类层级
        level = 1
        if parent_id:
            try:
                parent_id = int(parent_id)
                parent = Category.get(parent_id)
                if not parent:
                    return error_response("父分类不存在"), 400
                level = parent.level + 1
                
                # 限制层级深度
                if level > 5:
                    return error_response("分类层级不能超过5级"), 400
            except (ValueError, TypeError):
                return error_response("父分类ID格式错误"), 400
        else:
            parent_id = None  # 确保顶级分类的 parent_id 为 None
        
        # 按需放开同级同名：不进行同级重名校验
        # 注意：数据库未设置唯一约束，此变更将允许同一父分类下出现同名分类

        # 创建分类
        print(f"准备创建分类: name={name}, parent_id={parent_id}, description={description}, sort_order={sort_order}, level={level}, is_public={is_public}")
        
        category = Category(
            parent_id=parent_id,
            name=name,
            description=description,
            sort_order=sort_order,
            level=level,
            is_public=is_public
        )
        category.save()
        
        print(f"分类创建成功: {category.to_dict()}")
        return success_response(category.to_dict(), "success"), 201
        
    except Exception as e:
        print(f"创建分类异常: {str(e)}")
        import traceback
        traceback.print_exc()
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
        
        # 获取原始请求数据并解析为JSON，避免 get_json 触发 BadRequest
        raw_text = request.get_data(as_text=True)
        print("========更新分类raw========")
        print(raw_text)
        try:
            data = json.loads(raw_text) if raw_text else None
        except Exception:
            return error_response("请求数据不是有效的JSON"), 400

        if data is None:
            return error_response("请求数据不能为空"), 400
        
        # 更新字段
        if 'name' in data:
            name = data['name'].strip()
            if not name:
                return error_response("分类名称不能为空"), 400
            if len(name) > 50:
                return error_response("分类名称不能超过50个字符"), 400
            # 仅校验基本规则，重名检查在最终 parent/name 确认后统一进行
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
        
        # 按需放开同级同名：不进行同级重名校验（包括编辑场景）

        # 保存更新
        category.save()
        
        return success_response(category.to_dict(), "success")
        
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
            return success_response(None, "success")
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
        
        return success_response(data, "success")
        
    except Exception as e:
        return error_response(f"获取顶级分类失败: {str(e)}"), 500

# 新增：获取所有子分类（parent_id 非空）的平铺列表
@categories_bp.route('/categoriesChildren', methods=['GET'])
@jwt_required()
def get_all_children_categories():
    """
    返回系统内所有子分类（parent_id 非空）的平铺列表
    可选 is_public 过滤（0/1）
    """
    try:
        # 验证token
        is_valid, result = validate_token()
        if not is_valid:
            return error_response(result), 401

        is_public = request.args.get('is_public', type=int)

        # 复用现有模型查询，先取全部后在内存中过滤，避免修改模型方法
        all_categories, _ = Category.get_all({}, None, None, 'sort_order')

        children = [c for c in all_categories if c.parent_id is not None]
        if is_public is not None:
            children = [c for c in children if int(getattr(c, 'is_public', 0)) == int(is_public)]

        data = [c.to_dict() for c in children]
        return success_response(data, "success")
    except Exception as e:
        return error_response(f"获取子分类失败: {str(e)}"), 500

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
        
        return success_response(data, "success")
        
    except Exception as e:
        return error_response(f"获取公开分类失败: {str(e)}"), 500
