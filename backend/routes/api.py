from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from models.category import Category
from models.navs import Nav
import math

api_bp = Blueprint('api', __name__)

@api_bp.route('/health')
def health_check():
    """健康检查接口"""
    return jsonify({'status': 'ok', 'message': 'API服务运行正常'})

@api_bp.route('/')
def api_root():
    """API根接口"""
    return jsonify({
        'message': '导航系统API',
        'version': '1.0.0',
        'endpoints': {
            'auth': '/api/auth',
            'navigation': '/api/navs',
            'health': '/api/health',
            'home': '/api/web/home'
        }
    })

@api_bp.route('/web/home', methods=['GET'])
def get_home_data():
    """
    获取主页数据 - 用户端
    判断是否有JWT Token：
    1. 没有JWT Token：获取所有分类及所有公开的导航项，按层级结构返回
    2. 有JWT Token：获取所有分类及其导航项，按层级结构返回
    支持分页参数：page（页码）和size（每页条数）
    """
    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 9, type=int)
    
    # 参数验证
    if page < 1:
        page = 1
    if size < 1 or size > 50:  # 限制每页最大条数
        size = 9
    
    # 检查是否有有效的JWT Token
    has_token = False
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
        if user_id:
            has_token = True
    except:
        has_token = False
    
    try:
        # 获取所有顶级分类（parent_id为NULL的分类）
        top_categories, _ = Category.get_all({'parent_id': None}, sort='sort_order')
        
        # 按 sort_order 升序排序，相同 sort_order 按 id 升序
        top_categories.sort(key=lambda x: (x.sort_order, x.id))
        
        result = []
        
        # 构建层级结构
        for top_category in top_categories:
            category_data = {
                'id': top_category.id,
                'parent_id': top_category.parent_id,
                'name': top_category.name,
                'description': top_category.description,
                'sort_order': top_category.sort_order,
                'level': top_category.level,
                'is_public': int(top_category.is_public) if top_category.is_public is not None else 1,
                'created_at': top_category.created_at.strftime('%Y-%m-%d %H:%M:%S') if top_category.created_at else None,
                'children': []
            }
            
            # 获取子分类（parent_id等于当前分类id的分类）
            sub_categories, _ = Category.get_all({'parent_id': top_category.id}, sort='sort_order')
            
            # 按 sort_order 升序排序，相同 sort_order 按 id 升序
            sub_categories.sort(key=lambda x: (x.sort_order, x.id))
            
            for sub_category in sub_categories:
                sub_category_data = {
                    'id': sub_category.id,
                    'parent_id': sub_category.parent_id,
                    'name': sub_category.name,
                    'description': sub_category.description,
                    'sort_order': sub_category.sort_order,
                    'level': sub_category.level,
                    'is_public': int(sub_category.is_public) if sub_category.is_public is not None else 1,
                    'created_at': sub_category.created_at.strftime('%Y-%m-%d %H:%M:%S') if sub_category.created_at else None,
                    'navs': []
                }
                
                # 获取导航项
                nav_filters = {'category_id': sub_category.id}
                
                # 如果没有Token，只获取公开的导航项
                if not has_token:
                    nav_filters['is_public'] = True
                
                # 如果没有Token且分类不公开，navs设为空数组
                if not has_token and not sub_category.is_public:
                    sub_category_data['navs'] = []
                    sub_category_data['pagination'] = {
                        'page': page,
                        'size': size,
                        'total': 0,
                        'pages': 0
                    }
                else:
                    # 获取分页的导航项
                    navs, total = Nav.search(nav_filters, page=page, size=size, sort='sort_order')
                    
                    # 计算总页数
                    pages = math.ceil(total / size) if total > 0 else 0
                    
                    # 添加导航项数据
                    for nav in navs:
                        nav_data = nav.to_dict()
                        sub_category_data['navs'].append(nav_data)
                    
                    # 添加分页信息
                    sub_category_data['pagination'] = {
                        'page': page,
                        'size': size,
                        'total': total,
                        'pages': pages
                    }
                
                category_data['children'].append(sub_category_data)
            
            result.append(category_data)
        
        return jsonify({
            'code': 1,
            'msg': 'success',
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'code': 0,
            'msg': f'获取主页数据失败: {str(e)}',
            'data': []
        })