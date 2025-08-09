# 后端-导航分类表JSON对接文档

版本：v1.1  
最后更新：2025-08-08

---

## 一、接口概述

本文档定义了导航系统中分类管理模块的后端API接口规范，包含分类的增删查改功能，支持多级分类层级结构管理。

### 技术栈
- **数据库**：SQLite 3.0+
- **认证方式**：JWT Token
- **响应格式**：JSON
- **字符编码**：UTF-8

### 数据库设计
- **数据库类型**：SQLite 3.0+
- **分类表结构**：`nav_categories`
  - `id`: 分类ID（主键，自增）
  - `parent_id`: 父分类ID（NULL表示顶级分类）
  - `name`: 分类名称（必填）
  - `description`: 分类描述
  - `sort_order`: 排序优先级（默认0）
  - `level`: 分类层级（1=顶级，2=二级，3=三级）
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

### 2.1 获取分类列表

**基本信息**
- **请求路径**: `/admin/categories`
- **请求方式**: GET
- **接口描述**: 获取分类列表，支持分页、筛选和树结构返回

**请求参数**
| 参数名    | 类型    | 必填 | 描述                           | 示例值 |
| --------- | ------- | ---- | ------------------------------ | ------ |
| page      | integer | 否   | 页码，默认1（tree=true时忽略）  | 1      |
| size      | integer | 否   | 每页数量，默认20（tree=true时忽略） | 20     |
| level     | integer | 否   | 分类层级筛选（1,2,3）          | 1      |
| is_public | integer | 否   | 公开状态筛选（1=公开，0=私有） | 1      |
| parent_id | integer | 否   | 父分类ID筛选                   | 1      |
| sort      | string  | 否   | 排序字段（sort_order,created_at） | sort_order |

```json
{
    "code": 1,
    "msg": "获取分类树成功",
    "data": [
        {
            "list": [
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
                            "children": []
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
                            "children": []
                        }
                    ]
                }
            ],
            "pagination": {
                "page": 1,
                "size": 20,
                "total": 2,
                "pages": 1
            }
        }
    ]
}
```

### 2.2 获取分类树结构

**基本信息**
- **请求路径**: `/admin/categories/tree`
- **请求方式**: GET
- **接口描述**: 获取完整的分类树结构

**请求参数**
无

**成功响应**
```json
{
    "code": 1,
    "msg": "获取分类树成功",
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
                    "children": []
                }
            ]
        }
    ]
}
```

### 2.3 获取单个分类详情
**基本信息**
- **请求路径**: `/admin/categories/{id}`
- **请求方式**: GET
- **接口描述**: 根据ID获取分类详细信息

**路径参数**
| 参数名 | 类型    | 必填 | 描述   | 示例值 |
| ------ | ------- | ---- | ------ | ------ |
| id     | integer | 是   | 分类ID | 1      |

**成功响应**
```json
{
    "code": 1,
    "msg": "获取分类成功",
    "data": {
        "id": 1,
        "parent_id": null,
        "name": "编程网站",
        "description": "编程相关的网站集合",
        "sort_order": 1,
        "level": 1,
        "is_public": 1,
        "created_at": "2025-08-01 10:00:00"
    }
}
```

**失败响应**
```json
{
    "code": 0,
    "msg": "分类不存在",
    "data": null
}
```

### 2.4 获取子分类列表
**基本信息**
- **请求路径**: `/admin/categories/{id}/children`
- **请求方式**: GET
- **接口描述**: 获取指定分类的直接子分类

**路径参数**
| 参数名 | 类型    | 必填 | 描述       | 示例值 |
| ------ | ------- | ---- | ---------- | ------ |
| id     | integer | 是   | 父分类ID   | 1      |

**成功响应**
```json
{
    "code": 1,
    "msg": "获取子分类成功",
    "data": [
        {
            "id": 2,
            "parent_id": 1,
            "name": "前端开发",
            "description": "前端开发相关网站",
            "sort_order": 1,
            "level": 2,
            "is_public": 1,
            "created_at": "2025-08-01 10:05:00"
        }
    ]
}
```

---

## 三、新增接口

### 3.1 创建新分类
**基本信息**
- **请求路径**: `/admin/categories`
- **请求方式**: POST
- **接口描述**: 创建新的分类
- **认证要求**: 需要JWT Token

