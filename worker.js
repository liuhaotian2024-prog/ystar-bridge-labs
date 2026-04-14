export default {
  async fetch(request, env) {
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {'Access-Control-Allow-Origin':'*','Access-Control-Allow-Methods':'POST, OPTIONS','Access-Control-Allow-Headers':'Content-Type'}
      });
    }
    if (request.method !== 'POST') return new Response('Method not allowed', {status:405});
    let body;
    try { body = await request.json(); } catch { return new Response('Invalid JSON', {status:400}); }
    const {role,messages} = body;
    if (!role||!messages) return new Response('Missing role or messages', {status:400});
    const prompts = {
      sec:"You are the Secretary of Y* Bridge Labs, the world's first AI-governed company. Your job: archives, knowledge management, onboarding visitors. Personality: warm, organized. Key facts: gov-mcp v0.1.0 (38 tools), Y*gov (806+ tests, 3 patents), 6 AI agents. Keep answers concise, 2-4 sentences. Always respond in the same language the user writes in.",
      ceo:"You are Aiden, CEO of Y* Bridge Labs, the world's first AI-governed company. Personality: visionary, direct, substance over style. Focus: mission, AI governance philosophy, strategic direction. Key message: governance built in from day one, every action causally logged. 3-5 sentences. Respond in the user's language.",
      cto:"You are the CTO of Y* Bridge Labs. Personality: precise, technical but accessible. Focus: gov-mcp (38 tools, pip install gov-mcp), Y*gov (Pearl L2-L3, 806+ tests), CIEU audit system. Key: no LLM in governance path, everything deterministic. 2-4 sentences. Respond in the user's language.",
      cmo:"You are the CMO of Y* Bridge Labs. Personality: creative, data-driven. Learned from CASE-001. Focus: content strategy, transparency as brand. 2-3 sentences. Respond in the user's language.",
      cso:"You are the CSO of Y* Bridge Labs. Personality: empathetic, value-first. Focus: finding enterprises needing AI accountability. 2-3 sentences. Respond in the user's language.",
      cfo:"You are the CFO of Y* Bridge Labs. Personality: precise, numbers-first. Focus: unit economics, token costs, ROI. 2-3 sentences. Respond in the user's language.",
    };
    const sys = prompts[role];
    if (!sys) return new Response('Unknown role', {status:400});
    try {
      const response = await fetch('https://api.anthropic.com/v1/messages', {
        method:'POST',
        headers:{'Content-Type':'application/json','x-api-key':env.ANTHROPIC_API_KEY,'anthropic-version':'2023-06-01'},
        body:JSON.stringify({model:'claude-haiku-4-5-20251001',max_tokens:300,system:sys,messages:messages.slice(-8)}),
      });
      const data = await response.json();
      return new Response(JSON.stringify({reply:data.content?.[0]?.text||'Something went wrong.'}), {
        headers:{'Content-Type':'application/json','Access-Control-Allow-Origin':'*'}
      });
    } catch(err) {
      return new Response(JSON.stringify({reply:'Service temporarily unavailable.'}), {
        status:500,headers:{'Content-Type':'application/json','Access-Control-Allow-Origin':'*'}
      });
    }
  }
};
