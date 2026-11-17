from contextlib import asynccontextmanager

import sklearn
from fastapi import FastAPI, Request

from .predictor import FEATURE_ORDER, MODEL_PATH, Predictor
from .schemas import PredictRequest


@asynccontextmanager
async def lifespan(app: FastAPI):
    # runs once, when the server starts, before the first request. The model is stored on app.state so every request can reuse it. why not load it inside predict() instead?
    app.state.predictor = Predictor(MODEL_PATH)
    yield

app = FastAPI(title="Genrify Genre API", version="0.1.0", lifespan=lifespan) # FastAPI needs to be handed the startup function above. what is it called?

@app.get("/health", tags=["meta"])
def health(request: Request):
    predictor = request.app.state.predictor
    return {"status": "ok", "source": predictor.source, "sklearn_version": sklearn.__version__} # open /health. it no longer says "mock". the version must match the one that wrote the .pkl

@app.post("/predict", tags=["prediction"])
def predict(payload: PredictRequest, request: Request):
    predictor = request.app.state.predictor
    values = payload.model_dump()
    # build the list in the exact training order. which constant holds that order? (imported at the top). float() turns the bool explicit into 1.0 or 0.0
    vector = [float(values[name]) for name in FEATURE_ORDER]
    probabilities = predictor.predict(vector)
    genre = max(probabilities, key=probabilities.get) # max() needs a way to look up each genre's probability. which dict method takes a key and returns its value?
    return {
        "genre": genre,
        "confidence": probabilities[genre], # the probability of the winning genre
        "probabilities": probabilities,
        "source": predictor.source, # which attribute of the predictor says where this answer came from? ("model" or "mock")
    }
