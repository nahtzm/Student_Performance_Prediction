from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Backend cua Khoa da chay thanh cong!"}

@app.get("/health")
def health_check():
    return {"status": "ok"}