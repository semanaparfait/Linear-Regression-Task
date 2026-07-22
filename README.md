## Mission

The project focuses on predicting youth unemployment rates across countries using historical unemployment data. The goal is to help identify patterns that can support targeted youth employment btn 18-25 policy and planning.

## Dataset

Source file: `global_unemployment_data.csv`

The dataset contains country-level unemployment records with:

- `country_name`
- `sex`
- `age_group`
- `age_categories`
- yearly unemployment values from `2014` to `2024`

The notebook filters the data to the youth group (`15-24`) and uses the historical years `2014` to `2023` to predict `2024`.

Why this dataset fits the assignment:

- It is not a house-price dataset.
- It is tied to a real-world mission.
- It contains a rich mix of categorical and numeric variables.
- It supports regression modeling and comparison across multiple algorithms.

## Notebook Workflow

Main notebook: [Linear_Regression.ipynb](Linear_Regression.ipynb)

The notebook covers:

1. Loading and cleaning the dataset.
2. Filtering to youth unemployment records.
3. Visualizing the data with meaningful plots.
4. Preprocessing numeric and categorical variables.
5. Training and comparing regression models.
6. Saving the best-performing model with `joblib`.
7. Making a single-row prediction for deployment testing.

### Models Compared

The notebook compares four regression models built with scikit-learn:

- `LinearRegression`
- `SGDRegressor`
- `DecisionTreeRegressor`
- `RandomForestRegressor`

The best model is selected using test loss, specifically mean squared error.

### Visualizations Included

The notebook includes at least two useful visual checks for the task:

- A boxplot showing youth unemployment by gender.
- A correlation heatmap for recent yearly unemployment values.
- A scatter plot of actual vs predicted values for the final model.

## API

API folder: [summative/API](summative/API)

Main API file: [prediction.py](summative/API/prediction.py)

The API is built with:

- FastAPI
- Pydantic
- Uvicorn
- scikit-learn
- pandas
- numpy
- joblib

### Prediction Endpoint

`POST /predict`

This endpoint accepts the prediction inputs and returns the predicted youth unemployment rate for `2024`.

### Input Validation

Pydantic enforces data types and range checks:

- `country_name`: string
- `sex`: string
- yearly values: float
- yearly values are constrained to a realistic range of `0` to `100`

### CORS Configuration

The API uses CORS middleware with explicit allowed origins rather than a blanket wildcard.

Allowed origins currently include local development URLs and the deployed Render origin used by the app.

This is intentional because:

- It allows the Flutter app or local frontend to call the API safely.
- It restricts unwanted cross-origin access from unrelated sites.
- It keeps the deployment more secure than `allow_origins=["*"]`.

### Retraining Endpoint

`POST /retrain`

This endpoint is included as a retraining trigger so the model can be refreshed when new data is received. The current implementation runs the retraining task in the background, reloads the dataset, rebuilds the preprocessor, retrains the candidate models, and resaves the best model artifact.

## Flutter App

Flutter app folder: [summative/flutterapp](summative/flutterapp)

Main UI file: [lib/main.dart](summative/flutterapp/lib/main.dart)

The Flutter app is a single-page prediction screen with:

- Country selection
- Gender selection
- Historical input fields for yearly unemployment rates
- A `Predict` button
- A result area for displaying predictions or validation errors

The app calls the FastAPI prediction endpoint and sends the required inputs in JSON format.

## Project Structure

```text
ml_summative/
├── global_unemployment_data.csv
├── Linear_Regression.ipynb
├── README.md
└── summative/
    ├── API/
    │   ├── prediction.py
    │   └── requirements.txt
    └── flutterapp/
        ├── lib/
        │   └── main.dart
        └── pubspec.yaml
```

## Setup

### Python environment with uv

From the repository root:

```bash
uv venv
uv sync
```

The repository now includes a root `pyproject.toml` and `uv.lock` for reproducible Python dependency management.

### Run the API locally

```bash
cd summative/API
uvicorn prediction:app --reload
```

### Run the Flutter app

```bash
cd summative/flutterapp
flutter pub get
flutter run
```

- Swagger UI: `https://linear-regression-task.onrender.com/docs`
