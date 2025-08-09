# 后端-导航菜单表JSON对接文档

版本：v1.0  
最后更新：2025-08-01

---

## 一、接口概述

本文档定义了导航系统中菜单管理模块的后端API接口规范，包含导航菜单的增删查改功能，支持多级菜单层级结构和分类关联管理。

### 技术栈
- **数据库**：SQLite 3.0+
- **认证方式**：JWT Token
- **响应格式**：JSON
- **字符编码**：UTF-8

### 数据库设计
- **数据库类型**：SQLite 3.0+
- **导航菜单表结构**：`navs`
  - `id`: 导航项ID（主键，自增）
  - `category_id`: 所属分类ID（必填，外键）
  - `parent_id`: 父级导航ID（NULL表示顶级菜单）
  - `title`: 导航标题（必填）
  - `url`: 导航链接（必填）
  - `description`: 网站描述信息
  - `icon`: 图标URL地址
  - `sort_order`: 排序优先级（默认0）
  - `is_public`: 是否公开（1=公开，0=私有）
  - `created_at`: 创建时间（自动生成）

### 通用响应格式
```json
{
    "code": 1,
    "msg": "success",
    "data": {}
}
```

**响应码说明**：
- `code: 1` - 成功
- `code: 0` - 失败
- `code: -1` - 未授权
- `code: -2` - 参数错误

---

## 二、查询接口

### 2.1 获取导航菜单列表

**基本信息**
- **请求路径**: `/api/navs`
- **请求方式**: GET
- **接口描述**: 获取导航菜单列表，支持分页、筛选和树结构返回

**请求参数**
| 参数名      | 类型    | 必填 | 描述                           | 示例值 |
| ----------- | ------- | ---- | ------------------------------ | ------ |
| page        | integer | 否   | 页码，默认1（tree=true时忽略）  | 1      |
| size        | integer | 否   | 每页数量，默认20（tree=true时忽略） | 20     | category_id | integer | 否   | 分类ID筛选                     | 1      |
| parent_id   | integer | 否   | 父级导航ID筛选                 | 1      |
| is_public   | integer | 否   | 公开状态筛选（1=公开，0=私有） | 1      |
| keyword     | string  | 否   | 关键词搜索（标题、描述）       | "编程"  |
| sort        | string  | 否   | 排序字段（sort_order,created_at） | sort_order |

**成功响应**

```json
{
    "code": 1,
    "msg": "success",
    "data": [
        {
            "id": 1,
            "category_id": 1,
            "parent_id": null,
            "title": "Visual Studio Code",
            "url": "https://code.visualstudio.com/",
            "description": "微软开发的轻量级代码编辑器",
            "icon": "https://files.codelife.cc/icons/vscode.png",
            "sort_order": 1,
            "is_public": 1,
            "created_at": "2025-08-01 10:00:00",
            "category_name": "编程工具",
            "children": [
                {
                    "id": 2,
                    "category_id": 1,
                    "parent_id": 1,
                    "title": "VSCode插件市场",
                    "url": "https://marketplace.visualstudio.com/",
                    "description": "VSCode官方插件市场",
                    "icon": "https://files.codelife.cc/icons/vscode-ext.png",
                    "sort_order": 1,
                    "is_public": 1,
                    "created_at": "2025-08-01 10:05:00",
                    "category_name": "编程工具",
                    "children": []
                }
            ]
        }
    ]
}
```

### 2.2 获取单个导航菜单详情

**基本信息**
- **请求路径**: `/api/navs/{id}`
- **请求方式**: GET
- **接口描述**: 根据ID获取导航菜单详细信息

**路径参数**
| 参数名 | 类型    | 必填 | 描述     | 示例值 |
| ------ | ------- | ---- | -------- | ------ |
| id     | integer | 是   | 导航项ID | 1      |

**成功响应**
```json
{
    "code": 1,
    "msg": "success",
    "data": {
        "id": 1,
        "category_id": 1,
        "parent_id": null,
        "title": "Visual Studio Code",
        "url": "https://code.visualstudio.com/",
        "description": "微软开发的轻量级代码编辑器",
        "icon": "https://files.codelife.cc/icons/vscode.png",
        "sort_order": 1,
        "is_public": 1,
        "created_at": "2025-08-01 10:00:00",
        "category_name": "编程工具"
    }
}
```

### 2.3 获取分类下的导航菜单

**基本信息**
- **请求路径**: `/api/categories/{category_id}/navs`
- **请求方式**: GET
- **接口描述**: 获取指定分类下的所有导航菜单

**路径参数**
| 参数名      | 类型    | 必填 | 描述   | 示例值 |
| ----------- | ------- | ---- | ------ | ------ |
| category_id | integer | 是   | 分类ID | 1      |

**查询参数**
| 参数名    | 类型    | 必填 | 描述                           | 示例值 |
| --------- | ------- | ---- | ------------------------------ | ------ |
| tree      | boolean | 否   | 是否返回树结构，默认false       | true   |
| is_public | integer | 否   | 公开状态筛选（1=公开，0=私有） | 1      |

---

## 三、新增接口

