async function fetchCandidates() {
  const res = await fetch('/api/candidates');
  const candidates = await res.json();
  const list = document.getElementById('candidate-list');
  list.innerHTML = '';
  candidates.forEach(c => {
    const li = document.createElement('li');
    li.textContent = `${c.name} (${c.email})`;
    list.appendChild(li);
  });
}

document.getElementById('candidate-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const name = document.getElementById('name').value;
  const email = document.getElementById('email').value;
  await fetch('/api/candidates', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, email })
  });
  document.getElementById('name').value = '';
  document.getElementById('email').value = '';
  fetchCandidates();
});

fetchCandidates();
