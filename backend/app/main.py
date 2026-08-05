import os
import sys

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

if __name__ == "__main__":
    import uvicorn
    try:
        uvicorn.run(app, host="0.0.0.0", port=settings.API_PORT)
    except OSError as e:
        if "10048" in str(e) or "address" in str(e).lower():
            print(f"[AuraNode] Port {settings.API_PORT} is in use. Trying port 8001...")
            uvicorn.run(app, host="0.0.0.0", port=8001)
        else:
            raise e
