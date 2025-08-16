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


DROP TABLE IF EXISTS navs;
DROP TABLE IF EXISTS nav_categories;
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
INSERT OR IGNORE INTO nav_categories (name, parent_id, description, sort_order, level, is_public) VALUES 
('编程网站', NULL, '编程相关的网站集合', 1, 1, 1),
('工具网站', NULL, '各类实用工具网站', 2, 1, 1),
('免费观影', NULL, '免费影视资源网站', 3, 1, 1),
('热门推荐', NULL, '热门推荐网站', 4, 1, 1),
('软件下载', NULL, '软件下载资源', 5, 1, 1);

-- 获取一级分类ID（在应用代码中执行）
SELECT id FROM nav_categories WHERE name = '编程网站' AND parent_id IS NULL LIMIT 1;
SELECT id FROM nav_categories WHERE name = '工具网站' AND parent_id IS NULL LIMIT 1;
SELECT id FROM nav_categories WHERE name = '免费观影' AND parent_id IS NULL LIMIT 1;
SELECT id FROM nav_categories WHERE name = '软件下载' AND parent_id IS NULL LIMIT 1;

-- 插入二级分类（子分类）
-- 编程网站下的子分类
INSERT OR IGNORE INTO nav_categories (name, parent_id, description, sort_order, level, is_public) 
SELECT '编码工具', id, '编码和开发工具', 1, 2, 1 FROM nav_categories WHERE name = '编程网站' AND parent_id IS NULL;

INSERT OR IGNORE INTO nav_categories (name, parent_id, description, sort_order, level, is_public) 
SELECT '后端', id, '后端开发资源', 2, 2, 1 FROM nav_categories WHERE name = '编程网站' AND parent_id IS NULL;

INSERT OR IGNORE INTO nav_categories (name, parent_id, description, sort_order, level, is_public) 
SELECT '前端', id, '前端开发资源', 3, 2, 1 FROM nav_categories WHERE name = '编程网站' AND parent_id IS NULL;

INSERT OR IGNORE INTO nav_categories (name, parent_id, description, sort_order, level, is_public) 
SELECT '第三方对接', id, '第三方API和服务对接', 4, 2, 1 FROM nav_categories WHERE name = '编程网站' AND parent_id IS NULL;

INSERT OR IGNORE INTO nav_categories (name, parent_id, description, sort_order, level, is_public) 
SELECT '学习资源', id, '编程学习资源', 5, 2, 1 FROM nav_categories WHERE name = '编程网站' AND parent_id IS NULL;

INSERT OR IGNORE INTO nav_categories (name, parent_id, description, sort_order, level, is_public) 
SELECT '论坛区域', id, '技术论坛和社区', 6, 2, 1 FROM nav_categories WHERE name = '编程网站' AND parent_id IS NULL;

-- 工具网站下的子分类
INSERT OR IGNORE INTO nav_categories (name, parent_id, description, sort_order, level, is_public) 
SELECT 'PDF工具', id, 'PDF文件处理工具', 1, 2, 1 FROM nav_categories WHERE name = '工具网站' AND parent_id IS NULL;

INSERT OR IGNORE INTO nav_categories (name, parent_id, description, sort_order, level, is_public) 
SELECT '视频下载', id, '在线视频下载工具', 2, 2, 1 FROM nav_categories WHERE name = '工具网站' AND parent_id IS NULL;

INSERT OR IGNORE INTO nav_categories (name, parent_id, description, sort_order, level, is_public) 
SELECT '系统工具', id, '系统相关工具', 3, 2, 1 FROM nav_categories WHERE name = '工具网站' AND parent_id IS NULL;

INSERT OR IGNORE INTO nav_categories (name, parent_id, description, sort_order, level, is_public) 
SELECT '数码相关', id, '数码产品相关工具', 4, 2, 1 FROM nav_categories WHERE name = '工具网站' AND parent_id IS NULL;

INSERT OR IGNORE INTO nav_categories (name, parent_id, description, sort_order, level, is_public) 
SELECT '文件传输', id, '文件传输工具', 5, 2, 1 FROM nav_categories WHERE name = '工具网站' AND parent_id IS NULL;

INSERT OR IGNORE INTO nav_categories (name, parent_id, description, sort_order, level, is_public) 
SELECT '自媒体工具', id, '自媒体创作工具', 6, 2, 1 FROM nav_categories WHERE name = '工具网站' AND parent_id IS NULL;

-- 免费观影下的子分类
INSERT OR IGNORE INTO nav_categories (name, parent_id, description, sort_order, level, is_public) 
SELECT '在线观影', id, '在线观看影视资源', 1, 2, 1 FROM nav_categories WHERE name = '免费观影' AND parent_id IS NULL;

INSERT OR IGNORE INTO nav_categories (name, parent_id, description, sort_order, level, is_public) 
SELECT 'DB下载', id, '影视资源下载', 2, 2, 1 FROM nav_categories WHERE name = '免费观影' AND parent_id IS NULL;

INSERT OR IGNORE INTO nav_categories (name, parent_id, description, sort_order, level, is_public) 
SELECT '字幕下载', id, '字幕资源下载', 3, 2, 1 FROM nav_categories WHERE name = '免费观影' AND parent_id IS NULL;

INSERT OR IGNORE INTO nav_categories (name, parent_id, description, sort_order, level, is_public) 
SELECT '动漫网站', id, '动漫资源网站', 4, 2, 1 FROM nav_categories WHERE name = '免费观影' AND parent_id IS NULL;

-- 软件下载下的子分类
INSERT OR IGNORE INTO nav_categories (name, parent_id, description, sort_order, level, is_public) 
SELECT 'PC/安卓', id, 'PC和安卓软件下载', 1, 2, 1 FROM nav_categories WHERE name = '软件下载' AND parent_id IS NULL;

INSERT OR IGNORE INTO nav_categories (name, parent_id, description, sort_order, level, is_public) 
SELECT '浏览器插件', id, '浏览器插件下载', 2, 2, 1 FROM nav_categories WHERE name = '软件下载' AND parent_id IS NULL;

