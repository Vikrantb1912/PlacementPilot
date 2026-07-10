/* ============================================================
   PlacementPilot AI — Chat JavaScript (chat.js)
   Handles: sending messages, receiving AI responses,
            streaming-style display, module switching
   ============================================================ */

let currentModule = "general";
let isLoading = false;

/* ── 1. MODULE SWITCHING ─────────────────────────────────── */
const MODULE_LABELS = {
  general: "General Chat",
  dsa: "DSA & Algorithms",
  roadmap: "Placement Roadmap",
  resume: "Resume Review",
  interview: "Mock Interview",
  hr: "HR Preparation",
  aptitude: "Aptitude Practice",
  company: "Company Guide",
  projects: "Project Ideas",
};

function setModule(module, btn) {
  currentModule = module;
  const badge = document.getElementById("currentModuleBadge");
  if (badge) badge.textContent = MODULE_LABELS[module] || "General Chat";
}

/* ── 2. SEND MESSAGE ─────────────────────────────────────── */
async function sendMessage() {
  if (isLoading) return;
  const input = document.getElementById("chatInput");
  const msg = (input.value || "").trim();
  if (!msg) return;

  input.value = "";
  autoResize(input);
  appendMessage("user", msg);
  showTypingIndicator();
  setLoading(true);

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: msg, module: currentModule }),
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.error || `HTTP ${res.status}`);
    }

    const data = await res.json();
    hideTypingIndicator();
    appendMessage("assistant", data.response || "No response received.", data.timestamp);
  } catch (err) {
    hideTypingIndicator();
    appendMessage(
      "assistant",
      `⚠️ **Error:** ${err.message}\n\nPlease check your IBM API credentials in the \`.env\` file and try again.`
    );
  } finally {
    setLoading(false);
  }
}

/* ── 3. APPEND MESSAGE TO DOM ────────────────────────────── */
function appendMessage(role, content, timestamp) {
  const messages = document.getElementById("chatMessages");

  // Remove welcome screen on first message
  const welcome = messages.querySelector(".chat-welcome");
  if (welcome) welcome.remove();

  const row = document.createElement("div");
  row.className = `message-row ${role === "user" ? "user-row" : "bot-row"}`;

  const time = timestamp || new Date().toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" });

  if (role === "assistant") {
    row.innerHTML = `
      <div class="msg-avatar bot-avatar"><i class="bi bi-mortarboard-fill"></i></div>
      <div class="message-bubble bot-bubble">
        <div class="msg-content" id="msg-${Date.now()}"></div>
        <div class="msg-time">${time}</div>
      </div>`;
    messages.appendChild(row);

    // Render markdown
    const contentId = `msg-${Date.now() - 1}`;
    row.querySelector(".msg-content").id = contentId;
    renderMarkdown(contentId, content);
  } else {
    row.innerHTML = `
      <div class="message-bubble user-bubble">
        <div class="msg-content">${escapeHtmlChat(content)}</div>
        <div class="msg-time">${time}</div>
      </div>
      <div class="msg-avatar user-avatar"><i class="bi bi-person-fill"></i></div>`;
    messages.appendChild(row);
  }

  scrollToBottom();
}

function escapeHtmlChat(str) {
  const map = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" };
  return str.replace(/[&<>"']/g, c => map[c]);
}

/* ── 4. TYPING INDICATOR ─────────────────────────────────── */
function showTypingIndicator() {
  const indicator = document.getElementById("typingIndicator");
  if (indicator) {
    indicator.classList.remove("d-none");
    scrollToBottom();
  }
}

function hideTypingIndicator() {
  const indicator = document.getElementById("typingIndicator");
  if (indicator) indicator.classList.add("d-none");
}

/* ── 5. SCROLL TO BOTTOM ─────────────────────────────────── */
function scrollToBottom() {
  const messages = document.getElementById("chatMessages");
  if (messages) {
    requestAnimationFrame(() => {
      messages.scrollTop = messages.scrollHeight;
    });
  }
}

/* ── 6. LOADING STATE ────────────────────────────────────── */
function setLoading(loading) {
  isLoading = loading;
  const btn = document.getElementById("sendBtn");
  const input = document.getElementById("chatInput");
  if (btn) {
    btn.disabled = loading;
    btn.innerHTML = loading
      ? '<span class="spinner-border spinner-border-sm" style="width:14px;height:14px;border-width:2px"></span>'
      : '<i class="bi bi-send-fill"></i>';
  }
  if (input) input.disabled = loading;
}

/* ── 7. KEYBOARD HANDLER ─────────────────────────────────── */
function handleKey(event) {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendMessage();
  }
}

/* ── 8. AUTO RESIZE TEXTAREA ─────────────────────────────── */
function autoResize(el) {
  el.style.height = "auto";
  el.style.height = Math.min(el.scrollHeight, 150) + "px";
}

/* ── 9. SUGGESTION CHIPS ─────────────────────────────────── */
function sendSuggestion(btn) {
  const text = btn.textContent
    .replace(/^[^\w]+/, "") // remove leading emoji/symbol
    .trim();
  const input = document.getElementById("chatInput");
  if (input) {
    input.value = text;
    sendMessage();
  }
}

/* ── 10. CLEAR CHAT ──────────────────────────────────────── */
async function clearChat() {
  if (!confirm("Clear all chat history?")) return;
  try {
    await fetch("/api/clear-chat", { method: "POST" });
    const messages = document.getElementById("chatMessages");
    if (messages) {
      messages.innerHTML = `
        <div class="chat-welcome text-center py-4">
          <div class="welcome-icon"><i class="bi bi-mortarboard-fill"></i></div>
          <h5 class="fw-bold mt-3">Chat cleared!</h5>
          <p class="text-muted">Start a new conversation. Ask me anything about placements.</p>
        </div>`;
    }
    showToast("Chat history cleared", "success");
  } catch (e) {
    showToast("Failed to clear chat", "danger");
  }
}

/* ── 11. URL MODULE PARAM ────────────────────────────────── */
(function () {
  const params = new URLSearchParams(window.location.search);
  const mod = params.get("module");
  if (mod && MODULE_LABELS[mod]) {
    currentModule = mod;
    const badge = document.getElementById("currentModuleBadge");
    if (badge) badge.textContent = MODULE_LABELS[mod];

    // Activate sidebar button
    const btn = document.querySelector(`[data-module="${mod}"]`);
    if (btn) {
      document.querySelectorAll(".sidebar-topic-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
    }
  }
})();

/* ── 12. SCROLL ON LOAD ──────────────────────────────────── */
document.addEventListener("DOMContentLoaded", scrollToBottom);
