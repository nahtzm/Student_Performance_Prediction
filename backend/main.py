from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import joblib
import pandas as pd
import os
from datetime import datetime

# 1. Khởi tạo ứng dụng FastAPI
app = FastAPI(
    title="Academic Performance Prediction System",
    description="Hệ thống tích hợp AI dự đoán kết quả học tập - Nhóm 9",
    version="2.0.0"
)

# 2. Cấu hình CORS (Cho phép ReactJS gọi API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Cấu hình Cơ sở dữ liệu SQLite
DB_PATH = "predictions.db"

def init_db():
    """Khởi tạo cấu trúc bảng nếu chưa tồn tại"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prediction_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            study_hours FLOAT,
            previous_score FLOAT,
            attendance FLOAT,
            failures INTEGER,
            goout INTEGER,
            prediction_text TEXT,
            predicted_score FLOAT,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Gọi hàm khởi tạo DB khi ứng dụng startup
init_db()

# 4. Cấu hình Model AI
MODEL_PATH = "notebooks/models/best_model.pkl"
def load_ai_model():
    """Tải model từ file .pkl"""
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    return None

# 5. Schema dữ liệu (Sử dụng Pydantic để validate dữ liệu từ Frontend)
class StudentInput(BaseModel):
    study_hours: float   # studytime (1-4)
    previous_score: float # G2 (0-20)
    attendance: float    # absences (0-93)
    failures: int        # failures (0-3)
    goout: int           # goout (1-5)

# 6. Các Endpoints API

@app.get("/")
def health_check():
    """Kiểm tra trạng thái hệ thống"""
    model_exists = os.path.exists(MODEL_PATH)
    return {
        "status": "Online",
        "model_status": "Ready" if model_exists else "Model file not found",
        "database": "Connected",
        "group": "Group 9"
    }

@app.post("/predict")
async def predict(data: StudentInput):
    """Tiếp nhận dữ liệu, dự đoán và lưu vào database"""
    ai_model = load_ai_model()
    
    if not ai_model:
        raise HTTPException(
            status_code=500, 
            detail="Chưa tìm thấy file model .pkl trong thư mục models/. Vui lòng kiểm tra lại."
        )

    try:
        # TẠO DATAFRAME KHỚP VỚI CẤU TRÚC 30+ CỘT CỦA DATASET GỐC
        # Các cột không có từ FE sẽ được điền giá trị trung bình/mặc định
        input_dict = {
            "school": ["GP"], "sex": ["F"], "age": [17], "address": ["U"],
            "famsize": ["GT3"], "Pstatus": ["T"], "Medu": [2], "Fedu": [2],
            "Mjob": ["other"], "Fjob": ["other"], "reason": ["home"],
            "guardian": ["mother"], "traveltime": [1], 
            "studytime": [data.study_hours],
            "failures": [data.failures],
            "schoolsup": ["no"], "famsup": ["no"], "paid": ["no"], 
            "activities": ["no"], "nursery": ["yes"], "higher": ["yes"], 
            "internet": ["yes"], "romantic": ["no"], "famrel": [4], 
            "freetime": [3], 
            "goout": [data.goout],
            "Dalc": [1], "Walc": [1], "health": [3], 
            "absences": [int(data.attendance)],
            "G1": [data.previous_score],
            "G2": [data.previous_score]
        }
        
        # Feature Engineering (Nếu model của bạn được huấn luyện có các cột này)
        input_dict["study_per_absence"] = [data.study_hours / (data.attendance + 1)]
        input_dict["failure_impact"] = [data.failures * data.attendance]
        
        df = pd.DataFrame(input_dict)
        
        # Thực hiện dự đoán
        prediction_result = ai_model.predict(df)[0]
        
        # Xử lý hậu dự đoán
        final_score = round(float(prediction_result), 2)
        final_score = max(0, min(20, final_score)) # Giới hạn trong thang điểm 20

        # Phân loại kết quả
        result_text = "PASS" if final_score >= 10 else "FAIL"
        
        # Đưa ra lời khuyên dựa trên điểm số
        if final_score >= 16:
            advice = "Kết quả xuất sắc! Hãy tiếp tục duy trì phong độ này."
        elif final_score >= 10:
            advice = "Bạn đã vượt qua! Hãy cố gắng cải thiện điểm số ở các kỳ tới."
        else:
            advice = "Cảnh báo: Bạn có nguy cơ không đạt. Hãy tập trung học tập và giảm bớt thời gian đi chơi."

        # LƯU VÀO DATABASE
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO prediction_history 
            (study_hours, previous_score, attendance, failures, goout, prediction_text, predicted_score, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (data.study_hours, data.previous_score, data.attendance, data.failures, data.goout, 
              result_text, final_score, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()

        return {
            "prediction": result_text,
            "score": final_score,
            "advice": advice,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý Model AI: {str(e)}")

@app.get("/history")
def get_history():
    """Lấy danh sách 10 lần dự đoán gần nhất để hiển thị lên bảng"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM prediction_history ORDER BY id DESC LIMIT 10")
        rows = cursor.fetchall()
        conn.close()
        
        history_list = []
        for r in rows:
            history_list.append({
                "id": r[0],
                "study_hours": r[1],
                "previous_score": r[2],
                "attendance": r[3],
                "failures": r[4],
                "goout": r[5],
                "result": r[6],
                "score": r[7],
                "date": r[8]
            })
        return history_list
    except Exception as e:
        return {"error": f"Lỗi truy vấn lịch sử: {str(e)}"}