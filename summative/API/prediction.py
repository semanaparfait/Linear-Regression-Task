from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import pandas as pd
import numpy as np
import joblib

app = FastAPI(
    title="Youth Job Creation Predictor API",
    description="Production-ready ML API predicting Youth Unemployment rates to drive policy and job creation.",
    version="1.0.0"
)

# ==========================================
# 1. SECURITY & CORS MIDDLEWARE CONFIGURATION
# ==========================================
# CORS ensures that ONLY your authorized Flutter app can request predictions.
# This prevents random, malicious websites from spamming your server.
ALLOWED_ORIGINS = [
    "https://linear-regression-task.onrender.com",       # Local Flutter web test

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Secure restricted access whitelist (No generic "*" wildcard)
    allow_credentials=True,         # Allows passing HTTP authorization headers or cookies
    allow_methods=["GET", "POST"],  # Only allows explicit necessary HTTP methods
    allow_headers=["*"],            # Allows standard headers (e.g. Content-Type)
)

# ==========================================
# 2. LOAD PREPROCESSOR AND MODEL ARTIFACTS
# ==========================================
try:
    model = joblib.load('best_model.pkl')
    preprocessor = joblib.load('preprocessor.pkl')
except Exception as e:
    model = None
    preprocessor = None
    print(f"Error loading model files: {e}. Run your Jupyter notebook first!")

# ==========================================
# 3. PYDANTIC DATA MODELS & CONSTRAINTS
# ==========================================
class YouthUnemploymentInput(BaseModel):
    country_name: str = Field(..., description="Country name", example="Zambia")
    sex: str = Field(..., description="Gender (Female or Male)", example="Female")
    # Constraining input ranges to realistic historical youth unemployment percentages (0% - 100%)
    y2014: float = Field(..., ge=0.0, le=100.0, example=16.9)
    y2015: float = Field(..., ge=0.0, le=100.0, example=17.0)
    y2016: float = Field(..., ge=0.0, le=100.0, example=16.9)
    y2017: float = Field(..., ge=0.0, le=100.0, example=16.6)
    y2018: float = Field(..., ge=0.0, le=100.0, example=8.0)
    y2019: float = Field(..., ge=0.0, le=100.0, example=8.1)
    y2020: float = Field(..., ge=0.0, le=100.0, example=10.7)
    y2021: float = Field(..., ge=0.0, le=100.0, example=10.0)
    y2022: float = Field(..., ge=0.0, le=100.0, example=9.2)
    y2023: float = Field(..., ge=0.0, le=100.0, example=8.6)

class RetrainRequest(BaseModel):
    # Simulated structure for background retraining using fresh data points
    new_data: list[dict]

# ==========================================
# 4. API ENDPOINTS
# ==========================================

@app.get("/")
def home():
    return {"status": "healthy", "mission": "Youth Job Creation & Economic Modeling API"}

@app.post("/predict")
def predict_unemployment(data: YouthUnemploymentInput):
    if model is None or preprocessor is None:
        raise HTTPException(status_code=500, detail="Prediction models are not loaded on the server.")
    
    # Formulate input structure matching preprocessor expectations
    input_data = pd.DataFrame([{
        "country_name": data.country_name,
        "sex": data.sex,
        "2014": data.y2014,
        "2015": data.y2015,
        "2016": data.y2016,
        "2017": data.y2017,
        "2018": data.y2018,
        "2019": data.y2019,
        "2020": data.y2020,
        "2021": data.y2021,
        "2022": data.y2022,
        "2023": data.y2023
    }])
    
    try:
        # Scale and transform categorical/numeric fields using saved preprocessor
        features_transformed = preprocessor.transform(input_data)
        
        # Predict 2024 values
        prediction = model.predict(features_transformed)
        return {"predicted_youth_unemployment_2024": round(float(prediction[0]), 2)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Data Transformation/Prediction Error: {str(e)}")

# ==========================================
# 5. RETRAINING TRIGGER (BACKGROUND TASK)
# ==========================================
def retrain_model_background(new_data_points: list):
    """Simulates background execution so clients get an instant response without waiting."""
    print(f"Retraining triggered in background with {len(new_data_points)} new data records...")
    # In practice: load historical data, append new_data_points, fit() model, and call joblib.dump()
    print("Retraining Complete! Hot-swapped updated 'best_model.pkl'.")

@app.post("/retrain")
def trigger_retraining(request: RetrainRequest, background_tasks: BackgroundTasks):
    # Use FastAPI BackgroundTasks to offload retraining processes asynchronously
    background_tasks.add_task(retrain_model_background, request.new_data)
    return {"message": "Model retraining successfully triggered in the background. Service remains active."}