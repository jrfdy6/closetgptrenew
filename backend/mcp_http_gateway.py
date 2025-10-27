# mcp_http_gateway.py
import os
import httpx
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

MAIN_BACKEND_URL = "https://closetgptrenew-production.up.railway.app"
API_KEY = os.environ.get("API_KEY", "")

app = FastAPI(title="ClosetGPT ChatGPT App Gateway")

# Allow ChatGPT Apps requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For MVP, allow all origins
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/auth")
async def auth():
    """
    Placeholder OAuth endpoint for ChatGPT Apps SDK.
    For MVP, redirect or token exchange logic can be added later.
    """
    return {"message": "OAuth endpoint ready"}

@app.get("/test-proxy")
async def test_proxy():
    """
    Test endpoint to verify gateway can reach main backend
    """
    async with httpx.AsyncClient() as client:
        try:
            # Test connection to main backend
            r = await client.get(f"{MAIN_BACKEND_URL}/health")
            return {
                "gateway_status": "ok",
                "backend_url": MAIN_BACKEND_URL,
                "backend_reachable": True,
                "backend_status": r.status_code,
                "backend_response": r.json() if r.status_code == 200 else None
            }
        except httpx.RequestError as e:
            return {
                "gateway_status": "ok",
                "backend_url": MAIN_BACKEND_URL,
                "backend_reachable": False,
                "error": str(e)
            }

@app.get("/wardrobe")
async def get_wardrobe(request: Request):
    """
    Forward GET /wardrobe requests to main backend
    """
    headers = {"Authorization": f"Bearer {API_KEY}"}
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(f"{MAIN_BACKEND_URL}/wardrobe", headers=headers)
            return JSONResponse(content=r.json(), status_code=r.status_code)
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/suggest-outfits")
async def suggest_outfits(request: Request):
    """
    Forward POST /suggest-outfits requests to main backend
    """
    payload = await request.json()
    headers = {"Authorization": f"Bearer {API_KEY}"}
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(f"{MAIN_BACKEND_URL}/suggest-outfits", json=payload, headers=headers)
            return JSONResponse(content=r.json(), status_code=r.status_code)
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=str(e))

# Optional: add more endpoints later (add item, mark worn, etc.)

