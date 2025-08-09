-- 数据库修复脚本
-- 解决外键约束问题，使用NULL作为顶级分类的parent_id

-- 1. 删除现有的nav_categories表（如果存在数据，请先备份）
DROP TABLE IF EXISTS navs;
DROP TABLE IF EXISTS nav_categories;

-- 2. 重新创建nav_categories表（修复版本）
CREATE TABLE nav_categories (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '分类唯一标识',
    parent_id BIGINT DEFAULT NULL COMMENT '父分类ID（NULL表示顶级分类）',
    name VARCHAR(100) NOT NULL COMMENT '分类名称',
    description VARCHAR(500) COMMENT '分类描述',
    sort_order INT NOT NULL DEFAULT 0 COMMENT '排序优先级（数值越小越靠前）',
    level INT NOT NULL DEFAULT 1 COMMENT '分类层级（1=顶级，2=二级）',
    is_public BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否公开（所有用户可见）',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    -- 外键约束（允许parent_id为NULL）
    CONSTRAINT fk_categories_parent 
        FOREIGN KEY (parent_id) 
        REFERENCES nav_categories(id) 
        ON DELETE CASCADE,
    
    -- 唯一约束：同级分类名称唯一
    UNIQUE KEY uk_category_name_parent (name, parent_id)
) COMMENT '导航分类表（支持多级分类）';

