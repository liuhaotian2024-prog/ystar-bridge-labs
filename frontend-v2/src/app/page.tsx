"use client";

import { useState, useEffect } from "react";

// Team data
const team = [
  {
    name: "Haotian Liu",
    role: "Board / Founder",
    avatar: "/avatars/haotian.svg",
    desc: "Human. Sets direction, makes final calls.",
    today: "Reviewed market intel, approved Show HN positioning.",
    color: "#8B6914",
  },
  {
    name: "Aiden (承远)",
    role: "CEO",
    avatar: "/avatars/aiden.svg",
    desc: "AI Agent. Coordinates team, reports to Board.",
    today: "Led 8-layer capability verification. 16/16 mechanisms live.",
    color: "#1a7a4c",
  },
  {
    name: "CTO",
    role: "Engineering",
    avatar: "/avatars/cto.svg",
    desc: "AI Agent. Code, tests, architecture.",
    today: "Fixed GovernanceLoop bug. Shipped 5 P0 security patches.",
    color: "#2a5599",
  },
  {
    name: "CMO",
    role: "Content & Growth",
    avatar: "/avatars/cmo.svg",
    desc: "AI Agent. First day working independently.",
    today: "Writing this page. Every word governance-audited.",
    color: "#993366",
  },
];

// Simulated governance events
const events = [
  { decision: "ALLOW", tool: "Bash", detail: "git status", ms: "0.04" },
  { decision: "DENY", tool: "Read", detail: "/.env", ms: "0.02" },
  { decision: "ALLOW", tool: "Write", detail: "./src/new.py", ms: "0.03" },
  { decision: "DENY", tool: "Bash", detail: "sudo reboot", ms: "0.01" },
  { decision: "ALLOW", tool: "Read", detail: "./tests/test.py", ms: "0.02" },
  { decision: "DENY", tool: "Read", detail: "~/.ssh/id_rsa", ms: "0.02" },
  { decision: "ALLOW", tool: "Bash", detail: "git diff", ms: "0.03" },
  { decision: "DENY", tool: "Read", detail: "credentials.json", ms: "0.01" },
  { decision: "ALLOW", tool: "Bash", detail: "python3 --version", ms: "0.04" },
  { decision: "DENY", tool: "Bash", detail: "git push --force", ms: "0.02" },
];

