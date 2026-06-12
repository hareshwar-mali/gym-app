const API_BASE = 'http://127.0.0.1:8000/api';

function getToken() { return localStorage.getItem('access_token'); }
function getRefreshToken() { return localStorage.getItem('refresh_token'); }
function getGym() { return JSON.parse(localStorage.getItem('gym_data') || 'null'); }
function getRole() { return localStorage.getItem('role'); }

function saveAuth(data) {
  localStorage.setItem('access_token', data.access);
  localStorage.setItem('refresh_token', data.refresh);
  localStorage.setItem('role', data.role);
  if (data.gym) localStorage.setItem('gym_data', JSON.stringify(data.gym));
}

function clearAuth() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('gym_data');
  localStorage.removeItem('role');
}

async function refreshToken() {
  const refresh = getRefreshToken();
  if (!refresh) return false;
  try {
    const res = await fetch(`${API_BASE}/auth/token/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh })
    });
    if (res.ok) {
      const data = await res.json();
      localStorage.setItem('access_token', data.access);
      return true;
    }
  } catch {}
  return false;
}

async function api(method, endpoint, body = null, retry = true) {
  const token = getToken();
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const opts = { method, headers };
  if (body) opts.body = JSON.stringify(body);

  let res = await fetch(`${API_BASE}${endpoint}`, opts);

  if (res.status === 401 && retry) {
    const ok = await refreshToken();
    if (ok) return api(method, endpoint, body, false);
    clearAuth();
    window.location.href = getRootPath() + 'index.html';
    return null;
  }
  return res;
}

function getRootPath() {
  const path = window.location.pathname;
  if (path.includes('/gym-admin/') || path.includes('/super-admin/')) return '../';
  return '';
}

function checkGymAuth() {
  if (!getToken() || getRole() !== 'gym_owner') {
    window.location.href = getRootPath() + 'index.html';
    return null;
  }
  const gym = getGym();
  if (gym && (gym.status === 'trial_expired' || gym.status === 'expired')) {
    if (!window.location.href.includes('subscription.html')) {
      window.location.href = getRootPath() + 'gym-admin/subscription.html';
    }
  }
  return gym;
}

function checkSuperAuth() {
  if (!getToken() || getRole() !== 'super_admin') {
    window.location.href = getRootPath() + 'index.html';
    return false;
  }
  return true;
}

function logout() {
  clearAuth();
  window.location.href = getRootPath() + 'index.html';
}

function showToast(msg, type = 'success') {
  const existing = document.getElementById('toast');
  if (existing) existing.remove();
  const toast = document.createElement('div');
  toast.id = 'toast';
  toast.className = `toast toast-${type}`;
  toast.textContent = msg;
  document.body.appendChild(toast);
  setTimeout(() => toast.classList.add('show'), 10);
  setTimeout(() => { toast.classList.remove('show'); setTimeout(() => toast.remove(), 300); }, 3000);
}

function formatDate(dateStr) {
  if (!dateStr) return '—';
  return new Date(dateStr).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
}

function daysLeft(dateStr) {
  if (!dateStr) return 0;
  return Math.ceil((new Date(dateStr) - new Date()) / (1000 * 60 * 60 * 24));
}

function todayStr() {
  return new Date().toISOString().split('T')[0];
}

function getSubscriptionBanner(gym) {
  if (!gym) return '';
  const days = daysLeft(gym.subscription_end_date || gym.trial_end_date);
  const status = gym.status;
  if (status === 'trial_active') {
    if (days <= 3) return `<div class="sub-banner warn">⚠️ Your free trial expires in ${days} day${days !== 1 ? 's' : ''}. <a href="../gym-admin/subscription.html">Upgrade now</a></div>`;
    return `<div class="sub-banner info">🎯 Free Trial — ${days} days remaining</div>`;
  }
  if (status === 'expiring_soon') return `<div class="sub-banner warn">⚠️ Subscription expires in ${days} day${days !== 1 ? 's' : ''}. <a href="../gym-admin/subscription.html">Renew now</a></div>`;
  if (status === 'trial_expired' || status === 'expired') return `<div class="sub-banner danger">🚫 Your subscription has expired. <a href="../gym-admin/subscription.html">Choose a plan</a></div>`;
  return '';
}
