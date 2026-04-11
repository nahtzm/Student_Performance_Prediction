from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import joblib
import pandas as pd
import os
from datetime import datetime

# 1. Khởi tạo ứng dụng
app = FastAPI(
    title="Academic Performance Prediction System",
    description="Hệ thống tích hợp AI dự đoán kết quả học tập - Nhóm 9",
    version="2.0.0"
)

# 2. Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Cấu hình Cơ sở dữ liệu (SQLite)
DB_PATH = "predictions.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prediction_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            study_hours FLOAT,
            previous_score FLOAT,
            attendance FLOAT,
            prediction_text TEXT,
            predicted_score FLOAT,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# 4. Cấu hình Model AI (Dành cho Tuần 3)
MODEL_PATH = "models/pipeline.pkl"

def load_ai_model():
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    return None

# 5. Schema dữ liệu
class StudentInput(BaseModel):
    study_hours: float
    previous_score: float
    attendance: float

# 6. Các Endpoints

@app.get("/")
def health_check():
    model_status = "Ready" if os.path.exists(MODEL_PATH) else "Using Logic (Waiting for pkl file)"
    return {
        "status": "Online",
        "model_status": model_status,
        "database": "Connected"
    }

@app.post("/predict")
async def predict(data: StudentInput):
    ai_model = load_ai_model()
    
    # --- XỬ LÝ DỰ ĐOÁN ---
    if ai_model:
        # Nếu đã có file của Dũng: Chuyển dữ liệu sang DataFrame để Predict
        try:
            df = pd.DataFrame([data.dict()])
            # Giả sử model trả về xác suất hoặc điểm số
            prediction_result = ai_model.predict(df)[0]
            # Tùy vào model của Dũng trả về 0/1 hay điểm số mà bạn điều chỉnh dòng dưới
            final_score = float(prediction_result) 
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Lỗi khi chạy Model AI: {str(e)}")
    else:
        # Nếu chưa có file: Dùng logic tạm thời (giữ nguyên để bạn demo trước)
        final_score = (data.previous_score * 0.7) + (data.study_hours * 0.05) + (data.attendance * 0.02)
        final_score = min(round(final_score, 2), 10.0)

    # Quyết định kết quả chữ
    result_text = "PASS" if final_score >= 5.0 and data.attendance >= 75 else "FAIL"
    advice = "Duy trì phong độ!" if result_text == "PASS" else "Cần cải thiện thời gian học và chuyên cần."

    # --- LƯU VÀO DATABASE ---
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO prediction_history (study_hours, previous_score, attendance, prediction_text, predicted_score, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (data.study_hours, data.previous_score, data.attendance, result_text, final_score, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Lỗi lưu DB: {e}")

    return {
        "prediction": result_text,
        "score": final_score,
        "advice": advice,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/history")
def get_history():
    """Lấy 10 bản ghi gần nhất để hiện lên bảng ở FE"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM prediction_history ORDER BY id DESC LIMIT 10")
        rows = cursor.fetchall()
        conn.close()
        
        history = []
        for r in rows:
            history.append({
                "id": r[0], "study_hours": r[1], "previous_score": r[2], 
                "attendance": r[3], "result": r[4], "score": r[5], "date": r[6]
            })
        return history
    except Exception as e:
        return {"error": str(e)}