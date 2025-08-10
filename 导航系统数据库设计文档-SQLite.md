# 导航系统数据库设计文档

版本：v2.1  
最后更新：2025-01-08

---

## 数据库类型：SQLite 3.0+

## 数据库结构概述

本系统包含三个核心表：用户表(users)、导航分类表(nav_categories)和导航菜单表(navs)，实现了用户管理、导航分类和多级菜单功能。

```mermaid
erDiagram
    users ||--o{ navs : "权限控制"
    nav_categories ||--o| navs : "分类导航"
    nav_categories ||--o| nav_categories : "层级分类"
    navs ||--o| navs : "层级结构"

    users {
        bigint id PK "用户ID"
        varchar username "用户名"
        varchar password "密码"
        timestamp created_at "创建时间"
    }
    
    nav_categories {
        bigint id PK "分类ID"
        bigint parent_id FK "父分类ID"
        varchar name "分类名称"
        varchar description "分类描述"
        int sort_order "排序"
        int level "分类层级"
        boolean is_public "公开状态"
        timestamp created_at "创建时间"
    }
    
    navs {
        bigint id PK "导航ID"
        bigint category_id FK "分类ID"
        varchar title "标题"
        varchar url "链接"
        text description "描述信息"
        varchar icon "图标URL"
        int sort_order "排序"
        boolean is_public "公开状态"
        timestamp created_at "创建时间"
    }
```

## 表结构详情

### 1. 用户表 (users)

| 字段名     | 类型    | 约束        | 描述             | 示例值                |
| ---------- | ------- | ----------- | ---------------- | --------------------- |
| id         | INTEGER | PRIMARY KEY | 用户唯一标识     | 1                     |
| username   | TEXT    | NOT NULL    | 用户名           | "admin"               |
| password   | TEXT    | NOT NULL    | 密码（加密存储） | "******"              |
| created_at | TEXT    |             | 创建时间         | "2023-08-15 10:00:00" |

### 2. 导航分类表 (nav_categories)

| 字段名      | 类型    | 约束         | 描述                     | 示例值                |
| ----------- | ------- | ------------ | ------------------------ | --------------------- |
| id          | INTEGER | PRIMARY KEY  | 分类唯一标识             | 1                     |
| parent_id   | INTEGER | DEFAULT NULL | 父分类ID（NULL表示顶级） | NULL                  |
| name        | TEXT    | NOT NULL     | 分类名称                 | "编程网站"            |
| description | TEXT    |              | 分类描述                 | "编程相关的网站集合"  |
| sort_order  | INTEGER | DEFAULT 0    | 排序优先级               | 1                     |
| level       | INTEGER | DEFAULT 1    | 分类层级（1=顶级）       | 1                     |
| is_public   | INTEGER | DEFAULT 1    | 是否公开（1=公开）         | 1                     |
| created_at  | TEXT    |              | 创建时间                 | "2023-08-15 10:05:00" |

### 3. 导航菜单表 (navs)

| 字段名      | 类型    | 约束        | 描述                   | 示例值                          |
| ----------- | ------- | ----------- | ---------------------- | --------------------------------- |
| id          | INTEGER | PRIMARY KEY | 导航项唯一标识         | 1                                |
| category_id | INTEGER | FOREIGN KEY | 所属分类ID             | 1                                |
| title       | TEXT    | NOT NULL    | 导航标题               | "Visual Studio Code"             |
| url         | TEXT    | NOT NULL    | 导航链接               | "https://code.visualstudio.com/" |
| description | TEXT    |             | 网站描述信息           | "微软开发的轻量级代码编辑器"       |
| icon        | TEXT    |             | 图标URL地址            | "https://files.codelife.cc/..."  |
| sort_order  | INTEGER | DEFAULT 0   | 排序优先级             | 1                                |
| is_public   | INTEGER | DEFAULT 1   | 是否公开（1=公开）       | 1                                |
| created_at  | TEXT    |             | 创建时间               | "2023-08-15 10:10:00"            |

## 完整SQL语句