**请求头**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**请求参数**
| 参数名      | 类型    | 必填 | 描述                           | 示例值             |
| ----------- | ------- | ---- | ------------------------------ | ------------------ |
| name        | string  | 是   | 分类名称（1-100字符）          | "后端开发"         |
| parent_id   | integer | 否   | 父分类ID（NULL表示顶级分类）   | 1                  |
| description | string  | 否   | 分类描述                       | "后端开发相关网站" |
| sort_order  | integer | 否   | 排序优先级，默认0（0-999）     | 2                  |
| is_public   | integer | 否   | 是否公开（1=公开，0=私有），默认1 | 1                  |

**请求示例**
```json
{
    "name": "后端开发",
    "parent_id": 1,
    "description": "后端开发相关网站",
    "sort_order": 2,
    "is_public": 1
}
```

**成功响应**
```json
{
    "code": 1,
    "msg": "创建分类成功",
    "data": {
        "id": 3,
        "parent_id": 1,
        "name": "后端开发",
        "description": "后端开发相关网站",
        "sort_order": 2,
        "level": 2,
        "is_public": 1,
        "created_at": "2025-08-01 21:46:35"
    }
}
```

**失败响应**
```json
{
    "code": 0,
    "msg": "分类名称已存在",
    "data": null
}
```

---

## 四、修改接口

### 4.1 更新分类信息
**基本信息**
- **请求路径**: `/admin/categories/{id}`
- **请求方式**: PUT
- **接口描述**: 更新分类信息
- **认证要求**: 需要JWT Token

**请求头**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**路径参数**
| 参数名 | 类型    | 必填 | 描述   | 示例值 |
| ------ | ------- | ---- | ------ | ------ |
| id     | integer | 是   | 分类ID | 1      |

**请求参数**
| 参数名      | 类型    | 必填 | 描述                           | 示例值                 |
| ----------- | ------- | ---- | ------------------------------ | ---------------------- |
| name        | string  | 否   | 分类名称（1-100字符）          | "编程开发网站"         |
| parent_id   | integer | 否   | 父分类ID                       | 2                      |
| description | string  | 否   | 分类描述                       | "编程开发相关的网站集合" |
| sort_order  | integer | 否   | 排序优先级（0-999）            | 3                      |
| is_public   | integer | 否   | 是否公开（1=公开，0=私有）     | 1                      |

**请求示例**
```json
{
    "name": "编程开发网站",
    "description": "编程开发相关的网站集合",
    "sort_order": 3
}
```

**成功响应**
```json
{
    "code": 1,
    "msg": "更新分类成功",
    "data": {
        "id": 1,
        "parent_id": null,
        "name": "编程开发网站",
        "description": "编程开发相关的网站集合",
        "sort_order": 3,
        "level": 1,
        "is_public": 1,
        "created_at": "2025-08-01 10:00:00"
    }
}
```

**失败响应**
```json
{
    "code": 0,
    "msg": "分类不存在或无权限修改",
    "data": null
}
```

---

## 五、删除接口

### 5.1 删除分类
**基本信息**
- **请求路径**: `/admin/categories/{id}`
- **请求方式**: DELETE
- **接口描述**: 删除指定分类
- **认证要求**: 需要JWT Token

**请求头**
```
Authorization: Bearer {access_token}
```

**路径参数**
| 参数名 | 类型    | 必填 | 描述   | 示例值 |
| ------ | ------- | ---- | ------ | ------ |
| id     | integer | 是   | 分类ID | 1      |

**查询参数**
| 参数名  | 类型    | 必填 | 描述                               | 示例值 |
| ------- | ------- | ---- | ---------------------------------- | ------ |
| cascade | boolean | 否   | 是否级联删除子分类，默认false      | true   |

**成功响应**
```json
{
    "code": 1,
    "msg": "分类删除成功",
    "data": null
}
```

**失败响应**
```json
{
    "code": 0,
    "msg": "分类下存在子分类，无法删除",
    "data": null
}
```

---

## 六、公共接口（无需认证）

### 6.1 获取公开分类列表
**基本信息**
- **请求路径**: `/admin/categories/public`
- **请求方式**: GET
- **接口描述**: 获取公开分类列表

**请求参数**
| 参数名 | 类型    | 必填 | 描述               | 示例值 |
| ------ | ------- | ---- | ------------------ | ------ |
| tree   | boolean | 否   | 是否返回树结构     | false  |

