// frontend/js/auth.js
// 登录页面 (login.html) 特有的 JavaScript 逻辑

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const loginButton = document.getElementById('loginButton');
    const loginErrorDiv = document.getElementById('loginError'); // Changed from errorMessageDiv to loginError
    const loadingOverlay = document.getElementById('loadingOverlay'); // Direct access to loading overlay

    // Helper for loading state - specific to login page
    function showLoginLoading(show = true, message = '请稍候...') {
        if (loadingOverlay) {
            const msgElement = loadingOverlay.querySelector('span');
            if(msgElement) msgElement.textContent = message;
            loadingOverlay.style.visibility = show ? 'visible' : 'hidden';
            loadingOverlay.style.opacity = show ? '1' : '0';
        }
    }
    
    // Helper for toast - specific to login page
    function showLoginToast(message, type = 'info', duration = 3000) {
        const toast = document.getElementById('toast');
        const toastMessage = document.getElementById('toastMessage');
        if (!toast || !toastMessage) {
            console.warn("Toast elements not found in login.html");
            alert(message); // Fallback
            return;
        }

        toastMessage.textContent = message;
        toast.classList.remove('bg-gray-800', 'bg-green-500', 'bg-red-500', 'bg-blue-500', 'opacity-0'); // Clear previous state
        
        if (type === 'success') toast.classList.add('bg-green-500');
        else if (type === 'error') toast.classList.add('bg-red-500');
        else if (type === 'info') toast.classList.add('bg-blue-500');
        else toast.classList.add('bg-gray-800');

        toast.classList.add('opacity-100');
        setTimeout(() => {
            toast.classList.remove('opacity-100');
            toast.classList.add('opacity-0');
        }, duration);
    }


    // Check if already logged in (using /auth/status)
    // This part is slightly redundant if main.js on index.html handles the main auth flow,
    // but good for redirecting if user manually navigates to login.html while logged in.
    fetch('/auth/status')
        .then(response => response.json())
        .then(data => {
            if (data.logged_in && data.user) {
                showLoginToast('您已登录，正在跳转到主页...', 'info');
                setTimeout(() => { window.location.href = 'index.html'; }, 1500);
            }
        })
        .catch(error => {
            console.info("登录状态检查（login.html）：用户未登录或检查时出错。", error);
            // Not critical on login page, user is here to log in.
        });

    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault(); 
            
            if (loginButton) loginButton.disabled = true;
            showLoginLoading(true, '正在登录...');
            if (loginErrorDiv) loginErrorDiv.textContent = ''; // Clear previous error

            const username = loginForm.username.value.trim();
            const password = loginForm.password.value.trim();

            if (!username || !password) {
                showLoginLoading(false);
                showLoginToast('用户名和密码不能为空。', 'error');
                if (loginButton) loginButton.disabled = false;
                return;
            }

            try {
                const response = await fetch('/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password }),
                });

                const data = await response.json();
                showLoginLoading(false);

                if (response.ok && data.success) {
                    showLoginToast('登录成功！即将跳转到主页...', 'success');
                    // Store user information if needed for immediate display or other client-side logic
                    // The main page (index.html) will re-fetch /auth/status anyway.
                    if (data.user) {
                        // Example: sessionStorage.setItem('briefUserInfo', JSON.stringify({ username: data.user.用户名, role: data.user.角色?.角色名称 }));
                        // Storing the role name is useful for immediate UI changes on index.html before full module load
                        sessionStorage.setItem('userRoleName', data.user.角色?.角色名称 || `角色ID_${data.user.角色ID}`);
                        sessionStorage.setItem('username', data.user.用户名); // Store username
                    }
                    setTimeout(() => { window.location.href = 'index.html'; }, 1500);
                } else {
                    const message = data.message || `登录失败 (状态码: ${response.status})`;
                    if (loginErrorDiv) loginErrorDiv.textContent = message;
                    else showLoginToast(message, 'error'); // Fallback if specific div is missing
                    if (loginButton) loginButton.disabled = false;
                }
            } catch (error) {
                showLoginLoading(false);
                console.error('登录请求处理失败:', error);
                const message = `发生网络错误或服务器无响应。请稍后重试。(${error.message || '未知网络错误'})`;
                if (loginErrorDiv) loginErrorDiv.textContent = message;
                else showLoginToast(message, 'error');
                if (loginButton) loginButton.disabled = false;
            }
        });
    } else {
        console.error("登录表单 'loginForm' 未在页面中找到。");
    }
});

console.log("登录页面JavaScript (auth.js) 已加载并更新。");
