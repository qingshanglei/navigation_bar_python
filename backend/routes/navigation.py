from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from models.category import Category
from models.navs import Nav

nav_bp = Blueprint('navigation', __name__)

# 与 categories 路由保持一致的响应与鉴权工具
from utils.responses import success_response, error_response
from utils.auth import validate_token

@nav_bp.route('/search', methods=['GET'])
@jwt_required()
def search_navs():
    """分页检索导航菜单：支持 is_public、keyword、category_id、sort（created_at|sort_order）"""
    try:
        is_valid, result = validate_token()
        if not is_valid:
            return error_response(result), 401

        page = request.args.get('page', 1, type=int)
        size = request.args.get('size', 10, type=int)
        is_public = request.args.get('is_public', type=int)
        keyword = request.args.get('keyword', type=str)
        category_id = request.args.get('category_id', type=int)
        sort = request.args.get('sort', 'sort_order')

        filters = {}
        if is_public is not None:
            filters['is_public'] = is_public
        if keyword:
            filters['keyword'] = keyword
        if category_id is not None:
            filters['category_id'] = category_id

        items, total = Nav.search(filters, page, size, sort)

        # 附带分类名称（按需）
        cat_names = {}
        for it in items:
            if it.category_id not in cat_names:
                cat = Category.get(it.category_id)
                cat_names[it.category_id] = cat.name if cat else None

        data_list = []
        for it in items:
            d = it.to_dict()
            d['category_name'] = cat_names.get(it.category_id)
            data_list.append(d)

        pages = (total + size - 1) // size if total > 0 else 0
        return success_response({
            'list': data_list,
            'pagination': {
                'page': page,
                'size': size,
                'total': total,
                'pages': pages
            }
        }, "success")
    except Exception as e:
        return error_response(f"查询失败: {str(e)}"), 500

@nav_bp.route('/<int:nav_id>', methods=['GET'])
@jwt_required()
def get_nav(nav_id: int):
    try:
        is_valid, result = validate_token()
        if not is_valid:
            return error_response(result), 401
        nav = Nav.get(nav_id)
        if not nav:
            return error_response("导航项不存在"), 404
        d = nav.to_dict()
        cat = Category.get(nav.category_id)
        d['category_name'] = cat.name if cat else None
        return success_response(d, "success")
    except Exception as e:
        return error_response(f"获取失败: {str(e)}"), 500

@nav_bp.route('', methods=['POST'])
@jwt_required()
def create_nav():
    try:
        is_valid, result = validate_token()
        if not is_valid:
            return error_response(result), 401
        payload = request.get_json(force=True) or {}
        required = ['category_id', 'title', 'url']
        for field in required:
            if payload.get(field) in (None, ''):
                return error_response(f"缺少必填字段: {field}"), 400

        nav = Nav(
            category_id=payload.get('category_id'),
            title=payload.get('title'),
            url=payload.get('url'),
            description=payload.get('description'),
            icon=payload.get('icon'),
            sort_order=payload.get('sort_order', 0),
            is_public=bool(payload.get('is_public', 1)),
        )
        nav.save()
        d = nav.to_dict()
        cat = Category.get(nav.category_id)
        d['category_name'] = cat.name if cat else None
        return success_response(d, "success"), 201
    except Exception as e:
        return error_response(f"创建失败: {str(e)}"), 500

@nav_bp.route('/<int:nav_id>', methods=['PUT'])
@jwt_required()
def update_nav(nav_id: int):
    try:
        is_valid, result = validate_token()
        if not is_valid:
            return error_response(result), 401
        nav = Nav.get(nav_id)
        if not nav:
            return error_response("导航项不存在"), 404
        payload = request.get_json(force=True) or {}

        for field in ['category_id', 'title', 'url', 'description', 'icon', 'sort_order', 'is_public']:
            if field in payload and payload[field] is not None:
                setattr(nav, field, payload[field])
        nav.save()
        d = nav.to_dict()
        cat = Category.get(nav.category_id)
        d['category_name'] = cat.name if cat else None
        return success_response(d, "success")
    except Exception as e:
        return error_response(f"更新失败: {str(e)}"), 500

@nav_bp.route('/<int:nav_id>', methods=['DELETE'])
@jwt_required()
def delete_nav(nav_id: int):
    try:
        is_valid, result = validate_token()
        if not is_valid:
            return error_response(result), 401
        nav = Nav.get(nav_id)
        if not nav:
            return error_response("导航项不存在"), 404
        ok = nav.delete()
        if not ok:
            return error_response("删除失败"), 400
        return success_response(None, "success")
    except Exception as e:
        return error_response(f"删除失败: {str(e)}"), 500