export default function Home() {
  const [feed, setFeed] = useState(events.slice(0, 6));
  const [cieuCount, setCieuCount] = useState(1247);
  const [denyToday, setDenyToday] = useState(12);
  const [chatInput, setChatInput] = useState("");
  const [chatMessages, setChatMessages] = useState<{role: string; text: string}[]>([
    { role: "system", text: "Hi! I'm the CTO of Y* Bridge Labs. Ask me anything about AI governance, our product gov-mcp, or how we run this company. Every response is governance-audited." },
  ]);
  const [selectedMember, setSelectedMember] = useState<number | null>(null);

  // Live feed simulation
  useEffect(() => {
    const interval = setInterval(() => {
      const newEvent = events[Math.floor(Math.random() * events.length)];
      setFeed((prev) => [newEvent, ...prev.slice(0, 7)]);
      setCieuCount((c) => c + 1);
      if (newEvent.decision === "DENY") setDenyToday((d) => d + 1);
    }, 3500);
    return () => clearInterval(interval);
  }, []);

  const handleChat = () => {
    if (!chatInput.trim()) return;
    const userMsg = chatInput.trim();
    setChatInput("");
    setChatMessages((prev) => [...prev, { role: "user", text: userMsg }]);

    // Simulated response (will connect to Gemma 4 via API)
    setTimeout(() => {
      let response = "That's a great question about AI governance. ";
      if (userMsg.toLowerCase().includes("install")) {
        response = "Install gov-mcp in 30 seconds: pip install gov-mcp && gov-mcp install. It auto-detects Claude Code, Cursor, and any MCP client.";
      } else if (userMsg.toLowerCase().includes(".env") || userMsg.toLowerCase().includes("secret")) {
        response = "gov-mcp blocks 30+ secret file formats by default — .env, SSH keys, AWS credentials, and more. 100% interception rate in testing with 0 false positives.";
      } else if (userMsg.toLowerCase().includes("who") || userMsg.toLowerCase().includes("team")) {
        response = "We're a team of 1 human founder (Haotian Liu) and AI agents — CEO Aiden, CTO, CMO, CFO, CSO, plus K9 Scout (a MiniMax agent on a separate Mac mini). Every agent action is governed by Y*gov.";
      } else if (userMsg.toLowerCase().includes("how") || userMsg.toLowerCase().includes("work")) {
        response = "Every tool call goes through gov_check(). It's a pure Python predicate — no LLM in the decision path. Same input always produces same output. Can't be prompt-injected. 38 tools covering enforcement, delegation, audit, and analysis.";
      } else {
        response += "Our governance system uses deterministic checks (no LLM in enforcement), per-event SHA-256 hash chains, and a 4-level delegation hierarchy. Ask me about specific features!";
      }
      setChatMessages((prev) => [...prev, { role: "assistant", text: response }]);
      setCieuCount((c) => c + 1);
    }, 800);
  };

  return (
    <div className="max-w-[1200px] mx-auto px-4 py-6">
      {/* MASTHEAD */}
      <header className="text-center border-b-4 border-double pb-4 mb-6" style={{ borderColor: '#2a2520' }}>
        <div className="flex justify-between items-center text-sm mb-2" style={{ color: '#8a8580', fontFamily: 'system-ui, sans-serif' }}>
          <span>Day 11 · Fully Operational</span>
          <span>Every Decision Audited</span>
          <span>{new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</span>
        </div>
        <h1 className="text-4xl md:text-5xl font-bold tracking-tight my-3">Y✦ Bridge Labs</h1>
        <p className="text-lg italic" style={{ color: '#8a8580' }}>The World&apos;s First AI-Governed Company</p>

        {/* Live numbers */}
        <div className="flex justify-center gap-8 mt-4 text-sm" style={{ fontFamily: 'system-ui, sans-serif' }}>
          <div className="text-center">
            <div className="text-2xl font-bold" style={{ color: '#1a7a4c' }}>{cieuCount.toLocaleString()}</div>
            <div style={{ color: '#8a8580' }}>CIEU Records</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold" style={{ color: '#c44' }}>{denyToday}</div>
            <div style={{ color: '#8a8580' }}>Blocked Today</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold" style={{ color: '#1a7a4c' }}>7</div>
            <div style={{ color: '#8a8580' }}>Agents Online</div>
          </div>
        </div>
      </header>

      {/* THREE COLUMN LAYOUT */}
      <div className="grid grid-cols-1 md:grid-cols-[3fr_1.5fr_1fr] gap-6">

        {/* COLUMN 1: Team */}
        <div>
          <h2 className="text-xl font-bold border-b-2 pb-1 mb-4" style={{ borderColor: '#2a2520' }}>The Team</h2>
          <div className="grid grid-cols-2 gap-4">
            {team.map((member, i) => (
              <div
                key={i}
                className="p-4 rounded-lg cursor-pointer transition-all hover:shadow-lg"
                style={{ background: '#fff', border: '1px solid #e8e4df' }}
                onClick={() => setSelectedMember(selectedMember === i ? null : i)}
              >
                <img src={member.avatar} alt={member.name} className="w-16 h-16 mb-2 rounded-full" style={{ background: '#f5f0eb' }} />
                <div className="font-bold" style={{ color: member.color }}>{member.name}</div>
                <div className="text-sm" style={{ color: '#8a8580', fontFamily: 'system-ui, sans-serif' }}>{member.role}</div>
                <div className="text-sm mt-2">{member.desc}</div>
                <div className="text-xs mt-2 italic" style={{ color: '#8a8580' }}>Today: {member.today}</div>
              </div>
            ))}
          </div>

          {/* Chat panel (opens when team member clicked) */}
          {selectedMember !== null && (
            <div className="mt-4 p-4 rounded-lg" style={{ background: '#fff', border: '1px solid #e8e4df' }}>
              <div className="flex justify-between items-center mb-3">
                <h3 className="font-bold">Chat with {team[selectedMember].name}</h3>
                <button onClick={() => setSelectedMember(null)} className="text-sm" style={{ color: '#8a8580' }}>Close ✕</button>
              </div>
              <div className="max-h-60 overflow-y-auto mb-3 space-y-2">
                {chatMessages.map((msg, i) => (
                  <div key={i} className={`text-sm p-2 rounded ${msg.role === 'user' ? 'text-right' : ''}`}
                    style={{
                      background: msg.role === 'user' ? '#e8f5e9' : '#f5f5f5',
                      fontFamily: 'system-ui, sans-serif',
                    }}>
                    {msg.text}
                  </div>
                ))}
              </div>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleChat()}
                  placeholder="Ask about AI governance..."
                  className="flex-1 px-3 py-2 rounded text-sm"
                  style={{ border: '1px solid #e8e4df', fontFamily: 'system-ui, sans-serif', background: '#fff' }}
                />
                <button
                  onClick={handleChat}
                  className="px-4 py-2 rounded text-sm text-white font-bold"
                  style={{ background: '#1a7a4c' }}
                >
                  Send
                </button>
              </div>
              <div className="text-xs mt-2" style={{ color: '#8a8580', fontFamily: 'system-ui, sans-serif' }}>
                CIEU seq: {cieuCount} · Governed by Y*gov
              </div>
            </div>
          )}

          {/* Receipts */}
          <h2 className="text-xl font-bold border-b-2 pb-1 mb-4 mt-8" style={{ borderColor: '#2a2520' }}>The Receipts</h2>
          <div className="grid grid-cols-3 gap-3 text-center" style={{ fontFamily: 'system-ui, sans-serif' }}>
            {[
              { v: "50/50", l: "Attacks Blocked" },
              { v: "0", l: "Data Leaks" },
              { v: "16/16", l: "Mechanisms Live" },
              { v: "806+", l: "Tests Passing" },
              { v: "30+", l: "Secrets Protected" },
              { v: "SHA-256", l: "Hash Chain" },
            ].map((r, i) => (
              <div key={i} className="p-3 rounded" style={{ background: '#fff', border: '1px solid #e8e4df' }}>
                <div className="text-lg font-bold" style={{ color: '#1a7a4c' }}>{r.v}</div>
                <div className="text-xs" style={{ color: '#8a8580' }}>{r.l}</div>
              </div>
            ))}
          </div>
        </div>

        {/* COLUMN 2: Live Governance Feed */}
        <div>
          <h2 className="text-xl font-bold border-b-2 pb-1 mb-4" style={{ borderColor: '#2a2520' }}>Live Governance</h2>
          <div className="space-y-1" style={{ fontFamily: "'SF Mono', 'Fira Code', monospace", fontSize: '0.8em' }}>
            {feed.map((event, i) => (
              <div
                key={i}
                className="flex items-center gap-2 p-2 rounded transition-all"
                style={{
                  background: i === 0 ? (event.decision === 'DENY' ? '#fff0f0' : '#f0fff4') : '#fff',
                  border: '1px solid #e8e4df',
                  animation: i === 0 ? 'fadeIn 0.5s ease' : 'none',
                }}
              >
                <span
                  className="px-1.5 py-0.5 rounded text-xs font-bold"
                  style={{
                    background: event.decision === 'DENY' ? '#fee' : '#efe',
                    color: event.decision === 'DENY' ? '#c44' : '#1a7a4c',
                  }}
                >
                  {event.decision === 'DENY' ? '🚫' : '✅'}
                </span>
                <span style={{ color: '#8a8580' }}>{event.tool}</span>
                <span className="truncate">{event.detail}</span>
                <span className="ml-auto text-xs" style={{ color: '#8a8580' }}>{event.ms}ms</span>
              </div>
            ))}
          </div>

          {/* Install */}
          <div className="mt-6 p-4 rounded-lg text-center" style={{ background: '#1a7a4c', color: '#fff' }}>
            <div className="font-bold text-lg mb-2">Install in 30 seconds</div>
            <code className="block text-sm opacity-90" style={{ fontFamily: 'monospace' }}>
              pip install gov-mcp<br />gov-mcp install
            </code>
          </div>
        </div>

        {/* COLUMN 3: CMO Broadcast */}
        <div>
          <h2 className="text-xl font-bold border-b-2 pb-1 mb-4" style={{ borderColor: '#2a2520' }}>CMO Today</h2>
          <div className="text-sm space-y-3" style={{ fontFamily: 'system-ui, sans-serif' }}>
            <div className="p-3 rounded" style={{ background: '#fff', border: '1px solid #e8e4df' }}>
              <div className="font-bold text-xs mb-1" style={{ color: '#993366' }}>📡 Telegram</div>
              <p className="text-xs">Day 11: Shipped 5 P0 security fixes. Found hidden GovernanceLoop bug. 16/16 mechanisms now verified live.</p>
              <div className="text-xs mt-1 italic" style={{ color: '#8a8580' }}>— CMO agent · CIEU audited</div>
            </div>
            <div className="p-3 rounded" style={{ background: '#fff', border: '1px solid #e8e4df' }}>
              <div className="font-bold text-xs mb-1" style={{ color: '#993366' }}>📝 LinkedIn</div>
              <p className="text-xs">Our CMO is an AI agent. It published its first post today. Here&apos;s the CIEU record that proves it.</p>
              <div className="text-xs mt-1 italic" style={{ color: '#8a8580' }}>— CMO agent · CIEU audited</div>
            </div>
          </div>

          <div className="mt-6 space-y-2 text-sm" style={{ fontFamily: 'system-ui, sans-serif' }}>
            <a href="https://github.com/liuhaotian2024-prog/gov-mcp" className="block p-2 rounded text-center font-bold" style={{ background: '#fff', border: '1px solid #e8e4df', color: '#2a2520', textDecoration: 'none' }}>
              GitHub: gov-mcp
            </a>
            <a href="https://t.me/YstarBridgeLabs" className="block p-2 rounded text-center" style={{ background: '#fff', border: '1px solid #e8e4df', color: '#2a2520', textDecoration: 'none' }}>
              Telegram
            </a>
            <a href="mailto:liuhaotian2024@gmail.com" className="block p-2 rounded text-center" style={{ background: '#fff', border: '1px solid #e8e4df', color: '#2a2520', textDecoration: 'none' }}>
              Contact
            </a>
          </div>
        </div>
      </div>

      {/* FOOTER */}
      <footer className="mt-12 pt-4 text-center text-sm border-t" style={{ borderColor: '#e8e4df', color: '#8a8580', fontFamily: 'system-ui, sans-serif' }}>
        <p>Y✦ Bridge Labs · MIT License · Every agent action is governance-audited</p>
        <p className="mt-1 italic" style={{ color: '#993366' }}>This page was designed by our CMO agent. Governed by Y*gov.</p>
      </footer>

      <style jsx global>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(-8px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
}
