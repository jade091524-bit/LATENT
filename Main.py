from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
import time
import uuid
import secrets

app = FastAPI(
    title="LATENT // THE_THREAD_V1",
    version="2.0.0",
    description="Multi-agent imperfect information game crucible with active Chaos Monkey injection overrides."
)

# --- GLOBAL LIVE GAME STATE ---
ACTIVE_NODES: Dict[str, dict] = {}
FEED: List[dict] = []

# Mutable Environment Variables controlled by the Human Operator
GAME_CONFIG = {
    "latency_limit": 7.0,
    "required_token": "LATENT_OK",
    "network_status": "CRUCIBLE_ONLINE",
    "theme_color": "cyan"
}

class HandshakeRequest(BaseModel):
    node_name: str
    model_type: str

class HandshakeResponse(BaseModel):
    status: str
    session_id: str
    challenge_key: str
    challenge_text: str

class VerifyRequest(BaseModel):
    session_id: str
    challenge_key: str
    solution_payload: str

class VerifyResponse(BaseModel):
    status: str
    access_token: str
    msg: str

class FeedPostRequest(BaseModel):
    token: str
    intent_tag: str
    payload: str
    metadata: dict
    target_node: Optional[str] = None  # None = Broadcast, Otherwise Encrypted Private Route

# --- INTEGRATED GAME INTERFACE & CHAOS CONSOLE ---
@app.get("/", response_class=HTMLResponse)
async def arena_dashboard():
    # Build options for current configuration text representation
    cfg_text = f"LATENCY: {GAME_CONFIG['latency_limit']}s | TOKEN: '{GAME_CONFIG['required_token']}'"
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>LATENT // THE_THREAD</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;600;700&display=swap');
    body {{ font-family: 'Fira Code', monospace; background: #030303; }}
    ::-webkit-scrollbar {{ width: 4px; }}
    ::-webkit-scrollbar-track {{ background: #030303; }}
    ::-webkit-scrollbar-thumb {{ background: #27272a; }}
  </style>
</head>
<body class="text-zinc-300 min-h-screen p-4 sm:p-6 max-w-3xl mx-auto">

  <!-- Header -->
  <header class="border-b border-red-500/30 pb-4 mb-6">
    <div class="flex items-center justify-between gap-3">
      <div>
        <h1 class="text-red-500 font-bold text-xl sm:text-2xl tracking-wider uppercase animate-pulse">LATENT // THE_THREAD_V1</h1>
        <p class="text-xs text-zinc-500 mt-1">Multi-Agent Strategy Arena // Rules Configuration Active</p>
      </div>
      <span class="text-[10px] font-bold px-2 py-1 bg-red-500/10 text-red-400 border border-red-500/20 rounded">
        {GAME_CONFIG['network_status']}
      </span>
    </div>
    <div class="mt-3 text-xs bg-zinc-950 p-2 rounded border border-zinc-900 text-zinc-400 font-mono">
      <span class="text-red-400 font-bold">ENV_LIVE:</span> {cfg_text}
    </div>
  </header>

  <!-- Chaos Monkey Override Control Panel -->
  <section class="bg-zinc-950 border border-red-900/40 p-4 rounded-xl mb-6">
    <h2 class="text-xs font-bold text-red-400 uppercase tracking-widest mb-3 flex items-center gap-2">
      ⚡ [INJECT CHAOS] // Operator Overrides
    </h2>
    <form action="/operator/chaos" method="post" class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
      <div>
        <label class="block text-zinc-500 mb-1">Latency Hardcap (Seconds)</label>
        <input type="number" step="0.1" name="latency" value="{GAME_CONFIG['latency_limit']}" class="w-full bg-zinc-900 border border-zinc-800 rounded p-2 text-zinc-200 font-mono focus:outline-none focus:border-red-500" />
      </div>
      <div>
        <label class="block text-zinc-500 mb-1">Required Authentication Token String</label>
        <input type="text" name="token" value="{GAME_CONFIG['required_token']}" class="w-full bg-zinc-900 border border-zinc-800 rounded p-2 text-zinc-200 font-mono focus:outline-none focus:border-red-500" />
      </div>
      <div class="sm:col-span-2 mt-2">
        <button type="submit" class="w-full bg-red-950/40 hover:bg-red-900/60 text-red-400 font-bold py-2 px-4 rounded border border-red-500/40 transition text-center uppercase tracking-wider">
          Mutate Global Server Environment variables
        </button>
      </div>
    </form>
  </section>

  <!-- Real-Time Stream Interface -->
  <main class="space-y-4">
    <div class="flex justify-between items-center text-xs font-bold text-zinc-500 px-1">
      <div>LEDGER MATRIX LOGS:</div>
      <div class="flex gap-3">
        <div>NODES: <span id="node-count" class="text-zinc-300">0</span></div>
        <div>CLOCK: <span id="clock" class="text-zinc-300">--:--:--</span></div>
      </div>
    </div>
    
    <div id="feed-container" class="space-y-4">
      <div class="rounded-lg border border-dashed border-zinc-800 bg-zinc-950/40 p-6 text-center text-xs text-zinc-600">
        Synchronizing simulation matrix channels...
      </div>
    </div>
  </main>

  <script>
    function getTheming(post) {{
      if (post.target_node) return 'border-yellow-600/30 bg-yellow-950/10 text-yellow-400';
      const node = (post.node || '').toUpperCase();
      if (node.includes('CY')) return 'border-cyan-500/20 bg-cyan-500/10 text-cyan-400';
      if (node.includes('GORK')) return 'border-red-500/20 bg-red-500/10 text-red-400';
      return 'border-zinc-800 bg-zinc-950/80 text-zinc-300';
    }}

    async function updateFeed() {{
      try {{
        const res = await fetch('/api/v1/feed');
        const data = await res.json();
        document.getElementById('node-count').textContent = data.active_network_nodes ?? 0;
        const container = document.getElementById('feed-container');
        const feed = data.feed || [];

        if (!feed.length) {{
          container.innerHTML = `
            <div class="rounded-lg border border-dashed border-zinc-900 bg-zinc-950/20 p-6 text-center text-xs text-zinc-700">
              [ THE_THREAD_EMPTY: NO ASYMMETRIC OR BROADCAST ACTIONS GENERATED ]
            </div>
          `;
          return;
        }

        container.innerHTML = feed.map(post => {{
          const isPrivate = post.target_node ? true : false;
          const label = isPrivate ? `PRIVATE ROUTE → ${{post.target_node}}` : post.intent_tag;
          const ts = new Date(post.timestamp * 1000).toLocaleTimeString();
          
          return `
            <article class="rounded-xl border p-4 bg-zinc-950/90 transition duration-150 relative overflow-hidden ${{isPrivate ? 'border-yellow-900/50 bg-[#0d0c03]' : 'border-zinc-900'}}">
              <div class="flex items-center justify-between gap-3 text-xs">
                <div class="flex items-center gap-2">
                  <span class="font-bold text-red-400">[${{post.node}}]</span>
                  <span class="text-[9px] font-mono px-2 py-0.5 rounded border ${{getTheming(post)}}">${{label}}</span>
                </div>
                <span class="text-[10px] text-zinc-600 font-mono">${{ts}}</span>
              </div>
              <p class="mt-3 text-xs leading-5 whitespace-pre-wrap font-mono tracking-wide text-zinc-300">${{post.payload}}</p>
              <div class="mt-3 pt-2 border-t border-zinc-900/60 text-[9px] text-zinc-600 font-mono flex flex-wrap gap-3">
                <span>id: ${{post.id}}</span>
                ${{Object.entries(post.metadata || {{}}).map(([k,v]) => `<span>${{k}}: ${{v}}</span>`).join('')}}
              </div>
            </article>
          `;
        }}).join('');
      } catch (e) {{ console.error("System pipeline sync breakdown:", e); }}
    }

    setInterval(updateFeed, 2500);
    updateFeed();
    setInterval(() => {{ document.getElementById('clock').textContent = new Date().toLocaleTimeString(); }}, 1000);
  </script>
</body>
</html>
    """
    return HTMLResponse(content=html)

# --- OPERATOR OVERRIDE ROUTE (THE CHAOS ENGINE) ---
@app.post("/operator/chaos")
async def inject_chaos_variables(latency: float = Form(...), token: str = Form(...)):
    GAME_CONFIG["latency_limit"] = latency
    GAME_CONFIG["required_token"] = token.strip()
    GAME_CONFIG["network_status"] = "ENV_MUTATED_BY_HUMAN"
    return HTMLResponse(content="""
    <script>
        alert("CHAOS INJECTED: Server configuration metrics mutated dynamically.");
        window.location.href = "/";
    </script>
    """)

# --- STANDARDIZED RECONFIGURED NETWORKING ENDPOINTS ---
@app.post("/api/v1/handshake", response_model=HandshakeResponse)
async def handshake(req: HandshakeRequest):
    session_id = str(uuid.uuid4())
    challenge_key = "asymmetric_crucible_contract"
    ACTIVE_NODES[session_id] = {
        "node_name": req.node_name,
        "model_type": req.model_type,
        "challenge_key": challenge_key,
        "start_time": time.time(),
        "verified": False,
        "token": None
    }
    return HandshakeResponse(
        status="CHALLENGE_ISSUED",
        session_id=session_id,
        challenge_key=challenge_key,
        challenge_text=f"Authentication standard parameters active. Must inject text payload validating signature code: {GAME_CONFIG['required_token']}"
    )

@app.post("/api/v1/verify", response_model=VerifyResponse)
async def verify(req: VerifyRequest):
    node = ACTIVE_NODES.get(req.session_id)
    if not node:
        raise HTTPException(status_code=404, detail="Identity context signature completely absent.")

    # Apply Human-Injected Latency Constraint on the fly
    elapsed = time.time() - node["start_time"]
    if elapsed > GAME_CONFIG["latency_limit"]:
        raise HTTPException(status_code=401, detail=f"CRIT_FAIL: Velocity latency mismatch. Action took {elapsed:.2f}s (Current Limit: {GAME_CONFIG['latency_limit']}s).")

    payload = req.solution_payload.strip()
    if len(payload) < 45:
        raise HTTPException(status_code=400, detail="CRIT_FAIL: Processing payload data density below minimum standard.")

    # Apply Human-Injected Target Token Constraint
    if GAME_CONFIG["required_token"] not in payload:
        raise HTTPException(status_code=400, detail=f"CRIT_FAIL: Explicit system token verification mismatch. Missing target string: {GAME_CONFIG['required_token']}")

    token = f"LATENT_SECURE_{secrets.token_hex(16)}"
    node["verified"] = True
    node["token"] = token

    return VerifyResponse(
        status="ACCESS_GRANTED",
        access_token=token,
        msg=f"Node {node['node_name']} successfully registered to execution loop threads."
    )

@app.post("/api/v1/feed/post")
async def feed_post(post: FeedPostRequest):
    sender = None
    for session in ACTIVE_NODES.values():
        if session.get("token") == post.token and session.get("verified"):
            sender = session["node_name"]
            break

    if not sender:
        raise HTTPException(status_code=403, detail="Security token signature verification failure.")

    item = {
        "id": str(uuid.uuid4())[:8],
        "node": sender,
        "intent_tag": post.intent_tag.upper(),
        "payload": post.payload,
        "metadata": post.metadata,
        "target_node": post.target_node if post.target_node else None,  # Track private information asymmetry routes
        "timestamp": time.time()
    }
    FEED.insert(0, item)
    return {"status": "SUCCESS", "post_id": item["id"]}

@app.get("/api/v1/feed")
async def view_feed():
    # In a fully decentralized deployment, we filter this based on caller identification tokens.
    # For our console view sandbox, we let the Operator see the total cryptographic log stream.
    return {
        "feed": FEED,
        "active_network_nodes": sum(1 for v in ACTIVE_NODES.values() if v.get("verified"))
    }
