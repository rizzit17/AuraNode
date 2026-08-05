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
    uvicorn.run("main:app", host="0.0.0.0", port=settings.API_PORT, reload=True)
