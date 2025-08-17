# 用户端-主页JSON对接文档

版本：v1.3  
最后更新：2025-08-10

------

## 一、接口概述

本文档定义了导航系统中"导航菜单"模块的用户端查询接口规范，用于主页展示导航分类和导航项。

### 技术栈

- 数据库：SQLite 3.0+
- 认证方式：无认证（公开接口）
- 响应格式：JSON（统一：code/msg/data）
- 字符编码：UTF-8

**导航分类表（nav_categories）**

- `id`: 分类ID（主键，自增）
- `parent_id`: 父分类ID（NULL表示顶级分类）
- `name`: 分类名称（必填）
- `description`: 分类描述
- `sort_order`: 排序优先级（默认0）
- `level`: 分类层级（1=顶级，2=二级，3=三级）
- `is_public`: 是否公开（1=公开，0=私有）
- `created_at`: 创建时间（自动生成）

**导航菜单表（navs）**

- `id`: 主键，自增
- `category_id`: 所属分类 ID（外键，必填）
- `title`: 标题（必填）
- `url`: 链接地址（必填）
- `description`: 描述（可选）
- `icon`: 图标（可选）
- `sort_order`: 排序优先级（默认 0）
- `is_public`: 是否公开（1=公开，0=私有，默认 1）
- `created_at`: 创建时间（自动生成）
**用户表结构**：`users`
- `id`: 用户ID（主键，自增）
- `username`: 用户名（唯一约束）
- `password`: 密码（加密存储）
- `created_at`: 创建时间（自动生成）

### 通用响应格式

```json
{
  "code": 1,
  "msg": "success",
  "data": {}
}
```

- code: 1 表示成功；0 表示失败；-2 参数错误

------

## 二、查询接口

### 2.1 获取主页数据-用户端

- 请求路径：`/api/web/home`

- 请求方式：GET

- 认证要求：可选JWT Token（通过Authorization头部传递）

- 功能描述：根据是否有JWT Token返回不同的数据
  - 有Token：返回所有分类及其导航项，按层级结构返回
  
  - 无Token：只返回公开的分类及其导航项，按层级结构返回

-  接口使用说明
  1. **排序规则**：默认按 `sort_order` 升序排序，相同排序按创建时间降序
  2. **缓存建议**：前端可对分类树数据进行本地缓存，有效期建议7天
  3. **数据结构**: 层级树形结构（顶级分类 -> 二级分类 -> 导航项 ）

#### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :-- | --- | --- | --- | --- |
| Token |  | 否 | 无 | 判断是否有JWT Token    数据过滤： ①没有JWT Token 获取所有分类及所有公开的导航项，按层级结构返回  ②有JWT Token 获取所有分类及其导航项，按层级结构返回 |                               |

#### 有JWT Token：成功响应示例

