const state = {
  messages: [],
  participants: [],
};

const messagesEl = document.getElementById("messages");
const participantsEl = document.getElementById("participants");
const tupleViewEl = document.getElementById("tuple-view");
const eventCountEl = document.getElementById("event-count");
const composer = document.getElementById("composer");
const input = document.getElementById("message-input");

const fallbackSession = {
  participants: [
    { participant_id: "owner", display_name: "Owner", participant_type: "human", role: "company_owner" },
    { participant_id: "Aiden", display_name: "Aiden", participant_type: "agent", role: "CEO principal" },
    { participant_id: "StrategyAgent", display_name: "Strategy Agent", participant_type: "agent", role: "market analyst" },
    { participant_id: "FinanceAgent", display_name: "Finance Agent", participant_type: "agent", role: "wallet proposal analyst" },
  ],
  message_packets: [
    {
      message: {
        message_id: "fallback_001",
        sender_id: "Aiden",
        recipient_ids: ["owner"],
        message_kind: "governance_notice",
        human_readable_text: "The messenger is local-only and every formal message carries a CIEU/CZL five-tuple.",
        cieu_five_tuple: {
          Y_star_t: "Company communication becomes human-readable and machine-governed.",
          X_t: { source: "static UI fallback" },
          U_t: { speech_act: "explain_protocol" },
          Y_t_plus_1: "Owner can inspect message provenance.",
          R_t_plus_1: "pending until local runtime responds",
          residual_status: "planning_residual_pending",
        },
      },
    },
  ],
  CIEUStore_summary: { event_count: 0 },
};

async function loadDemo() {
  try {
    const res = await fetch("/api/demo-session");
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    hydrate(await res.json());
  } catch (error) {
    hydrate(fallbackSession);
  }
}

function hydrate(session) {
  state.participants = session.participants || [];
  state.messages = (session.message_packets || []).map((packet) => packet.message);
  renderParticipants();
  renderMessages();
  eventCountEl.textContent = `${session.CIEUStore_summary?.event_count || 0} CIEU events`;
  if (state.messages[0]) renderTuple(state.messages[0]);
}

function renderParticipants() {
  participantsEl.innerHTML = "";
  state.participants.forEach((participant) => {
    const li = document.createElement("li");
    li.innerHTML = `<strong>${participant.display_name}</strong><span>${participant.participant_type}</span>`;
    participantsEl.appendChild(li);
  });
}

function renderMessages() {
  messagesEl.innerHTML = "";
  state.messages.forEach((message) => {
    const card = document.createElement("article");
    card.className = `message ${message.sender_id}`;
    card.tabIndex = 0;
    card.innerHTML = `
      <div class="meta">
        <span>${message.sender_id} -> ${(message.recipient_ids || []).join(", ")}</span>
        <span>${message.message_kind}</span>
      </div>
      <p>${escapeHtml(message.human_readable_text || "")}</p>
      <div class="tuple-strip">
        <span>Y*</span><span>X</span><span>U</span><span>Y+1</span><span>R+1</span>
      </div>
    `;
    card.addEventListener("click", () => renderTuple(message));
    card.addEventListener("keypress", (event) => {
      if (event.key === "Enter") renderTuple(message);
    });
    messagesEl.appendChild(card);
  });
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function renderTuple(message) {
  const tuple = message.cieu_five_tuple || {};
  const labels = [
    ["Y*_t", tuple.Y_star_t],
    ["X_t", tuple.X_t],
    ["U_t", tuple.U_t],
    ["Y_t+1", tuple.Y_t_plus_1],
    ["R_t+1", tuple.R_t_plus_1],
    ["Residual Status", tuple.residual_status],
  ];
  tupleViewEl.innerHTML = "";
  labels.forEach(([label, value]) => {
    const div = document.createElement("div");
    div.className = "tuple-card";
    div.innerHTML = `<strong>${label}</strong><code>${escapeHtml(formatValue(value))}</code>`;
    tupleViewEl.appendChild(div);
  });
}

composer.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  try {
    const res = await fetch("/api/messages", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, recipient_id: "Aiden" }),
    });
    const payload = await res.json();
    const turnMessages = (payload.message_packets || [])
      .map((packet) => packet.message)
      .filter(Boolean);
    if (turnMessages.length) {
      state.messages.push(...turnMessages);
      renderMessages();
      renderTuple(turnMessages[turnMessages.length - 1]);
    } else if (payload.packet?.message) {
      state.messages.push(payload.packet.message);
      renderMessages();
      renderTuple(payload.packet.message);
    }
  } catch (error) {
    const fallbackMessage = {
      sender_id: "owner",
      recipient_ids: ["Aiden"],
      message_kind: "human_to_agent",
      human_readable_text: text,
      cieu_five_tuple: {
        Y_star_t: "Owner message should become governed local communication.",
        X_t: { source: "browser fallback" },
        U_t: { speech_act: "owner_message" },
        Y_t_plus_1: "Aiden should receive a governed packet when server is available.",
        R_t_plus_1: "pending",
        residual_status: "planning_residual_pending",
      },
    };
    state.messages.push(fallbackMessage);
    renderMessages();
    renderTuple(fallbackMessage);
  }
});

function formatValue(value) {
  if (typeof value === "string") return value;
  return JSON.stringify(value, null, 2);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

loadDemo();