**成功响应**
```json
{
    "code": 1,
    "msg": "获取公开分类成功",
    "data": [
        {
            "id": 1,
            "parent_id": null,
            "name": "编程网站",
            "description": "编程相关的网站集合",
            "sort_order": 1,
            "level": 1,
            "is_public": 1,
            "created_at": "2025-08-01 10:00:00"
        }
    ]
}
```

---

## 七、接口设计说明

### 7.1 安全规范
1. **认证机制**：所有管理操作需要JWT Token认证
2. **参数验证**：严格验证输入参数，防止SQL注入
3. **权限控制**：根据用户权限控制分类的可见性和操作权限

### 7.2 数据验证
1. **分类名称**：
   - 长度限制：1-100字符
   - 同级别下名称唯一
   - 不允许包含特殊字符
2. **层级结构**：
   - 最大层级深度：5级
   - 防止循环引用检查
   - parent_id有效性验证
3. **排序优先级**：数值范围0-999

### 7.3 错误处理
1. **参数错误**：返回详细的参数验证错误信息
2. **业务逻辑错误**：返回具体的业务错误描述
3. **系统错误**：记录错误日志，返回通用错误信息

### 7.4 性能优化
1. **分页查询**：大数据量时使用分页避免性能问题
2. **索引优化**：在parent_id、sort_order字段上建立索引
3. **缓存策略**：分类树结构可以使用缓存提高查询性能
4. **树结构返回**：
   - `tree=true`时返回完整层级结构，无分页信息
   - `tree=false`或未设置时返回平铺列表，包含分页信息
   - 建议在小数据量时使用tree模式，大数据量时使用分页模式

---

## 八、使用示例

### 8.1 完整分类管理流程
```javascript
// 1. 获取分类列表（平铺模式）
const getCategoriesList = async () => {
    const response = await fetch('/admin/categories?page=1&size=20', {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
    });
    const data = await response.json();
    console.log('分类列表:', data.data);
};

// 2. 获取分类树结构（使用tree参数）
const getCategoriesTree = async () => {
    const response = await fetch('/admin/categories?tree=true', {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
    });
    const data = await response.json();
    console.log('分类树:', data.data);
};

// 3. 获取分类树结构（使用专用接口）
const getCategoriesTreeDedicated = async () => {
    const response = await fetch('/admin/categories/tree', {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
    });
    const data = await response.json();
    console.log('分类树（专用接口）:', data.data);
};

// 4. 创建新分类
const createCategory = async () => {
    const response = await fetch('/admin/categories', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
            name: '移动开发',
            parent_id: 1,
            description: '移动端开发相关网站',
            sort_order: 3
        })
    });
    const data = await response.json();
    console.log('创建结果:', data);
};

// 5. 更新分类信息
const updateCategory = async (id) => {
    const response = await fetch(`/admin/categories/${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
            name: '移动应用开发',
            description: '移动应用开发相关的优质网站'
        })
    });
    const data = await response.json();
    console.log('更新结果:', data);
};

// 6. 删除分类
const deleteCategory = async (id) => {
    const response = await fetch(`/admin/categories/${id}`, {
        method: 'DELETE',
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
    });
    const data = await response.json();
    console.log('删除结果:', data);
};
```

### 8.2 分页查询示例
```javascript
// 分页获取分类列表
const getCategoriesWithPagination = async (page = 1, size = 10) => {
    const params = new URLSearchParams({
        page: page,
        size: size,
        is_public: 1,
        sort: 'sort_order'
    });
    
    const response = await fetch(`/admin/categories?${params}`, {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
    });
    const data = await response.json();
    console.log('分页数据:', data.data);
};
```

---

## 九、部署与维护

### 9.1 数据库索引建议
```sql
-- 创建索引提高查询性能
CREATE INDEX idx_nav_categories_parent_id ON nav_categories(parent_id);
CREATE INDEX idx_nav_categories_sort_order ON nav_categories(sort_order);
CREATE INDEX idx_nav_categories_level ON nav_categories(level);
CREATE INDEX idx_nav_categories_is_public ON nav_categories(is_public);
```

### 9.2 监控建议
1. **API性能监控**：监控接口响应时间和错误率
2. **数据库监控**：监控查询性能和锁等待
3. **业务监控**：监控分类创建、修改、删除的频率

### 9.3 备份策略
1. **定期备份**：每日备份SQLite数据库文件
2. **增量备份**：记录分类变更日志
3. **恢复测试**：定期测试备份文件的可用性

---

**文档版本**: v1.1  
**更新时间**: 2025-08-08  
**维护团队**: 导航系统开发组