-- 3. 重新创建navs表
CREATE TABLE navs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '导航项唯一标识',
    category_id BIGINT NOT NULL COMMENT '所属分类ID',
    parent_id BIGINT DEFAULT NULL COMMENT '父级导航ID（NULL表示顶级）',
    title VARCHAR(100) NOT NULL COMMENT '导航显示名称',
    url VARCHAR(500) NOT NULL COMMENT '导航跳转链接',
    description TEXT COMMENT '网站描述信息',
    icon VARCHAR(500) COMMENT '图标URL地址',
    sort_order INT NOT NULL DEFAULT 0 COMMENT '排序优先级（数值越小越靠前）',
    is_public BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否公开（所有用户可见）',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    -- 外键约束
    CONSTRAINT fk_navs_category 
        FOREIGN KEY (category_id) 
        REFERENCES nav_categories(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    
    -- 导航项的层级关系
    CONSTRAINT fk_navs_parent 
        FOREIGN KEY (parent_id) 
        REFERENCES navs(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) COMMENT '导航菜单表（支持层级结构）';

-- 4. 创建索引
CREATE INDEX idx_navs_category ON navs(category_id) COMMENT '分类ID索引（快速按分类查询）';
CREATE INDEX idx_navs_sort ON navs(sort_order) COMMENT '排序索引（菜单排序）';
CREATE INDEX idx_navs_public ON navs(is_public) COMMENT '公开状态索引（用于筛选公开导航项）';

CREATE INDEX idx_categories_parent ON nav_categories(parent_id) COMMENT '父分类索引（构建分类树）';
CREATE INDEX idx_categories_name ON nav_categories(name) COMMENT '分类名称索引';
CREATE INDEX idx_categories_sort ON nav_categories(sort_order) COMMENT '分类排序索引';
CREATE INDEX idx_categories_public ON nav_categories(is_public) COMMENT '公开状态索引';

-- 5. 插入测试数据
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

-- 获取二级分类ID
SET @coding_tools_id = (SELECT id FROM nav_categories WHERE name = '编码工具');
SET @backend_id = (SELECT id FROM nav_categories WHERE name = '后端');
SET @frontend_id = (SELECT id FROM nav_categories WHERE name = '前端');
SET @pdf_tools_id = (SELECT id FROM nav_categories WHERE name = 'PDF转换');

-- 插入导航项数据
-- 编码工具分类下的导航项
INSERT INTO navs (category_id, title, url, description, icon, sort_order) VALUES
(@coding_tools_id, 'Visual Studio Code', 'https://code.visualstudio.com/', '微软开发的轻量级代码编辑器', 'https://files.codelife.cc/website/visual-studio-code.svg', 1),
(@coding_tools_id, 'GitHub', 'https://github.com/', '全球最大的代码托管平台', 'https://files.codelife.cc/website/github.svg', 2),
(@coding_tools_id, 'Gitee', 'https://gitee.com/', '中国本土的代码托管平台', 'https://files.codelife.cc/website/gitee.svg', 3),
(@coding_tools_id, 'MarsCode', 'https://marscode.com.cn/', '豆包旗下的智能编程工具', 'https://lf-cdn.marscode.com.cn/obj/marscode-cn-release/marscode-icon.png', 4),
(@coding_tools_id, 'CodePen', 'https://codepen.io/', '前端代码在线编辑器', 'https://files.codelife.cc/website/codepen.svg', 5),
(@coding_tools_id, 'JSFiddle', 'https://jsfiddle.net/', '在线JavaScript代码测试工具', 'https://files.codelife.cc/website/jsfiddle.png', 6),
(@coding_tools_id, 'StackBlitz', 'https://stackblitz.com/', '在线IDE，支持多种框架', 'https://files.codelife.cc/website/stackblitz.svg', 7),
(@coding_tools_id, 'GitLab', 'https://gitlab.com/', '开源的代码托管平台', 'https://files.codelife.cc/website/gitlab.svg', 8),
(@coding_tools_id, 'Bitbucket', 'https://bitbucket.org/', 'Atlassian旗下的代码托管平台', 'https://files.codelife.cc/website/bitbucket.svg', 9),
(@coding_tools_id, 'Docker', 'https://www.docker.com/', '容器化平台', 'https://files.codelife.cc/website/docker.svg', 10);

-- 后端分类下的导航项
INSERT INTO navs (category_id, title, url, description, icon, sort_order) VALUES
(@backend_id, 'MyBatis', 'https://mybatis.org/mybatis-3/', 'Java持久层框架', 'https://files.codelife.cc/user-website-icon/20220803/J_G1ipNrekOYJSmTCACZ99269.png', 1),
(@backend_id, 'Spring', 'https://spring.io/', 'Java企业级开发框架', 'https://files.codelife.cc/website/5b307dd14c14a60c5612d29d.png', 2),
(@backend_id, 'MySQL', 'https://dev.mysql.com/', '开源关系型数据库', 'https://files.codelife.cc/website/5f4386f4aa121b0c2ac69e22.png', 3),
(@backend_id, 'Maven', 'https://maven.apache.org/', 'Java项目管理工具', 'https://files.codelife.cc/website/5b3110634c14a60c5612d3e1.png', 4),
(@backend_id, 'Redis', 'https://redis.io/', '内存数据结构存储', 'https://files.codelife.cc/website/redis.svg', 5),
(@backend_id, 'MongoDB', 'https://www.mongodb.com/', '文档型数据库', 'https://files.codelife.cc/website/mongodb.svg', 6),
(@backend_id, 'PostgreSQL', 'https://www.postgresql.org/', '高级开源关系型数据库', 'https://files.codelife.cc/website/postgresql.svg', 7);

-- 前端分类下的导航项
INSERT INTO navs (category_id, title, url, description, icon, sort_order) VALUES
(@frontend_id, 'React', 'https://react.dev/', '用于构建用户界面的JavaScript库', 'https://files.codelife.cc/website/react.svg', 1),
(@frontend_id, 'Vue.js', 'https://vuejs.org/', '渐进式JavaScript框架', 'https://files.codelife.cc/website/vue.svg', 2),
(@frontend_id, 'TypeScript', 'https://www.typescriptlang.org/', 'JavaScript的超集，添加了类型系统', 'https://files.codelife.cc/website/typescript.svg', 3),
(@frontend_id, 'Figma', 'https://www.figma.com/', '协作式设计工具', 'https://files.codelife.cc/website/figma.svg', 4),
(@frontend_id, 'Canva可画', 'https://www.canva.cn/', '在线设计工具平台', 'https://files.codelife.cc/website/canva.svg', 5);

-- 添加测试用户
INSERT INTO users (username, password) VALUES
('admin', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iOEfeVdi'),
('user1', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iOEfeVdi'),
('guest', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iOEfeVdi');

-- 验证数据插入
SELECT '=== 分类数据 ===' as info;
SELECT id, name, parent_id, level, sort_order FROM nav_categories ORDER BY level, sort_order;

SELECT '=== 导航项数据 ===' as info;
SELECT n.id, n.title, c.name as category_name, n.sort_order 
FROM navs n 
JOIN nav_categories c ON n.category_id = c.id 
ORDER BY c.id, n.sort_order;
