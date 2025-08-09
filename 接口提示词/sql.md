# 导航系统数据库SQL脚本

## 1. 创建表结构

### 导航分类表
```sql
CREATE TABLE nav_categories (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '分类唯一标识',
    name VARCHAR(50) NOT NULL UNIQUE COMMENT '分类名称',
    description VARCHAR(255) COMMENT '分类描述',
    sort_order INT DEFAULT 0 COMMENT '排序优先级',
    is_public BOOLEAN DEFAULT TRUE COMMENT '是否公开',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) COMMENT '导航分类表';
```

### 导航菜单表
```sql
CREATE TABLE navs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '导航项唯一标识',
    category_id BIGINT NOT NULL COMMENT '所属分类ID',
    parent_id BIGINT COMMENT '父级导航ID',
    title VARCHAR(100) NOT NULL COMMENT '导航标题',
    url VARCHAR(255) COMMENT '导航链接',
    icon VARCHAR(255) COMMENT '图标URL',
    sort_order INT DEFAULT 0 COMMENT '排序优先级',
    is_public BOOLEAN DEFAULT TRUE COMMENT '是否公开',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    FOREIGN KEY (category_id) REFERENCES nav_categories(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES navs(id) ON DELETE SET NULL
) COMMENT '导航菜单表';
```

### 用户表（无权限管理）
```sql
-- 创建用户表
CREATE TABLE users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '用户唯一标识',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    password VARCHAR(255) NOT NULL COMMENT '密码（加密存储）',
    nickname VARCHAR(50) COMMENT '昵称',
    avatar VARCHAR(255) COMMENT '头像URL',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否激活',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT '用户表';
```

## 2. 插入全部数据

### 插入分类数据
```sql
-- 清除现有数据
DELETE FROM navs;
DELETE FROM nav_categories;

-- 插入主分类
INSERT INTO nav_categories (name, description, sort_order) VALUES
('编程网站', '开发者工具和技术网站集合', 1),
('工具网站', '实用在线工具集合', 2);
```

