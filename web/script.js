// 导航栏Web应用交互功能
document.addEventListener('DOMContentLoaded', function() {
    
    // 移动端菜单切换
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const mobileSidebar = document.querySelector('.mobile-sidebar');
    const mobileSidebarOverlay = document.querySelector('.mobile-sidebar-overlay');
    const mobileSidebarClose = document.querySelector('.mobile-sidebar-close');
    
    function openMobileSidebar() {
        mobileSidebar.classList.add('active');
        mobileSidebarOverlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
    
    function closeMobileSidebar() {
        mobileSidebar.classList.remove('active');
        mobileSidebarOverlay.classList.remove('active');
        document.body.style.overflow = '';
    }
    
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', openMobileSidebar);
    }
    
    if (mobileSidebarClose) {
        mobileSidebarClose.addEventListener('click', closeMobileSidebar);
    }
    
    if (mobileSidebarOverlay) {
        mobileSidebarOverlay.addEventListener('click', closeMobileSidebar);
    }
    
    // Tab切换功能 - 区域隔离方案
    function initTabSwitching(containerSelector) {
        const container = document.querySelector(containerSelector);
        if (!container) {
            console.warn(`容器未找到: ${containerSelector}`);
            return;
        }

        const tabItems = container.querySelectorAll('.tab-item');
        const tabContents = container.querySelectorAll('.tab-content');

        console.log(`初始化Tab切换 - 容器: ${containerSelector}, Tab数量: ${tabItems.length}, 内容数量: ${tabContents.length}`);

        tabItems.forEach(item => {
            item.addEventListener('click', function(e) {
                e.stopPropagation(); // 阻止事件冒泡
                const tabId = this.getAttribute('data-tab');
                console.log(`点击Tab: ${tabId} 在容器: ${containerSelector}`);

                // 只在当前容器内切换
                tabItems.forEach(tab => tab.classList.remove('active'));
                tabContents.forEach(content => content.classList.remove('active'));

                // 添加当前活动状态
                this.classList.add('active');
                const targetContent = container.querySelector(`#${tabId}-tab`);
                if (targetContent) {
                    targetContent.classList.add('active');
                    console.log(`成功切换到Tab: ${tabId}`);
                } else {
                    console.error(`未找到目标内容: #${tabId}-tab`);
                }

                // Tab切换后启动增强保护模式
                setTimeout(() => {
                    if (typeof startInteractionProtection === 'function') {
                        startInteractionProtection();
                    }
                }, 50);
            });
        });
    }

    // 初始化各个区域的Tab切换
    initTabSwitching('[data-area="programming"]');
    initTabSwitching('[data-area="tools"]');
    initTabSwitching('[data-area="movies"]');
    initTabSwitching('[data-area="software"]');

    // 初始化侧边导航栏功能
    initSidebarNavigation();

    // 初始化中心Tab切换功能
    initCenterTabSwitching();
    
    // 搜索引擎选项切换
    const searchEngineOptions = document.querySelectorAll('.search-engine-option');
    const searchInput = document.querySelector('.center-search-input');
    
    searchEngineOptions.forEach(option => {
        option.addEventListener('click', function(e) {
            e.preventDefault();
            
            // 移除所有活动状态
            searchEngineOptions.forEach(opt => opt.classList.remove('active'));
            
            // 添加当前活动状态
            this.classList.add('active');
            
            // 更新搜索框占位符
            const engineName = this.textContent;
            if (searchInput) {
                searchInput.placeholder = `${engineName}全网搜索`;
            }
        });
    });
    
    // 中心Tab导航切换
    const centerTabItems = document.querySelectorAll('.center-tab-item');
    
    centerTabItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            
            // 移除所有活动状态
            centerTabItems.forEach(tab => tab.classList.remove('active'));
            
            // 添加当前活动状态
            this.classList.add('active');
        });
    });
    
    // 侧边导航项切换
    const sidebarItems = document.querySelectorAll('.sidebar-item');
    const mobileSidebarItems = document.querySelectorAll('.mobile-sidebar-item');
    
    function handleSidebarItemClick(items) {
        items.forEach(item => {
            item.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation(); // 阻止事件冒泡

                // 移除所有活动状态
                items.forEach(sidebarItem => sidebarItem.classList.remove('active'));

                // 添加当前活动状态
                this.classList.add('active');

                // 如果是移动端菜单，点击后关闭菜单
                if (this.classList.contains('mobile-sidebar-item')) {
                    closeMobileSidebar();
                }

                // 侧边栏导航点击后启动保护模式
                setTimeout(() => {
                    if (typeof startInteractionProtection === 'function') {
                        startInteractionProtection();
                    }
                }, 50);
            });
        });
    }
    
    handleSidebarItemClick(sidebarItems);
    handleSidebarItemClick(mobileSidebarItems);
    
    // 卡片悬停效果增强
    const cards = document.querySelectorAll('.card, .recommend-card, .search-card');

    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px) scale(1.02)';
        });

        card.addEventListener('mouseleave', function() {
            this.style.transform = '';
        });

        // 为卡片添加点击保护
        card.addEventListener('click', function(e) {
            // 如果是外部链接，确保正常跳转
            if (this.href && this.target === '_blank') {
                // 不阻止默认行为，让链接正常工作
            }

            // 点击后立即启动增强保护模式
            setTimeout(() => {
                if (typeof startInteractionProtection === 'function') {
                    startInteractionProtection();
                }
            }, 50);
        });
    });
    
    // 搜索功能
    const searchButton = document.querySelector('.center-search-button');
    
    if (searchButton && searchInput) {
        function performSearch() {
            const query = searchInput.value.trim();
            const activeEngine = document.querySelector('.search-engine-option.active');
            
            if (query && activeEngine) {
                const engineName = activeEngine.textContent;
                console.log(`使用${engineName}搜索: ${query}`);
                // 这里可以添加实际的搜索逻辑
                alert(`使用${engineName}搜索: ${query}`);
            }
        }
        
        searchButton.addEventListener('click', performSearch);
        
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                performSearch();
            }
        });
    }
    
    // 搜索框聚焦效果
    if (searchInput) {
        searchInput.addEventListener('focus', function() {
            this.parentElement.style.boxShadow = '0 0 0 2px rgba(30, 136, 229, 0.3)';
        });
        
        searchInput.addEventListener('blur', function() {
            this.parentElement.style.boxShadow = '';
        });
    }
    
    // 平滑滚动效果
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // 响应式处理和窗口大小改变
    let resizeTimer;
    window.addEventListener('resize', function() {
        // 防抖处理，避免频繁触发
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            handleResponsiveChanges();
        }, 250);
    });

    function handleResponsiveChanges() {
        const windowWidth = window.innerWidth;

        // 大于768px时关闭移动端菜单
        if (windowWidth > 768) {
            closeMobileSidebar();
        }

        // 响应式Tab滚动处理
        handleTabScrolling();

        // 响应式卡片布局调整
        handleCardLayout();

        console.log(`窗口大小变化: ${windowWidth}px`);
    }

    // Tab滚动处理
    function handleTabScrolling() {
        const centerTabs = document.querySelector('.center-tabs');
        if (centerTabs && window.innerWidth <= 768) {
            // 确保活动tab可见
            const activeTab = centerTabs.querySelector('.center-tab-item.active');
            if (activeTab) {
                activeTab.scrollIntoView({
                    behavior: 'smooth',
                    block: 'nearest',
                    inline: 'center'
                });
            }
        }
    }

    // 卡片布局处理
    function handleCardLayout() {
        const cards = document.querySelectorAll('.card');
        const windowWidth = window.innerWidth;

        cards.forEach(card => {
            if (windowWidth <= 576) {
                card.style.minHeight = '70px';
            } else if (windowWidth <= 768) {
                card.style.minHeight = '80px';
            } else {
                card.style.minHeight = '100px';
            }
        });
    }

    // 触摸手势支持
    let touchStartX = 0;
    let touchStartY = 0;

    document.addEventListener('touchstart', function(e) {
        touchStartX = e.touches[0].clientX;
        touchStartY = e.touches[0].clientY;
    }, { passive: true });

    document.addEventListener('touchend', function(e) {
        if (!touchStartX || !touchStartY) return;

        const touchEndX = e.changedTouches[0].clientX;
        const touchEndY = e.changedTouches[0].clientY;

        const deltaX = touchStartX - touchEndX;
        const deltaY = touchStartY - touchEndY;

        // 水平滑动距离大于垂直滑动距离，且滑动距离足够
        if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 50) {
            if (deltaX > 0) {
                // 向左滑动，关闭侧边菜单
                closeMobileSidebar();
            } else {
                // 向右滑动，打开侧边菜单（仅在移动端）
                if (window.innerWidth <= 768) {
                    openMobileSidebar();
                }
            }
        }

        touchStartX = 0;
        touchStartY = 0;
    }, { passive: true });

    // 键盘导航支持
    document.addEventListener('keydown', function(e) {
        // ESC键关闭移动端菜单
        if (e.key === 'Escape') {
            closeMobileSidebar();
        }

        // Tab键导航支持
        if (e.key === 'Tab') {
            // 确保焦点元素可见
            setTimeout(() => {
                const focusedElement = document.activeElement;
                if (focusedElement) {
                    focusedElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'nearest'
                    });
                }
            }, 100);
        }
    });

    // 设备方向改变处理
    window.addEventListener('orientationchange', function() {
        setTimeout(function() {
            handleResponsiveChanges();
            // 重新计算视口高度
            document.documentElement.style.setProperty('--vh', `${window.innerHeight * 0.01}px`);
        }, 500);
    });

    // 初始化视口高度变量
    document.documentElement.style.setProperty('--vh', `${window.innerHeight * 0.01}px`);

    // 添加加载动画效果
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                entry.target.classList.add('animated');
            }
        });
    }, observerOptions);

    // 为卡片添加进入动画
    document.querySelectorAll('.card, .recommend-card, .search-card').forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = `opacity 0.6s ease ${index * 0.1}s, transform 0.6s ease ${index * 0.1}s`;
        observer.observe(card);
    });

    // 性能优化：减少重排重绘
    function optimizePerformance() {
        // 使用 requestAnimationFrame 优化动画
        const animatedElements = document.querySelectorAll('.card, .recommend-card, .search-card');

        animatedElements.forEach(element => {
            element.addEventListener('mouseenter', function() {
                requestAnimationFrame(() => {
                    this.style.transform = 'translateY(-5px) scale(1.02)';
                });
            });

            element.addEventListener('mouseleave', function() {
                requestAnimationFrame(() => {
                    this.style.transform = '';
                });
            });

            // 为动画元素添加点击保护（如果还没有添加的话）
            if (!element.hasAttribute('data-click-protected')) {
                element.setAttribute('data-click-protected', 'true');
                element.addEventListener('click', function() {
                    // 点击后启动增强保护模式
                    setTimeout(() => {
                        if (typeof startInteractionProtection === 'function') {
                            startInteractionProtection();
                        }
                    }, 50);
                });
            }
        });
    }

    // 懒加载图片（如果有的话）
    function lazyLoadImages() {
        const images = document.querySelectorAll('img[data-src]');
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    imageObserver.unobserve(img);
                }
            });
        });

        images.forEach(img => imageObserver.observe(img));
    }

    // 初始化所有功能
    function init() {
        handleResponsiveChanges();
        optimizePerformance();
        lazyLoadImages();
        initPagination();

        // 添加页面加载完成标识
        document.body.classList.add('loaded');

        console.log('导航栏Web应用已加载完成 - 响应式增强版');
    }

    // 下拉菜单增强功能
    const navDropdowns = document.querySelectorAll('.nav-dropdown');

    // 保存原始下拉菜单内容，防止被意外清空
    const originalMenuContents = new Map();
    navDropdowns.forEach((dropdown, index) => {
        const menu = dropdown.querySelector('.dropdown-menu');
        if (menu) {
            originalMenuContents.set(index, menu.innerHTML);
        }
    });

    // DOM保护机制 - 检测并恢复下拉菜单内容
    function protectDropdownContent() {
        let recoveredCount = 0;
        navDropdowns.forEach((dropdown, index) => {
            const menu = dropdown.querySelector('.dropdown-menu');
            if (menu && menu.children.length === 0) {
                console.warn(`🔧 检测到下拉菜单 ${index} 内容丢失，正在恢复...`);
                menu.innerHTML = originalMenuContents.get(index);
                recoveredCount++;
                console.log(`✅ 下拉菜单 ${index} 已成功恢复`);
            }
        });

        // 如果有恢复操作，输出统计信息
        if (recoveredCount > 0) {
            console.log(`📊 本次检查恢复了 ${recoveredCount} 个下拉菜单`);
        }
    }

    // 定期检查下拉菜单内容完整性
    setInterval(protectDropdownContent, 1000);

    // 在用户交互期间更频繁地检查
    let interactionTimer = null;
    function startInteractionProtection() {
        if (interactionTimer) clearInterval(interactionTimer);
        interactionTimer = setInterval(protectDropdownContent, 100);

        // 5秒后恢复正常检查频率
        setTimeout(() => {
            if (interactionTimer) {
                clearInterval(interactionTimer);
                interactionTimer = null;
            }
        }, 5000);
    }

    // 暴露保护函数到全局作用域，供其他函数调用
    window.protectDropdownContent = protectDropdownContent;
    window.startInteractionProtection = startInteractionProtection;

    // 全面保护机制状态报告
    console.log('🛡️ 下拉菜单保护机制已启动');
    console.log('📊 保护覆盖范围：');
    console.log('  ✅ 头部导航栏下拉菜单（邮箱、网盘、视频）');
    console.log('  ✅ 中心Tab切换（搜索引擎、求职等）');
    console.log('  ✅ 编程网站区域（Tab切换、分页操作）');
    console.log('  ✅ 右侧内容区域（所有卡片点击）');
    console.log('  ✅ 侧边栏导航（桌面端、移动端）');
    console.log('  ✅ 全局点击事件处理');
    console.log('🔄 保护机制：实时监控 + 事件隔离 + 自动恢复');

    // 保护机制健康检查
    function healthCheck() {
        const totalMenus = navDropdowns.length;
        let healthyMenus = 0;

        navDropdowns.forEach((dropdown, index) => {
            const menu = dropdown.querySelector('.dropdown-menu');
            if (menu && menu.children.length > 0) {
                healthyMenus++;
            }
        });

        const healthPercentage = Math.round((healthyMenus / totalMenus) * 100);
        console.log(`💚 下拉菜单健康状态: ${healthyMenus}/${totalMenus} (${healthPercentage}%)`);

        return healthPercentage === 100;
    }

    // 每30秒进行一次健康检查
    setInterval(healthCheck, 30000);

    // 初始健康检查
    setTimeout(healthCheck, 2000);

    navDropdowns.forEach((dropdown, index) => {
        const trigger = dropdown.querySelector('.dropdown-trigger');
        const menu = dropdown.querySelector('.dropdown-menu');
        const items = dropdown.querySelectorAll('.dropdown-item');

        // 键盘导航支持
        trigger.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ' || e.key === 'ArrowDown') {
                e.preventDefault();
                menu.style.opacity = '1';
                menu.style.visibility = 'visible';
                menu.style.transform = 'translateY(0)';
                if (items.length > 0) {
                    items[0].focus();
                }
            }
        });

        // 菜单项键盘导航
        items.forEach((item, index) => {
            item.addEventListener('keydown', function(e) {
                switch(e.key) {
                    case 'ArrowDown':
                        e.preventDefault();
                        const nextIndex = (index + 1) % items.length;
                        items[nextIndex].focus();
                        break;
                    case 'ArrowUp':
                        e.preventDefault();
                        const prevIndex = (index - 1 + items.length) % items.length;
                        items[prevIndex].focus();
                        break;
                    case 'Escape':
                        e.preventDefault();
                        menu.style.opacity = '0';
                        menu.style.visibility = 'hidden';
                        menu.style.transform = 'translateY(-10px)';
                        trigger.focus();
                        break;
                    case 'Tab':
                        // 允许Tab键正常工作，但关闭菜单
                        menu.style.opacity = '0';
                        menu.style.visibility = 'hidden';
                        menu.style.transform = 'translateY(-10px)';
                        break;
                }
            });
        });

        // 为下拉菜单项添加点击保护
        const menuItems = dropdown.querySelectorAll('.dropdown-item');
        menuItems.forEach(item => {
            item.addEventListener('click', function(e) {
                // 阻止事件冒泡，防止触发其他全局事件处理器
                e.stopPropagation();

                // 确保链接正常工作
                if (this.href && this.target === '_blank') {
                    window.open(this.href, '_blank');
                    e.preventDefault();
                }

                // 点击后立即检查并保护下拉菜单内容
                setTimeout(protectDropdownContent, 100);
            });
        });
    });

    // 全局点击事件处理 - 关闭所有下拉菜单
    document.addEventListener('click', function(e) {
        // 检查点击的是否是卡片或链接
        const isCard = e.target.closest('.card, .recommend-card, .search-card');
        const isExternalLink = e.target.closest('a[target="_blank"]');

        navDropdowns.forEach(dropdown => {
            const menu = dropdown.querySelector('.dropdown-menu');
            if (!dropdown.contains(e.target)) {
                menu.style.opacity = '0';
                menu.style.visibility = 'hidden';
                menu.style.transform = 'translateY(-10px)';
            }
        });

        // 如果点击的是卡片或外部链接，启动保护模式
        if (isCard || isExternalLink) {
            setTimeout(() => {
                if (typeof protectDropdownContent === 'function') {
                    protectDropdownContent();
                }
                if (typeof startInteractionProtection === 'function') {
                    startInteractionProtection();
                }
            }, 100);
        }
    });

    // 分页功能
    function initPagination() {
    document.querySelectorAll('.pagination-controls').forEach(controls => {
        const tabContent = controls.closest('.tab-content');
        const pages = tabContent.querySelectorAll('.search-cards[data-page]');
        const prevBtn = controls.querySelector('.prev-btn');
        const nextBtn = controls.querySelector('.next-btn');
        const pageInfo = controls.querySelector('.page-info');

        let currentPage = 1;
        const totalPages = pages.length;

        function updatePage() {
            pages.forEach((page, index) => {
                page.style.display = (index + 1) === currentPage ? 'grid' : 'none';
            });
            pageInfo.textContent = `${currentPage} / ${totalPages}`;
            prevBtn.disabled = currentPage === 1;
            nextBtn.disabled = currentPage === totalPages;
        }

        prevBtn.addEventListener('click', (e) => {
            e.stopPropagation(); // 阻止事件冒泡
            if (currentPage > 1) {
                currentPage--;
                updatePage();
                // 启动增强保护模式
                if (typeof startInteractionProtection === 'function') {
                    startInteractionProtection();
                }
            }
        });

        nextBtn.addEventListener('click', (e) => {
            e.stopPropagation(); // 阻止事件冒泡
            if (currentPage < totalPages) {
                currentPage++;
                updatePage();
                // 启动增强保护模式
                if (typeof startInteractionProtection === 'function') {
                    startInteractionProtection();
                }
            }
        });

        // 初始化页面状态
        updatePage();
    });
}

    // 页面加载完成后初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
});

