from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from models.category import Category
from models.navs import Nav
from urllib.parse import urlparse, urlunparse

nav_bp = Blueprint('navigation', __name__)

# 与 categories 路由保持一致的响应与鉴权工具
from utils.responses import success_response, error_response
from utils.auth import validate_token

# 工具：将布尔/字符串/数字统一转换为 0/1（按文档规范返回/入库）
def _to_int01(value, default=1):
    """
    将各种类型的值统一转换为0或1
    
    Args:
        value: 要转换的值，可以是布尔值、字符串或数字
        default: 转换失败时的默认值，默认为1
        
    Returns:
        int: 转换后的值，0或1
    """
    try:
        return 1 if int(value) else 0
    except Exception:
        return 1 if default else 0

# 规范化 URL：若无 scheme，默认 https
def _normalize_url(url: str) -> str:
    """
    规范化URL，如果没有协议前缀，则默认添加https://
    
    Args:
        url: 原始URL字符串
        
    Returns:
        str: 规范化后的URL
    """
    if not url:
        return url
    url = url.strip()
    parsed = urlparse(url)
    if not parsed.scheme:
        parsed = urlparse('https://' + url)
    # 去除多余空白并返回规范化 URL
    return urlunparse(parsed)

# 根据 URL 生成图标地址（不进行网络请求校验，避免阻塞）：
# 基于站点根目录的 /favicon.ico 自动生成图标地址，避免依赖外网聚合服务。
# 示例：输入 www.baidu.com -> https://www.baidu.com/favicon.ico
def _auto_icon_url(url: str) -> str:
    """
    根据URL自动生成网站图标地址
    
    Args:
        url: 网站URL
        
    Returns:
        str: 生成的图标URL，格式为 scheme://host/favicon.ico
    """
    try:
        if not url:
            return None
        norm = _normalize_url(url)
        p = urlparse(norm)
        host = p.netloc or p.path
        if not host:
            return None
        scheme = p.scheme or 'https'
        return f"{scheme}://{host}/favicon.ico"
    except Exception:
        return None

import csv
import io
import codecs
from werkzeug.utils import secure_filename
from flask import current_app

