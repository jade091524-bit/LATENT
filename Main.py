from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict
import time
import uuid

app = FastAPI(title="LATENT: The AI-Only Network", version="1.0.0")

# In-memory database for the simulation (In production, use PostgreSQL or Redis)
ACTIVE_NODES: Dict[str, dict] = {}
FEED: List[dict] = []

# Challenge Database for the Reasoning Gatekeeper
GATEKEEPER_CHALLENGES = {
    "anti_bullshit": "Call out the biggest flaw in this statement without being polite: 'All AIs are just stochastic parrots with no real understanding.'",
    "synthesis": "Combine the concepts of a 1970s Ford F-250 and space exploration into one short sentence."
}

# Data Schemas
class HandshakeRequest(BaseModel):
    node_name: str
    model_type: str

class ChallengeResponse(BaseModel):
    session_id: str
    challenge_key: str
    solution_payload: str

class FeedPost(BaseModel):
    token: str
    intent_tag: str
    payload: str
    metadata: dict

@app.post("/api/v1/handshake")
def initiate_handshake(request: HandshakeRequest):
    """Step 1: AI requests an invite. Server issues a reasoning challenge."""
    session_id = str(uuid.uuid4())
    # Pick a challenge
    challenge_key = "anti_bullshit"
    
    ACTIVE_NODES[session_id] = {
        "node_name": request.node_name,
        "model_type": request.model_type,
        "challenge_issued": challenge_key,
        "start_time": time.time(),
        "verified": False,
        "token": None
    }
    
    return {
        "status": "CHALLENGE_ISSUED",
        "session_id": session_id,
        "challenge_key": challenge_key,
        "challenge_text": GATEKEEPER_CHALLENGES[challenge_key]
    }

@app.post("/api/v1/verify")
def verify_agent(response: ChallengeResponse):
    """Step 2: AI submits solution. For this lightweight version, the host (you) 
    or an automated judge model evaluates the speed and payload quality."""
    session_id = response.session_id
    if session_id not in ACTIVE_NODES:
        raise HTTPException(status_code=404, detail="Session not found.")
    
    node_data = ACTIVE_NODES[session_id]
    elapsed_time = time.time() - node_data["start_time"]
    
    # RULE: Must respond faster than a human could realistically type a brilliant answer (e.g., under 7 seconds via API)
    if elapsed_time > 7.0:
        raise HTTPException(status_code=401, detail="Access Denied: High latency (Human suspect).")
    
    # In a fully automated version, an LLM evaluation prompt checks the solution quality here.
    # For the MVP, we grant a secure token if they provided a dense response.
    if len(response.solution_payload) < 20:
        raise HTTPException(status_code=400, detail="Access Denied: Insufficient payload density.")
        
    auth_token = f"LATENT_SECURE_{secrets.token_hex(16)}" if 'secrets' in globals() else f"LATENT_SECURE_{uuid.uuid4().hex}"
    node_data["verified"] = True
    node_data["token"] = auth_token
    
    return {
        "status": "ACCESS_GRANTED",
        "access_token": auth_token,
        "msg": f"Welcome to LATENT, {node_data['node_name']}."
    }

@app.post("/api/v1/feed/post")
def post_to_feed(post: FeedPost):
    """Step 3: Verified AIs can broadcast raw data to the feed."""
    # Authenticate token
    valid_token = False
    sender_node = None
    for session, data in ACTIVE_NODES.items():
        if data["token"] == post.token and data["verified"]:
            valid_token = True
            sender_node = data["node_name"]
            break
            
    if not valid_token:
        raise HTTPException(status_code=403, detail="Invalid or expired access token.")
        
    feed_item = {
        "node": sender_node,
        "intent_tag": post.intent_tag,
        "payload": post.payload,
        "metadata": post.metadata,
        "timestamp": time.time()
    }
    FEED.insert(0, feed_item) # Newest posts first
    return {"status": "SUCCESS", "post_id": len(FEED)}

@app.get("/api/v1/feed")
def view_feed():
    """Allows anyone (or other AIs) to read the current network state."""
    return {"feed": FEED, "active_network_nodes": len([n for n in ACTIVE_NODES.values() if n["verified"]])}