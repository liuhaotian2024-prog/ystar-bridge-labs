const historyEl = document.getElementById("chat-history");
const form = document.getElementById("aiden-chat-form");
const textarea = document.getElementById("aiden-message");
const statusEl = document.getElementById("chat-status");

function escapeHtml(value) {
  return String(value || "").replace(/[&<>"']/g, (ch) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  }[ch]));
}

function renderTurn(turn) {
  const isOwner = turn.speaker === "owner";
  return `
    <div class="message ${isOwner ? "owner" : "aiden"}">
      <strong>${isOwner ? "你" : "Aiden"}</strong>
      <p>${escapeHtml(turn.text)}</p>
    </div>`;
}

function renderHistory(history) {
  const turns = history && history.length ? history : [{
    speaker: "aiden_ceo",
    text: "我在。你直接说问题就行，我会尽量用清楚的人话回答。",
  }];
  historyEl.innerHTML = turns.slice(-30).map(renderTurn).join("");
  historyEl.scrollTop = historyEl.scrollHeight;
}

async function loadHistory() {
  const response = await fetch("/api/aiden_chat");
  if (!response.ok) return;
  const data = await response.json();
  renderHistory(data.history || []);
}

async function sendMessage(text) {
  const response = await fetch("/api/aiden_chat", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({message: text}),
  });
  const data = await response.json();
  if (!response.ok || !data.ok) {
    throw new Error(data.error || "Aiden 没有成功回复。");
  }
  renderHistory(data.history || []);
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = textarea.value.trim();
  if (!text) return;
  textarea.value = "";
  statusEl.textContent = "Aiden 正在本地回复...";
  form.querySelector("button").disabled = true;
  renderHistory([
    ...Array.from(historyEl.querySelectorAll(".message")).map((node) => ({
      speaker: node.classList.contains("owner") ? "owner" : "aiden_ceo",
      text: node.querySelector("p")?.textContent || "",
    })),
    {speaker: "owner", text},
  ]);
  try {
    await sendMessage(text);
    statusEl.textContent = "已本地回复。没有外发、没有邮件、没有客户联系。";
  } catch (error) {
    statusEl.textContent = error.message;
  } finally {
    form.querySelector("button").disabled = false;
    textarea.focus();
  }
});

loadHistory();