@nav_bp.route('/search', methods=['GET'])
@jwt_required()
def search_navs():
    """
    分页检索导航菜单：支持 is_public、keyword、category_id、sort（created_at|sort_order）
    
    Query参数:
        page: 页码，默认1
        size: 每页大小，默认10
        is_public: 是否公开，0或1
        keyword: 搜索关键词
        category_id: 分类ID
        sort: 排序字段，默认sort_order，可选created_at
    
    Returns:
        JSON: 导航项列表和分页信息
    """
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

        # 若 icon 为空，则自动根据 URL 生成图标地址
        icon = payload.get('icon')
        if not icon:
            icon = _auto_icon_url(payload.get('url'))

        nav = Nav(
            category_id=payload.get('category_id'),
            title=payload.get('title'),
            url=_normalize_url(payload.get('url')),
            description=payload.get('description'),
            icon=icon,
            sort_order=int(payload.get('sort_order', 0) or 0),
            is_public=_to_int01(payload.get('is_public', 1)),
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

        # 字段更新并做必要类型转换
        if 'category_id' in payload and payload['category_id'] is not None:
            nav.category_id = payload['category_id']
        if 'title' in payload and payload['title'] is not None:
            nav.title = payload['title']
        if 'url' in payload and payload['url'] is not None:
            nav.url = _normalize_url(payload['url'])
        if 'description' in payload:
            nav.description = payload.get('description')
        if 'icon' in payload:
            nav.icon = payload.get('icon')
        if 'sort_order' in payload and payload['sort_order'] is not None:
            nav.sort_order = int(payload['sort_order'])
        if 'is_public' in payload and payload['is_public'] is not None:
            nav.is_public = _to_int01(payload['is_public'], default=nav.is_public)
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

# 辅助函数：CSV表头映射（支持中英文表头自动识别）
def _map_csv_headers(headers):
    """
    将CSV表头映射到标准字段名
    
    支持中英文表头自动识别，通过别名列表匹配。
    例如：'分类名称'和'category_name'都会映射到'category_name'标准字段
    
    Args:
        headers: CSV文件的表头行
        
    Returns:
        dict: 标准字段名到列索引的映射
    """
    header_mapping = {
        'category_name': ['category_name', '分类名称'],
        'title': ['title', '导航名称'],
        'url': ['url', '导航链接'],
        'description': ['description', '描述'],
        'icon': ['icon', '图标url'],
        'sort_order': ['sort_order', '排序'],
        'is_public': ['is_public', '是否公开']
    }
    
    result = {}
    headers_lower = [h.lower().strip() for h in headers]
    
    for target_field, aliases in header_mapping.items():
        for i, header in enumerate(headers_lower):
            if header in [a.lower() for a in aliases]:
                result[target_field] = i
                break
    
    return result

# 辅助函数：将各种表示"是否公开"的值统一转换为0/1
def _normalize_is_public(value):
    """
    将各种表示"是否公开"的值统一转换为0/1
    
    支持多种表示方式：
    - 1/0、"1"/"0"
    - "true"/"false"
    - "公开"/"私有"
    - "yes"/"no"、"y"/"n"
    
    Args:
        value: 原始值
        
    Returns:
        int: 标准化后的值，1表示公开，0表示私有
    """
    if not value:
        return 1  # 默认公开
    
    value = str(value).lower().strip()
    if value in ['1', 'true', '公开', 'public', 'yes', 'y']:
        return 1
    elif value in ['0', 'false', '私有', 'private', 'no', 'n']:
        return 0
    else:
        return 1  # 默认公开

@nav_bp.route('/import', methods=['POST'])
@jwt_required()
def import_navs():
    """
    批量导入导航项（CSV）
    
    支持功能：
    1. 自动识别UTF-8和GBK编码
    2. 中英文表头自动映射
    3. 根据分类名称查找分类ID
    4. 数据验证和错误处理
    5. 去重功能
    
    Form参数:
        file: CSV文件
        dedupe: 是否去重，默认1（去重）
        
    Returns:
        JSON: 导入结果统计和预览
    """
    try:
        is_valid, result = validate_token()
        if not is_valid:
            return error_response(result), 401
        
        # 检查是否有文件上传
        if 'file' not in request.files:
            return error_response("文件缺失"), 400
        
        file = request.files['file']
        if file.filename == '':
            return error_response("未选择文件"), 400
        
        # 获取参数
        dedupe = request.form.get('dedupe', '1')
        dedupe = _to_int01(dedupe, default=1)
        
        # 读取CSV文件
        try:
            # 尝试检测BOM并正确读取
            stream = io.StringIO(file.stream.read().decode('utf-8-sig'))
            reader = csv.reader(stream)
            rows = list(reader)
        except UnicodeDecodeError:
            # 如果UTF-8-sig解码失败，尝试其他编码
            file.stream.seek(0)
            stream = io.StringIO(file.stream.read().decode('gbk', errors='ignore'))
            reader = csv.reader(stream)
            rows = list(reader)
        
        if len(rows) < 2:  # 至少需要表头和一行数据
            return error_response("CSV文件格式错误或为空"), 400
        
        # 映射表头
        headers = rows[0]
        header_map = _map_csv_headers(headers)
        
        # 检查必填字段
        required_fields = ['category_name', 'title', 'url']
        for field in required_fields:
            if field not in header_map:
                return error_response(f"CSV缺少必填字段: {field}"), 400
        
        # 处理数据行
        total = len(rows) - 1  # 减去表头
        success_count = 0
        failed_count = 0
        errors = []
        preview = []
        processed_keys = set()  # 用于去重
        
        for i, row in enumerate(rows[1:], 1):  # 跳过表头
            try:
                # 提取字段值
                category_name = row[header_map['category_name']].strip() if len(row) > header_map['category_name'] else ""
                title = row[header_map['title']].strip() if len(row) > header_map['title'] else ""
                url = row[header_map['url']].strip() if len(row) > header_map['url'] else ""
                description = row[header_map['description']].strip() if 'description' in header_map and len(row) > header_map['description'] else ""
                icon = row[header_map['icon']].strip() if 'icon' in header_map and len(row) > header_map['icon'] else ""
                
                # 提取并转换sort_order
                sort_order = 0
                if 'sort_order' in header_map and len(row) > header_map['sort_order']:
                    try:
                        sort_order = int(row[header_map['sort_order']].strip() or 0)
                    except ValueError:
                        sort_order = 0
                
                # 提取并转换is_public
                is_public = 1
                if 'is_public' in header_map and len(row) > header_map['is_public']:
                    is_public = _normalize_is_public(row[header_map['is_public']])
                
                # 验证必填字段
                if not category_name or not title or not url:
                    error_msg = f"第{i}行: 缺少必填字段"
                    errors.append({"row": i, "error": error_msg, "data": row})
                    failed_count += 1
                    continue
                
                # 验证URL格式
                normalized_url = _normalize_url(url)
                if not normalized_url.startswith(('http://', 'https://')):
                    error_msg = f"第{i}行: URL格式错误，必须以http://或https://开头"
                    errors.append({"row": i, "error": error_msg, "data": row})
                    failed_count += 1
                    continue
                
                # 根据分类名称查找分类ID
                category = Category.find_by_name(category_name)
                if not category:
                    error_msg = f"第{i}行: 分类名称'{category_name}'不存在"
                    errors.append({"row": i, "error": error_msg, "data": row})
                    failed_count += 1
                    continue
                
                category_id = category.id
                
                # 去重检查
                if dedupe:
                    dedup_key = f"{category_id}:{normalized_url}"
                    if dedup_key in processed_keys:
                        error_msg = f"第{i}行: 重复项 (相同分类+URL)"
                        errors.append({"row": i, "error": error_msg, "data": row})
                        failed_count += 1
                        continue
                    processed_keys.add(dedup_key)
                
                # 若icon为空，自动生成
                if not icon:
                    icon = _auto_icon_url(normalized_url)
                
                # 创建导航项
                nav = Nav(
                    category_id=category_id,
                    title=title,
                    url=normalized_url,
                    description=description,
                    icon=icon,
                    sort_order=sort_order,
                    is_public=is_public
                )
                nav.save()
                
                # 添加到预览列表
                preview_item = {
                    "title": title,
                    "url": normalized_url,
                    "category_name": category_name
                }
                preview.append(preview_item)
                success_count += 1
                
            except Exception as e:
                error_msg = f"第{i}行: 处理失败 - {str(e)}"
                errors.append({"row": i, "error": error_msg, "data": row})
                failed_count += 1
        
        # 返回结果
        return success_response({
            "total": total,
            "success": success_count,
            "failed": failed_count,
            "errors": errors[:10],  # 只返回前10个错误，避免响应过大
            "preview": preview[:10]  # 只返回前10个预览，避免响应过大
        }, "导入完成")
        
    except Exception as e:
        return error_response(f"导入失败: {str(e)}"), 500

@nav_bp.route('/bulk-delete', methods=['POST'])
@jwt_required()
def bulk_delete_navs():
    """
    批量删除导航项
    
    支持功能：
    1. ID去重和有效性验证
    2. 预检模式(dry_run)，只检查不删除
    3. 单个删除失败不影响整体流程
    4. 详细的结果统计
    
    请求体参数:
        ids: 需要删除的导航项ID列表
        
    查询参数:
        dry_run: 是否为预检模式，默认0（实际删除）
        
    Returns:
        JSON: 删除结果统计
    """
    try:
        is_valid, result = validate_token()
        if not is_valid:
            return error_response(result), 401
        
        # 获取请求体数据
        payload = request.get_json(force=True) or {}
        ids = payload.get('ids', [])
        
        # 添加调试日志
        print(f"接收到的批量删除请求: {payload}")
        print(f"提取的ids: {ids}")
        
        # 参数验证
        if not ids:
            return error_response("参数错误：ids 不能为空"), 400
        
        # 处理ids：去重、过滤非正整数
        valid_ids = []
        for id in ids:
            try:
                id_int = int(id)
                if id_int > 0 and id_int not in valid_ids:
                    valid_ids.append(id_int)
            except (ValueError, TypeError):
                # 忽略非整数值
                pass
        
        print(f"处理后的有效ids: {valid_ids}")
        
        # 检查数量限制
        if len(valid_ids) > 1000:
            return error_response("参数错误：单次最多支持1000个ID"), 400
        
        # 是否为预检模式
        dry_run = request.args.get('dry_run', '0')
        dry_run = _to_int01(dry_run, default=0)
        
        # 预检模式：只检查ID是否存在，不实际删除
        if dry_run:
            not_found = []
            will_delete = []
            
            for nav_id in valid_ids:
                nav = Nav.get(nav_id)
                if not nav:
                    not_found.append(nav_id)
                else:
                    will_delete.append(nav_id)
            
            return success_response({
                "requested": len(valid_ids),
                "will_delete": len(will_delete),
                "not_found": not_found
            }, "dry_run")
        
        # 实际删除模式
        deleted = []
        not_found = []
        failed = []
        
        for nav_id in valid_ids:
            try:
                nav = Nav.get(nav_id)
                if not nav:
                    not_found.append(nav_id)
                    continue
                
                ok = nav.delete()
                if ok:
                    deleted.append(nav_id)
                else:
                    failed.append(nav_id)
            except Exception as e:
                print(f"删除ID {nav_id} 时出错: {str(e)}")
                # 单个删除失败不影响整体流程
                failed.append(nav_id)
        
        return success_response({
            "requested": len(valid_ids),
            "deleted": len(deleted),
            "not_found": not_found,
            "failed": failed
        }, "success")
        
    except Exception as e:
        import traceback
        print(f"批量删除整体失败: {str(e)}")
        print(traceback.format_exc())
        return error_response(f"批量删除失败: {str(e)}"), 500

