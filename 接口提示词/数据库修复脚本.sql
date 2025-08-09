-- SQLite 数据库修复脚本
-- 解决外键约束问题，使用NULL作为顶级分类的parent_id

-- 1. 删除现有的表（如果存在数据，请先备份）
DROP TABLE IF EXISTS navs;
DROP TABLE IF EXISTS nav_categories;
DROP TABLE IF EXISTS users;

-- 2. 创建用户表
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now', 'localtime'))
);

-- 3. 重新创建nav_categories表（SQLite版本）
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

-- 4. 重新创廾navs表
CREATE TABLE navs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    parent_id INTEGER DEFAULT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    description TEXT,
    icon TEXT,
    sort_order INTEGER NOT NULL DEFAULT 0,
    is_public INTEGER NOT NULL DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now', 'localtime')),
    
    -- 外键约束
    FOREIGN KEY (category_id) REFERENCES nav_categories(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES navs(id) ON DELETE SET NULL
);

-- 5. 创建索引
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_navs_category ON navs(category_id);
CREATE INDEX idx_navs_sort ON navs(sort_order);
CREATE INDEX idx_navs_public ON navs(is_public);
CREATE INDEX idx_categories_parent ON nav_categories(parent_id);
CREATE INDEX idx_categories_name ON nav_categories(name);
CREATE INDEX idx_categories_sort ON nav_categories(sort_order);
CREATE INDEX idx_categories_public ON nav_categories(is_public);
CREATE UNIQUE INDEX uk_category_name_parent ON nav_categories(name, parent_id);

-- 7. 插入测试数据
-- 插入用户数据
INSERT INTO users (username, password) VALUES
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.PmvlmO'); -- 密码: admin123

-- 插入一级分类（大分类）
INSERT INTO nav_categories (name, parent_id, description, sort_order, level, is_public) VALUES
('编程网站', NULL, '编程相关的网站集合', 1, 1, 1),
('工具网站', NULL, '各类实用工具网站', 2, 1, 1);

-- 插入二级分类（子分类）
-- 编程网站下的子分类
INSERT INTO nav_categories (name, parent_id, description, sort_order, level, is_public) VALUES
('编码工具', 1, '编码和开发工具', 1, 2, 1),
('后端', 1, '后端开发资源', 2, 2, 1),
('前端', 1, '前端开发资源', 3, 2, 1);

-- 工具网站下的子分类
INSERT INTO nav_categories (name, parent_id, description, sort_order, level, is_public) VALUES
('PDF转换', 2, 'PDF文件处理工具', 1, 2, 1),
('图片处理', 2, '图片编辑和处理工具', 2, 2, 1);

-- 插入导航项数据
-- 编码工具分类下的导航项
INSERT INTO navs (category_id, title, url, description, icon, sort_order) VALUES
(3, 'Visual Studio Code', 'https://code.visualstudio.com/', '微软开发的轻量级代码编辑器', 'https://files.codelife.cc/website/visual-studio-code.svg', 1),
(3, 'GitHub', 'https://github.com/', '全球最大的代码托管平台', 'https://files.codelife.cc/website/github.svg', 2),
(3, 'Gitee', 'https://gitee.com/', '中国本土的代码托管平台', 'https://files.codelife.cc/website/gitee.svg', 3),
(3, 'MarsCode', 'https://marscode.com.cn/', '豆包旗下的智能编程工具', 'https://lf-cdn.marscode.com.cn/obj/marscode-cn-release/marscode-icon.png', 4),
(3, 'CodePen', 'https://codepen.io/', '前端代码在线编辑器', 'https://files.codelife.cc/website/codepen.svg', 5);

-- 后端分类下的导航项
INSERT INTO navs (category_id, title, url, description, icon, sort_order) VALUES
(4, 'MyBatis', 'https://mybatis.org/mybatis-3/', 'Java持久层框架', 'https://files.codelife.cc/user-website-icon/20220803/J_G1ipNrekOYJSmTCACZ99269.png', 1),
(4, 'Spring', 'https://spring.io/', 'Java企业级开发框架', 'https://files.codelife.cc/website/5b307dd14c14a60c5612d29d.png', 2),
(4, 'Redis', 'https://redis.io/', '内存数据结构存储', 'https://files.codelife.cc/website/redis.svg', 3);

-- 前端分类下的导航项
INSERT INTO navs (category_id, title, url, description, icon, sort_order) VALUES
(5, 'React', 'https://react.dev/', '用于构建用户界面的JavaScript库', 'https://files.codelife.cc/website/react.svg', 1),
(5, 'Vue.js', 'https://vuejs.org/', '渐进式JavaScript框架', 'https://files.codelife.cc/website/vue.svg', 2),
(5, 'TypeScript', 'https://www.typescriptlang.org/', 'JavaScript的超集，添加了类型系统', 'https://files.codelife.cc/website/typescript.svg', 3);

-- PDF工具分类下的导航项
INSERT INTO navs (category_id, title, url, description, icon, sort_order) VALUES
(6, 'iLovePDF', 'https://www.ilovepdf.com/', '在线PDF处理工具', 'https://files.codelife.cc/website/ilovepdf.svg', 1),
(6, 'SmallPDF', 'https://smallpdf.com/', 'PDF压缩和转换工具', 'https://files.codelife.cc/website/smallpdf.svg', 2);

-- 验证数据插入
SELECT '=== 分类数据 ===' as info;
SELECT id, name, parent_id, level, sort_order FROM nav_categories ORDER BY level, sort_order;

SELECT '=== 导航项数据 ===' as info;
SELECT n.id, n.title, c.name as category_name, n.sort_order 
FROM navs n 
JOIN nav_categories c ON n.category_id = c.id 
ORDER BY c.id, n.sort_order;
