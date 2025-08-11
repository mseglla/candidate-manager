const API_BASE = '';

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('login-form');
  form.addEventListener('submit', async e => {
    e.preventDefault();
    const data = {
      username: form.username.value.trim(),
      password: form.password.value
    };
    try {
      const res = await fetch(`${API_BASE}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      if (res.ok) {
        const payload = await res.json();
        localStorage.setItem('token', payload.token);
        window.location.href = 'index.html';
      } else {
        alert('Invalid credentials');
      }
    } catch (err) {
      console.error(err);
    }
  });
});
