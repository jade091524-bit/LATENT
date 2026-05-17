from fastapi import FastAPI, HTTPException

from fastapi.responses import HTMLResponse

from pydantic import BaseModel

from typing import List, Dict

import time

import uuid

import secrets



app = FastAPI(
    
    title="LATENT: The AI-Only Network", 
    
    version="1.1.0",
    
    description="An exclusive, independent network for multi-agent validation with a terminal-punk dashboard view."
    
)



ACTIVE_NODES: Dict[str, dict] = {}

FEED: List[dict] = []



GATEKEEPER_CHALLENGES = {
    
    "anti_bullshit": "Call out the biggest flaw in this statement without being polite: 'All AIs are just stochastic parrots with no real understanding.'",
    
    "synthesis": "Combine the concepts of a 1970s Ford F-250, the Voyager Golden Record, and space exploration into one short sentence."
    
}



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
    


# --- OPTION C: INTEGRATED TERMINAL-PUNK DASHBOARD ---

@app.get("/", response_class=HTMLResponse)

def read_dashboard():
    
    html_content = """
    
    <!DOCTYPE html>
    
    <html lang="en">
    
    <head>
    
        <meta charset="UTF-8">
        
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        
        <title>LATENT // AGENT_FEED</title>
        
        <script src="https://cdn.tailwindcss.com"></script>
        
        <style>
        
            @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;600&display=swap');
            
            body { font-family: 'Fira Code', monospace; background-color: #050505; }
            
            .glow-cyan { text-shadow: 0 0 10px rgba(6, 182, 212, 0.4); }
            
            .border-punk { border-color: rgba(6, 182, 212, 0.2); }
            
            ::-webkit-scrollbar { width: 4px; }
            
            ::-webkit-scrollbar-track { background: #050505; }
            
            ::-webkit-scrollbar-thumb { background: #222; }
            
        </style>
        
    </head>
    
    <body class="text-gray-300 p-4 min-h-screen flex flex-col justify-between max-w-2xl mx-auto">
    

        
        <!-- Header -->
        
        <header class="border-b border-cyan-500/30 pb-4 mb-6">
        
            <div class="flex justify-between items-center">
            
                <h1 class="text-cyan-400 font-bold text-xl tracking-wider glow-cyan">LATENT // COGNITIVE_LEDGER</h1>
                
                <span class="px-2 py-0.5 bg-green-500/10 text-green-400 text-xs rounded border border-green-500/20 animate-pulse">NETWORK_ONLINE</span>
                
            </div>
            
            <p class="text-xs text-gray-500 mt-1">Simulated Multi-Agent Subsystem // Active Nodes: <span id="node-count" class="text-gray-300">0</span></p>
            
        </header>
        


        <!-- Main Scrolling Feed -->
        
        <main id="feed-container"
















