// 侧边导航栏功能
function initSidebarNavigation() {
    // 移动端侧边栏导航点击后自动关闭
    const mobileSidebarItems = document.querySelectorAll('.mobile-sidebar-item');
    const mobileSidebar = document.querySelector('.mobile-sidebar');
    const overlay = document.querySelector('.mobile-sidebar-overlay');

    mobileSidebarItems.forEach(item => {
        // 检查是否已经添加了保护事件监听器，避免重复添加
        if (!item.hasAttribute('data-sidebar-protected')) {
            item.setAttribute('data-sidebar-protected', 'true');
            item.addEventListener('click', (e) => {
                e.stopPropagation(); // 阻止事件冒泡

                // 延迟关闭侧边栏，让滚动动画先执行
                setTimeout(() => {
                    if (mobileSidebar) {
                        mobileSidebar.classList.remove('active');
                    }
                    if (overlay) {
                        overlay.classList.remove('active');
                    }
                }, 100);

                // 侧边栏点击后启动保护模式
                setTimeout(() => {
                    if (typeof startInteractionProtection === 'function') {
                        startInteractionProtection();
                    }
                }, 150);
            });
        }
    });

    // 滚动监听，高亮当前区域对应的导航项
    const sections = [
        { id: 'section-welfare', nav: '.sidebar-item[href="#section-welfare"]' },
        { id: 'section-recommend', nav: '.sidebar-item[href="#section-recommend"]' },
        { id: 'section-programming', nav: '.sidebar-item[href="#section-programming"]' },
        { id: 'section-tools', nav: '.sidebar-item[href="#section-tools"]' },
        { id: 'section-movies', nav: '.sidebar-item[href="#section-movies"]' },
        { id: 'section-software', nav: '.sidebar-item[href="#section-software"]' },
        { id: 'section-links', nav: '.sidebar-item[href="#section-links"]' }
    ];

    // 节流函数
    function throttle(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // 滚动监听函数
    function updateActiveNavigation() {
        const scrollPosition = window.scrollY + 100; // 偏移量

        let currentSection = '';
        sections.forEach(section => {
            const element = document.getElementById(section.id);
            if (element) {
                const offsetTop = element.offsetTop;
                const offsetHeight = element.offsetHeight;

                if (scrollPosition >= offsetTop && scrollPosition < offsetTop + offsetHeight) {
                    currentSection = section.id;
                }
            }
        });

        // 更新导航项活动状态
        document.querySelectorAll('.sidebar-item').forEach(item => {
            item.classList.remove('active');
        });

        if (currentSection) {
            const activeNav = document.querySelector(`.sidebar-item[href="#${currentSection}"]`);
            if (activeNav) {
                activeNav.classList.add('active');
            }
        }
    }

    // 添加滚动监听（使用节流）
    window.addEventListener('scroll', throttle(updateActiveNavigation, 100));

    // 初始化时设置活动状态
    updateActiveNavigation();
}

// 中心Tab切换功能
function initCenterTabSwitching() {
    const tabItems = document.querySelectorAll('.center-tab-item');
    // 只选择中心Tab区域的tab-content，而不是所有的tab-content
    const centerTabArea = document.querySelector('.center-tab-area');
    const tabContents = centerTabArea.querySelectorAll('.tab-content');

    tabItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();

            // 移除所有Tab的激活状态
            tabItems.forEach(tab => tab.classList.remove('active'));

            // 隐藏所有中心Tab内容
            tabContents.forEach(content => {
                content.style.display = 'none';
                content.classList.remove('active');
            });

            // 激活当前点击的Tab
            item.classList.add('active');

            // 显示对应的Tab内容
            const targetTab = item.dataset.tab;
            const targetContent = document.getElementById(`${targetTab}-content`);

            if (targetContent) {
                targetContent.style.display = 'block';
                targetContent.classList.add('active');
            }
        });
    });
}
