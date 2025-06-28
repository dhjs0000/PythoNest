// 等待DOM完全加载
document.addEventListener('DOMContentLoaded', function() {
    // 导航栏滚动效果
    const navbar = document.querySelector('.navbar');
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.style.padding = '0.5rem 0';
            navbar.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
        } else {
            navbar.style.padding = '1rem 0';
            navbar.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
        }
    });

    // 平滑滚动效果
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80,
                    behavior: 'smooth'
                });
                
                // 更新活动链接
                document.querySelectorAll('.nav-links a').forEach(link => {
                    link.classList.remove('active');
                });
                this.classList.add('active');
            }
        });
    });
    
    // 响应式菜单切换
    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');
    
    hamburger.addEventListener('click', function() {
        navLinks.classList.toggle('active');
        
        // 汉堡按钮动画
        const bars = document.querySelectorAll('.bar');
        bars.forEach(bar => {
            bar.classList.toggle('active');
        });
    });
    
    // 点击菜单项后关闭移动菜单
    document.querySelectorAll('.nav-links a').forEach(link => {
        link.addEventListener('click', function() {
            if (navLinks.classList.contains('active')) {
                navLinks.classList.remove('active');
                
                // 重置汉堡按钮状态
                const bars = document.querySelectorAll('.bar');
                bars.forEach(bar => {
                    bar.classList.remove('active');
                });
            }
        });
    });
    
    // 标签页功能
    const tabButtons = document.querySelectorAll('.tab-btn');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            // 更新按钮状态
            tabButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // 获取要显示的选项卡
            const tabId = this.getAttribute('data-tab');
            
            // 隐藏所有选项卡内容
            document.querySelectorAll('.tab-pane').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // 显示所选选项卡
            document.getElementById(tabId + '-tab').classList.add('active');
        });
    });

    // 动画元素出现效果
    const animateElements = document.querySelectorAll('.feature-card, .download-card, .step, .tab-pane img');
    
    // 检查元素是否在视口中
    function checkIfInView() {
        const windowHeight = window.innerHeight;
        const windowTopPosition = window.scrollY;
        const windowBottomPosition = windowTopPosition + windowHeight;
        
        animateElements.forEach(element => {
            const elementHeight = element.offsetHeight;
            const elementTopPosition = element.offsetTop;
            const elementBottomPosition = elementTopPosition + elementHeight;
            
            // 检查元素是否在视口中
            if (
                elementBottomPosition >= windowTopPosition && 
                elementTopPosition <= windowBottomPosition
            ) {
                element.classList.add('in-view');
            }
        });
    }
    
    // 初始检查
    checkIfInView();
    
    // 滚动时检查
    window.addEventListener('scroll', checkIfInView);
    
    // 创建小的动画效果，类似于打字机效果，用于主标题
    const heroTitle = document.querySelector('.hero-content h1');
    if (heroTitle) {
        const text = heroTitle.textContent;
        heroTitle.textContent = '';
        
        let i = 0;
        const typeInterval = setInterval(function() {
            if (i < text.length) {
                heroTitle.textContent += text.charAt(i);
                i++;
            } else {
                clearInterval(typeInterval);
            }
        }, 50);
    }
    
    // 添加CSS自定义样式，用于页面中的动画元素
    const style = document.createElement('style');
    style.textContent = `
        .feature-card, .download-card, .step, .tab-pane img {
            opacity: 0;
            transform: translateY(20px);
            transition: opacity 0.6s ease, transform 0.6s ease;
        }
        
        .feature-card.in-view, .download-card.in-view, .step.in-view, .tab-pane img.in-view {
            opacity: 1;
            transform: translateY(0);
        }
        
        .hamburger .bar {
            transition: all 0.3s ease-in-out;
        }
        
        .hamburger .bar:nth-child(1).active {
            transform: rotate(-45deg) translate(-5px, 6px);
        }
        
        .hamburger .bar:nth-child(2).active {
            opacity: 0;
        }
        
        .hamburger .bar:nth-child(3).active {
            transform: rotate(45deg) translate(-5px, -6px);
        }
    `;
    document.head.appendChild(style);
}); 