INSERT OR IGNORE INTO nav_categories (name, parent_id, description, sort_order, level, is_public) 
SELECT '系统镜像下载', id, '系统镜像下载', 3, 2, 1 FROM nav_categories WHERE name = '软件下载' AND parent_id IS NULL;
```

### 2. 添加导航菜单项

根据 data.json 中的具体数据，添加导航项示例。

- SQLite 版本（推荐）：通过子查询获取分类 id，确保 category_id 正确链接到 nav_categories.id。

#### **编程网站、工具网站：**

**编程网站区域（92个网站）：**

- 编码工具：33个网站（MarsCode、GitHub、Gitee、Docker等）
- 后端：17个网站（MyBatis、Spring、MySQL、Redis等）
- 前端：16个网站（React、Vue、TypeScript、Element等）
- 第三方对接：12个网站（企业微信、支付宝、飞书等API）
- 学习资源：8个网站（菜鸟教程、慕课网、CSDN等）
- 论坛区域：8个网站（技术社区、问答平台等）

**工具网站区域（35个网站）：**

- PDF工具：7个网站（iLovePDF、PDF转换器等）
- 视频下载：4个网站（Y2mate、SaveFrom等）
- 系统工具：4个网站（kms.cx、优启通等）
- 数码相关：11个网站（鲁大师、CPU性能测试等）
- 文件传输：6个网站（文叔叔、WeTransfer等）
- 自媒体工具：3个网站（Markdown编辑器等）



```sql
-- 编码工具分类下的导航项（31个网站）
INSERT INTO navs (category_id, title, url, description, icon, sort_order) VALUES
((SELECT id FROM nav_categories WHERE name = '编码工具' LIMIT 1), 'MarsCode', 'https://www.marscode.cn/?utm_source=advertising&utm_medium=itablink_ug_cpa&utm_term=hw_marscode_itablink&utm_content=home', 'AI驱动的云开发平台', 'fa-solid fa-code', 1),
((SELECT id FROM nav_categories WHERE name = '编码工具' LIMIT 1), '码云Gitee', 'https://gitee.com/', '国内领先的代码托管平台', 'https://files.codelife.cc/website/gitee.svg', 2),
((SELECT id FROM nav_categories WHERE name = '编码工具' LIMIT 1), 'GitHub', 'https://github.com/', '全球最大的代码托管平台', 'https://files.codelife.cc/website/github.svg', 3),
((SELECT id FROM nav_categories WHERE name = '编码工具' LIMIT 1), 'Vercel', 'https://vercel.com/', '前端应用部署平台', 'fa-solid fa-rocket', 4),
((SELECT id FROM nav_categories WHERE name = '编码工具' LIMIT 1), 'gitcode', 'https://gitcode.net/', '开源代码托管平台', 'https://gitcode.net/uploads/-/system/appearance/favicon/1/icon.png', 5),
((SELECT id FROM nav_categories WHERE name = '编码工具' LIMIT 1), 'CodePen', 'http://codepen.io', '在线代码编辑器', 'https://files.codelife.cc/website/codepen.svg', 6),
((SELECT id FROM nav_categories WHERE name = '编码工具' LIMIT 1), 'Vite', 'https://vitejs.dev/', '下一代前端构建工具', 'https://files.codelife.cc/website/vitejs.svg', 7),
((SELECT id FROM nav_categories WHERE name = '编码工具' LIMIT 1), 'gulp.js', 'https://www.gulpjs.com.cn', '自动化构建工具', 'https://files.codelife.cc/icons/5b583b22e7be2e1804a3dc47.png', 8),
((SELECT id FROM nav_categories WHERE name = '编码工具' LIMIT 1), 'npm', 'https://www.npmjs.com/', 'Node.js包管理器', 'fa-solid fa-cube', 9),
((SELECT id FROM nav_categories WHERE name = '编码工具' LIMIT 1), 'Repository', 'https://mvnrepository.com/', 'Maven中央仓库', 'https://files.codelife.cc/website/5acb1d9017fa1105a20f93ec.png', 10),
((SELECT id FROM nav_categories WHERE name = '编码工具' LIMIT 1), 'mavenlibs', 'https://mavenlibs.com/', 'Maven依赖库搜索', 'fa-solid fa-search', 11),
((SELECT id FROM nav_categories WHERE name = '编码工具' LIMIT 1), 'Maven', 'https://maven.apache.org/', 'Java项目管理工具', 'https://files.codelife.cc/website/5b3110634c14a60c5612d3e1.png', 12),
((SELECT id FROM nav_categories WHERE name = '编码工具' LIMIT 1), 'BootCDN', 'https://www.bootcdn.cn/', '免费CDN加速服务', 'https://files.codelife.cc/icons/60b9eadfae5a9ba4024b397e.png', 13),
((SELECT id FROM nav_categories WHERE name = '编码工具' LIMIT 1), 'Staticfile CDN', 'http://www.staticfile.org/', '静态文件CDN服务', 'fa-solid fa-cloud', 14),
((SELECT id FROM nav_categories WHERE name = '编码工具' LIMIT 1), 'jsDelivr', 'https://www.jsdelivr.com/', '免费开源CDN服务', 'https://files.codelife.cc/icons/www.jsdelivr.com.svg', 15),
((SELECT id FROM nav_categories WHERE name = '编码工具' LIMIT 1), 'unpkg', 'https://unpkg.com/', 'npm包CDN服务', 'fa-solid fa-box', 16),
((SELECT id FROM nav_categories WHERE name = '编码工具' LIMIT 1), '亚云', 'https://www.asiayun.com/', '云服务器托管平台', 'https://files.codelife.cc/website/asiayun.svg', 17),
((SELECT id FROM nav_categories WHERE name = '编码工具' LIMIT 1), '七牛云存储', 'https://s.qiniu.com/naaI7f', '对象存储和CDN服务', 'https://files.codelife.cc/website/qiniu.svg', 18),
((SELECT id FROM nav_categories WHERE name = '编码工具' LIMIT 1), '仓库服务', 'https://developer.aliyun.com/mvn/guide', '阿里云Maven仓库', 'fa-solid fa-warehouse', 19),
((SELECT id FROM nav_categories WHERE name = '编码工具' LIMIT 1), 'Tomcat', 'https://tomcat.apache.org/', 'Java Web服务器', 'fa-solid fa-server', 20),
((SELECT id FROM nav_categories WHERE name = '编码工具' LIMIT 1), 'Docker', 'https://www.docker.com/', '容器化应用平台', 'https://files.codelife.cc/website/docker.svg', 21),
((SELECT id FROM nav_categories WHERE name = '编码工具' LIMIT 1), 'Jenkins', 'https://www.jenkins.io/', '持续集成工具', 'https://files.codelife.cc/website/jenkins.svg', 22),
((SELECT id FROM nav_categories WHERE name = '编码工具' LIMIT 1), 'Postman', 'https://www.postman.com/', 'API开发测试工具', 'https://files.codelife.cc/website/postman.svg', 23),
((SELECT id FROM nav_categories WHERE name = '编码工具' LIMIT 1), 'Insomnia', 'https://insomnia.rest/', 'REST API客户端', 'https://files.codelife.cc/website/insomnia.svg', 24),
((SELECT id FROM nav_categories WHERE name = '编码工具' LIMIT 1), 'Apifox', 'https://www.apifox.cn/', 'API一体化协作平台', 'https://files.codelife.cc/icons/www.apifox.cn.svg', 25),
((SELECT id FROM nav_categories WHERE name = '编码工具' LIMIT 1), 'Eolink', 'https://www.eolink.com/', 'API管理平台', 'https://files.codelife.cc/icons/www.eolink.com.svg', 26),
((SELECT id FROM nav_categories WHERE name = '编码工具' LIMIT 1), 'ShowDoc', 'https://www.showdoc.com.cn/', '在线API文档工具', 'https://files.codelife.cc/icons/www.showdoc.com.cn.svg', 27),
((SELECT id FROM nav_categories WHERE name = '编码工具' LIMIT 1), '语雀', 'https://www.yuque.com/', '专业的云端知识库', 'https://files.codelife.cc/icons/www.yuque.com.svg', 28),
((SELECT id FROM nav_categories WHERE name = '编码工具' LIMIT 1), 'Notion', 'https://www.notion.so/', '一体化工作空间', 'https://files.codelife.cc/website/notion.svg', 29),
((SELECT id FROM nav_categories WHERE name = '编码工具' LIMIT 1), 'Figma', 'https://www.figma.com/', '协作式设计工具', 'https://files.codelife.cc/website/figma.svg', 30),
((SELECT id FROM nav_categories WHERE name = '编码工具' LIMIT 1), 'Sketch', 'https://www.sketch.com/', '矢量图形设计工具', 'https://files.codelife.cc/website/sketch.svg', 31),
((SELECT id FROM nav_categories WHERE name = '编码工具' LIMIT 1), 'Canva可画', 'https://www.canva.cn/', '在线设计工具平台', 'https://files.codelife.cc/website/canva.svg', 32),
((SELECT id FROM nav_categories WHERE name = '编码工具' LIMIT 1), 'ProcessOn', 'https://www.processon.com/', '在线流程图制作', 'https://files.codelife.cc/icons/www.processon.com.svg', 33);