```sql
-- 创建用户表
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now', 'localtime'))
);

-- 创建导航分类表
CREATE TABLE nav_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_id INTEGER DEFAULT NULL,
    name TEXT NOT NULL,
    description TEXT,
    sort_order INTEGER NOT NULL DEFAULT 0,
    level INTEGER NOT NULL DEFAULT 1,
    is_public INTEGER NOT NULL DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now', 'localtime')),
    
    -- 外键约束（允许parent_id为NULL）
    FOREIGN KEY (parent_id) REFERENCES nav_categories(id) ON DELETE CASCADE
);

-- 创建导航菜单表
CREATE TABLE navs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    description TEXT,
    icon TEXT,
    sort_order INTEGER NOT NULL DEFAULT 0,
    is_public INTEGER NOT NULL DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now', 'localtime')),
    
    -- 外键约束
    FOREIGN KEY (category_id) REFERENCES nav_categories(id) ON DELETE CASCADE
);



-- 创建索引优化查询性能
CREATE INDEX idx_users_username ON users(username);

CREATE INDEX idx_navs_category ON navs(category_id);
CREATE INDEX idx_navs_sort ON navs(sort_order);
CREATE INDEX idx_navs_public ON navs(is_public);

CREATE INDEX idx_categories_parent ON nav_categories(parent_id);
CREATE INDEX idx_categories_name ON nav_categories(name);
CREATE INDEX idx_categories_sort ON nav_categories(sort_order);
CREATE INDEX idx_categories_public ON nav_categories(is_public);

-- 创建唯一约束：同级分类名称唯一
CREATE UNIQUE INDEX uk_category_name_parent ON nav_categories(name, parent_id);
```

## 外键约束

外键约束已在表创建时定义，无需额外添加。

## 数据操作示例

> 关键说明：navs.category_id 为外键，必须指向已存在的 nav_categories.id。插入导航项前应先确保对应分类记录存在，否则将触发外键约束错误。

### 重要说明：外键约束修复

如果你在执行数据插入时遇到外键约束错误，请先执行以下修复操作：

```sql
-- 删除现有表（如果存在数据，请先备份）
DROP TABLE IF EXISTS navs;
DROP TABLE IF EXISTS nav_categories;

-- nav_categories表
CREATE TABLE nav_categories (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '分类唯一标识',
    parent_id BIGINT DEFAULT NULL COMMENT '父分类ID（NULL表示顶级分类）',
    name VARCHAR(100) NOT NULL COMMENT '分类名称',
    description VARCHAR(500) COMMENT '分类描述',
    sort_order INT NOT NULL DEFAULT 0 COMMENT '排序优先级（数值越小越靠前）',
    level INT NOT NULL DEFAULT 1 COMMENT '分类层级（1=顶级，2=二级）',
    is_public BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否公开（所有用户可见）',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    CONSTRAINT fk_categories_parent 
        FOREIGN KEY (parent_id) 
        REFERENCES nav_categories(id) 
        ON DELETE CASCADE,
    
    UNIQUE KEY uk_category_name_parent (name, parent_id)
) COMMENT '导航分类表（支持多级分类）';

-- navs表
CREATE TABLE navs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '导航项唯一标识',
    category_id BIGINT NOT NULL COMMENT '所属分类ID',
    title VARCHAR(100) NOT NULL COMMENT '导航显示名称',
    url VARCHAR(500) NOT NULL COMMENT '导航跳转链接',
    description TEXT COMMENT '网站描述信息',
    icon VARCHAR(500) COMMENT '图标URL地址',
    sort_order INT NOT NULL DEFAULT 0 COMMENT '排序优先级（数值越小越靠前）',
    is_public BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否公开（所有用户可见）',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    CONSTRAINT fk_navs_category 
        FOREIGN KEY (category_id) 
        REFERENCES nav_categories(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) COMMENT '导航菜单表（按分类分组，取消自关联层级）';

-- 创建索引
CREATE INDEX idx_navs_category ON navs(category_id);
CREATE INDEX idx_navs_sort ON navs(sort_order);
CREATE INDEX idx_categories_parent ON nav_categories(parent_id);
CREATE INDEX idx_categories_sort ON nav_categories(sort_order);
```

### 1. 创建导航分类

根据data.json数据结构，创建多级分类体系：

```sql
-- 插入一级分类（大分类）
INSERT INTO nav_categories (name, parent_id, description, sort_order, level, is_public) VALUES
('编程网站', NULL, '编程相关的网站集合', 1, 1, TRUE),
('工具网站', NULL, '各类实用工具网站', 2, 1, TRUE);

-- 获取一级分类ID
SET @programming_id = (SELECT id FROM nav_categories WHERE name = '编程网站' AND parent_id IS NULL);
SET @tools_id = (SELECT id FROM nav_categories WHERE name = '工具网站' AND parent_id IS NULL);

-- 插入二级分类（子分类）
INSERT INTO nav_categories (name, parent_id, description, sort_order, level, is_public) VALUES
-- 编程网站下的子分类
('编码工具', @programming_id, '编码和开发工具', 1, 2, TRUE),
('后端', @programming_id, '后端开发资源', 2, 2, TRUE),
('前端', @programming_id, '前端开发资源', 3, 2, TRUE),
-- 工具网站下的子分类
('PDF转换', @tools_id, 'PDF文件处理工具', 1, 2, TRUE),
('图片处理', @tools_id, '在线图片编辑工具', 2, 2, TRUE);
```

