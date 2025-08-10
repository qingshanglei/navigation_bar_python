# 后端-导航菜单表JSON对接文档

版本：v1.2  
最后更新：2025-08-10

------

## 一、接口概述

本文档定义了导航系统中“导航菜单”管理模块的后端 API 接口规范，包含导航项（Nav）的增删查改与检索能力。

### 技术栈

- 数据库：SQLite 3.0+
- 认证方式：JWT Token
- 响应格式：JSON（统一：code/msg/data）
- 字符编码：UTF-8

### 数据库设计（navs）

- 表名：navs（或等价实现，保持字段语义一致）
- 字段：
  - id：主键，自增
  - category_id：所属分类 ID（外键，必填）
  - title：标题（必填）
  - url：链接地址（必填）
  - description：描述（可选）
  - icon：图标（可选）
  - sort_order：排序优先级（默认 0）
  - is_public：是否公开（1=公开，0=私有，默认 1）
  - created_at：创建时间（自动生成）

### 通用响应格式

```json
{
  "code": 1,
  "msg": "success",
  "data": {}
}
```

- code: 1 表示成功；0 表示失败；-1 未授权；-2 参数错误

------

## 二、查询接口

### 2.1 分页检索导航菜单

- 请求路径：/admin/navs/search
- 请求方式：GET
- 认证要求：需要 JWT Token
- 描述：按条件分页检索导航项
- 请求参数：

| 参数名 | 位置 | 类型 | 必填 | 默认值 | 说明 |  |
| --- | --- | --- | --- | --- | --- | --- |
| page | query | int | 否 | 1 | 页码（从 1 开始） |  |
| size | query | int | 否 | 10 | 每页条数（建议 10/20/50） |  |
| is_public | query | int | 否 | - | 公开状态（0=私有，1=公开） |  |
| keyword | query | string | 否 | - | 关键词，匹配标题/描述 |  |
| category_id | query | int | 否 | - | 分类 ID(parent_id，不为空) |  |

- 成功响应示例：

```json
{
  "code": 1,
  "msg": "success",
  "data": {
    "list": [
      {
        "id": 101,
        "category_id": 1,
        "category_title": "编程网站", // 分类title  
        "title": "Vue.js",
        "url": "https://vuejs.org/",
        "description": "Vue 官方站",
        "icon": "mdi:vue",
        "sort_order": 1,
        "is_public": 1,
        "created_at": "2025-08-01 12:00:00",
        "category_name": "前端开发"
      },
      {
        "id": 101,
        "category_id": 1,
        "category_title": "编程网站", // 分类title 
        "title": "Vue.js",
        "url": "https://vuejs.org/",
        "description": "Vue 官方站",
        "icon": "mdi:vue",
        "sort_order": 1,
        "is_public": 1,
        "created_at": "2025-08-01 12:00:00",
        "category_name": "前端开发"
      }
    ],
    "pagination": {
      "page": 1,
      "size": 10,
      "total": 1,
      "pages": 1
    }
  }
}
```

### 2.2 获取单个导航详情

- 请求路径：/admin/navs/{id}
- 请求方式：GET
- 认证要求：需要 JWT Token
- 路径参数：

| 参数名 | 位置 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- | --- |
| id | path | int | 是 | - | 导航项 ID |

- 成功响应示例：

```json
{
  "code": 1,
  "msg": "success",
  "data": {
    "id": 101,
    "category_id": 1,
    "category_title": "编程网站", // 分类title   
    "title": "Vue.js",
    "url": "https://vuejs.org/",
    "description": "Vue 官方站",
    "icon": "mdi:vue",
    "sort_order": 1,
    "is_public": 1,
    "created_at": "2025-08-01 12:00:00",
    "category_name": "前端开发"
  }
}
```

------

## 三、新增接口

### 3.1 创建导航项

- 请求路径：/admin/navs
- 请求方式：POST
- 认证要求：需要 JWT Token
- 请求头：

