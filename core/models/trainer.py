import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib
from pathlib import Path

MODEL_DIR = Path("data/models")
MODEL_PATH = MODEL_DIR / "dividend_predictor.pkl"

def train_model(data: pd.DataFrame):
    """
    Trains a simple RandomForestClassifier on dividend stock data.
    This is a placeholder model and should be replaced with more
    sophisticated logic as the data pipeline matures.
    """
    if data.empty or "Dividend Yield" not in data.columns:
        raise ValueError("Insufficient or invalid data for training.")

    # Basic feature engineering
    data = data.dropna(subset=["Dividend Yield", "Stock Price"])
    data["Target"] = data["Dividend Yield"] > data["Dividend Yield"].median()

    X = data[["Stock Price", "Dividend Amount"]]
    y = data["Target"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    accuracy = model.score(X_test, y_test)
    print(f"[+] Model trained with accuracy: {accuracy:.2%}")

    # Save model
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"[+] Model saved to: {MODEL_PATH}")

def load_model():
    """
    Loads the trained model from disk.
    """
    if not MODEL_PATH.exists():
        raise FileNotFoundError("Model not found. Train the model first.")
    return joblib.load(MODEL_PATH)