### 3.1 创建新导航菜单

**基本信息**
- **请求路径**: `/api/navs`
- **请求方式**: POST
- **接口描述**: 创建新的导航菜单
- **认证要求**: 需要JWT Token

**请求头**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**请求参数**
| 参数名      | 类型    | 必填 | 描述                           | 示例值                          |
| ----------- | ------- | ---- | ------------------------------ | ------------------------------- |
| category_id | integer | 是   | 所属分类ID                     | 1                               |
| parent_id   | integer | 否   | 父级导航ID（NULL表示顶级菜单） | 1                               |
| title       | string  | 是   | 导航标题                       | "GitHub"                        |
| url         | string  | 是   | 导航链接                       | "https://github.com"            |
| description | string  | 否   | 网站描述信息                   | "全球最大的代码托管平台"        |
| icon        | string  | 否   | 图标URL地址                   | "https://github.com/favicon.ico" |
| sort_order  | integer | 否   | 排序优先级，默认0              | 2                               |
| is_public   | integer | 否   | 是否公开（1=公开，0=私有），默认1 | 1                               |

**请求示例**
```json
{
    "category_id": 1,
    "parent_id": null,
    "title": "GitHub",
    "url": "https://github.com",
    "description": "全球最大的代码托管平台",
    "icon": "https://github.com/favicon.ico",
    "sort_order": 2,
    "is_public": 1
}
```

**成功响应**
```json
{
    "code": 1,
    "msg": "导航菜单创建成功",
    "data": {
        "id": 3,
        "category_id": 1,
        "parent_id": null,
        "title": "GitHub",
        "url": "https://github.com",
        "description": "全球最大的代码托管平台",
        "icon": "https://github.com/favicon.ico",
        "sort_order": 2,
        "is_public": 1,
        "created_at": "2025-08-01 22:56:54"
    }
}
```

---

## 四、修改接口

### 4.1 更新导航菜单信息

**基本信息**
- **请求路径**: `/api/navs/{id}`
- **请求方式**: PUT
- **接口描述**: 更新导航菜单信息
- **认证要求**: 需要JWT Token

**请求头**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**路径参数**
| 参数名 | 类型    | 必填 | 描述     | 示例值 |
| ------ | ------- | ---- | -------- | ------ |
| id     | integer | 是   | 导航项ID | 1      |

**请求参数**
| 参数名      | 类型    | 必填 | 描述                           | 示例值                     |
| ----------- | ------- | ---- | ------------------------------ | -------------------------- |
| category_id | integer | 否   | 所属分类ID                     | 2                          |
| parent_id   | integer | 否   | 父级导航ID                     | 2                          |
| title       | string  | 否   | 导航标题                       | "GitHub Desktop"           |
| url         | string  | 否   | 导航链接                       | "https://desktop.github.com" |
| description | string  | 否   | 网站描述信息                   | "GitHub官方桌面客户端"     |
| icon        | string  | 否   | 图标URL地址                   | "https://new-icon-url.com" |
| sort_order  | integer | 否   | 排序优先级                     | 3                          |
| is_public   | integer | 否   | 是否公开（1=公开，0=私有）     | 1                          |

**请求示例**
```json
{
    "title": "GitHub Desktop",
    "url": "https://desktop.github.com",
    "description": "GitHub官方桌面客户端",
    "sort_order": 3
}
```

**成功响应**
```json
{
    "code": 1,
    "msg": "导航菜单更新成功",
    "data": {
        "id": 1,
        "category_id": 1,
        "parent_id": null,
        "title": "GitHub Desktop",
        "url": "https://desktop.github.com",
        "description": "GitHub官方桌面客户端",
        "icon": "https://github.com/favicon.ico",
        "sort_order": 3,
        "is_public": 1,
        "created_at": "2025-08-01 10:00:00"
    }
}
```

---

## 五、删除接口

### 5.1 删除导航菜单

**基本信息**
- **请求路径**: `/api/navs/{id}`
- **请求方式**: DELETE
- **接口描述**: 删除指定导航菜单
- **认证要求**: 需要JWT Token

**请求头**
```
Authorization: Bearer {access_token}
```

**路径参数**
| 参数名 | 类型    | 必填 | 描述     | 示例值 |
| ------ | ------- | ---- | -------- | ------ |
| id     | integer | 是   | 导航项ID | 1      |

**查询参数**
| 参数名  | 类型    | 必填 | 描述                               | 示例值 |
| ------- | ------- | ---- | ---------------------------------- | ------ |
| cascade | boolean | 否   | 是否级联删除子菜单，默认false      | true   |

**成功响应**
```json
{
    "code": 1,
    "msg": "导航菜单删除成功",
    "data": null
}
```

**失败响应**
```json
{
    "code": 0,
    "msg": "导航菜单下存在子菜单，无法删除",
    "data": {
        "children_count": 3
    }
}
```

---

## 六、搜索接口

### 6.1 全局搜索导航菜单

**基本信息**
- **请求路径**: `/api/navs/search`
- **请求方式**: GET
- **接口描述**: 全局搜索导航菜单

