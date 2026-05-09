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
const sendButton = composer.querySelector("button[type='submit']");
const runtimeStatusEl = document.createElement("div");
runtimeStatusEl.className = "runtime-status idle";
runtimeStatusEl.textContent = "Ready";
composer.insertAdjacentElement("beforebegin", runtimeStatusEl);

const MESSENGER_REQUEST_TIMEOUT_MS = 150000;
const LONG_OWNER_MESSAGE_COLLAPSE_CHARS = 420;

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
state.expandedMessageIds = new Set();

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
  state.messages.forEach((message, index) => {
    const messageId = message.message_id || `${message.sender_id}_${index}`;
    const collapseState = getMessageCollapseState(message, messageId);
    const card = document.createElement("article");
    card.className = `message ${message.sender_id}${message.pending ? " pending" : ""}`;
    card.tabIndex = 0;
    card.innerHTML = `
      <div class="meta">
        <span>${message.sender_id} -> ${(message.recipient_ids || []).join(", ")}</span>
        <span>${message.message_kind}</span>
      </div>
      <p>${escapeHtml(collapseState.displayText)}</p>
      ${collapseState.isLong ? `<button type="button" class="message-toggle" data-message-id="${escapeHtml(messageId)}">${collapseState.isExpanded ? "收起长输入" : `展开完整输入（${collapseState.fullLength} 字）`}</button>` : ""}
      <div class="tuple-strip">
        <span>Y*</span><span>X</span><span>U</span><span>Y+1</span><span>R+1</span>
      </div>
    `;
    const toggle = card.querySelector(".message-toggle");
    if (toggle) {
      toggle.addEventListener("click", (event) => {
        event.stopPropagation();
        toggleExpandedMessage(messageId);
      });
    }
    card.addEventListener("click", () => renderTuple(message));
    card.addEventListener("keypress", (event) => {
      if (event.key === "Enter") renderTuple(message);
    });
    messagesEl.appendChild(card);
  });
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function getMessageCollapseState(message, messageId) {
  const text = String(message.human_readable_text || "");
  const isOwner = message.sender_id === "owner";
  const isLong = isOwner && text.length > LONG_OWNER_MESSAGE_COLLAPSE_CHARS;
  const isExpanded = state.expandedMessageIds.has(messageId);
  if (!isLong || isExpanded) {
    return { displayText: text, isLong, isExpanded, fullLength: text.length };
  }
  return {
    displayText: `${text.slice(0, LONG_OWNER_MESSAGE_COLLAPSE_CHARS).trim()}\n\n...（你的长输入已折叠，点击下方按钮展开完整内容。）`,
    isLong,
    isExpanded,
    fullLength: text.length,
  };
}

function toggleExpandedMessage(messageId) {
  if (state.expandedMessageIds.has(messageId)) {
    state.expandedMessageIds.delete(messageId);
  } else {
    state.expandedMessageIds.add(messageId);
  }
  renderMessages();
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
  const pendingId = `pending_${Date.now()}`;
  const pendingMessage = buildLocalOwnerMessage(text, pendingId);
  pendingMessage.pending = true;
  state.messages.push(pendingMessage);
  renderMessages();
  renderTuple(pendingMessage);
  setComposerBusy(true, "Aiden is thinking through governed retrieval, brain, and CIEU routing...");
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), MESSENGER_REQUEST_TIMEOUT_MS);
  try {
    const res = await fetch("/api/messages", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, recipient_id: "Aiden" }),
      signal: controller.signal,
    });
    const payload = await res.json().catch(() => ({
      turn_status: "runtime_error",
      error: `HTTP ${res.status} without JSON response`,
    }));
    removeMessage(pendingId);
    const turnMessages = (payload.message_packets || [])
      .map((packet) => packet.message)
      .filter(Boolean);
    if (isRuntimeFailurePayload(payload) && !turnMessages.some((message) => message.sender_id === "owner")) {
      const preserved = buildLocalOwnerMessage(text, `preserved_${Date.now()}`);
      preserved.pending = false;
      preserved.message_kind = "human_to_agent_local_preserved";
      preserved.cieu_five_tuple.X_t.delivery_state = "server_runtime_failed_but_browser_preserved_input";
      turnMessages.unshift(preserved);
    }
    if (turnMessages.length) {
      state.messages.push(...turnMessages);
      renderMessages();
      renderTuple(turnMessages[turnMessages.length - 1]);
      updateEventCount(payload);
      if (payload.turn_status && !["completed", "allow", "ALLOW"].includes(payload.turn_status)) {
        setRuntimeStatus(`Aiden returned ${payload.turn_status}; see the latest notice.`, "warn");
      } else {
        setRuntimeStatus("Aiden replied through the governed local messenger.", "ok");
      }
    } else if (payload.packet?.message) {
      state.messages.push(payload.packet.message);
      renderMessages();
      renderTuple(payload.packet.message);
      updateEventCount(payload);
      setRuntimeStatus("Aiden replied through the governed local messenger.", "ok");
    } else {
      const notice = appendSystemNotice(
        `Aiden Messenger Runtime Notice: the server responded but did not return a displayable message. Status: ${payload.turn_status || payload.error || "unknown"}.`
      );
      renderMessages();
      renderTuple(notice);
      setRuntimeStatus("Aiden returned no message; a governed notice was added.", "warn");
    }
  } catch (error) {
    markPendingMessagePreserved(pendingId);
    const notice = appendSystemNotice(
      error.name === "AbortError"
        ? "Aiden Messenger Runtime Notice: the local runtime did not answer before the browser timeout. The message is visible here, but the backend should be inspected or restarted before retrying."
        : `Aiden Messenger Runtime Notice: the local messenger request failed: ${error.message || error}.`
    );
    renderMessages();
    renderTuple(notice);
    setRuntimeStatus("Aiden runtime request failed visibly; no silent hang.", "error");
  } finally {
    clearTimeout(timeoutId);
    setComposerBusy(false);
  }
});

