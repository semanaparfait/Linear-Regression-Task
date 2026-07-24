from pathlib import Path

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import pandas as pd
import joblib
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, SGDRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeRegressor

app = FastAPI(
    title="Youth Job Creation Predictor API",
    description="Production-ready ML API predicting Youth Unemployment rates to drive policy and job creation.",
    version="1.0.0"
)

ALLOWED_ORIGINS = [
    "https://linear-regression-task.onrender.com",
    "http://localhost:5000",
    "http://127.0.0.1:5000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  
    allow_credentials=True,        
    allow_methods=["*"],  
    allow_headers=["*"],            
)


BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent.parent
DATASET_PATH = ROOT_DIR / "global_unemployment_data.csv"
MODEL_PATH = BASE_DIR / "best_model.pkl"
PREPROCESSOR_PATH = BASE_DIR / "preprocessor.pkl"

AFRICAN_COUNTRIES = {
    "Algeria", "Angola", "Benin", "Botswana", "Burkina Faso", "Burundi", "Cabo Verde",
    "Cameroon", "Central African Republic", "Chad", "Comoros", "Congo",
    "Democratic Republic of the Congo", "Djibouti", "Egypt", "Equatorial Guinea",
    "Eritrea", "Eswatini", "Ethiopia", "Gabon", "Gambia", "Ghana", "Guinea",
    "Guinea-Bissau", "Ivory Coast", "Kenya", "Lesotho", "Liberia", "Libya",
    "Madagascar", "Malawi", "Mali", "Mauritania", "Mauritius", "Morocco",
    "Mozambique", "Namibia", "Niger", "Nigeria", "Rwanda", "Sao Tome and Principe",
    "Senegal", "Seychelles", "Sierra Leone", "Somalia", "South Africa",
    "South Sudan", "Sudan", "Tanzania", "Togo", "Tunisia", "Uganda",
    "Zambia", "Zimbabwe",
}

YEAR_COLUMNS = [str(year) for year in range(2014, 2025)]
FEATURE_COLUMNS = [str(year) for year in range(2014, 2024)]
TARGET_COLUMN = "2024"


def _normalize_training_frame(frame: pd.DataFrame) -> pd.DataFrame:
    normalized = frame.copy()

    column_map = {
        "y2014": "2014",
        "y2015": "2015",
        "y2016": "2016",
        "y2017": "2017",
        "y2018": "2018",
        "y2019": "2019",
        "y2020": "2020",
        "y2021": "2021",
        "y2022": "2022",
        "y2023": "2023",
    }
    normalized = normalized.rename(columns=column_map)

    required_columns = {"country_name", "sex", "age_categories", *YEAR_COLUMNS}
    missing_columns = sorted(required_columns.difference(normalized.columns))
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

    normalized = normalized[normalized["country_name"].isin(AFRICAN_COUNTRIES)].copy()
    normalized = normalized[normalized["age_categories"].astype(str).str.lower() == "youth"].copy()

    for year in YEAR_COLUMNS:
        normalized[year] = pd.to_numeric(normalized[year], errors="coerce")
        normalized[year] = normalized[year].fillna(normalized[year].median())

    normalized[TARGET_COLUMN] = normalized[TARGET_COLUMN].fillna(normalized[TARGET_COLUMN].median())
    return normalized


def _build_preprocessor() -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            ("num", Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
            ]), FEATURE_COLUMNS),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), ["country_name", "sex"]),
        ]
    )


def _train_and_select_best_model(frame: pd.DataFrame):
    X = frame.drop(columns=[TARGET_COLUMN, "age_group", "age_categories"])
    y = frame[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    preprocessor = _build_preprocessor()
    X_train_scaled = preprocessor.fit_transform(X_train)
    X_test_scaled = preprocessor.transform(X_test)

    candidates = {
        "Linear Regression": LinearRegression(),
        "SGD Linear Regression": SGDRegressor(max_iter=1000, random_state=42),
        "Decision Tree": DecisionTreeRegressor(max_depth=5, random_state=42),
        "Random Forest": RandomForestRegressor(n_estimators=100, max_depth=6, random_state=42),
    }

    results = {}
    fitted_models = {}
    for name, candidate in candidates.items():
        candidate.fit(X_train_scaled, y_train)
        predictions = candidate.predict(X_test_scaled)
        results[name] = mean_squared_error(y_test, predictions)
        fitted_models[name] = candidate

    best_model_name = min(results, key=results.get)
    return fitted_models[best_model_name], preprocessor, results, best_model_name


def _persist_artifacts(fitted_model, fitted_preprocessor) -> None:
    joblib.dump(fitted_model, MODEL_PATH)
    joblib.dump(fitted_preprocessor, PREPROCESSOR_PATH)


def _load_training_source() -> pd.DataFrame:
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Training dataset not found: {DATASET_PATH}")
    return pd.read_csv(DATASET_PATH)


try:
    model = joblib.load(MODEL_PATH)
    preprocessor = joblib.load(PREPROCESSOR_PATH)
except Exception as e:
    model = None
    preprocessor = None
    print(f"Error loading model files: {e}. Run your Jupyter notebook first!")


class YouthUnemploymentInput(BaseModel):
    country_name: str = Field(..., description="Country name", example="Zambia")
    sex: str = Field(..., description="Gender (Female or Male)", example="Female")
 
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
    
    new_data: list[dict]



@app.get("/")
def home():
    return {"status": "healthy", "mission": "Youth Job Creation & Economic Modeling API"}

@app.post("/predict")
def predict_unemployment(data: YouthUnemploymentInput):
    if model is None or preprocessor is None:
        raise HTTPException(status_code=500, detail="Prediction models are not loaded on the server.")
    
    
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
      
        features_transformed = preprocessor.transform(input_data)

        prediction = model.predict(features_transformed)
        return {"predicted_youth_unemployment_2024": round(float(prediction[0]), 2)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Data Transformation/Prediction Error: {str(e)}")


def retrain_model_background(new_data_points: list):
    global model, preprocessor

    print(f"Retraining triggered in background with {len(new_data_points)} new data records...")

    base_frame = _load_training_source()
    new_frame = pd.DataFrame(new_data_points)
    combined_frame = pd.concat([base_frame, new_frame], ignore_index=True)
    training_frame = _normalize_training_frame(combined_frame)

    fitted_model, fitted_preprocessor, results, best_model_name = _train_and_select_best_model(training_frame)
    _persist_artifacts(fitted_model, fitted_preprocessor)

    model = fitted_model
    preprocessor = fitted_preprocessor

    print(f"Retraining Complete! Best model: {best_model_name}.")
    print(f"Updated model losses: {results}")

@app.post("/retrain")
def trigger_retraining(request: RetrainRequest, background_tasks: BackgroundTasks):
    if not request.new_data:
        raise HTTPException(status_code=400, detail="new_data must contain at least one record.")

    background_tasks.add_task(retrain_model_background, request.new_data)
    return {"message": "Model retraining successfully triggered in the background. Service remains active."}