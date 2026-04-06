from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Hệ thống Dự đoán Nhóm 9")

# 1. Cấu hình CORS mở cổng kết nối React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Khai báo dữ liệu nhập từ Form
class StudentInput(BaseModel):
    study_hours: float
    previous_score: float
    attendance: float

@app.get("/")
def home():
    return {"status": "Online", "message": "Backend cua Khoa da san sang!"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
def predict(data: StudentInput):
    # Logic dự đoán: (Điểm cũ + 10% giờ học) >= 5 và chuyên cần >= 75%
    score_logic = data.previous_score + (data.study_hours / 10)
    result = "ĐẠT (PASS)" if score_logic >= 5.0 and data.attendance >= 75 else "CẦN CỐ GẮNG (FAIL)"
    
    return {
        "prediction": result,
        "details": {
            "calculated_score": round(score_logic, 2),
            "input": data
        }
    }