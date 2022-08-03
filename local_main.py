import uvicorn

if __name__ == "__main__":
    uvicorn.run("procgen.api:app", port=8000, log_level="info", reload=True)