### 插入编程网站数据
```sql
-- 编码工具子分类
INSERT INTO navs (category_id, title, url, icon, sort_order) VALUES
(1, 'Visual Studio Code', 'https://code.visualstudio.com/', 'https://files.codelife.cc/website/visual-studio-code.svg', 1),
(1, 'GitHub', 'https://github.com/', 'https://files.codelife.cc/website/github.svg', 2),
(1, 'Gitee', 'https://gitee.com/', 'https://files.codelife.cc/website/gitee.svg', 3),
(1, 'MarsCode', 'https://marscode.com.cn/', 'https://lf-cdn.marscode.com.cn/obj/marscode-cn-release/marscode-icon.png', 4),
(1, 'CodePen', 'https://codepen.io/', 'https://files.codelife.cc/website/codepen.svg', 5),
(1, 'JSFiddle', 'https://jsfiddle.net/', 'https://files.codelife.cc/website/jsfiddle.png', 6),
(1, 'StackBlitz', 'https://stackblitz.com/', 'https://files.codelife.cc/website/stackblitz.svg', 7),
(1, 'GitLab', 'https://gitlab.com/', 'https://files.codelife.cc/website/gitlab.svg', 8),
(1, 'Bitbucket', 'https://bitbucket.org/', 'https://files.codelife.cc/website/bitbucket.svg', 9),
(1, 'Docker', 'https://www.docker.com/', 'https://files.codelife.cc/website/docker.svg', 10),
(1, 'Travis CI', 'https://travis-ci.org/', 'https://files.codelife.cc/website/travis-ci.svg', 11),
(1, 'Postman', 'https://www.postman.com/', 'https://files.codelife.cc/website/postman.svg', 12),
(1, 'Insomnia', 'https://insomnia.rest/', 'https://files.codelife.cc/website/insomnia.svg', 13),
(1, 'Apifox', 'https://www.apifox.cn/', 'https://files.codelife.cc/icons/www.apifox.cn.svg', 14),
(1, 'Eolink', 'https://www.eolink.com/', 'https://files.codelife.cc/icons/www.eolink.com.svg', 15),
(1, 'ShowDoc', 'https://www.showdoc.com.cn/', 'https://files.codelife.cc/icons/www.showdoc.com.cn.svg', 16),
(1, '语雀', 'https://www.yuque.com/', 'https://files.codelife.cc/icons/www.yuque.com.svg', 17),
(1, 'Notion', 'https://www.notion.so/', 'https://files.codelife.cc/website/notion.svg', 18),
(1, 'Figma', 'https://www.figma.com/', 'https://files.codelife.cc/website/figma.svg', 19),
(1, 'Sketch', 'https://www.sketch.com/', 'https://files.codelife.cc/website/sketch.svg', 20),
(1, 'Canva可画', 'https://www.canva.cn/', 'https://files.codelife.cc/website/canva.svg', 21),
(1, 'ProcessOn', 'https://www.processon.com/', 'https://files.codelife.cc/icons/www.processon.com.svg', 22);

-- 前端框架子分类
INSERT INTO navs (category_id, title, url, icon, sort_order) VALUES
(1, 'React', 'https://react.dev/', 'https://files.codelife.cc/website/react.svg', 23),
(1, 'Vue.js', 'https://vuejs.org/', 'https://files.codelife.cc/website/vue.svg', 24),
(1, 'Angular', 'https://angular.io/', 'https://files.codelife.cc/website/angular.svg', 25),
(1, 'TypeScript', 'https://www.typescriptlang.org/', 'https://files.codelife.cc/website/typescript.svg', 26),
(1, 'Webpack', 'https://webpack.js.org/', 'https://files.codelife.cc/website/webpack.svg', 27),
(1, 'Vite', 'https://vitejs.dev/', 'https://files.codelife.cc/website/vite.svg', 28),
(1, 'Next.js', 'https://nextjs.org/', 'https://files.codelife.cc/website/nextjs.svg', 29),
(1, 'Nuxt.js', 'https://nuxt.com/', 'https://files.codelife.cc/website/nuxt.svg', 30),
(1, 'Tailwind CSS', 'https://tailwindcss.com/', 'https://files.codelife.cc/website/tailwindcss.svg', 31),
(1, 'Bootstrap', 'https://getbootstrap.com/', 'https://files.codelife.cc/website/bootstrap.svg', 32);

-- 后端技术子分类
INSERT INTO navs (category_id, title, url, icon, sort_order) VALUES
(1, 'MyBatis', 'https://mybatis.org/mybatis-3/', 'https://files.codelife.cc/user-website-icon/20220803/J_G1ipNrekOYJSmTCACZ99269.png', 33),
(1, 'MyBatis-Plus', 'https://baomidou.com/', 'https://files.codelife.cc/icons/20bacf68b2efe5b2.png', 34),
(1, 'Maven', 'https://maven.apache.org/', 'https://files.codelife.cc/website/5b3110634c14a60c5612d3e1.png', 35),
(1, 'MySQL', 'https://dev.mysql.com/', 'https://files.codelife.cc/website/5f4386f4aa121b0c2ac69e22.png', 36),
(1, 'Spring', 'https://spring.io/', 'https://files.codelife.cc/website/5b307dd14c14a60c5612d29d.png', 37),
(1, 'AspectJ', 'http://www.eclipse.org/aspectj/', 'https://files.codelife.cc/user-website-icon/20220814/wRMKMVFZ1rcjFhTxnLOeM9848.png', 38),
(1, 'Kotlin 语言中文站', 'https://www.kotlincn.net', 'https://www.kotlincn.net/assets/images/apple-touch-icon-72x72.png', 39),
(1, 'Repository', 'https://mvnrepository.com/', 'https://files.codelife.cc/website/5acb1d9017fa1105a20f93ec.png', 40),
(1, 'Redis', 'https://redis.io/', 'https://files.codelife.cc/website/redis.svg', 41),
(1, 'MongoDB', 'https://www.mongodb.com/', 'https://files.codelife.cc/website/mongodb.svg', 42),
(1, 'PostgreSQL', 'https://www.postgresql.org/', 'https://files.codelife.cc/website/postgresql.svg', 43),
(1, 'Elasticsearch', 'https://www.elastic.co/', 'https://files.codelife.cc/website/elasticsearch.svg', 44),
(1, 'Apache Kafka', 'https://kafka.apache.org/', 'https://files.codelife.cc/website/kafka.svg', 45),
(1, 'Apache ZooKeeper', 'https://zookeeper.apache.org/', 'https://files.codelife.cc/website/zookeeper.svg', 46),
(1, 'Apache Dubbo', 'https://dubbo.apache.org/', 'https://files.codelife.cc/website/dubbo.svg', 47),
(1, 'Nacos', 'https://nacos.io/', 'https://files.codelife.cc/website/nacos.svg', 48),
(1, 'RabbitMQ', 'https://www.rabbitmq.com/', 'https://files.codelife.cc/website/rabbitmq.svg', 49),
(1, 'Apache RocketMQ', 'https://rocketmq.apache.org/', 'https://files.codelife.cc/website/rocketmq.svg', 50);
```