-- 后端分类下的导航项（17个网站）
INSERT INTO navs (category_id, title, url, description, icon, sort_order) VALUES
((SELECT id FROM nav_categories WHERE name = '后端' LIMIT 1), 'MyBatis', 'https://mybatis.org/mybatis-3/', 'Java持久层框架', 'https://files.codelife.cc/user-website-icon/20220803/J_G1ipNrekOYJSmTCACZ99269.png', 1),
((SELECT id FROM nav_categories WHERE name = '后端' LIMIT 1), 'MyBatis-Plus', 'https://baomidou.com/', 'MyBatis增强工具', 'https://files.codelife.cc/icons/20bacf68b2efe5b2.png', 2),
((SELECT id FROM nav_categories WHERE name = '后端' LIMIT 1), 'Maven', 'https://maven.apache.org/', 'Java项目管理工具', 'https://files.codelife.cc/website/5b3110634c14a60c5612d3e1.png', 3),
((SELECT id FROM nav_categories WHERE name = '后端' LIMIT 1), 'MySQL', 'https://dev.mysql.com/', '开源关系型数据库', 'https://files.codelife.cc/website/5f4386f4aa121b0c2ac69e22.png', 4),
((SELECT id FROM nav_categories WHERE name = '后端' LIMIT 1), 'Spring', 'https://spring.io/', 'Java企业级开发框架', 'https://files.codelife.cc/website/5b307dd14c14a60c5612d29d.png', 5),
((SELECT id FROM nav_categories WHERE name = '后端' LIMIT 1), 'AspectJ', 'http://www.eclipse.org/aspectj/', '面向切面编程框架', 'https://files.codelife.cc/user-website-icon/20220814/wRMKMVFZ1rcjFhTxnLOeM9848.png', 6),
((SELECT id FROM nav_categories WHERE name = '后端' LIMIT 1), 'Kotlin 语言中文站', 'https://www.kotlincn.net/', '现代化编程语言', 'https://www.kotlincn.net/assets/images/apple-touch-icon-72x72.png', 7),
((SELECT id FROM nav_categories WHERE name = '后端' LIMIT 1), 'Repository', 'https://mvnrepository.com/', 'Maven中央仓库', 'https://files.codelife.cc/website/5acb1d9017fa1105a20f93ec.png', 8),
((SELECT id FROM nav_categories WHERE name = '后端' LIMIT 1), 'Redis', 'https://redis.io/', '内存数据结构存储', 'https://files.codelife.cc/website/redis.svg', 9),
((SELECT id FROM nav_categories WHERE name = '后端' LIMIT 1), 'MongoDB', 'https://www.mongodb.com/', '文档型数据库', 'https://files.codelife.cc/website/mongodb.svg', 10),
((SELECT id FROM nav_categories WHERE name = '后端' LIMIT 1), 'PostgreSQL', 'https://www.postgresql.org/', '高级开源关系型数据库', 'https://files.codelife.cc/website/postgresql.svg', 11),
((SELECT id FROM nav_categories WHERE name = '后端' LIMIT 1), 'Elasticsearch', 'https://www.elastic.co/', '分布式搜索引擎', 'https://files.codelife.cc/website/elasticsearch.svg', 12),
((SELECT id FROM nav_categories WHERE name = '后端' LIMIT 1), 'Apache Kafka', 'https://kafka.apache.org/', '分布式流处理平台', 'https://files.codelife.cc/website/kafka.svg', 13),
((SELECT id FROM nav_categories WHERE name = '后端' LIMIT 1), 'Apache ZooKeeper', 'https://zookeeper.apache.org/', '分布式协调服务', 'https://files.codelife.cc/website/zookeeper.svg', 14),
((SELECT id FROM nav_categories WHERE name = '后端' LIMIT 1), 'Apache Dubbo', 'https://dubbo.apache.org/', '高性能RPC框架', 'https://files.codelife.cc/website/dubbo.svg', 15),
((SELECT id FROM nav_categories WHERE name = '后端' LIMIT 1), 'Nginx', 'https://nginx.org/', '高性能Web服务器', 'https://files.codelife.cc/website/nginx.svg', 16),
((SELECT id FROM nav_categories WHERE name = '后端' LIMIT 1), 'JetBrains全家桶激活', 'https://jetbrains.asiones.com/', '每日提供最新jetbrains全家桶激活服务器', 'https://www.xiaozhongjishu.com/wp-content/uploads/2024/08/80e76-jetbrains.asiones.com.png', 17);

-- 前端分类下的导航项（16个网站）
INSERT INTO navs (category_id, title, url, description, icon, sort_order) VALUES
((SELECT id FROM nav_categories WHERE name = '前端' LIMIT 1), 'React', 'https://react.dev/', '用于构建用户界面的库', 'https://files.codelife.cc/website/react.svg', 1),
((SELECT id FROM nav_categories WHERE name = '前端' LIMIT 1), 'Nuxt.js', 'https://nuxt.com/', 'Vue.js应用框架', 'fa-solid fa-layer-group', 2),
((SELECT id FROM nav_categories WHERE name = '前端' LIMIT 1), 'TypeScript', 'https://www.typescriptlang.org/', 'JavaScript的超集', 'https://files.codelife.cc/website/typescript.svg', 3),
((SELECT id FROM nav_categories WHERE name = '前端' LIMIT 1), 'Vite', 'https://vitejs.dev/', '下一代前端构建工具', 'https://files.codelife.cc/website/vitejs.svg', 4),
((SELECT id FROM nav_categories WHERE name = '前端' LIMIT 1), 'Arco Design', 'https://arco.design/', '企业级设计语言', 'fa-solid fa-palette', 5),
((SELECT id FROM nav_categories WHERE name = '前端' LIMIT 1), 'Ant Design Vue', 'https://antdv.com/', 'Vue企业级UI组件库', 'https://files.codelife.cc/website/ant-design-vue.svg', 6),
((SELECT id FROM nav_categories WHERE name = '前端' LIMIT 1), 'iView', 'https://iviewui.com/', 'Vue.js UI组件库', 'fa-solid fa-cube', 7),
((SELECT id FROM nav_categories WHERE name = '前端' LIMIT 1), 'Vue2', 'https://v2.vuejs.org/', 'Vue.js 2.x版本文档', 'https://files.codelife.cc/website/vuejs.svg', 8),
((SELECT id FROM nav_categories WHERE name = '前端' LIMIT 1), 'Vue3', 'https://vuejs.org/', '渐进式JavaScript框架', 'https://files.codelife.cc/website/vuejs.svg', 9),
((SELECT id FROM nav_categories WHERE name = '前端' LIMIT 1), 'Element', 'https://element.eleme.io/', 'Vue 2组件库', 'fa-solid fa-th', 10),
((SELECT id FROM nav_categories WHERE name = '前端' LIMIT 1), 'Element-Plus', 'https://element-plus.org/', 'Vue 3组件库', 'fa-solid fa-th-large', 11),
((SELECT id FROM nav_categories WHERE name = '前端' LIMIT 1), 'EasyUI', 'https://www.jeasyui.com/', 'jQuery UI组件库', 'fa-solid fa-window-maximize', 12),
((SELECT id FROM nav_categories WHERE name = '前端' LIMIT 1), 'Layui', 'https://layui.dev/', '经典模块化前端框架', 'fa-solid fa-layer-group', 13),
((SELECT id FROM nav_categories WHERE name = '前端' LIMIT 1), 'ZUI', 'https://openzui.com/', '开源HTML5跨屏框架', 'fa-solid fa-mobile-alt', 14),
((SELECT id FROM nav_categories WHERE name = '前端' LIMIT 1), 'AXUI前端框架', 'https://axui.org/', '轻量级前端UI框架', 'fa-solid fa-code', 15),
((SELECT id FROM nav_categories WHERE name = '前端' LIMIT 1), 'VUE后台管理系统模板', 'https://vue-admin-template.com/', 'Vue管理系统模板', 'fa-solid fa-tachometer-alt', 16);

-- 第三方对接分类下的导航项（12个网站）
INSERT INTO navs (category_id, title, url, description, icon, sort_order) VALUES
((SELECT id FROM nav_categories WHERE name = '第三方对接' LIMIT 1), '企业微信开发', 'https://developer.work.weixin.qq.com/', '企业级办公通讯API', 'fa-brands fa-weixin', 1),
((SELECT id FROM nav_categories WHERE name = '第三方对接' LIMIT 1), '支付宝商家平台', 'https://open.alipay.com/', '移动支付接口服务', 'https://img.alicdn.com/tfs/TB1qEwuzrj1gK0jSZFOXXc7GpXa-32-32.ico', 2),
((SELECT id FROM nav_categories WHERE name = '第三方对接' LIMIT 1), '飞书开放平台', 'https://open.feishu.cn/', '协作办公开发平台', 'https://sf3-scmcdn-cn.feishucdn.com/obj/feishu-static/developer/console/frontend/favicon-logo.svg', 3),
((SELECT id FROM nav_categories WHERE name = '第三方对接' LIMIT 1), '闲鱼小程序文档', 'https://miniapp.xianyu.com/', '二手交易小程序开发', 'fa-solid fa-mobile', 4),
((SELECT id FROM nav_categories WHERE name = '第三方对接' LIMIT 1), '阿奇索', 'https://www.archiso.org/', '第三方服务平台', 'fa-solid fa-plug', 5),
((SELECT id FROM nav_categories WHERE name = '第三方对接' LIMIT 1), 'Server酱', 'https://sct.ftqq.com/', '消息推送服务', 'fa-solid fa-bell', 6),
((SELECT id FROM nav_categories WHERE name = '第三方对接' LIMIT 1), '闲鱼开放平台', 'https://open.xianyu.com/', '二手交易API接口', 'fa-solid fa-shopping-cart', 7),
((SELECT id FROM nav_categories WHERE name = '第三方对接' LIMIT 1), '淘宝联盟开放平台', 'https://open.taobao.com/', '电商推广API服务', 'fa-solid fa-store', 8),
((SELECT id FROM nav_categories WHERE name = '第三方对接' LIMIT 1), '欢拓云直播', 'https://www.talk-fun.com/', '在线直播技术服务', 'fa-solid fa-video', 9),
((SELECT id FROM nav_categories WHERE name = '第三方对接' LIMIT 1), '易游数据', 'https://www.yiyou.com/', '游戏数据分析平台', 'fa-solid fa-gamepad', 10),
((SELECT id FROM nav_categories WHERE name = '第三方对接' LIMIT 1), '科益网络验证', 'https://www.keyi.net/', '软件授权验证系统', 'fa-solid fa-shield-alt', 11),
((SELECT id FROM nav_categories WHERE name = '第三方对接' LIMIT 1), '文心云网络验证', 'https://www.wenxinyun.com/', '网络验证解决方案', 'fa-solid fa-lock', 12);

