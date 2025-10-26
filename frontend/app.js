const API_BASE = "http://localhost:5000/api";

let currentConversationId = null;
const chatWindow = document.getElementById("chatWindow");
const form = document.getElementById("chatForm");
const messageInput = document.getElementById("messageInput");
const analysisPanel = document.getElementById("analysisPanel");
const resourceList = document.getElementById("resourceList");
const newConversationButton = document.getElementById("newConversation");

function renderMessage(sender, text) {
  const wrapper = document.createElement("div");
  wrapper.className = `message ${sender}`;
  wrapper.innerText = text;
  chatWindow.appendChild(wrapper);
  chatWindow.scrollTo({ top: chatWindow.scrollHeight, behavior: "smooth" });
}

async function sendMessage(event) {
  event.preventDefault();
  const text = messageInput.value.trim();
  if (!text) {
    return;
  }

  renderMessage("user", text);
  messageInput.value = "";
  messageInput.focus();

  try {
    const response = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: text,
        conversation_id: currentConversationId,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      renderMessage("bot", error.error || "Sorry, something went wrong.");
      return;
    }

    const data = await response.json();
    currentConversationId = data.conversation_id;
    renderMessage("bot", data.response);
    updateAnalysis(data.conversation_id);
  } catch (error) {
    console.error(error);
    renderMessage(
      "bot",
      "I'm having trouble connecting right now. Please double-check your connection and try again."
    );
  }
}

async function updateAnalysis(conversationId) {
  if (!conversationId) {
    analysisPanel.innerHTML = '<p class="muted">No conversation selected.</p>';
    return;
  }

  try {
    const response = await fetch(`${API_BASE}/conversations/${conversationId}/analysis`);
    if (!response.ok) {
      throw new Error("Unable to fetch analysis");
    }
    const data = await response.json();
    renderAnalysis(data);
  } catch (error) {
    console.error(error);
    analysisPanel.innerHTML = '<p class="muted">Analysis is not available at the moment.</p>';
  }
}

function renderAnalysis(data) {
  const { risk_level, message_count, user_message_count, bot_message_count, keyword_flags, last_message_at } = data;

  const riskBadgeClass = risk_level === "immediate_danger" ? "badge urgent" : "badge";
  const riskLabel = risk_level.replace(/_/g, " ");

  const keywordMarkup = keyword_flags.length
    ? keyword_flags
        .map(
          (flag) => `
            <div class="analysis-card">
              <h3>Flagged message <span class="muted">#${flag.message_id}</span></h3>
              <p>${flag.excerpt}</p>
              <p class="muted">Triggers: ${flag.triggers.join(", ")}</p>
              <span class="badge">Level: ${flag.assessed_level.replace(/_/g, " ")}</span>
            </div>
          `
        )
        .join("")
    : '<p class="muted">No keywords detected in recent messages.</p>';

  analysisPanel.innerHTML = `
    <div class="analysis-card">
      <h3>Overview</h3>
      <p>Messages exchanged: <strong>${message_count}</strong></p>
      <p>User messages: <strong>${user_message_count}</strong> &bull; Support messages: <strong>${bot_message_count}</strong></p>
      <p>Last activity: <strong>${new Date(last_message_at).toLocaleString()}</strong></p>
      <span class="${riskBadgeClass}">Risk: ${riskLabel}</span>
    </div>
    ${keywordMarkup}
  `;
}

async function loadResources() {
  try {
    const response = await fetch(`${API_BASE}/resources`);
    if (!response.ok) {
      throw new Error("Unable to load resources");
    }

    const data = await response.json();
    resourceList.innerHTML = data.resources
      .map((resource) => {
        const lines = [];
        lines.push(`<strong>${resource.name}</strong>`);
        if (resource.phone) {
          lines.push(`<span>Phone: <a href="tel:${resource.phone}">${resource.phone}</a></span>`);
        }
        if (resource.chat) {
          lines.push(`<span>Chat: <a href="${resource.chat}" target="_blank" rel="noopener noreferrer">Open chat</a></span>`);
        }
        if (resource.url) {
          lines.push(`<span>More info: <a href="${resource.url}" target="_blank" rel="noopener noreferrer">Visit site</a></span>`);
        }
        if (resource.notes) {
          lines.push(`<span class="muted">${resource.notes}</span>`);
        }
        return `<li class="resource-card">${lines.join("<br>")}</li>`;
      })
      .join("");
  } catch (error) {
    console.error(error);
    resourceList.innerHTML = '<li class="resource-card">Resources are unavailable right now.</li>';
  }
}

function resetConversation() {
  currentConversationId = null;
  chatWindow.innerHTML = "";
  analysisPanel.innerHTML = '<p class="muted">Start a new conversation to see insights.</p>';
  messageInput.focus();
}

form.addEventListener("submit", sendMessage);
newConversationButton.addEventListener("click", resetConversation);

loadResources();
