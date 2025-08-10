const API_BASE = '';

async function fetchUsers() {
  const res = await fetch(`${API_BASE}/users`);
  if (!res.ok) throw new Error('Failed to load users');
  return res.json();
}

function renderUsers(users) {
  const tbody = document.getElementById('users-body');
  tbody.innerHTML = '';
  users.forEach(u => {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${u.name}</td><td>${u.email}</td><td><button data-id="${u.id}" class="delete">Delete</button></td>`;
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
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  if (!res.ok) throw new Error('Failed to add user');
  return res.json();
}

async function deleteUser(id) {
  const res = await fetch(`${API_BASE}/users/${id}`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Failed to delete user');
}

document.addEventListener('DOMContentLoaded', () => {
  loadUsers();

  document.getElementById('user-form').addEventListener('submit', async e => {
    e.preventDefault();
    const form = e.target;
    const data = {
      name: form.name.value.trim(),
      email: form.email.value.trim()
    };
    if (!data.name || !data.email) return;
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