input.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && (event.metaKey || event.ctrlKey)) {
    event.preventDefault();
    composer.requestSubmit();
  }
});

function buildLocalOwnerMessage(text, messageId) {
  return {
    message_id: messageId,
    sender_id: "owner",
    recipient_ids: ["Aiden"],
    message_kind: "human_to_agent_pending",
    human_readable_text: text,
    cieu_five_tuple: {
      Y_star_t: "Owner message should become governed local communication.",
      X_t: { source: "browser optimistic packet", delivery_state: "pending_server_confirmation" },
      U_t: { speech_act: "owner_message_to_aiden" },
      Y_t_plus_1: "Aiden runtime should return a governed reply or a visible runtime notice.",
      R_t_plus_1: "pending until server responds",
      residual_status: "runtime_residual_pending",
    },
  };
}

function appendSystemNotice(text) {
  const notice = {
    message_id: `browser_notice_${Date.now()}`,
    sender_id: "Aiden",
    recipient_ids: ["owner"],
    message_kind: "governance_notice",
    human_readable_text: text,
    cieu_five_tuple: {
      Y_star_t: "Aiden messenger failures must be visible and recoverable.",
      X_t: { source: "browser runtime watchdog" },
      U_t: { speech_act: "runtime_notice", external_action_executed: false },
      Y_t_plus_1: "Owner sees the correct path instead of a silent UI stall.",
      R_t_plus_1: "runtime visibility residual open",
      residual_status: "runtime_residual_open",
    },
  };
  state.messages.push(notice);
  return notice;
}

function removeMessage(messageId) {
  state.messages = state.messages.filter((message) => message.message_id !== messageId);
}

function markPendingMessagePreserved(messageId) {
  const message = state.messages.find((item) => item.message_id === messageId);
  if (!message) return;
  message.pending = false;
  message.message_kind = "human_to_agent_local_preserved";
  message.cieu_five_tuple.X_t.delivery_state = "browser_request_failed_but_input_preserved";
  message.cieu_five_tuple.R_t_plus_1 = "runtime failure visible; owner input preserved";
}

function isRuntimeFailurePayload(payload) {
  const status = String(payload.turn_status || "");
  return status.startsWith("runtime_") || Boolean(payload.runtime_error);
}

function updateEventCount(payload) {
  eventCountEl.textContent = `${payload.CIEUStore_summary?.event_count || 0} CIEU events`;
}

function setComposerBusy(isBusy, busyText) {
  input.disabled = isBusy;
  sendButton.disabled = isBusy;
  if (isBusy) setRuntimeStatus(busyText, "busy");
}

function setRuntimeStatus(text, kind = "idle") {
  runtimeStatusEl.textContent = text || "Ready";
  runtimeStatusEl.className = `runtime-status ${kind}`;
}

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
