const chatWindow = document.getElementById('chatWindow');
const chatInput = document.getElementById('chatInput');
const sendButton = document.getElementById('sendButton');
const refreshButton = document.getElementById('refreshButton');
const themeToggle = document.getElementById('themeToggle');

function appendMessage(htmlContent, type) {
  const msgDiv = document.createElement('div');
  msgDiv.className = 'message ' + (type === 'user' ? 'user' : 'bot');
  msgDiv.innerHTML = htmlContent;
  chatWindow.appendChild(msgDiv);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function renderRecommendations(recommendations) {
  let html = `<div><strong>Here are some recommendations:</strong></div>`;
  recommendations.forEach(rec => {
    html += `<div class="rec-item" id="rec-${rec.id}">
               <div>
                 <strong>${rec.title}</strong>
                 <small>(score: ${parseFloat(rec.similarity).toFixed(2)})</small>
               </div>
               <div class="feedback-buttons">
                 <i class="fas fa-thumbs-up text-success" title="Good" onclick="sendFeedback('${rec.id}', 1)"></i>
                 <i class="fas fa-thumbs-down text-danger" title="Bad" onclick="sendFeedback('${rec.id}', -1)"></i>
               </div>
             </div>`;
  });
  return html;
}

function processUserMessage() {
  const message = chatInput.value.trim();
  if (!message) return;
  appendMessage(message, 'user');
  chatInput.value = '';
  fetch("/retrain", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ preferences: message })
  })
  .then(res => res.json())
  .then(data => {
    if (data.error) {
      appendMessage("Error: " + data.error, 'bot');
    } else {
      const recHtml = renderRecommendations(data.recommendations);
      appendMessage(recHtml, 'bot');
    }
  })
  .catch(err => {
    console.error(err);
    appendMessage("Error connecting to server", 'bot');
  });
}

function sendFeedback(animeId, rating) {
  const username = "chatUser";
  fetch("/feedback", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username: username, anime_id: parseInt(animeId), rating: rating })
  })
  .then(res => res.json())
  .then(data => alert(data.message || data.error))
  .catch(err => {
    console.error(err);
    alert("Error sending feedback");
  });
}

function refreshRecommendations() {
  const prev_ids = [];
  document.querySelectorAll('.rec-item').forEach(item => {
    const idStr = item.getAttribute('id');
    if (idStr && idStr.startsWith("rec-")) {
      prev_ids.push(idStr.replace("rec-", ""));
    }
  });
  const userMessages = document.querySelectorAll('.message.user');
  let lastMessage = "";
  if (userMessages.length > 0) {
    lastMessage = userMessages[userMessages.length - 1].innerText;
  }
  fetch("/retrain", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ preferences: lastMessage, prev_ids: prev_ids })
  })
  .then(res => res.json())
  .then(data => {
    if (data.error) {
      appendMessage("Error: " + data.error, 'bot');
    } else {
      const recHtml = renderRecommendations(data.recommendations);
      appendMessage(recHtml, 'bot');
    }
  })
  .catch(err => {
    console.error(err);
    appendMessage("Error refreshing recommendations", 'bot');
  });
}

function initChat() {
  if (chatWindow.children.length === 0) {
    appendMessage("Specify your Anilist username or what you like", "bot");
  }
}

document.addEventListener("DOMContentLoaded", initChat);
sendButton.addEventListener('click', processUserMessage);
chatInput.addEventListener('keyup', e => {
  if (e.key === 'Enter') processUserMessage();
});
refreshButton.addEventListener('click', e => {
  e.preventDefault();
  refreshRecommendations();
});
themeToggle.addEventListener('click', () => {
  document.body.classList.toggle('dark');
});