```json
{
    "code": 1,
    "msg": "success",
    "data": [
        {
            "id": 1,
            "parent_id": null,
            "name": "编程网站",
            "description": "编程相关的网站集合",
            "sort_order": 1,
            "level": 1,
            "is_public": 1,
            "created_at": "2025-08-01 10:00:00",
            "children": [
                {
                    "id": 2,
                    "parent_id": 1,
                    "name": "前端开发",
                    "description": "前端开发相关网站",
                    "sort_order": 1,
                    "level": 2,
                    "is_public": 1,
                    "created_at": "2025-08-01 10:05:00",
                    "navs": [
                        {
                            "id": 101,
                            "category_id": 2,
                            "title": "Vue.js",
                            "url": "https://vuejs.org/",
                            "description": "Vue 官方文档",
                            "icon": "https://vuejs.org/logo.png",
                            "sort_order": 1,
                            "is_public": 1,
                            "created_at": "2025-08-01 12:00:00"
                        },
                        {
                            "id": 102,
                            "category_id": 2,
                            "title": "React",
                            "url": "https://react.dev/",
                            "description": "React 官方文档",
                            "icon": "https://react.dev/favicon.ico",
                            "sort_order": 2,
                            "is_public": 1,
                            "created_at": "2025-08-01 12:30:00"
                        }
                    ]
                },
                {
                    "id": 3,
                    "parent_id": 1,
                    "name": "后端开发",
                    "description": "后端开发相关网站",
                    "sort_order": 2,
                    "level": 2,
                    "is_public": 1,
                    "created_at": "2025-08-01 10:10:00",
                    "navs": [
                        {
                            "id": 201,
                            "category_id": 3,
                            "title": "Node.js",
                            "url": "https://nodejs.org/",
                            "description": "Node.js 官方网站",
                            "icon": "https://nodejs.org/static/images/logo.svg",
                            "sort_order": 1,
                            "is_public": 1,
                            "created_at": "2025-08-01 13:00:00"
                        }
                    ]
                }
            ]
        },
        {
            "id": 4,
            "parent_id": null,
            "name": "设计资源",
            "description": "设计相关资源网站",
            "sort_order": 2,
            "level": 1,
            "is_public": 1,
            "created_at": "2025-08-01 11:00:00",
            "children": [
                {
                    "id": 5,
                    "parent_id": 4,
                    "name": "图标库",
                    "description": "免费图标资源",
                    "sort_order": 1,
                    "level": 2,
                    "is_public": 1,
                    "created_at": "2025-08-01 11:05:00",
                    "navs": [
                        {
                            "id": 301,
                            "category_id": 5,
                            "title": "Font Awesome",
                            "url": "https://fontawesome.com/",
                            "description": "流行的图标库",
                            "icon": "https://fontawesome.com/favicon.ico",
                            "sort_order": 1,
                            "is_public": 1,
                            "created_at": "2025-08-01 14:00:00"
                        }
                    ]
                }
            ]
        }
    ]
}
```

#### 没有JWT Token：成功响应示例

```json
{
    "code": 1,
    "msg": "success",
    "data": [
        {
            "id": 1,
            "parent_id": null,
            "name": "编程网站",
            "description": "编程相关的网站集合",
            "sort_order": 1,
            "level": 1,
            "is_public": 1,
            "created_at": "2025-08-01 10:00:00",
            "children": [
                {
                    "id": 2,
                    "parent_id": 1,
                    "name": "前端开发",
                    "description": "前端开发相关网站",
                    "sort_order": 1,
                    "level": 2,
                    "is_public": 0, //  没有JWT Token,is_public为私有的，navs数据直接返回空
                    "created_at": "2025-08-01 10:05:00",
                    "navs": []
                },
                {
                    "id": 3,
                    "parent_id": 1,
                    "name": "后端开发",
                    "description": "后端开发相关网站",
                    "sort_order": 2,
                    "level": 2,
                    "is_public": 1,
                    "created_at": "2025-08-01 10:10:00",
                    "navs": [
                        {
                            "id": 201,
                            "category_id": 3,
                            "title": "Node.js",
                            "url": "https://nodejs.org/",
                            "description": "Node.js 官方网站",
                            "icon": "https://nodejs.org/static/images/logo.svg",
                            "sort_order": 1,
                            "is_public": 1,
                            "created_at": "2025-08-01 13:00:00"
                        }
                    ]
                }
            ]
        },
        {
            "id": 4,
            "parent_id": null,
            "name": "设计资源",
            "description": "设计相关资源网站",
            "sort_order": 2,
            "level": 1,
            "is_public": 1,
            "created_at": "2025-08-01 11:00:00",
            "children": [
                {
                    "id": 5,
                    "parent_id": 4,
                    "name": "图标库",
                    "description": "免费图标资源",
                    "sort_order": 1,
                    "level": 2,
                    "is_public": 1,
                    "created_at": "2025-08-01 11:05:00",
                    "navs": [
                        {
                            "id": 301,
                            "category_id": 5,
                            "title": "Font Awesome",
                            "url": "https://fontawesome.com/",
                            "description": "流行的图标库",
                            "icon": "https://fontawesome.com/favicon.ico",
                            "sort_order": 1,
                            "is_public": 1,
                            "created_at": "2025-08-01 14:00:00"
                        }
                    ]
                }
            ]
        }
    ]
}
```





