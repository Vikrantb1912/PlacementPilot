/* ============================================================
   PlacementPilot AI — Main JavaScript (main.js)
   Handles: dark mode, markdown rendering, copy, AI helpers
   ============================================================ */

/* ── 1. DARK MODE ─────────────────────────────────────────── */
(function () {
  const STORAGE_KEY = "pp-theme";
  const html = document.documentElement;

  function setTheme(dark) {
    html.setAttribute("data-bs-theme", dark ? "dark" : "light");
    localStorage.setItem(STORAGE_KEY, dark ? "dark" : "light");
    const icon = document.getElementById("darkToggle");
    if (icon) {
      icon.innerHTML = dark
        ? '<i class="bi bi-sun-fill"></i>'
        : '<i class="bi bi-moon-stars"></i>';
    }
  }

  function initTheme() {
    const saved = localStorage.getItem(STORAGE_KEY);
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    setTheme(saved ? saved === "dark" : prefersDark);
  }

  initTheme();

  document.addEventListener("DOMContentLoaded", () => {
    const btn = document.getElementById("darkToggle");
    if (btn) {
      btn.addEventListener("click", () => {
        const isDark = html.getAttribute("data-bs-theme") === "dark";
        setTheme(!isDark);
      });
    }

    // Flash auto-dismiss
    setTimeout(() => {
      document.querySelectorAll(".pp-alert").forEach(el => {
        const bsAlert = bootstrap.Alert.getOrCreateInstance(el);
        if (bsAlert) bsAlert.close();
      });
    }, 4000);

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(a => {
      a.addEventListener("click", e => {
        const target = document.querySelector(a.getAttribute("href"));
        if (target) {
          e.preventDefault();
          target.scrollIntoView({ behavior: "smooth" });
        }
      });
    });
  });
})();

/* ── 2. MARKDOWN RENDERER ────────────────────────────────── */
/**
 * Convert simple markdown-like text to HTML.
 * Handles: headings, bold, code, lists, hr, blockquote, line breaks.
 */
