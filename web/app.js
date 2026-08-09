const messages = document.querySelector('#messages');
const form = document.querySelector('#chatForm');
const prompt = document.querySelector('#prompt');
const send = document.querySelector('#send');

function addMessage(role, text) {
  const row = document.createElement('div');
  row.className = `message ${role}`;
  const avatar = document.createElement('div');
  avatar.className = 'avatar';
  avatar.textContent = role === 'user' ? 'EU' : 'Z';
  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.textContent = text;
  row.append(avatar, bubble);
  messages.appendChild(row);
  messages.scrollTop = messages.scrollHeight;
  return bubble;
}

function clearWelcome() {
  const welcome = messages.querySelector('.welcome');
  if (welcome) welcome.remove();
}

async function sendMessage(text) {
  clearWelcome();
  addMessage('user', text);
  const bubble = addMessage('agent', 'Pensando…');
  send.disabled = true;
  prompt.disabled = true;
  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({message: text})
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Falha ao consultar o agente.');
    bubble.textContent = data.response;
    if (data.tool_used) bubble.textContent += `\n\nFerramenta: ${data.tool_used}`;
  } catch (error) {
    bubble.textContent = `Erro: ${error.message}`;
  } finally {
    send.disabled = false;
    prompt.disabled = false;
    prompt.focus();
  }
}

form.addEventListener('submit', event => {
  event.preventDefault();
  const text = prompt.value.trim();
  if (!text) return;
  prompt.value = '';
  prompt.style.height = 'auto';
  sendMessage(text);
});

prompt.addEventListener('input', () => {
  prompt.style.height = 'auto';
  prompt.style.height = `${Math.min(prompt.scrollHeight, 140)}px`;
});

document.querySelectorAll('[data-prompt]').forEach(button => {
  button.addEventListener('click', () => sendMessage(button.dataset.prompt));
});

document.querySelector('#newChat').addEventListener('click', () => location.reload());