-- 学习资源分类下的导航项（8个网站）
INSERT INTO navs (category_id, title, url, description, icon, sort_order) VALUES
((SELECT id FROM nav_categories WHERE name = '学习资源' LIMIT 1), '菜鸟教程', 'https://www.runoob.com/', '编程入门学习平台', 'https://files.codelife.cc/website/runoob.svg', 1),
((SELECT id FROM nav_categories WHERE name = '学习资源' LIMIT 1), 'w3cschool', 'https://www.w3cschool.cn/', 'Web技术学习网站', 'https://files.codelife.cc/website/w3cschool.svg', 2),
((SELECT id FROM nav_categories WHERE name = '学习资源' LIMIT 1), '慕课网', 'https://www.imooc.com/', '在线编程视频教程', 'https://files.codelife.cc/website/imooc.svg', 3),
((SELECT id FROM nav_categories WHERE name = '学习资源' LIMIT 1), 'CSDN', 'https://www.csdn.net/', '中文技术社区博客', 'https://files.codelife.cc/website/csdn.svg', 4),
((SELECT id FROM nav_categories WHERE name = '学习资源' LIMIT 1), '博客园', 'https://www.cnblogs.com/', '.NET技术博客平台', 'https://files.codelife.cc/icons/www.cnblogs.com.svg', 5),
((SELECT id FROM nav_categories WHERE name = '学习资源' LIMIT 1), '掘金', 'https://juejin.cn/', '技术社区和分享平台', 'fa-solid fa-gem', 6),
((SELECT id FROM nav_categories WHERE name = '学习资源' LIMIT 1), 'Stack Overflow', 'https://stackoverflow.com/', '程序员问答社区', 'fa-brands fa-stack-overflow', 7),
((SELECT id FROM nav_categories WHERE name = '学习资源' LIMIT 1), 'GitHub', 'https://github.com/', '开源代码学习平台', 'https://files.codelife.cc/website/github.svg', 8);

-- 论坛区域分类下的导航项（8个网站）
INSERT INTO navs (category_id, title, url, description, icon, sort_order) VALUES
((SELECT id FROM nav_categories WHERE name = '论坛区域' LIMIT 1), 'CSDN', 'https://www.csdn.net/', '中文技术社区博客', 'https://files.codelife.cc/website/csdn.svg', 1),
((SELECT id FROM nav_categories WHERE name = '论坛区域' LIMIT 1), '博客园', 'https://www.cnblogs.com/', '.NET技术博客平台', 'https://files.codelife.cc/icons/www.cnblogs.com.svg', 2),
((SELECT id FROM nav_categories WHERE name = '论坛区域' LIMIT 1), '掘金', 'https://juejin.cn/', '技术社区和分享平台', 'fa-solid fa-gem', 3),
((SELECT id FROM nav_categories WHERE name = '论坛区域' LIMIT 1), 'V2EX', 'https://www.v2ex.com/', '创意工作者社区', 'fa-solid fa-comments', 4),
((SELECT id FROM nav_categories WHERE name = '论坛区域' LIMIT 1), 'Ruby China', 'https://ruby-china.org/', 'Ruby技术社区', 'fa-solid fa-gem', 5),
((SELECT id FROM nav_categories WHERE name = '论坛区域' LIMIT 1), 'SegmentFault', 'https://segmentfault.com/', '技术问答社区', 'fa-solid fa-question-circle', 6),
((SELECT id FROM nav_categories WHERE name = '论坛区域' LIMIT 1), '开源中国', 'https://www.oschina.net/', '中文开源技术社区', 'fa-solid fa-code-branch', 7),
((SELECT id FROM nav_categories WHERE name = '论坛区域' LIMIT 1), '软件宝库', 'https://www.softwarerepo.com/', '专注分享各种专业软件的飞书共享文档', 'fa-solid fa-archive', 8);

-- ========== 工具网站区域 ==========

-- PDF工具分类下的导航项（7个网站）
INSERT INTO navs (category_id, title, url, description, icon, sort_order) VALUES
((SELECT id FROM nav_categories WHERE name = 'PDF工具' LIMIT 1), 'iLovePDF', 'https://www.ilovepdf.com/', '完全免费的PDF工具', 'fa-solid fa-file-pdf', 1),
((SELECT id FROM nav_categories WHERE name = 'PDF工具' LIMIT 1), 'PDF转换器', 'https://www.pdf-converter.com/', '一款免费的PDF转word工具', 'fa-solid fa-exchange-alt', 2),
((SELECT id FROM nav_categories WHERE name = 'PDF工具' LIMIT 1), 'Pdf2Go', 'https://www.pdf2go.com/', '在线PDF处理工具', 'fa-solid fa-file-pdf', 3),
((SELECT id FROM nav_categories WHERE name = 'PDF工具' LIMIT 1), 'ALL2ALL', 'https://www.all2all.com/', '万能格式转换工具', 'fa-solid fa-sync-alt', 4),
((SELECT id FROM nav_categories WHERE name = 'PDF工具' LIMIT 1), 'PDF.IO', 'https://pdf.io/', '简单易用的PDF工具', 'fa-solid fa-file-pdf', 5),
((SELECT id FROM nav_categories WHERE name = 'PDF工具' LIMIT 1), '在线文档转换', 'https://www.online-convert.com/', '多格式在线转换工具', 'fa-solid fa-file-alt', 6),
((SELECT id FROM nav_categories WHERE name = 'PDF工具' LIMIT 1), 'PDF24 Tools', 'https://tools.pdf24.org/', '免费PDF在线工具集', 'fa-solid fa-toolbox', 7);

-- 视频下载分类下的导航项（4个网站）
INSERT INTO navs (category_id, title, url, description, icon, sort_order) VALUES
((SELECT id FROM nav_categories WHERE name = '视频下载' LIMIT 1), 'Y2mate', 'https://www.y2mate.com', 'YouTube视频下载', 'fa-brands fa-youtube', 1),
((SELECT id FROM nav_categories WHERE name = '视频下载' LIMIT 1), 'SaveFrom', 'https://savefrom.net', '多平台视频下载', 'fa-solid fa-download', 2),
((SELECT id FROM nav_categories WHERE name = '视频下载' LIMIT 1), 'VideoFK', 'https://www.videofk.com', '在线视频解析下载', 'fa-solid fa-video', 3),
((SELECT id FROM nav_categories WHERE name = '视频下载' LIMIT 1), '唧唧Down', 'https://www.jijidown.com', 'B站视频下载工具', 'fa-solid fa-film', 4);

-- 系统工具分类下的导航项（4个网站）
INSERT INTO navs (category_id, title, url, description, icon, sort_order) VALUES
((SELECT id FROM nav_categories WHERE name = '系统工具' LIMIT 1), 'kms.cx', 'https://kms.cx/', '提供免费KMS激活服务，支持Windows系统和Office软件一键激活', 'https://www.xiaozhongjishu.com/wp-content/uploads/2025/06/1749364953-windows-1.png', 1),
((SELECT id FROM nav_categories WHERE name = '系统工具' LIMIT 1), '优启通', 'http://uqitong.com/', '纯净无广告无植入', 'https://www.xiaozhongjishu.com/wp-content/uploads/2022/03/c982a-uqitong.com.png', 2),
((SELECT id FROM nav_categories WHERE name = '系统工具' LIMIT 1), 'FirPE装机工具', 'https://firpe.cn/', '纯净PE装机工具', 'https://www.xiaozhongjishu.com/wp-content/uploads/2022/03/90d9a-firpe.cn.png', 3),
((SELECT id FROM nav_categories WHERE name = '系统工具' LIMIT 1), '微PE工具箱', 'https://www.wepe.com.cn/', '纯净PE装系统工具', 'https://www.xiaozhongjishu.com/wp-content/uploads/2022/03/74e96-www.wepe.com.cn.png', 4);

