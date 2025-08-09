// 导航项交互效果
document.addEventListener('DOMContentLoaded', function() {
    // 导航项悬停效果
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            this.classList.add('hover');
        });
        item.addEventListener('mouseleave', function() {
            this.classList.remove('hover');
        });
    });
    
    // 搜索框聚焦效果
    const searchInputs = document.querySelectorAll('.search-input');
    searchInputs.forEach(input => {
        input.addEventListener('focus', function() {
            const searchBox = this.closest('.search-box');
            if (searchBox) {
                searchBox.classList.add('focused');
            }
        });
        input.addEventListener('blur', function() {
            const searchBox = this.closest('.search-box');
            if (searchBox) {
                searchBox.classList.remove('focused');
            }
        });
    });
    
    // 卡片悬停效果
    const cards = document.querySelectorAll('.search-card, .recommend-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.classList.add('hover');
        });
        card.addEventListener('mouseleave', function() {
            this.classList.remove('hover');
        });
    });
    
    // 菜单切换
    const desktopMenuToggle = document.querySelector('.desktop-menu-toggle');
    const desktopMenu = document.querySelector('.desktop-menu');
    if (desktopMenuToggle && desktopMenu) {
        desktopMenuToggle.addEventListener('click', function() {
            desktopMenu.classList.toggle('show');
        });
    }
    
    const tabletMenuToggle = document.querySelector('.tablet-menu-toggle');
    const tabletMenu = document.querySelector('.tablet-menu');
    if (tabletMenuToggle && tabletMenu) {
        tabletMenuToggle.addEventListener('click', function() {
            tabletMenu.classList.toggle('show');
        });
    }
    
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const mobileMenu = document.querySelector('.mobile-menu');
    if (mobileMenuToggle && mobileMenu) {
        mobileMenuToggle.addEventListener('click', function() {
            mobileMenu.classList.toggle('show');
        });
    }
    
    // 标签切换功能
    const tabItems = document.querySelectorAll('.tab-item');
    tabItems.forEach(tab => {
        tab.addEventListener('click', function() {
            // 移除所有标签的活动状态
            tabItems.forEach(item => {
                item.classList.remove('active');
            });
            
            // 添加当前标签的活动状态
            this.classList.add('active');
            
            // 获取标签数据
            const tabId = this.getAttribute('data-tab');
            
            // 隐藏所有内容
            const tabContents = document.querySelectorAll('.tab-content');
            tabContents.forEach(content => {
                content.classList.remove('active');
            });
            
            // 显示对应内容
            const activeContent = document.getElementById(tabId + '-tab');
            if (activeContent) {
                activeContent.classList.add('active');
            }
        });
    });
    
    // 搜索引擎选项切换
    const searchEngineOptions = document.querySelectorAll('.search-engine-option');
    if (searchEngineOptions.length > 0) {
        searchEngineOptions.forEach(option => {
            option.addEventListener('click', function() {
                // 移除所有选项的活动状态
                searchEngineOptions.forEach(opt => {
                    opt.classList.remove('active');
                });
                
                // 添加当前选项的活动状态
                this.classList.add('active');
                
                // 这里可以添加更改搜索引擎的逻辑
                const engineName = this.getAttribute('data-engine');
                console.log('Selected search engine:', engineName);
            });
        });
    }
    
    // 演示交互状态
    // 这部分代码用于演示原型中的交互状态，实际项目中可能不需要
    
    // 导航项悬停状态演示
    const hoverNavItem = document.querySelector('.nav-item.hover');
    if (hoverNavItem) {
        setInterval(() => {
            hoverNavItem.classList.toggle('pulse-effect');
        }, 1500);
    }
    
    // 搜索按钮悬停状态演示
    const hoverSearchButton = document.querySelector('.search-button.hover');
    if (hoverSearchButton) {
        setInterval(() => {
            hoverSearchButton.classList.toggle('pulse-effect');
        }, 1500);
    }
    
    // 卡片悬停状态演示
    const hoverCard = document.querySelector('.card.hover');
    if (hoverCard) {
        setInterval(() => {
            hoverCard.classList.toggle('float-effect');
        }, 1500);
    }
    
    // 添加CSS类用于动画效果
    const style = document.createElement('style');
    style.textContent = `
        .hover-effect {
            background-color: rgba(255, 255, 255, 0.1);
        }
        
        .search-focus {
            box-shadow: 0 0 0 2px var(--primary-color);
        }
        
        .card-hover {
            transform: translateY(-5px);
            box-shadow: var(--shadow-md);
        }
        
        .card-active {
            transform: translateY(-2px);
            box-shadow: var(--shadow-sm);
        }
        
        .pulse-effect {
            animation: pulse 1.5s infinite;
        }
        
        .float-effect {
            animation: float 1.5s infinite;
        }
        
        @keyframes pulse {
            0% {
                opacity: 1;
            }
            50% {
                opacity: 0.7;
            }
            100% {
                opacity: 1;
            }
        }
        
        @keyframes float {
            0% {
                transform: translateY(-5px);
            }
            50% {
                transform: translateY(-8px);
            }
            100% {
                transform: translateY(-5px);
            }
        }
    `;
    document.head.appendChild(style);
    
    // 添加响应式设计演示功能
    const responsiveContainers = document.querySelectorAll('.responsive-container');
    
    responsiveContainers.forEach(container => {
        const title = container.querySelector('h3');
        const view = container.querySelector('div[class$="-view"]');
        
        if (title && view) {
            // 默认展开平板视图
            if (title.textContent.trim() === '平板视图') {
                view.classList.add('expanded');
            }
            
            title.addEventListener('click', function() {
                view.classList.toggle('expanded');
            });
        }
    });
    
    // 添加CSS类用于响应式演示
    const responsiveStyle = document.createElement('style');
    responsiveStyle.textContent = `
        .desktop-view, .tablet-view, .mobile-view {
            transition: max-height 0.5s ease-out;
        }
        
        .tablet-menu, .mobile-menu {
            display: none;
        }
        
        .show {
            display: flex !important;
        }
    `;
    document.head.appendChild(responsiveStyle);
    
    // 添加设计规范交互功能
    const colorSwatches = document.querySelectorAll('.color-swatch');
    
    colorSwatches.forEach(swatch => {
        swatch.addEventListener('click', function() {
            const color = window.getComputedStyle(this).backgroundColor;
            const tempInput = document.createElement('input');
            document.body.appendChild(tempInput);
            tempInput.value = color;
            tempInput.select();
            document.execCommand('copy');
            document.body.removeChild(tempInput);
            
            // 显示复制成功提示
            const tooltip = document.createElement('div');
            tooltip.className = 'color-tooltip';
            tooltip.textContent = '颜色已复制!';
            this.appendChild(tooltip);
            
            setTimeout(() => {
                tooltip.remove();
            }, 1500);
        });
    });
    
    // 添加CSS类用于颜色复制提示
    const colorTooltipStyle = document.createElement('style');
    colorTooltipStyle.textContent = `
        .color-swatch {
            cursor: pointer;
            position: relative;
        }
        
        .color-tooltip {
            position: absolute;
            top: -30px;
            left: 50%;
            transform: translateX(-50%);
            background-color: var(--dark-color);
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            white-space: nowrap;
            animation: fadeIn 0.3s;
        }
        
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateX(-50%) translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateX(-50%) translateY(0);
            }
        }
    `;
    document.head.appendChild(colorTooltipStyle);
}); 