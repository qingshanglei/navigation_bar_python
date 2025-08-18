# 后端-用户 JSON 对接文档

版本：v1.0  
最后更新：2025-08-01

---

## 概述

本文档描述了导航系统中用户相关的 RESTful API 接口，包括用户登录、密码管理等核心功能。

### 数据库设计
- **数据库类型**：SQLite 3.0+
- **用户表结构**：`users`
  - `id`: 用户ID（主键，自增）
  - `username`: 用户名（唯一约束）
  - `password`: 密码（加密存储）
  - `created_at`: 创建时间（自动生成）

### 通用响应格式
```json
{
    "code": 1,        // 1:成功, 0:失败
    "msg": "success", // 响应消息
    "data": {}        // 响应数据
}
```

### 认证机制
- 使用 JWT Token 进行身份验证
- Token 有效期：24小时
- 需要认证的接口在请求头中携带：`Authorization: Bearer <token>`

---

## 一、用户认证接口

### 1.1 用户登录
**基本信息**
- **请求路径**: `/api/auth/login`
- **请求方式**: POST
- **接口描述**: 用户登录获取访问令牌
- **是否需要认证**: 否

**请求参数**
| 参数名 | 类型 | 是否必须 | 备注 |
|---------|------|----------|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 用户密码 |
| remember_me | boolean | 否 | 是否记住登录状态（默认false） |

**请求示例**
```json
{
    "username": "admin",
    "password": "123456",
    "remember_me": true
}
```

**成功响应**
```json
{
    "code": 1,
    "msg": "登录成功",
    "data": {
        "user": {
            "id": 1,
            "username": "admin",
            "created_at": "2025-01-08 10:00:00"
        },
        "token": {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "Bearer",
            "expires_in": 86400,
            "expires_at": "2025-08-02 20:44:56"
        }
    }
}
```

**失败响应**
```json
{
    "code": 0,
    "msg": "用户名或密码错误",
    "data": null
}
```

### 1.2 用户登出

**基本信息**
- **请求路径**: `/api/auth/logout`
- **请求方式**: POST
- **接口描述**: 用户登出，使令牌失效
- **是否需要认证**: 是

**请求参数**
无

**请求头**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**响应数据**
```json
{
    "code": 1,
    "msg": "登出成功",
    "data": null
}
```

### 1.3 刷新令牌
**基本信息**
- **请求路径**: `/api/auth/refresh`
- **请求方式**: POST
- **接口描述**: 刷新访问令牌
- **是否需要认证**: 是

**请求参数**
无

**响应数据**
```json
{
    "code": 1,
    "msg": "令牌刷新成功",
    "data": {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "Bearer",
        "expires_in": 86400,
        "expires_at": "2025-08-02 20:44:56"
    }
}
```

---

## 二、密码管理接口

### 2.1 修改密码

**基本信息**
- **请求路径**: `/api/auth/change-password`
- **请求方式**: PUT
- **接口描述**: 用户修改登录密码
- **是否需要认证**: 是

**请求参数**
| 参数名 | 类型 | 是否必须 | 备注 |
|---------|------|----------|------|
| new_password | string | 是 | 新密码（6-20位） |

**请求示例**
```json
{
    "new_password": "newpassword123"
}
```

**成功响应**
```json
{
    "code": 1,
    "msg": "密码修改成功",
    "data": null
}
```

**失败响应示例**
```json
{
    "code": 0,
    "msg": "新密码长度必须在6-20位之间",
    "data": null
}
```

---

## 三、用户信息接口

### 3.1 获取用户信息
**基本信息**
- **请求路径**: `/api/user/profile`
- **请求方式**: GET
- **接口描述**: 获取当前登录用户信息
- **是否需要认证**: 是

**请求参数**
无

**响应数据**
```json
{
    "code": 1,
    "msg": "success",
    "data": {
        "id": 1,
        "username": "admin",
        "created_at": "2025-01-08 10:00:00"
    }
}
```

---

## 四、接口设计说明

### 4.1 安全规范
1. **密码安全**：
   - 密码使用 bcrypt 加密存储
   - 最小长度6位，最大长度20位
   - 支持字母、数字、特殊字符组合

2. **令牌安全**：
   - JWT Token 包含用户ID和过期时间
   - Token 存储在客户端，服务端验证签名
   - 支持令牌刷新和主动失效

3. **接口安全**：
   - 登录失败次数限制（5次/小时）
   - 密码重置令牌有效期30分钟
   - 敏感操作需要验证当前密码

### 4.2 错误处理
1. **认证错误**：
   - `401`: 未认证或令牌无效
   - `403`: 权限不足
   - `429`: 请求频率限制
2. **参数错误**：
   - `400`: 参数格式错误或缺失
   - `422`: 参数验证失败

### 4.3 数据验证
1. **用户名验证**：
   - 长度3-20位
   - 支持字母、数字、下划线
   - 不区分大小写

   2.**密码验证**：
- 长度6-20位
- 至少包含字母和数字
- 不允许与用户名相同

### 4.4 日志记录
1. **登录日志**：记录登录时间、IP地址、设备信息
2. **操作日志**：记录密码修改等操作
3. **安全日志**：记录异常登录等安全事件

---

## 五、使用示例

### 5.1 完整登录流程
```javascript
// 1. 用户登录
const loginResponse = await fetch('/api/auth/login', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        username: 'admin',
        password: '123456'
    })
});

const loginData = await loginResponse.json();
if (loginData.code === 1) {
    // 保存令牌
    localStorage.setItem('access_token', loginData.data.token.access_token);
    
    // 2. 使用令牌访问受保护接口
    const profileResponse = await fetch('/api/user/profile', {
        headers: {
            'Authorization': `Bearer ${loginData.data.token.access_token}`
        }
    });
    
    const profileData = await profileResponse.json();
    console.log('用户信息:', profileData.data);
}
```

### 5.2 密码修改流程
```javascript
// 修改密码
const changePasswordResponse = await fetch('/api/auth/change-password', {
    method: 'PUT',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
    },
    body: JSON.stringify({
        new_password: 'newpassword123'
    })
});

const changePasswordData = await changePasswordResponse.json();
if (changePasswordData.code === 1) {
    alert('密码修改成功');
} else {
    alert(changePasswordData.msg);
}
```

该用户JSON对接文档提供了完整的用户认证和密码管理功能，与导航系统的SQLite数据库设计完全兼容，为前端开发提供了标准的用户管理API规范。