-- 数码相关分类下的导航项（11个网站）
INSERT INTO navs (category_id, title, url, description, icon, sort_order) VALUES
((SELECT id FROM nav_categories WHERE name = '数码相关' LIMIT 1), '鲁大师天梯榜', 'https://www.ludashi.com/rank/cpuRanking.html', '专业硬件性能排行榜单', 'https://www.xiaozhongjishu.com/wp-content/uploads/2025/01/1737468380-ludashi.png', 1),
((SELECT id FROM nav_categories WHERE name = '数码相关' LIMIT 1), 'SiliconCat', 'https://siliconcat.net', 'CPU、GPU性能对比查看', 'https://www.xiaozhongjishu.com/wp-content/uploads/2024/12/1734238445-logo-tuya.png', 2),
((SELECT id FROM nav_categories WHERE name = '数码相关' LIMIT 1), '显卡性能天梯图', 'https://m.ithome.com/html/projects/graphics/index.html', 'IT之家出品的显卡性能天梯图', 'https://www.xiaozhongjishu.com/wp-content/uploads/2024/04/6be7e-m.ithome.com.png', 3),
((SELECT id FROM nav_categories WHERE name = '数码相关' LIMIT 1), '手机CPU性能天梯图', 'https://www.mydrivers.com/zhuanti/tianti/01', '快科技手机CPU性能排行', 'https://www.xiaozhongjishu.com/wp-content/uploads/2024/04/cab0a-www.mydrivers.com.png', 4),
((SELECT id FROM nav_categories WHERE name = '数码相关' LIMIT 1), 'CPU-Z Benchmark', 'https://valid.x86.fr/bench/1', '桌面CPU单核多核性能排行', 'https://www.xiaozhongjishu.com/wp-content/uploads/2024/04/ade18-valid.x86.fr.png', 5),
((SELECT id FROM nav_categories WHERE name = '数码相关' LIMIT 1), '手机型号汇总 MobileModels', 'https://khwang9883.github.io/MobileModels', '各厂商手机型号与宣传名汇总', 'https://www.xiaozhongjishu.com/wp-content/uploads/2024/03/手机 - 1.png', 6),
((SELECT id FROM nav_categories WHERE name = '数码相关' LIMIT 1), 'SCOPK 极客湾移动芯片排行', 'https://www.socpk.com', '极客湾手机处理器排行数据', 'https://www.xiaozhongjishu.com/wp-content/uploads/2024/02/c0c57-www.socpk.com.png', 7),
((SELECT id FROM nav_categories WHERE name = '数码相关' LIMIT 1), 'TopCPU', 'https://www.topcpu.net', 'CPU和GPU规格对比与性能评级', 'https://www.xiaozhongjishu.com/wp-content/uploads/2023/11/7e655-www.topcpu.net.png', 8),
((SELECT id FROM nav_categories WHERE name = '数码相关' LIMIT 1), 'iPhone 参数大全', 'https://kylebing.cn/tools/iphone', 'iPhone全系列参数查询', 'https://www.xiaozhongjishu.com/wp-content/uploads/2023/03/c6075-kylebing.cn.png', 9),
((SELECT id FROM nav_categories WHERE name = '数码相关' LIMIT 1), '苹果产品参数中心', 'https://hubapple.cn', 'Apple产品型号查询', 'https://www.xiaozhongjishu.com/wp-content/uploads/2022/04/9da9f-www.onlineit.cn.png', 10),
((SELECT id FROM nav_categories WHERE name = '数码相关' LIMIT 1), 'NotebookCheck', 'https://www.notebookcheck.net/Mobile-Processors-Benchmark-List.2436.0.html', '桌面及手机CPU排行榜', 'https://www.xiaozhongjishu.com/wp-content/uploads/2021/05/mobile-processos.png', 11);

-- 文件传输分类下的导航项（6个网站）
INSERT INTO navs (category_id, title, url, description, icon, sort_order) VALUES
((SELECT id FROM nav_categories WHERE name = '文件传输' LIMIT 1), '文叔叔', 'https://www.wenshushu.cn/', '最大传输5G', 'https://www.xiaozhongjishu.com/wp-content/uploads/2020/11/文叔叔.ico', 1),
((SELECT id FROM nav_categories WHERE name = '文件传输' LIMIT 1), 'WeTransfer', 'https://wetransfer.com', '国际文件传输服务', 'fa-solid fa-cloud-arrow-up', 2),
((SELECT id FROM nav_categories WHERE name = '文件传输' LIMIT 1), 'Firefox Send', 'https://send.firefox.com', 'Mozilla文件分享', 'fa-brands fa-firefox', 3),
((SELECT id FROM nav_categories WHERE name = '文件传输' LIMIT 1), '奶牛快传', 'https://cowtransfer.com/', '免费版最大2G', 'https://www.xiaozhongjishu.com/wp-content/uploads/2020/11/奶牛快传.png', 4),
((SELECT id FROM nav_categories WHERE name = '文件传输' LIMIT 1), 'Airportal', 'https://airportal.cn/', '最大支持2GB文件传输', 'https://www.xiaozhongjishu.com/wp-content/uploads/2022/03/airpotal.png', 5),
((SELECT id FROM nav_categories WHERE name = '文件传输' LIMIT 1), '钛盘', 'https://app.tmp.link/', '最大传输10G', 'https://www.xiaozhongjishu.com/wp-content/uploads/2021/01/钛盘.png', 6);

-- 自媒体工具分类下的导航项（3个网站）
INSERT INTO navs (category_id, title, url, description, icon, sort_order) VALUES
((SELECT id FROM nav_categories WHERE name = '自媒体工具' LIMIT 1), '在线Markdown编辑器', 'https://markdown.com.cn/editor/', '样式主题非常多', 'https://www.xiaozhongjishu.com/wp-content/uploads/2023/08/e43e4-markdown.com.cn.png', 1),
((SELECT id FROM nav_categories WHERE name = '自媒体工具' LIMIT 1), 'MDNice', 'https://www.mdnice.com/', 'Markdown排版', 'https://www.xiaozhongjishu.com/wp-content/uploads/2020/12/mdnice.png', 2),
((SELECT id FROM nav_categories WHERE name = '自媒体工具' LIMIT 1), '可能吧排版', 'https://knb.im/mp/', '公众文章Markdown排版', 'https://www.xiaozhongjishu.com/wp-content/uploads/2020/12/可能吧排版.ico', 3);
```

#### 软件下载：

```sql
-- ========== 软件下载区域 ==========

