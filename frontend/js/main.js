// frontend/js/main.js
// 主应用程序的通用 JavaScript 逻辑

/**
 * 全局加载状态管理
 */
const loadingOverlay = document.getElementById('loadingOverlay');

function showLoading(message = '加载中...') {
    if (loadingOverlay) {
        const p = loadingOverlay.querySelector('p');
        if (p) p.textContent = message;
        loadingOverlay.style.display = 'flex';
    }
}

function hideLoading() {
    if (loadingOverlay) {
        loadingOverlay.style.display = 'none';
    }
}

/**
 * 全局消息提示 (Toast)
 * @param {string} message - 要显示的消息内容
 * @param {string} type - 消息类型 ('success', 'error', 'info')
 * @param {number} duration - 显示时长 (毫秒)
 */
function showToast(message, type = 'info', duration = 3000) {
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        console.warn('Toast container not found!');
        return;
    }

    const toastId = `toast-${Date.now()}`;
    const toast = document.createElement('div');
    toast.id = toastId;
    
    // Base classes for all toasts - relying on Tailwind for styling these through style.css
    // These are just structural or very basic styling not covered by Tailwind component classes easily
    toast.style.padding = '1rem';
    toast.style.borderRadius = '0.5rem';
    toast.style.boxShadow = '0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06)';
    toast.style.display = 'flex';
    toast.style.alignItems = 'center';
    toast.style.color = 'white';
    toast.style.marginBottom = '0.5rem';


    let bgColorClass = 'bg-blue-500'; // Default for info
    let iconSvg = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" style="width: 1.5rem; height: 1.5rem; margin-right: 0.5rem;"><path stroke-linecap="round" stroke-linejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" /></svg>`;

    if (type === 'success') {
        bgColorClass = 'bg-green-500';
        iconSvg = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" style="width: 1.5rem; height: 1.5rem; margin-right: 0.5rem;"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>`;
    } else if (type === 'error') {
        bgColorClass = 'bg-red-500';
        iconSvg = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" style="width: 1.5rem; height: 1.5rem; margin-right: 0.5rem;"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" /></svg>`;
    }
    
    // Add Tailwind class for background color. Assumes style.css has these.
    toast.classList.add(bgColorClass); 
    
    toast.innerHTML = `${iconSvg}<span>${message}</span>`;
    toastContainer.appendChild(toast);

    setTimeout(() => {
        const currentToast = document.getElementById(toastId);
        if (currentToast) {
            currentToast.remove();
        }
    }, duration);
}


/**
 * 检查用户登录状态
 * @returns {Promise<object|null>} 用户数据或 null
 */
async function checkLoginStatus() {
    showLoading('检查登录状态...');
    try {
        const response = await fetch('/auth/status'); // Assumes API is on the same origin
        hideLoading();
        if (!response.ok) {
            if (response.status === 401 || response.status === 404) {
                 console.warn('User not logged in or session invalid.');
                 return null;
            }
            throw new Error(`认证状态检查失败: ${response.statusText} (状态码: ${response.status})`);
        }
        const data = await response.json();
        if (data.logged_in && data.user) {
            return data.user;
        } else {
            console.warn('User data not found in response or not logged in.');
            return null;
        }
    } catch (error) {
        hideLoading();
        console.error('检查登录状态时出错:', error);
        showToast(`检查登录状态失败: ${error.message || '未知错误'}`, 'error');
        return null;
    }
}

/**
 * 处理用户登出
 */
async function handleLogout() {
    showLoading('正在退出...');
    try {
        const response = await fetch('/auth/logout', { method: 'POST' });
        const data = await response.json();
        hideLoading();

        if (response.ok && data.success) {
            showToast('已成功退出登录。', 'success');
            sessionStorage.removeItem('userRoleName'); // 清除存储的角色名
            // localStorage.removeItem('currentUserInfo'); // Example if storing more user info
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 1500);
        } else {
            throw new Error(data.message || '退出登录失败');
        }
    } catch (error) {
        hideLoading();
        console.error('退出登录时出错:', error);
        showToast(`退出登录失败: ${error.message || '未知错误'}`, 'error');
    }
}


/**
 * 动态加载导航菜单
 * @param {Array<object>} modules - 用户有权限访问的模块列表
 */
function populateNavMenu(modules) {
    const navContainer = document.getElementById('mainNav');
    if (!navContainer) return;

    navContainer.innerHTML = ''; 

    modules.forEach(module => {
        const link = document.createElement('a');
        // Using a generic template page for now, passing module info via query params
        // Or, each module could have its own HTML page if routes are simple
        link.href = `data_module_template.html?module_name=${encodeURIComponent(module.模块名称)}&module_route=${encodeURIComponent(module.模块路由 || '')}&module_id=${module.模块ID}`;
        link.target = "contentFrame"; // Load into iframe
        link.className = 'block px-3 py-2 rounded hover:bg-gray-700 transition-colors'; // Tailwind classes
        link.textContent = module.模块名称;
        link.dataset.moduleId = module.模块ID;
        link.dataset.route = module.模块路由;

        link.addEventListener('click', function(event) {
            // event.preventDefault(); // Allow default behavior for iframe target
            const pageTitle = document.querySelector('#mainContent h1');
            const pageDescription = document.querySelector('#mainContent p:first-of-type'); // More specific selector
            
            if (pageTitle) pageTitle.textContent = `模块: ${module.模块名称}`;
            if (pageDescription) pageDescription.textContent = `正在查看/管理 ${module.模块名称} 相关数据。`;
            
            document.querySelectorAll('#mainNav a').forEach(a => a.classList.remove('bg-gray-900', 'font-semibold'));
            link.classList.add('bg-gray-900', 'font-semibold');

            const sidebar = document.getElementById('sidebar');
            if (sidebar && sidebar.classList.contains('translate-x-0') && window.innerWidth < 640) {
                toggleSidebar(false); // Close sidebar on selection (small screens)
            }
        });
        navContainer.appendChild(link);
    });
}

/**
 * 获取用户权限和模块信息 (Mocked)
 * @param {number} userId - 用户ID
 * @returns {Promise<Array<object>|null>} 模块列表或 null
 */
async function fetchUserModules(userId, userRoleName) {
    showLoading('获取用户模块...');
    try {
        // In a real app, this would be:
        // const response = await fetch(`/api/user/${userId}/modules_with_permissions`);
        // if (!response.ok) throw new Error('获取用户模块失败');
        // const data = await response.json();
        // hideLoading();
        // return data.modules;

        await new Promise(resolve => setTimeout(resolve, 300)); // Simulate API delay
        
        let mockModules = [];
        // userRoleName should be derived from the actual user object's role
        if (userRoleName === 'Admin') {
            mockModules = [
                { "模块ID": 101, "模块名称": "用户管理", "模块路由": "/admin/users" },
                { "模块ID": 102, "模块名称": "角色管理", "模块路由": "/admin/roles" },
                { "模块ID": 201, "模块名称": "纤维数据管理", "模块路由": "/data/fibers" },
                { "模块ID": 202, "模块名称": "织物数据管理", "模块路由": "/data/fabrics" },
                { "模块ID": 203, "模块名称": "层压板数据管理", "模块路由": "/data/laminates" },
                { "模块ID": 204, "模块名称": "防弹数据管理", "模块路由": "/data/ballistic" },
            ];
        } else if (userRoleName === 'Researcher') {
             mockModules = [
                { "模块ID": 201, "模块名称": "纤维数据查看", "模块路由": "/data/fibers/view" },
                { "模块ID": 202, "模块名称": "织物数据查看", "模块路由": "/data/fabrics/view" },
                { "模块ID": 203, "模块名称": "层压板数据查看", "模块路由": "/data/laminates/view" },
                { "模块ID": 204, "模块名称": "防弹数据查看", "模块路由": "/data/ballistic/view" },
                { "模块ID": 301, "模块名称": "实验记录管理", "模块路由": "/data/experiments" },
            ];
        } else { // Guest or other roles
            mockModules = [
                 { "模块ID": 901, "模块名称": "公开数据查询", "模块路由": "/public/query" },
                 { "模块ID": 902, "模块名称": "关于系统", "模块路由": "/public/about" },
            ];
        }
        hideLoading();
        return mockModules;

    } catch (error) {
        hideLoading();
        console.error('获取用户模块时出错:', error);
        showToast(`获取用户模块失败: ${error.message || '未知错误'}`, 'error');
        return null;
    }
}

/**
 * 切换侧边栏显示 (小屏幕)
 * @param {boolean} [forceOpen] - 可选，强制打开或关闭。不提供则切换。
 */
function toggleSidebar(forceOpen) {
    const sidebar = document.getElementById('sidebar');
    const menuIconOpen = document.getElementById('menuIconOpen');
    const menuIconClose = document.getElementById('menuIconClose');

    if (!sidebar || !menuIconOpen || !menuIconClose) return;

    let isOpen; // Is the sidebar currently open?
    if (typeof forceOpen === 'boolean') {
        isOpen = !forceOpen; 
    } else {
        // Check based on class that makes it visible (sm:translate-x-0 is for larger screens)
        isOpen = sidebar.classList.contains('translate-x-0');
    }
    
    // On small screens, -translate-x-full means hidden, translate-x-0 means visible
    if (!isOpen) { // If it's hidden or forced to open
        sidebar.classList.remove('-translate-x-full');
        sidebar.classList.add('translate-x-0');
        menuIconOpen.classList.add('hidden');
        menuIconClose.classList.remove('hidden');
    } else { // If it's visible or forced to close
        sidebar.classList.add('-translate-x-full');
        sidebar.classList.remove('translate-x-0');
        menuIconOpen.classList.remove('hidden');
        menuIconClose.classList.add('hidden');
    }
}

// --- 初始化逻辑 ---
document.addEventListener('DOMContentLoaded', async () => {
    const logoutButton = document.getElementById('logoutButton');
    if (logoutButton) {
        logoutButton.addEventListener('click', handleLogout);
    }

    const menuToggleButton = document.getElementById('menuToggleButton');
    if (menuToggleButton) {
        menuToggleButton.addEventListener('click', () => toggleSidebar());
    }

    const isLoginPage = window.location.pathname.endsWith('login.html');
    const currentUser = await checkLoginStatus();

    if (!currentUser) {
        if (!isLoginPage) {
            showToast('请先登录。即将跳转到登录页面...', 'info', 2000);
            setTimeout(() => { window.location.href = 'login.html'; }, 2000);
        }
        // Else, already on login page, do nothing.
        return; 
    }

    // User is logged in
    if (isLoginPage) { // If logged in and somehow on login page, redirect to index
        window.location.href = 'index.html';
        return;
    }

    // Main page logic (index.html)
    const userRoleName = currentUser.角色 && currentUser.角色.角色名称 ? currentUser.角色.角色名称 : 'Guest';
    sessionStorage.setItem('userRoleName', userRoleName); // Store for potential use by other scripts/pages

    const modules = await fetchUserModules(currentUser.用户ID, userRoleName);
    if (modules) {
        populateNavMenu(modules);
        if (modules.length > 0 && document.getElementById('mainNav').firstChild && typeof document.getElementById('mainNav').firstChild.click === 'function') {
            document.getElementById('mainNav').firstChild.click(); // Auto-select first module
        } else if (modules.length === 0) {
            const navContainer = document.getElementById('mainNav');
            if(navContainer) navContainer.innerHTML = "<p class='px-3 py-2 text-gray-400 text-sm'>无可用模块。</p>";
            const contentFrame = document.getElementById('contentFrame');
            if(contentFrame) contentFrame.srcdoc = "<p class='p-4 text-gray-500'>当前用户角色没有配置任何模块访问权限。</p>";
        }
    } else {
        showToast('未能加载用户模块信息，部分功能可能不可用。', 'error');
        const contentFrame = document.getElementById('contentFrame');
        if(contentFrame) contentFrame.srcdoc = "<p class='p-4 text-red-500'>加载用户模块失败，请联系管理员。</p>";
    }
});

console.log("主应用JavaScript (main.js) 已加载。");