### 插入工具网站数据
```sql
-- PDF转换工具子分类
INSERT INTO navs (category_id, title, url, icon, sort_order) VALUES
(2, 'iLovePDF', 'https://www.ilovepdf.com/', 'https://www.xiaozhongjishu.com/wp-content/uploads/2020/11/iLovePDF.png', 1),
(2, 'PDF转换器', 'https://www.pdf2go.com/zh', 'https://www.xiaozhongjishu.com/wp-content/uploads/2020/11/pdf2go.png', 2),
(2, 'PDF Eagle', 'https://cn.pdf eagle.com/', 'https://www.xiaozhongjishu.com/wp-content/uploads/2020/11/PDFEagle.png', 3),
(2, 'Smallpdf', 'https://smallpdf.com/cn', 'https://www.xiaozhongjishu.com/wp-content/uploads/2020/11/smallpdf.png', 4),
(2, 'PDF24 Tools', 'https://tools.pdf24.org/zh/', 'https://www.xiaozhongjishu.com/wp-content/uploads/2020/11/pdf24.png', 5),
(2, 'CleverPDF', 'https://www.cleverpdf.com/', 'https://www.xiaozhongjishu.com/wp-content/uploads/2020/11/cleverpdf.png', 6),
(2, '超级PDF', 'https://xpdf.net/', 'https://www.xiaozhongjishu.com/wp-content/uploads/2020/11/xpdf.png', 7),
(2, 'PDF派', 'https://www.pdfpai.com/', 'https://www.xiaozhongjishu.com/wp-content/uploads/2020/11/pdfpai.png', 8);

-- 数码相关工具子分类
INSERT INTO navs (category_id, title, url, icon, sort_order) VALUES
(2, '鲁大师天梯榜', 'https://www.ludashi.com/tianti', 'https://www.xiaozhongjishu.com/wp-content/uploads/2020/11/ludashi.png', 9),
(2, 'SiliconCat', 'https://www.siliconcat.com/', 'https://www.xiaozhongjishu.com/wp-content/uploads/2020/11/siliconcat.png', 10),
(2, '显卡性能天梯图', 'https://www.mydrivers.com/zhuanti/tianti/gpu/', 'https://www.xiaozhongjishu.com/wp-content/uploads/2020/11/mydrivers.png', 11),
(2, '手机性能排行榜', 'https://www.phonearena.com/phones/benchmarks', 'https://www.xiaozhongjishu.com/wp-content/uploads/2020/11/phonearena.png', 12),
(2, '快科技天梯榜', 'https://www.mydrivers.com/zhuanti/tianti/', 'https://www.xiaozhongjishu.com/wp-content/uploads/2020/11/mydrivers.png', 13),
(2, '纳米AI搜索', 'https://bot.n.cn/', 'https://www.xiaozhongjishu.com/wp-content/uploads/2024/04/1744285564-n.cn.png', 14),
(2, '苹果产品参数中心', 'https://www.xiaozhongjishu.com/apple/', 'https://www.xiaozhongjishu.com/wp-content/uploads/2022/08/9da9f-www.onlineit.cn.png', 15),
(2, 'NotebookCheck', 'https://www.notebookcheck.net/Mobile-Processors-Benchmark-List.2436.0.html', 'https://www.xiaozhongjishu.com/wp-content/uploads/2021/05/mobile-processos.png', 16);

### 插入用户数据
```sql
-- 插入示例用户
INSERT INTO users (username, password, nickname) VALUES
('admin', '$2a$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '管理员'),
('user1', '$2a$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '用户1');```
```

## 3. 查询验证

### 查看所有分类
```sql
SELECT * FROM nav_categories ORDER BY sort_order;
```

### 查看完整导航数据
```sql
SELECT 
    n.id,
    n.title,
    n.url,
    n.icon,
    c.name as category_name,
    n.sort_order
FROM navs n
JOIN nav_categories c ON n.category_id = c.id
ORDER BY c.sort_order, n.sort_order;
```

### 按分类查看导航
```sql
SELECT 
    c.name as category,
    COUNT(n.id) as total_navs
FROM nav_categories c
LEFT JOIN navs n ON c.id = n.category_id
GROUP BY c.id, c.name;
```

## 4. 使用说明

1. **创建数据库**：先执行CREATE TABLE语句创建表结构
2. **插入数据**：执行INSERT语句添加测试数据
3. **验证数据**：使用SELECT查询验证数据是否正确插入

## 5. 扩展功能

### 添加子分类支持
```sql
-- 添加子分类（通过parent_id实现）
INSERT INTO navs (category_id, parent_id, title, url, icon, sort_order) VALUES
(1, 1, 'React中文文档', 'https://zh-hans.react.dev/', 'https://files.codelife.cc/website/react.svg', 1);
```



```json
{

    "编程网站": {
        "编码工具": [
            {
                "name": "Visual Studio Code",
                "url": "https://code.visualstudio.com/",
                "description": "微软开发的轻量级代码编辑器",
                "icon": "https://files.codelife.cc/website/visual-studio-code.svg"
            },
            {
                "name": "GitHub",
                "url": "https://github.com/",
                "description": "全球最大的代码托管平台",
                "icon": "https://files.codelife.cc/website/github.svg"
            }
        ],
        "后端": [
            {
                "name": "MyBatis",
                "url": "https://mybatis.org/mybatis-3/",
                "description": "Java持久层框架",
                "icon": "https://files.codelife.cc/user-website-icon/20220803/J_G1ipNrekOYJSmTCACZ99269.png"
            },
            {
                "name": "MyBatis-Plus",
                "url": "https://baomidou.com/",
                "description": "MyBatis增强工具",
                "icon": "https://files.codelife.cc/icons/20bacf68b2efe5b2.png"
            },
            {
                "name": "Maven",
                "url": "https://maven.apache.org/",
                "description": "Java项目管理工具",
                "icon": "https://files.codelife.cc/website/5b3110634c14a60c5612d3e1.png"
            }
        ]

    }
```



