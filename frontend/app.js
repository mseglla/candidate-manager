const API_BASE = '';
const token = localStorage.getItem('token');
if (!token) {
  window.location.href = 'login.html';
}

async function fetchUsers() {
  const res = await fetch(`${API_BASE}/users`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  if (!res.ok) throw new Error('Failed to load users');
  return res.json();
}

function renderUsers(users) {
  const tbody = document.getElementById('users-body');
  tbody.innerHTML = '';
  users.forEach(u => {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${u.username}</td><td>${u.email}</td><td><button data-id="${u.id}" class="delete">Delete</button></td>`;
    tbody.appendChild(tr);
  });
}

async function loadUsers() {
  try {
    const users = await fetchUsers();
    renderUsers(users);
  } catch (e) {
    console.error(e);
  }
}

async function addUser(data) {
  const res = await fetch(`${API_BASE}/users`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(data)
  });
  if (!res.ok) throw new Error('Failed to add user');
  return res.json();
}

async function deleteUser(id) {
  const res = await fetch(`${API_BASE}/users/${id}`, {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${token}` }
  });
  if (!res.ok) throw new Error('Failed to delete user');
}

document.addEventListener('DOMContentLoaded', () => {
  loadUsers();

  document.getElementById('user-form').addEventListener('submit', async e => {
    e.preventDefault();
    const form = e.target;
    const data = {
      username: form.username.value.trim(),
      email: form.email.value.trim(),
      password: form.password.value
    };
    if (!data.username || !data.email || !data.password) return;
    try {
      await addUser(data);
      form.reset();
      loadUsers();
    } catch (err) {
      console.error(err);
    }
  });

  document.getElementById('users-table').addEventListener('click', async e => {
    if (e.target.matches('button.delete')) {
      const id = e.target.dataset.id;
      try {
        await deleteUser(id);
        loadUsers();
      } catch (err) {
        console.error(err);
      }
    }
  });
});
