from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import llm_router

app = FastAPI()

# For testing, allow all origins
origins = ["*"] 

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True, 
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(llm_router.router)

@app.get("/")
def read_root():
    version = "0.1.1"
    message = "Welcome to API "+ "v" + version
    return {"message": message}
