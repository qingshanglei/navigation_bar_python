YcAi 项目开发规范文档（增补）

一、本次需求概述
1.1 背景
- 原登录页 web/login.html 已完成基础表单与 login.js 的交互逻辑。
- 需在 web/login copy.html 中基于 Vue3 + Element Plus 重写登录界面，以提升交互与一致性，并验证与既有后端接口的兼容性。

1.2 目标
- 使用 Element Plus 的 el-form、el-input、el-checkbox、el-button、消息提示组件等，构建现代化登录 UI。
- 复用原有登录逻辑：接口地址、字段与存储策略保持一致（记住我、token、user_info、跳转）。
- 保持所有路径为相对路径，不新增多余文件与全局副作用。

二、功能清单
- 用户名/密码输入、显示/隐藏密码、记住我、提交按钮加载态、错误与成功提示、回车提交、登录成功跳转 index.html。

三、实现方式
- 前端：基于 Vue3 CDN 与 Element Plus CDN，在 login copy.html 内内联脚本实现逻辑（不新增文件）。
- 表单校验：沿用原规则（用户名 3-20 位、字母数字下划线；密码 6-20 位），用 Element Plus 校验器实现。
- 网络请求：使用 fetch 调用 http://localhost:5000/api/auth/login，响应 code===1 为成功，其他为失败。
- 状态与存储：成功后写入 localStorage（access_token、user_info）；记住我保存 saved_username。

四、实现步骤
1) 在 login copy.html 引入 Vue3 与 Element Plus（CDN），保留相对路径规范。
2) 以 el-form 重构表单结构与交互，加入校验规则与 loading 状态。
3) 实现与原 login.js 等价的提交逻辑与本地存储、跳转逻辑。
4) 自查所有导入、定义与相对路径是否正确；避免影响其他页面。
5) 联调后端，确保成功与失败流程消息提示正确；进行回归测试。

五、预期效果
- 代码量相对原生实现减少，UI 一致性更好，表单交互与提示更完善。
- 首屏加载使用 CDN 资源，登录交互更顺畅；不破坏现有后端与数据流。

六、影响评估与回归点
- 仅作用于 login copy.html，不影响原 login.html。
- 需验证本地存储键名、跳转地址、接口字段与响应格式完全一致。