-- PC/安卓分类下的导航项（32个网站）
INSERT INTO navs (category_id, title, url, description, icon, sort_order) VALUES
((SELECT id FROM nav_categories WHERE name = 'PC/安卓' LIMIT 1), 'Adobe全家桶下载', 'https://www.yuque.com/books/share/0a375170-2bf9-460b-b0e2-a34134e384c1', 'Adobe全系列软件下载', 'https://www.xiaozhongjishu.com/wp-content/uploads/2023/12/bitbug_favicon-3.ico', 1),
((SELECT id FROM nav_categories WHERE name = 'PC/安卓' LIMIT 1), '423Down', 'https://www.423down.com/', '专业软件下载站', 'https://www.xiaozhongjishu.com/wp-content/uploads/2021/11/8cde5-www.423down.com.png', 2),
((SELECT id FROM nav_categories WHERE name = 'PC/安卓' LIMIT 1), '果壳剥壳', 'https://www.ghpym.com/', '软件破解分享平台', 'https://www.xiaozhongjishu.com/wp-content/uploads/2020/12/果壳剥壳.png', 3),
((SELECT id FROM nav_categories WHERE name = 'PC/安卓' LIMIT 1), '开源大世界', 'https://kydsj.vip/doku.php?id=wiki:网站目录', '专注盘点各种开源软件下载地址', 'https://www.xiaozhongjishu.com/wp-content/uploads/2024/03/a09e0-kydsj.vip.png', 4),
((SELECT id FROM nav_categories WHERE name = 'PC/安卓' LIMIT 1), '易破Jie', 'https://www.ypojie.com/', '软件破解资源分享', 'https://www.xiaozhongjishu.com/wp-content/uploads/2020/12/易破解.ico', 5),
((SELECT id FROM nav_categories WHERE name = 'PC/安卓' LIMIT 1), '软仓', 'https://ruancang.net/', '精校 完整 极致 专业软件下载', 'https://www.xiaozhongjishu.com/wp-content/uploads/2023/03/ec199-ruancang.net.png', 6),
((SELECT id FROM nav_categories WHERE name = 'PC/安卓' LIMIT 1), 'JetBrains全家桶激活', 'https://jetbrains.asiones.com/', '每日提供最新jetbrains全家桶激活服务器', 'https://www.xiaozhongjishu.com/wp-content/uploads/2024/08/80e76-jetbrains.asiones.com.png', 7),
((SELECT id FROM nav_categories WHERE name = 'PC/安卓' LIMIT 1), '乐于分享网', 'https://fffxx.com/', '爱生活，爱网络！', 'https://www.xiaozhongjishu.com/wp-content/uploads/2025/05/1746323118-logo.png', 8),
((SELECT id FROM nav_categories WHERE name = 'PC/安卓' LIMIT 1), '绿色纯净软件下载', 'https://www.azhongruanjian.com/?from=xzjs_hot', '小众技术旗下软件下载站', 'https://www.xiaozhongjishu.com/wp-content/uploads/2023/09/favicon.ico', 9),
((SELECT id FROM nav_categories WHERE name = 'PC/安卓' LIMIT 1), '软件宝库', 'https://drk3jhz5hb.feishu.cn/base/ZBmDbYu57aPvJwsNgk3c2LWpnwe?table=tbli32fkmWsThsL6&view=vewyeuFTQj', '专注分享各种专业软件的飞书共享文档', 'https://www.xiaozhongjishu.com/wp-content/uploads/2025/07/1751939119-purple_baseV2.jpg', 10),
((SELECT id FROM nav_categories WHERE name = 'PC/安卓' LIMIT 1), 'QiuQuan''s Blog', 'http://www.qiuquan.cc/', '专业的软件分享平台', 'https://www.xiaozhongjishu.com/wp-content/uploads/2025/01/1737640237-qiuquan_ico.png', 11),
((SELECT id FROM nav_categories WHERE name = 'PC/安卓' LIMIT 1), 'OpenAlternative', 'https://openalternative.co/', '专注于提供流行软件的开源替代品', 'https://www.xiaozhongjishu.com/wp-content/uploads/2024/11/1731294909-favicon.png', 12),
((SELECT id FROM nav_categories WHERE name = 'PC/安卓' LIMIT 1), '软件搜搜', 'https://hew666.github.io/rjss/', '可以搜索软件下载源的网站', 'https://www.xiaozhongjishu.com/wp-content/uploads/2024/10/1729474645-github-1.png', 13),
((SELECT id FROM nav_categories WHERE name = 'PC/安卓' LIMIT 1), '系统迷', 'https://www.xitmi.com/', '系统软件资源分享', 'https://www.xiaozhongjishu.com/wp-content/uploads/2022/06/39193-www.xitmi.com.png', 14),
((SELECT id FROM nav_categories WHERE name = 'PC/安卓' LIMIT 1), '蓝鲨', 'https://www.lan-sha.com/', '专注分享各种破解软件', 'https://www.xiaozhongjishu.com/wp-content/uploads/2021/11/a3612-www.bsh.me.png', 15),
((SELECT id FROM nav_categories WHERE name = 'PC/安卓' LIMIT 1), 'Localization', 'http://www.th-sjy.com/', '本地化软件资源', 'https://www.xiaozhongjishu.com/wp-content/uploads/2021/11/426ee-www.th-sjy.com.png', 16),
((SELECT id FROM nav_categories WHERE name = 'PC/安卓' LIMIT 1), '大眼仔', 'http://www.dayanzai.me/', '软件资源分享站', 'https://www.xiaozhongjishu.com/wp-content/uploads/2021/11/c4fbc-www.dayanzai.me.png', 17),
((SELECT id FROM nav_categories WHERE name = 'PC/安卓' LIMIT 1), '盒子部落', 'https://www.hezibuluo.com/', '软件资源分享社区', 'https://www.xiaozhongjishu.com/wp-content/uploads/2020/12/盒子部落.png', 18),
((SELECT id FROM nav_categories WHERE name = 'PC/安卓' LIMIT 1), '清华大学开源镜像站', 'https://tuna.moe/', '清华大学开源软件镜像站', 'https://files.codelife.cc/website/5b7ec3970576296373cac5ce.png', 19),
((SELECT id FROM nav_categories WHERE name = 'PC/安卓' LIMIT 1), '国王软件站', 'https://www.52king.vip/', '国王软件资源分享', 'https://files.codelife.cc/user-website-icon/20241104/uBoInHYxS4sDqmder1Qv87077.png', 20),
((SELECT id FROM nav_categories WHERE name = 'PC/安卓' LIMIT 1), 'HelloWindows', 'https://hellowindows.cn/', 'Hello Windows系统资源', 'https://hellowindows.cn/logo-s.png', 21),
((SELECT id FROM nav_categories WHERE name = 'PC/安卓' LIMIT 1), '夸父资源站', 'https://www.kuafuzys.com/', '夸父资源分享站', 'https://www.kuafuzys.com/view/img/favicon.ico', 22),
((SELECT id FROM nav_categories WHERE name = 'PC/安卓' LIMIT 1), '小刀娱乐网', 'https://www.xiaodao0.com/', '免费资源分享平台，全网干货共享', 'https://files.codelife.cc/icons/5a46150f45f98212f4ddaa73.png', 23),
((SELECT id FROM nav_categories WHERE name = 'PC/安卓' LIMIT 1), '马可菠萝', 'http://www.macbl.com/', 'Mac软件资源分享', 'https://files.codelife.cc/icons/60b9efd9ae5a9ba4024b4980.png', 24),
((SELECT id FROM nav_categories WHERE name = 'PC/安卓' LIMIT 1), '爱纯净', 'http://www.aichunjing.com/', '纯净系统软件资源', 'https://files.codelife.cc/icons/e6a290b3a4b35683.png', 25),
((SELECT id FROM nav_categories WHERE name = 'PC/安卓' LIMIT 1), '小众软件', 'http://www.appinn.com/', '小众软件推荐', 'https://files.codelife.cc/icons/www.appinn.com.svg', 26),
((SELECT id FROM nav_categories WHERE name = 'PC/安卓' LIMIT 1), '爱资料在线工具', 'https://www.toolnb.com/', '在线工具集合', 'https://files.codelife.cc/icons/60b9ebf0ae5a9ba4024b3cf7.png', 27),
((SELECT id FROM nav_categories WHERE name = 'PC/安卓' LIMIT 1), '软件个锤子', 'https://www.rjgcz.com/mzsm', '软件个锤子资源分享', 'https://www.rjgcz.com/wp-content/uploads/2024/06/cropped-软件个锤子 - 01-32x32.jpg', 28),
((SELECT id FROM nav_categories WHERE name = 'PC/安卓' LIMIT 1), '工具123', 'http://www.gjw123.com/', '在线工具集合', 'https://files.codelife.cc/icons/06dbe290eee177e7.png', 29),
((SELECT id FROM nav_categories WHERE name = 'PC/安卓' LIMIT 1), '佛系软件', 'https://foxirj.com/', '佛系软件资源分享', 'https://files.codelife.cc/icons/foxirj.com.svg', 30),
((SELECT id FROM nav_categories WHERE name = 'PC/安卓' LIMIT 1), '爱资源', 'https://www.iwyu.com/', '爱资源分享平台', 'https://files.codelife.cc/icons/iwyu.svg', 31),
((SELECT id FROM nav_categories WHERE name = 'PC/安卓' LIMIT 1), '仓库全能王', 'https://www.hoposoft.com/exechengxu', '全能王软件仓库', 'https://www.hoposoft.com/wp-content/uploads/2021/08/zhanbiao.png', 32),
((SELECT id FROM nav_categories WHERE name = 'PC/安卓' LIMIT 1), '多开鸭', 'https://www.duokaiya.com/', '多开鸭软件工具', 'https://www.duokaiya.com/wp-content/uploads/2023060420540083.png', 33);

