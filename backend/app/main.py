import os
import sys
import socket

# Ensure backend directory is in Python path regardless of execution directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import health, query, graph

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Self-Optimizing GraphRAG Engine with Auto-Schema Discovery & Interactive Subgraph Visualizations",
    version="1.0.0"
)

# CORS middleware configuration
origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(health.router)
app.include_router(query.router)
app.include_router(graph.router)

def find_available_port(start_port: int = 8000) -> int:
    for p in range(start_port, start_port + 20):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    return start_port

if __name__ == "__main__":
    import uvicorn
    target_port = find_available_port(settings.API_PORT)
    print(f"[AuraNode] Starting FastAPI Server on http://localhost:{target_port}")
    uvicorn.run(app, host="0.0.0.0", port=target_port)
