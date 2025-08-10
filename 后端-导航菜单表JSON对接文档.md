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

| 参数名 | 位置 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- | --- |
| page | query | int | 否 | 1 | 页码（从 1 开始） |
| size | query | int | 否 | 10 | 每页条数（建议 10/20/50） |
| is_public | query | int | 否 | - | 公开状态（0=私有，1=公开） |
| keyword | query | string | 否 | - | 关键词，匹配标题/描述 |
| category_id | query | int | 否 | - | 分类 ID(parent_id，不为空) |



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



表格参考：


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

### 3.2 批量导入导航项（CSV）

- 请求路径：/admin/navs/import
- 请求方式：POST
- 认证要求：需要 JWT Token
- 请求头：

```
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

- 表单字段（multipart/form-data）：

| 字段名 | 必填 | 类型 | 说明 |
| --- | --- | --- | --- |
| file | 是 | file | CSV 文件（UTF-8，无 BOM，逗号分隔） |
| dedupe | 否 | int/bool | 去重开关，1=开启（默认），基于 category_name+url 判重（按名称解析到ID后再判重）；0=关闭 |

- CSV 要求：
  - 编码 UTF-8，首行必须为表头；分隔符为英文逗号 ,
  - 支持字段：category_name,title,url,description,icon,sort_order,is_public
  - 必填字段：category_name,title,url
  - icon 允许为空：后端可按“若为空则自动获取 url 站点图标”策略补全
  - sort_order 缺省按 0 处理；is_public 缺省按 default_is_public 或 1

#### CSV 表头兼容与自动映射（为不一致表头做兼容优化）

为兼容不同来源的 CSV 表头，后端对以下字段支持多种别名（不区分大小写，自动去除首尾空格）：

| 目标字段 | 必填 | 支持的表头别名 | 取值与归一化说明 |
| --- | --- | --- | --- |
| category_name（用于按名称匹配ID） | 是 | 分类名称 | 用于按名称匹配分类ID；未匹配则失败 |
| title | 是                      | 导航名称                       |  |
| url | 是 | 导航链接 | 仅允许 http/https |
| description | 否 | 描述 |  |
| icon | 否 | 图标URL | 可空；为空可由后端按 URL 自动补全站点图标 |
| sort_order | 否 | 排序 |  |
| is_public | 否 | 是否公开 | （公开：1，私有：0，默认：公开） |

自动映射规则：

1. 读取首行表头后，统一小写并去空格，与上表别名做映射得到标准字段名。
3. 提供 category_name 时，后端将按分类名称查询分类ID；未匹配到则判为失败行并记录 errors。
5. is_public 允许 1/0、"1"/"0"、"true"/"false"、"公开"/"私有"（大小写/中英文不敏感，统一归一化为 1/0）。

中文表头示例（可被自动识别）：

```csv
分类名称,导航名称,导航链接,描述,图标URL,排序,是否公开
编程网站,Vue.js,https://vuejs.org/,Vue 官方站,,1,1
编程网站,MDN,https://developer.mozilla.org/,Web 文档,,2,公开
```

说明：示例中的“公开”列允许值为 1/0 或 公开/私有/true/false，后端会归一化处理。

- 示例 CSV：

```csv
category_name,title,url,description,icon,sort_order,is_public
编程网站,Vue,https://vuejs.org/,Vue 官方站,,1,1
编程网站,MDN,https://developer.mozilla.org/,Web 文档,,2,1
语言,Python,https://www.python.org/,Python 官方站,,0,1
```

- 成功响应示例：

```json
{
  "code": 1,
  "msg": "success",
  "data": {
    "total": 3,
    "success": 3,
    "failed": 0, //失败行数
    "errors": [], //失败行数据
    "preview": [ //成功行数据（按名称解析分类）
      {"title": "Vue.js", "url": "https://vuejs.org/", "category_name": "编程网站"},
      {"title": "MDN", "url": "https://developer.mozilla.org/", "category_name": "编程网站"}
    ]
  }
}
```

- 可能的失败响应：

```json
{ "code": 0, "msg": "文件缺失或格式错误", "data": null }
```

- 业务规则说明：
  - 去重策略：当 dedupe=1 时，按“由 category_name 解析得到的分类名称 + url”进行判重，命中则跳过并计入 errors
  - 字段校验：title/url 为空判为失败；url 非 http/https 判为失败；
  - 批量导入规模建议：单次不超过 5,000 行；更大数据量建议分批次导入
  
- cURL 示例：

```bash
curl -X POST "http://localhost:5000/admin/navs/import" \
  -H "Authorization: Bearer <TOKEN>" \
  -F "file=@/path/to/navs.csv" \
  -F "dedupe=1" \
  -F "dry_run=0"
```

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
 - 成功响应示例：

 ```json
 {
   "code": 1,
   "msg": "success",
   "data": null
 }
 ```

 ### 5.2 批量删除导航项

 - 请求路径：/admin/navs/delete-batchId
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
| ids | body | int[] | 是 | - | 需要删除的导航项 ID 列表（去重后处理） |

 - 业务规则：
   - 单次最多支持 1000 个 ID；超出请分批调用
   - 后端会对 `ids` 去重，并忽略非正整数与空值
   - 幂等性：已不存在/已删除的 ID 将计入 `not_found`，不会导致整体失败
   - 执行策略：逐条删除，单条失败不会阻塞其他 ID 的删除；统计明细在响应给出

 - 成功响应示例：

 ```json
 {
   "code": 1,
   "msg": "success",
   "data": {
     "requested": 5, //请求的ID数量
     "deleted": 4, //删除的ID数量
     "not_found": [999], //未找到的ID
     "failed": [] //失败的ID
   }
 }
 ```

 - dry_run 示例响应：

 ```json
 {
   "code": 1,
   "msg": "dry_run",
   "data": {
     "requested": 5,
     "will_delete": 4,
     "not_found": [999]
   }
 }
 ```

 - 失败响应示例：

 ```json
 { "code": 0, "msg": "参数错误：ids 不能为空", "data": null }
 ```

 - cURL 示例：

 ```bash
 curl -X POST "http://localhost:5000/admin/navs/delete-batchId" \
   -H "Authorization: Bearer <TOKEN>" \
   -H "Content-Type: application/json" \
   -d '{"ids": [101,102,103]}'
 ```

 - 前端确认提示词（建议）：
   - 标题：批量删除确认
   - 正文：已选择 {count} 条导航项。此操作不可撤销，将永久删除所选导航项。是否继续？
   - 补充说明：
     - 删除后不可恢复；请确认这些导航项未被前台页面引用
     - 如需先查看影响范围，可使用“仅预检（dry_run）”
   - 操作按钮：取消 / 确认删除
   - 异常与部分成功提示：
     - 批量删除完成：成功 {deleted} 条，未找到 {not_found} 条，失败 {failed} 条

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