-- 浏览器插件分类下的导航项（7个网站）
INSERT INTO navs (category_id, title, url, description, icon, sort_order) VALUES
((SELECT id FROM nav_categories WHERE name = '浏览器插件' LIMIT 1), 'ExtPose插件排行榜', 'https://extpose.com/top-installs', 'Chrome插件安装排行榜', 'https://www.xiaozhongjishu.com/wp-content/uploads/2023/09/55073-extpose.com.png', 1),
((SELECT id FROM nav_categories WHERE name = '浏览器插件' LIMIT 1), 'CrxDL', 'https://crxdl.com/', '免费的Chrome插件下载站', 'https://www.xiaozhongjishu.com/wp-content/uploads/2023/05/88e77-crxdl.com.png', 2),
((SELECT id FROM nav_categories WHERE name = '浏览器插件' LIMIT 1), 'CXYHUB', 'https://www.cxyhub.com/', '优质谷歌插件下载站', 'https://www.xiaozhongjishu.com/wp-content/uploads/2021/11/95d75-www.cxyhub.com.png', 3),
((SELECT id FROM nav_categories WHERE name = '浏览器插件' LIMIT 1), 'Chrome插件下载', 'https://huajiakeji.com/', '谷歌浏览器插件下载', 'https://www.xiaozhongjishu.com/wp-content/uploads/2020/12/Chrome插件下载.ico', 4),
((SELECT id FROM nav_categories WHERE name = '浏览器插件' LIMIT 1), 'Chrome网上应用店', 'https://chrome.google.com/webstore/category/extensions', 'Google官方插件商店', 'fa-brands fa-chrome', 5),
((SELECT id FROM nav_categories WHERE name = '浏览器插件' LIMIT 1), 'Edge插件商店', 'https://microsoftedge.microsoft.com/addons/Microsoft-Edge-Extensions-Home', 'Microsoft Edge官方插件商店', 'fa-brands fa-edge', 6),
((SELECT id FROM nav_categories WHERE name = '浏览器插件' LIMIT 1), 'Firefox插件商店', 'https://addons.mozilla.org/zh-CN/firefox/', 'Firefox官方插件商店', 'fa-brands fa-firefox', 7);

-- 系统镜像下载分类下的导航项（7个网站）
INSERT INTO navs (category_id, title, url, description, icon, sort_order) VALUES
((SELECT id FROM nav_categories WHERE name = '系统镜像下载' LIMIT 1), 'WinNew', 'https://winnew.cn/', '专注于提供微软官方原版Windows系统镜像直链下载', 'https://www.xiaozhongjishu.com/wp-content/uploads/2025/02/1740060771-a2218-9554q.png', 1),
((SELECT id FROM nav_categories WHERE name = '系统镜像下载' LIMIT 1), 'Puresys系统下载站', 'https://sys.puresys.net/index.html', '专注于提供Windows系统纯净版本下载', 'https://www.xiaozhongjishu.com/wp-content/uploads/2025/02/1740058763-windows-6.png', 2),
((SELECT id FROM nav_categories WHERE name = '系统镜像下载' LIMIT 1), 'ITELLYOU系统镜像下载', 'https://next.itellyou.cn/', '著名的Windows原生系统镜像下载站', 'https://www.xiaozhongjishu.com/wp-content/uploads/2023/10/96207-next.itellyou.cn.png', 3),
((SELECT id FROM nav_categories WHERE name = '系统镜像下载' LIMIT 1), 'MSDN我告诉你', 'https://msdn.itellyou.cn/', '经典的Windows系统镜像下载站', 'fa-brands fa-windows', 4),
((SELECT id FROM nav_categories WHERE name = '系统镜像下载' LIMIT 1), '微软官方下载', 'https://www.microsoft.com/zh-cn/software-download/', '微软官方系统下载页面', 'fa-brands fa-microsoft', 5),
((SELECT id FROM nav_categories WHERE name = '系统镜像下载' LIMIT 1), 'Ubuntu官方下载', 'https://ubuntu.com/download', 'Ubuntu Linux系统官方下载', 'fa-brands fa-ubuntu', 6),
((SELECT id FROM nav_categories WHERE name = '系统镜像下载' LIMIT 1), 'CentOS官方下载', 'https://www.centos.org/download/', 'CentOS Linux系统官方下载', 'fa-brands fa-centos', 7);

-- 热门推荐分类下的导航项（4个网站）
INSERT INTO navs (category_id, title, url, description, icon, sort_order) VALUES
((SELECT id FROM nav_categories WHERE name = '热门推荐' LIMIT 1), '扣子', 'https://www.coze.cn/', '字节跳动AI智能助手平台', 'fa-solid fa-robot', 1),
((SELECT id FROM nav_categories WHERE name = '热门推荐' LIMIT 1), '豆包', 'https://www.doubao.com/', '字节跳动AI对话助手', 'fa-solid fa-comments', 2),
((SELECT id FROM nav_categories WHERE name = '热门推荐' LIMIT 1), '飞书', 'https://www.feishu.cn/', '先进企业协作与管理平台', 'fa-solid fa-users', 3),
((SELECT id FROM nav_categories WHERE name = '热门推荐' LIMIT 1), 'Canva可画', 'https://www.canva.cn/', '在线设计工具和模板平台', 'fa-solid fa-palette', 4);
```



#### 免费观影：



```sql

-- 在线观影分类下的导航项（15个网站）
INSERT INTO navs (category_id, title, url, description, icon, sort_order) VALUES
((SELECT id FROM nav_categories WHERE name = '在线观影' LIMIT 1), '硬核影视', 'https://yingheapp.com/', '大量超清影片资源！', 'https://www.xiaozhongjishu.com/wp-content/uploads/2023/08/afc62-yingheapp.com.png', 1),
((SELECT id FROM nav_categories WHERE name = '在线观影' LIMIT 1), '玖玖影视', 'https://www.99ys.com/', '免费短视频、热门剧集在线观看', 'https://www.xiaozhongjishu.com/wp-content/uploads/2025/07/1753105866-WechatIMG50.png', 2),
((SELECT id FROM nav_categories WHERE name = '在线观影' LIMIT 1), '豌豆影视 Pro', 'https://www.wandou.tv/', '数万部高清影视资源，每日更新', 'https://www.xiaozhongjishu.com/wp-content/uploads/2025/03/1742460215-wandou-logo_mini.png', 3),
((SELECT id FROM nav_categories WHERE name = '在线观影' LIMIT 1), '5点电影', 'https://www.5dianying.com/', '海量高清免费电影、电视剧', 'https://www.xiaozhongjishu.com/wp-content/uploads/2025/03/1742472740-PixPin_2025-03-20_20-11-15.png', 4),
((SELECT id FROM nav_categories WHERE name = '在线观影' LIMIT 1), 'HDmoli', 'https://www.hdmoli.com/', '专注高清影视资源平台', 'fa-solid fa-film', 5),
((SELECT id FROM nav_categories WHERE name = '在线观影' LIMIT 1), '低端影视', 'https://ddys.tv/', '很有特色的高清影视站', 'https://www.xiaozhongjishu.com/wp-content/uploads/2021/05/低端影视.png', 6),
((SELECT id FROM nav_categories WHERE name = '在线观影' LIMIT 1), '电影先生', 'https://www.dyxs.org/', '免费电影、电视剧、综艺、动漫', 'https://www.xiaozhongjishu.com/wp-content/uploads/2021/06/电影先生.png', 7),
((SELECT id FROM nav_categories WHERE name = '在线观影' LIMIT 1), '奈飞工厂', 'https://www.nfgc.tv/', '专注奈飞影视资源整合', 'fa-solid fa-tv', 8),
((SELECT id FROM nav_categories WHERE name = '在线观影' LIMIT 1), '王子TV', 'https://www.wangzi.tv/', '汇集丰富剧集资源的综合影视平台', 'fa-solid fa-crown', 9),
((SELECT id FROM nav_categories WHERE name = '在线观影' LIMIT 1), '肥牛影视', 'https://www.feiniu.tv/', '专注免费电影资源的在线观影平台', 'https://www.xiaozhongjishu.com/wp-content/uploads/2025/06/1750901283-卡通牛.png', 10),
((SELECT id FROM nav_categories WHERE name = '在线观影' LIMIT 1), '共青春影院', 'https://www.gqc.tv/', '海量影视资源的在线平台', 'fa-solid fa-heart', 11),
((SELECT id FROM nav_categories WHERE name = '在线观影' LIMIT 1), '饭碗TV', 'https://www.fanwan.tv/', '免费观看全网影片，还有各种短剧资源', 'fa-solid fa-bowl-food', 12),
((SELECT id FROM nav_categories WHERE name = '在线观影' LIMIT 1), '来看点播', 'https://www.laikan.com/', '免费观看最新电影、电视剧', 'fa-solid fa-play-circle', 13),
((SELECT id FROM nav_categories WHERE name = '在线观影' LIMIT 1), '网飞猫', 'https://www.wfm.tv/', '汇聚海量影视资源的在线平台', 'fa-solid fa-cat', 14),
((SELECT id FROM nav_categories WHERE name = '在线观影' LIMIT 1), '茶杯狐', 'https://www.cupfox.com/', '专业的影视资源导航网站', 'fa-solid fa-search', 15);

