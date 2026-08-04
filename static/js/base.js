const token = localStorage.getItem('token');
if (!token) window.location.href = '/';

async function fetchWithAuth(url, options = {}) {
    options.headers = { ...options.headers, 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' };
    return fetch(url, options);
}

function performLogout() { localStorage.removeItem('token'); window.location.href = '/'; }

function showToast(msg, type='success') {
    const el = document.getElementById('toastMsg');
    if (!el) return;
    el.classList.remove('hidden');
    el.innerText = msg;
    if(type === 'error') { el.className = 'text-center p-4 mx-6 mb-6 rounded-lg bg-red-500/20 text-red-400 border border-red-500/30'; }
    else if(type === 'info') { el.className = 'text-center p-4 mx-6 mb-6 rounded-lg bg-blue-500/20 text-blue-400 border border-blue-500/30'; }
    else { el.className = 'text-center p-4 mx-6 mb-6 rounded-lg bg-green-500/20 text-green-400 border border-green-500/30'; }
    setTimeout(() => { el.classList.add('hidden'); }, 10000);
}