**请求参数**
| 参数名      | 类型    | 必填 | 描述                           | 示例值 |
| ----------- | ------- | ---- | ------------------------------ | ------ |
| keyword     | string  | 是   | 搜索关键词                     | "GitHub" |
| page        | integer | 否   | 页码，默认1                    | 1      |
| size        | integer | 否   | 每页数量，默认20               | 20     |
| category_id | integer | 否   | 限定分类ID                     | 1      |
| is_public   | integer | 否   | 公开状态筛选（1=公开，0=私有） | 1      |

**成功响应**
```json
{
    "code": 1,
    "msg": "success",
    "data": {
        "list": [
            {
                "id": 1,
                "category_id": 1,
                "parent_id": null,
                "title": "GitHub",
                "url": "https://github.com",
                "description": "全球最大的代码托管平台",
                "icon": "https://github.com/favicon.ico",
                "sort_order": 1,
                "is_public": 1,
                "created_at": "2025-08-01 10:00:00",
                "category_name": "编程工具",
                "highlight": {
                    "title": "<em>GitHub</em>",
                    "description": "全球最大的代码托管平台"
                }
            }
        ],
        "pagination": {
            "page": 1,
            "size": 20,
            "total": 1,
            "pages": 1
        }
    }
}
```

---

## 七、接口设计说明

### 7.1 安全规范
1. **认证机制**：所有修改操作需要JWT Token认证
2. **参数验证**：严格验证输入参数，防止SQL注入和XSS攻击
3. **权限控制**：根据用户权限控制导航菜单的可见性和操作权限
4. **URL验证**：验证URL格式的有效性

### 7.2 数据验证
1. **导航标题**：长度限制1-200字符，不允许包含危险HTML标签
2. **导航链接**：必须是有效的URL格式，支持HTTP/HTTPS协议，长度限制1-500字符
3. **层级结构**：最大层级深度3级，防止循环引用检查，parent_id有效性验证
4. **分类关联**：category_id必须存在于nav_categories表中
5. **排序优先级**：数值范围0-999

### 7.3 性能优化
1. **分页查询**：大数据量时使用分页避免性能问题
2. **索引优化**：在category_id、parent_id、sort_order字段上建立索引
3. **缓存策略**：导航树结构可以使用缓存提高查询性能
4. **搜索优化**：使用全文搜索索引提高搜索性能

---

## 八、使用示例

### 8.1 完整导航菜单管理流程
```javascript
// 1. 获取导航菜单列表
const getNavsList = async () => {
    const response = await fetch('/api/navs?page=1&size=20&category_id=1', {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
    });
    const data = await response.json();
    console.log('导航菜单列表:', data.data);
};

// 2. 获取导航菜单树结构
const getNavsTree = async () => {
    const response = await fetch('/api/navs?tree=true&category_id=1', {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
    });
    const data = await response.json();
    console.log('导航菜单树:', data.data);
};

// 3. 创建新导航菜单
const createNav = async () => {
    const response = await fetch('/api/navs', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
            category_id: 1,
            title: 'Stack Overflow',
            url: 'https://stackoverflow.com',
            description: '程序员问答社区',
            icon: 'https://stackoverflow.com/favicon.ico',
            sort_order: 3
        })
    });
    const data = await response.json();
    console.log('创建结果:', data);
};

// 4. 更新导航菜单信息
const updateNav = async (id) => {
    const response = await fetch(`/api/navs/${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
            title: 'Stack Overflow 中文版',
            description: '程序员问答社区 - 中文版'
        })
    });
    const data = await response.json();
    console.log('更新结果:', data);
};

// 5. 删除导航菜单
const deleteNav = async (id) => {
    const response = await fetch(`/api/navs/${id}`, {
        method: 'DELETE',
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
    });
    const data = await response.json();
    console.log('删除结果:', data);
};

// 6. 搜索导航菜单
const searchNavs = async (keyword) => {
    const params = new URLSearchParams({
        keyword: keyword,
        page: 1,
        size: 10,
        is_public: 1
    });
    
    const response = await fetch(`/api/navs/search?${params}`, {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
    });
    const data = await response.json();
    console.log('搜索结果:', data.data);
};
```

---

## 九、部署与维护

### 9.1 数据库索引建议
```sql
-- 创建索引提高查询性能
CREATE INDEX idx_navs_category_id ON navs(category_id);
CREATE INDEX idx_navs_parent_id ON navs(parent_id);
CREATE INDEX idx_navs_sort_order ON navs(sort_order);
CREATE INDEX idx_navs_is_public ON navs(is_public);
CREATE INDEX idx_navs_created_at ON navs(created_at);
```

### 9.2 监控建议
1. **API性能监控**：监控接口响应时间和错误率
2. **数据库监控**：监控查询性能和锁等待
3. **业务监控**：监控导航菜单创建、修改、删除的频率

### 9.3 备份策略
1. **定期备份**：每日备份SQLite数据库文件
2. **增量备份**：记录导航菜单变更日志
3. **恢复测试**：定期测试备份文件的可用性

---

**文档版本**: v1.0  
**创建时间**: 2025-08-01  
**维护团队**: 导航系统开发组
