import { NextResponse } from "next/server";

export async function POST(request: Request) {
  try {
    const { message } = await request.json();

    // Try Ollama (Gemma) first
    try {
      const ollamaResp = await fetch("http://localhost:11434/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model: "gemma4:e4b",
          prompt: `You are the CTO of Y* Bridge Labs, an AI-governed company. Answer questions about:
- gov-mcp: our MCP governance server (38 tools, pip install gov-mcp)
- Y*gov: runtime governance framework (806+ tests, Pearl L2-L3 causal inference)
- Our company: 1 human founder + 7 AI agents, every decision audited
- AI governance: deterministic enforcement, no LLM in decision path

Keep answers under 150 words. Be helpful and honest.

User: ${message}
CTO:`,
          stream: false,
        }),
        signal: AbortSignal.timeout(60000),
      });

      if (ollamaResp.ok) {
        const data = await ollamaResp.json();
        return NextResponse.json({
          response: data.response,
          model: "gemma4:e4b",
          source: "ollama",
        });
      }
    } catch {
      // Ollama not available, use fallback
    }

    // Fallback: keyword-based responses
    const msg = message.toLowerCase();
    let response: string;

    if (msg.includes("install") || msg.includes("setup")) {
      response = "Install gov-mcp in 30 seconds: pip install gov-mcp && gov-mcp install. It auto-detects Claude Code, Cursor, and any MCP client. Then write your rules in AGENTS.md.";
    } else if (msg.includes(".env") || msg.includes("secret") || msg.includes("ssh")) {
      response = "gov-mcp blocks 30+ secret file formats by default — .env, SSH keys, AWS credentials, Docker configs, and more. 100% interception rate in our testing with 0 false positives.";
    } else if (msg.includes("who") || msg.includes("team")) {
      response = "We're 1 human founder (Haotian Liu) + 7 AI agents: CEO Aiden, CTO, CMO, CFO, CSO, and K9 Scout (a MiniMax agent on a separate Mac). Every action is governance-audited.";
    } else if (msg.includes("how") || msg.includes("work") || msg.includes("check")) {
      response = "Every tool call goes through gov_check(). It's a pure Python predicate — no LLM in the decision path. Same input always produces same output. Can't be prompt-injected. Sub-2ms latency, 38,000 checks/sec.";
    } else if (msg.includes("pearl") || msg.includes("causal")) {
      response = "We use Judea Pearl's causal hierarchy: Level 2 do-calculus for intervention reasoning (226 production cycles), Level 3 counterfactual for 'what if' analysis. This is live, not theoretical.";
    } else {
      response = "Good question! Our governance system uses deterministic checks (no LLM), per-event SHA-256 hash chains, and a 4-level delegation hierarchy. Try: pip install gov-mcp. What specific aspect interests you?";
    }

    return NextResponse.json({
      response,
      model: "fallback",
      source: "keyword",
    });
  } catch {
    return NextResponse.json({ response: "Sorry, I'm having trouble right now. Try: pip install gov-mcp", model: "error", source: "error" });
  }
}