-- DB下载分类下的导航项（12个网站）
INSERT INTO navs (category_id, title, url, description, icon, sort_order) VALUES
((SELECT id FROM nav_categories WHERE name = 'DB下载' LIMIT 1), '团长资源', 'https://www.tuanzhang.tv/', '海量影视资源免费下载', 'fa-solid fa-download', 1),
((SELECT id FROM nav_categories WHERE name = 'DB下载' LIMIT 1), '破晓电影', 'https://www.poxiao.com/', '免费的最新电影下载资源网站', 'https://www.xiaozhongjishu.com/wp-content/uploads/2024/12/1733577704-logo.gif', 2),
((SELECT id FROM nav_categories WHERE name = 'DB下载' LIMIT 1), 'SeedHub', 'https://www.seedhub.tv/', '优质影视资讯分享站', 'fa-solid fa-seedling', 3),
((SELECT id FROM nav_categories WHERE name = 'DB下载' LIMIT 1), '迅雷电影天堂', 'https://www.xl720.com/', '只提供迅雷下载链接的电影下载网站', 'https://www.xiaozhongjishu.com/wp-content/uploads/2024/06/1718766437-迅雷 - tuya.png', 4),
((SELECT id FROM nav_categories WHERE name = 'DB下载' LIMIT 1), '不太灵影视', 'https://www.btl.tv/', '提供磁力链接和种子下载', 'https://www.xiaozhongjishu.com/wp-content/uploads/2023/12/favicon-32x32-1.png', 5),
((SELECT id FROM nav_categories WHERE name = 'DB下载' LIMIT 1), '电影港网', 'https://www.dygang.com/', '支持种子下载，支持在线播放', 'https://www.xiaozhongjishu.com/wp-content/uploads/2024/06/1717982422-favicon.ico', 6),
((SELECT id FROM nav_categories WHERE name = 'DB下载' LIMIT 1), '人人电影网', 'https://www.rr.tv/', '人人电影网和人人影视', 'https://www.xiaozhongjishu.com/wp-content/uploads/2022/03/人人电影网.png', 7),
((SELECT id FROM nav_categories WHERE name = 'DB下载' LIMIT 1), 'MP4电影', 'https://www.mp4dy.com/', 'MP4格式电影资源', 'https://www.xiaozhongjishu.com/wp-content/uploads/2021/07/MP4电影.ico', 8),
((SELECT id FROM nav_categories WHERE name = 'DB下载' LIMIT 1), '观影GYING', 'https://www.gying.com/', '高清影视资源聚合平台', 'https://www.xiaozhongjishu.com/wp-content/uploads/2021/06/片库.ico', 9),
((SELECT id FROM nav_categories WHERE name = 'DB下载' LIMIT 1), '6V电影网', 'https://www.6vdy.com/', '6V电影资源下载', 'https://www.xiaozhongjishu.com/wp-content/uploads/2020/11/6V电影网.ico', 10),
((SELECT id FROM nav_categories WHERE name = 'DB下载' LIMIT 1), '音范丝', 'https://www.yinfans.com/', '音乐影视资源分享', 'fa-solid fa-music', 11),
((SELECT id FROM nav_categories WHERE name = 'DB下载' LIMIT 1), '哈哩哈哩', 'https://www.halihali.tv/', '动漫、影视、综艺在线资源平台', 'fa-solid fa-laugh', 12);

-- 字幕下载分类下的导航项（2个网站）
INSERT INTO navs (category_id, title, url, description, icon, sort_order) VALUES
((SELECT id FROM nav_categories WHERE name = '字幕下载' LIMIT 1), '字幕库', 'http://zimuku.org', '界面简洁很清爽', 'https://www.xiaozhongjishu.com/wp-content/uploads/2021/06/字幕库.png', 1),
((SELECT id FROM nav_categories WHERE name = '字幕下载' LIMIT 1), 'SubHD', 'https://subhd.tv/', '成立于2014年', 'https://www.xiaozhongjishu.com/wp-content/uploads/2021/06/subhd.png', 2);

-- 动漫网站分类下的导航项（17个网站）
INSERT INTO navs (category_id, title, url, description, icon, sort_order) VALUES
((SELECT id FROM nav_categories WHERE name = '动漫网站' LIMIT 1), 'AGE动漫', 'https://www.agefans.tv/', '👍专业看动漫！', 'https://www.xiaozhongjishu.com/wp-content/uploads/2020/11/age动漫.ico', 1),
((SELECT id FROM nav_categories WHERE name = '动漫网站' LIMIT 1), '哈哩哈哩', 'https://www.halihali.tv/', '动漫、影视、综艺在线资源平台', 'fa-solid fa-laugh', 2),
((SELECT id FROM nav_categories WHERE name = '动漫网站' LIMIT 1), '稀饭动漫', 'https://www.xifan.tv/', '免费追番的网站', 'https://www.xiaozhongjishu.com/wp-content/uploads/2024/06/1717984323-813e41f81d6f85bfd7a44bf8a813f9e5-tuya.png', 3),
((SELECT id FROM nav_categories WHERE name = '动漫网站' LIMIT 1), '哔咪动漫', 'https://www.bimiacg.net/', '聚合全网最新番剧资源', 'https://www.xiaozhongjishu.com/wp-content/uploads/2022/02/e0a63-www.bimiacg4.net.png', 4),
((SELECT id FROM nav_categories WHERE name = '动漫网站' LIMIT 1), '樱花动漫', 'https://www.yinghuacd.com/', '专注动漫领域，提供高清动漫在线播放', 'https://www.xiaozhongjishu.com/wp-content/uploads/2022/02/aaa69-www.yinghuacd.com.png', 5),
((SELECT id FROM nav_categories WHERE name = '动漫网站' LIMIT 1), '久久动漫', 'https://www.99dm.tv/', '专注于动漫追番与补番的在线平台', 'https://www.xiaozhongjishu.com/wp-content/uploads/2025/07/1751339113-PixPin_2025-07-01_11-04-40.jpg', 6),
((SELECT id FROM nav_categories WHERE name = '动漫网站' LIMIT 1), '风车动漫', 'https://www.fengche.tv/', '风车动漫在线观看', 'fa-solid fa-fan', 7),
((SELECT id FROM nav_categories WHERE name = '动漫网站' LIMIT 1), '趣动漫', 'https://www.qudm.tv/', '趣动漫在线观看', 'fa-solid fa-smile', 8),
((SELECT id FROM nav_categories WHERE name = '动漫网站' LIMIT 1), '嘀哩嘀哩', 'https://www.dilidili.tv/', '嘀哩嘀哩动漫', 'fa-solid fa-play', 9),
((SELECT id FROM nav_categories WHERE name = '动漫网站' LIMIT 1), '布米米', 'https://www.bumimi.tv/', '布米米动漫', 'fa-solid fa-cat', 10),
((SELECT id FROM nav_categories WHERE name = '动漫网站' LIMIT 1), '怡萱动漫', 'https://www.yxdm.tv/', '怡萱动漫在线观看', 'https://files.codelife.cc/icons/5b7f885318cf186378cf9647.png', 11),
((SELECT id FROM nav_categories WHERE name = '动漫网站' LIMIT 1), 'Animex动漫社', 'https://www.animex.tv/', 'Animex动漫资源', 'https://files.codelife.cc/icons/d704b03ae3904441.png', 12),
((SELECT id FROM nav_categories WHERE name = '动漫网站' LIMIT 1), 'Getchu', 'https://www.getchu.com/', '日本动漫游戏资源', 'fa-solid fa-gamepad', 13),
((SELECT id FROM nav_categories WHERE name = '动漫网站' LIMIT 1), '爱恋动漫BT', 'https://www.kisssub.org/', '爱恋动漫BT下载', 'https://files.codelife.cc/icons/5ae046e6af00d737e448dd35.png', 14),
((SELECT id FROM nav_categories WHERE name = '动漫网站' LIMIT 1), '动漫花园BT', 'https://www.dmhy.org/', '动漫花园BT下载', 'https://files.codelife.cc/icons/b03ae3904441b930.png', 15),
((SELECT id FROM nav_categories WHERE name = '动漫网站' LIMIT 1), 'AGE动漫新站', 'https://agefans.one/', '专注动漫的网站', 'https://himg.bdimg.com/sys/portrait/item/e7f961676566616e730806.jpg', 16),
((SELECT id FROM nav_categories WHERE name = '动漫网站' LIMIT 1), '哔咪动漫新站', 'https://www.bimiacg14.net/', '聚合全网最新番剧资源', 'https://www.xiaozhongjishu.com/wp-content/uploads/2022/02/e0a63-www.bimiacg4.net.png', 17);
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
