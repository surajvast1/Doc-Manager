from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.routes import upload_delete
from app.routes import process_routes
from app.routes import response




app = FastAPI()

@app.get("/", response_class=RedirectResponse, include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

# Include routers with prefix
app.include_router(upload_delete.router, tags=["Upload and delete"])
app.include_router(process_routes.router,tags=["Process"])
app.include_router(response.router,tags=["Response"])



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 