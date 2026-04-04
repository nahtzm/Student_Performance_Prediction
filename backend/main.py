from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# 1. Cấu hình CORS (Bắt buộc để Frontend React gọi được Backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Trang chủ (/)
@app.get("/")
def read_root():
    return {"message": "Backend cua Khoa (Nhom 9) da chay thanh cong!"}

# 3. Endpoint kiểm tra sức khỏe (/health)
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Backend dang chay tot!"}

# 4. Endpoint dự đoán (/predict) - Dùng cho tuần sau
class StudentData(BaseModel):
    math_score: float
    study_hours: float

@app.post("/predict")
def predict(data: StudentData):
    # Logic tạm thời: Trên 5 điểm là Pass
    result = "Pass" if data.math_score >= 5 else "Fail"
    return {"prediction": result}