function renderMarkdown(containerId, text) {
  if (!text) return;
  const el = document.getElementById(containerId);
  if (!el) return;

  let html = escapeHtml(text);

  // Headings
  html = html.replace(/^#{4}\s+(.+)$/gm, "<h4>$1</h4>");
  html = html.replace(/^#{3}\s+(.+)$/gm, "<h3>$1</h3>");
  html = html.replace(/^#{2}\s+(.+)$/gm, "<h2>$1</h2>");
  html = html.replace(/^#{1}\s+(.+)$/gm, "<h2>$1</h2>");

  // Bold **text** or __text__
  html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/__(.+?)__/g, "<strong>$1</strong>");

  // Italic *text*
  html = html.replace(/\*([^*\n]+)\*/g, "<em>$1</em>");

  // Inline code `code`
  html = html.replace(/`([^`\n]+)`/g, '<code>$1</code>');

  // Code blocks ```
  html = html.replace(/```[\w]*\n?([\s\S]*?)```/g, (_, code) =>
    `<pre><code>${code.trim()}</code></pre>`
  );

  // Horizontal rule
  html = html.replace(/^---+$/gm, "<hr/>");

  // Blockquote
  html = html.replace(/^&gt;\s*(.+)$/gm, "<blockquote>$1</blockquote>");

  // Ordered list items
  html = html.replace(/^\d+\.\s+(.+)$/gm, "<li>$1</li>");
  html = html.replace(/(<li>.*<\/li>(\n|$))+/g, m => `<ol>${m}</ol>`);

  // Unordered list items (- or •)
  html = html.replace(/^[-•]\s+(.+)$/gm, "<li>$1</li>");

  // Wrap consecutive <li> not inside <ol> in <ul>
  html = html.replace(/(?<!<ol>)(<li>[\s\S]*?<\/li>\n?)+(?!<\/ol>)/g, m => {
    if (m.trim().startsWith("<li>")) return `<ul>${m}</ul>`;
    return m;
  });

  // Line breaks → <br>
  html = html.replace(/\n{2,}/g, "</p><p>");
  html = html.replace(/\n/g, "<br/>");
  html = `<p>${html}</p>`;

  // Clean up: p tags around block elements
  html = html.replace(/<p>(<h[1-6]>|<ul>|<ol>|<pre>|<hr|<blockquote>)/g, "$1");
  html = html.replace(/(<\/h[1-6]>|<\/ul>|<\/ol>|<\/pre>|<\/blockquote>)<\/p>/g, "$1");
  html = html.replace(/<p><\/p>/g, "");

  el.innerHTML = html;
  el.classList.add("ai-result-content");

  // Scroll into view
  el.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function escapeHtml(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

/* ── 3. AI LOADING STATE ─────────────────────────────────── */
function showAILoading(containerId, message = "AI is thinking...") {
  const el = document.getElementById(containerId);
  if (!el) return;
  el.innerHTML = `
    <div class="ai-loading">
      <div class="ai-spinner"></div>
      <div class="text-muted small">${message}</div>
      <div class="text-muted" style="font-size:0.72rem">Powered by IBM Granite · IBM watsonx.ai</div>
    </div>`;
}

/* ── 4. COPY TO CLIPBOARD ────────────────────────────────── */
function copyResult(containerId) {
  const el = document.getElementById(containerId);
  if (!el) return;
  const text = el.innerText || el.textContent;
  navigator.clipboard.writeText(text).then(() => {
    showToast("Copied to clipboard!", "success");
  }).catch(() => {
    // Fallback
    const ta = document.createElement("textarea");
    ta.value = text;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand("copy");
    document.body.removeChild(ta);
    showToast("Copied!", "success");
  });
}

/* ── 5. TOAST NOTIFICATIONS ──────────────────────────────── */
function showToast(message, type = "info") {
  let container = document.getElementById("pp-toast-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "pp-toast-container";
    container.style.cssText = "position:fixed;bottom:1.5rem;right:1.5rem;z-index:9999;display:flex;flex-direction:column;gap:0.5rem;";
    document.body.appendChild(container);
  }
  const colors = { success: "#10b981", danger: "#ef4444", info: "#3b82d4", warning: "#f59e0b" };
  const icons = { success: "check-circle-fill", danger: "x-circle-fill", info: "info-circle-fill", warning: "exclamation-triangle-fill" };
  const toast = document.createElement("div");
  toast.style.cssText = `
    background:var(--pp-surface);
    border:1px solid var(--pp-border);
    border-left:4px solid ${colors[type] || colors.info};
    border-radius:10px;padding:0.65rem 1rem;
    font-size:0.85rem;display:flex;align-items:center;gap:0.5rem;
    box-shadow:0 4px 16px rgba(0,0,0,0.15);
    animation:slideInRight 0.3s ease;max-width:280px;
  `;
  toast.innerHTML = `<i class="bi bi-${icons[type] || icons.info}" style="color:${colors[type]};font-size:1rem"></i>${message}`;
  container.appendChild(toast);

  // Add keyframe if not already
  if (!document.getElementById("pp-toast-style")) {
    const style = document.createElement("style");
    style.id = "pp-toast-style";
    style.textContent = "@keyframes slideInRight{from{transform:translateX(100%);opacity:0}to{transform:translateX(0);opacity:1}}";
    document.head.appendChild(style);
  }

  setTimeout(() => {
    toast.style.transition = "opacity 0.3s";
    toast.style.opacity = "0";
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

/* ── 6. SIDEBAR TOGGLE (mobile) ─────────────────────────── */
function toggleSidebar() {
  const sidebar = document.querySelector(".chat-sidebar");
  if (sidebar) sidebar.classList.toggle("open");
}

// Close sidebar on outside click
document.addEventListener("click", e => {
  const sidebar = document.querySelector(".chat-sidebar");
  const toggle = document.getElementById("sidebarToggle");
  if (sidebar && sidebar.classList.contains("open")) {
    if (!sidebar.contains(e.target) && !toggle.contains(e.target)) {
      sidebar.classList.remove("open");
    }
  }
});