### 2. 添加导航菜单项

根据 data.json 中的具体数据，添加导航项示例。

- SQLite 版本（推荐）：通过子查询获取分类 id，确保 category_id 正确链接到 nav_categories.id。

```sql
-- 编码工具分类下的导航项（category = "编码工具"）
INSERT INTO navs (category_id, title, url, description, icon, sort_order)
VALUES
((SELECT id FROM nav_categories WHERE name = '编码工具' LIMIT 1), 'Visual Studio Code', 'https://code.visualstudio.com/', '微软开发的轻量级代码编辑器', 'https://files.codelife.cc/website/visual-studio-code.svg', 1),
((SELECT id FROM nav_categories WHERE name = '编码工具' LIMIT 1), 'GitHub', 'https://github.com/', '全球最大的代码托管平台', 'https://files.codelife.cc/website/github.svg', 2),
((SELECT id FROM nav_categories WHERE name = '编码工具' LIMIT 1), 'Gitee', 'https://gitee.com/', '中国本土的代码托管平台', 'https://files.codelife.cc/website/gitee.svg', 3);

-- 后端分类下的导航项（category = "后端"）
INSERT INTO navs (category_id, title, url, description, icon, sort_order)
VALUES
((SELECT id FROM nav_categories WHERE name = '后端' LIMIT 1), 'MyBatis', 'https://mybatis.org/mybatis-3/', 'Java 持久层框架', 'https://files.codelife.cc/user-website-icon/20220803/J_G1ipNrekOYJSmTCACZ99269.png', 1),
((SELECT id FROM nav_categories WHERE name = '后端' LIMIT 1), 'Spring', 'https://spring.io/', 'Java 企业级开发框架', 'https://files.codelife.cc/website/5b307dd14c14a60c5612d29d.png', 2),
((SELECT id FROM nav_categories WHERE name = '后端' LIMIT 1), 'MySQL', 'https://dev.mysql.com/', '开源关系型数据库', 'https://files.codelife.cc/website/5f4386f4aa121b0c2ac69e22.png', 3);

-- 前端分类下的导航项（category = "前端"）
INSERT INTO navs (category_id, title, url, description, icon, sort_order)
VALUES
((SELECT id FROM nav_categories WHERE name = '前端' LIMIT 1), 'React', 'https://react.dev/', '用于构建用户界面的 JavaScript 库', 'https://files.codelife.cc/website/react.svg', 1),
((SELECT id FROM nav_categories WHERE name = '前端' LIMIT 1), 'Vue.js', 'https://vuejs.org/', '渐进式 JavaScript 框架', 'https://files.codelife.cc/website/vue.svg', 2);
```

- MySQL 版本（可选）：通过变量保存分类 id，再插入 navs（同样遵循 category_id -> nav_categories.id 的外键约束）。

```sql
-- 获取分类ID用于插入
SET @coding_tools_id = (SELECT id FROM nav_categories WHERE name = '编码工具');
SET @backend_id = (SELECT id FROM nav_categories WHERE name = '后端');
SET @frontend_id = (SELECT id FROM nav_categories WHERE name = '前端');

-- 编码工具分类下的导航项
INSERT INTO navs (category_id, title, url, description, icon, sort_order) VALUES
(@coding_tools_id, 'Visual Studio Code', 'https://code.visualstudio.com/', '微软开发的轻量级代码编辑器', 'https://files.codelife.cc/website/visual-studio-code.svg', 1),
(@coding_tools_id, 'GitHub', 'https://github.com/', '全球最大的代码托管平台', 'https://files.codelife.cc/website/github.svg', 2);

-- 后端分类下的导航项
INSERT INTO navs (category_id, title, url, description, icon, sort_order) VALUES
(@backend_id, 'MyBatis', 'https://mybatis.org/mybatis-3/', 'Java持久层框架', 'https://files.codelife.cc/user-website-icon/20220803/J_G1ipNrekOYJSmTCACZ99269.png', 1),
(@backend_id, 'Spring', 'https://spring.io/', 'Java企业级开发框架', 'https://files.codelife.cc/website/5b307dd14c14a60c5612d29d.png', 2);

-- 前端分类下的导航项
INSERT INTO navs (category_id, title, url, description, icon, sort_order) VALUES
(@frontend_id, 'React', 'https://react.dev/', '用于构建用户界面的JavaScript库', 'https://files.codelife.cc/website/react.svg', 1),
(@frontend_id, 'Vue.js', 'https://vuejs.org/', '渐进式JavaScript框架', 'https://files.codelife.cc/website/vue.svg', 2);



```

> 提示：若子查询/变量查不到对应分类（返回 NULL），将违反外键约束导致插入失败。请先创建并确认分类存在再插入导航项。

{{ ... }}