```
Authorization: Bearer {access_token}
Content-Type: application/json
```

- 请求体参数：

| 参数名 | 位置 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- | --- |
| category_id | body | int | 是 | - | 所属分类 ID |
| title | body | string | 是 | - | 标题 |
| url | body | string | 是 | - | 链接地址 |
| description | body | string | 否 | - | 描述 |
| icon | body | string | 否 | - | 图标(icon若为空，自动获取url网站的图标保存) |
| sort_order | body | int | 否 | 0 | 排序优先级 |
| is_public | body | int | 否 | 1 | 是否公开（0/1） |

- 请求示例：

```json
{
  "category_id": 1,  
  "title": "Vue.js",
  "url": "https://vuejs.org/",
  "description": "Vue 官方站",
  "icon": "mdi:vue",
  "sort_order": 1,
  "is_public": 1
}
```

- 成功响应示例：

```json
{
  "code": 1,
  "msg": "success",
  "data": {
    "id": 101,
    "category_id": 1,
    "title": "Vue.js",
    "url": "https://vuejs.org/",
    "description": "Vue 官方站",
    "icon": "mdi:vue",
    "sort_order": 1,
    "is_public": 1,
    "created_at": "2025-08-01 12:00:00",
    "category_name": "前端开发"
  }
}
```

------

## 四、修改接口

### 4.1 更新导航项

- 请求路径：/admin/navs/{id}
- 请求方式：PUT
- 认证要求：需要 JWT Token
- 路径参数：

| 参数名 | 位置 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- | --- |
| id | path | int | 是 | - | 导航项 ID |

- 请求体参数：

| 参数名 | 位置 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- | --- |
| category_id | body | int | 否 | - | 所属分类 ID |
| title | body | string | 否 | - | 标题 |
| url | body | string | 否 | - | 链接地址 |
| description | body | string | 否 | - | 描述 |
| icon | body | string | 否 | - | 图标 |
| sort_order | body | int | 否 | - | 排序优先级 |
| is_public | body | int | 否 | - | 是否公开（0/1） |

- 请求示例：

```json
{
  "code": 1,
  "msg": "success",
  "data": {
    "id": 101,
    "category_id": 1,
    "title": "Vue.js",
    "url": "https://vuejs.org/",
    "description": "Vue 官方站",
    "icon": "mdi:vue",
    "sort_order": 1,
    "is_public": 1,
    "created_at": "2025-08-01 12:00:00",
    "category_name": "前端开发"
  }
}
```

成功响应示例：

```json
{
  "code": 1,
  "msg": "success",
  "data": {
    "id": 101,
    "category_id": 1,
    "title": "Vue.js 官网",
    "url": "https://vuejs.org/",
    "description": "Vue 官方站",
    "icon": "mdi:vue",
    "sort_order": 2,
    "is_public": 1,
    "created_at": "2025-08-01 12:00:00",
    "category_name": "前端开发"
  }
}
```

------

## 五、删除接口

### 5.1 删除导航项

- 请求路径：/admin/navs/{id}
- 请求方式：DELETE
- 认证要求：需要 JWT Token
- 路径参数：

| 参数名 | 位置 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- | --- |
| id | path | int | 是 | - | 导航项 ID |

- 成功响应示例：

```json
{
  "code": 1,
  "msg": "success",
  "data": null
}
```

------

## 六、错误响应示例

```json
{
  "code": 0,
  "msg": "参数错误或业务失败原因",
  "data": null
}
```

- 未认证或令牌失效：HTTP 401 + 统一 JSON 提示

------

## 七、设计与校验

- 安全规范：所有管理接口需 JWT 认证；参数校验防注入；权限控制
- 数据校验：title/url 必填；category_id 合法；sort_order 数值范围合理
- 性能：检索使用分页；必要字段建索引（category_id、sort_order）
