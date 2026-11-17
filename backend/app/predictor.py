import joblib
from pathlib import Path

# Path(__file__) is this file. .parent is app/, .parent.parent is backend/, so this points at backend/models/<file>. what is the model's file name? (look in backend/models/)
MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "genre_classifier.pkl"

# the order the model was trained on. scikit-learn matches columns by position, not by name. Do not reorder
FEATURE_ORDER = (
    "danceability", "energy", "key", "loudness", "mode", "speechiness", "acousticness",
    "instrumentalness", "liveness", "valence", "tempo", "time_signature", "duration_ms",
    "popularity", "explicit",
)


class Predictor:
    source = "model" # reported in every response, so a caller can tell a real prediction from the old "mock"

    def __init__(self, path: Path) -> None:
        # which joblib function reads a .pkl file back into Python objects? (the opposite of dump)
        bundle = joblib.load(path)
        self.model = bundle["model"] # the trained LogisticRegression
        # the bundle is a dict with keys "model", "scaler", "label_encoder", "feature_cols", "classes". the model was trained on scaled numbers, so which key holds the StandardScaler?
        self.scaler = bundle["scaler"]
        # the LabelEncoder stores the genre names in its classes_ attribute. what is the attribute called? (it ends in an underscore)
        self.genres = list(bundle["label_encoder"].classes_)
        # the scaler remembers the column names it was trained with, so passing a plain list makes scikit-learn warn on every request. We already control the order, so drop the names
        del self.scaler.feature_names_in_

    def predict(self, vector: list[float]) -> dict[str, float]:
        # which scaler method applies the scaling learned in training? (not fit_transform, which would re-learn it from this one row). the extra [ ] makes one row of samples
        scaled = self.scaler.transform([vector])
        # which model method returns one probability per genre, not just the winner? it returns a table with one row per sample. what index picks out the only row? (the shape is (1, 5))
        probabilities = self.model.predict_proba(scaled)[0]
        return {genre: float(p) for genre, p in zip(self.genres, probabilities)}
