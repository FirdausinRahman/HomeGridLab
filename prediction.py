import json
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from pyproj import Transformer
from xgboost import XGBRegressor


# ============================================================
# 1. PATH & MODEL
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "xgb_model.json"
SCHEMA_PATH = BASE_DIR / "predictor_schema.json"

KDE_DIR = BASE_DIR / "Data" / "KDE"
COST_DIR = BASE_DIR / "Data" / "Cost"

model = XGBRegressor()
model.load_model(MODEL_PATH)


with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
    schema = json.load(f)

if isinstance(schema, dict):
    FEATURE_COLUMNS = schema["columns"]
else:
    FEATURE_COLUMNS = schema


# ============================================================
# 2. RASTER CONFIGURATION
# ============================================================

KDE_RASTERS = {
    "sum_XC_X3": "XC_Finances.tif",
    "sum_XE_X5": "XE_Government.tif",
    "sum_XI_X9": "XI_Religion.tif",
    "sum_XJ_X10": "XJ_Retail.tif",
    "sum_XK_X11": "XK_Security.tif",
    "sum_XM_X13": "XM_Sport.tif",
}


COST_RASTERS = {
    "sum_XC_X3": "3_Finances_Cost.tif",
    "sum_XE_X5": "5_Gov_Cost.tif",
    "sum_XI_X9": "9_Religion_Cost.tif",
    "sum_XJ_X10": "10_Retail_Cost.tif",
    "sum_XK_X11": "11_Security_Cost.tif",
    "sum_XM_X13": "13_Sport_Cost.tif",
}


# ============================================================
# 3. COORDINATE TRANSFORMATION
# ============================================================

TRANSFORMER = Transformer.from_crs(
    "EPSG:4326",
    "EPSG:32748",
    always_xy=True
)


# ============================================================
# 4. KDE MIN-MAX VALUES
# ============================================================

KDE_MIN_MAX = {}

for predictor, filename in KDE_RASTERS.items():

    with rasterio.open(KDE_DIR / filename) as src:

        raster = src.read(1, masked=True)

        KDE_MIN_MAX[predictor] = (
            float(raster.min()),
            float(raster.max())
        )

# ============================================================
# 5. RASTER SAMPLING
# ============================================================

def sample_raster(path, x, y):
    """
    Mengambil nilai raster pada koordinat x, y.

    Return:
        float -> jika data tersedia
        None  -> jika titik berada di luar coverage / NoData
    """

    with rasterio.open(path) as src:

        # ----------------------------------------------------
        # Check apakah koordinat berada di dalam raster
        # ----------------------------------------------------

        bounds = src.bounds

        if not (
            bounds.left <= x <= bounds.right
            and
            bounds.bottom <= y <= bounds.top
        ):
            return None

        # ----------------------------------------------------
        # Sample raster
        # ----------------------------------------------------

        value = next(
            src.sample([(x, y)])
        )[0]

        # ----------------------------------------------------
        # Check NoData
        # ----------------------------------------------------

        if src.nodata is not None:

            if np.isclose(value, src.nodata):
                return None

        # ----------------------------------------------------
        # Check invalid value
        # ----------------------------------------------------

        if not np.isfinite(value):
            return None

        return float(value)


# ============================================================
# 6. KDE PREPROCESSING
# ============================================================

def preprocess_kde(raw_value, predictor):
    """
    Raw KDE
    → Min-Max 0–100
    → log1p
    """

    minimum, maximum = KDE_MIN_MAX[predictor]

    if maximum == minimum:
        return 0.0

    minmax_value = (
        (raw_value - minimum)
        / (maximum - minimum)
    ) * 100

    return float(
        np.log1p(minmax_value)
    )


# ============================================================
# 7. COST PREPROCESSING
# ============================================================

def preprocess_cost(raw_value):
    """
    Raw Cost
    → log1p
    """

    return float(
        np.log1p(raw_value)
    )


# ============================================================
# 8. GET SPATIAL PREDICTORS
# ============================================================

def get_spatial_predictors(latitude, longitude):

    x, y = TRANSFORMER.transform(
        longitude,
        latitude
    )

    predictors = {}

    for predictor in KDE_RASTERS:

        kde_path = (
            KDE_DIR /
            KDE_RASTERS[predictor]
        )

        cost_path = (
            COST_DIR /
            COST_RASTERS[predictor]
        )

        # ----------------------------------------------------
        # KDE
        # ----------------------------------------------------

        kde_raw = sample_raster(
            kde_path,
            x,
            y
        )

        # Jika KDE tidak memiliki data
        if kde_raw is None:
            return None

        # ----------------------------------------------------
        # Cost
        # ----------------------------------------------------

        cost_raw = sample_raster(
            cost_path,
            x,
            y
        )

        # Jika Cost tidak memiliki data
        if cost_raw is None:
            return None

        # ----------------------------------------------------
        # Preprocessing
        # ----------------------------------------------------

        kde_value = preprocess_kde(
            kde_raw,
            predictor
        )

        cost_value = preprocess_cost(
            cost_raw
        )

        # ----------------------------------------------------
        # Combined predictor
        # ----------------------------------------------------

        predictors[predictor] = (
            kde_value +
            cost_value
        )

    return predictors


# ============================================================
# 9. PREPARE MODEL INPUT
# ============================================================

def prepare_prediction_input(
    spatial_predictors,
    bentuk_tapak,
    orientasi,
    kondisi_wilayah_sekitar
):

    data = spatial_predictors.copy()

    data["bentuk_tapak"] = (
        bentuk_tapak
    )

    data["orientasi"] = (
        orientasi
    )

    data["kondisi_wilayah_sekitar"] = (
        kondisi_wilayah_sekitar
    )

    df = pd.DataFrame([data])

    df = pd.get_dummies(
        df,
        columns=[
            "bentuk_tapak",
            "orientasi",
            "kondisi_wilayah_sekitar"
        ],
        drop_first=True
    )

    df = df.reindex(
        columns=FEATURE_COLUMNS,
        fill_value=0
    )

    return df


# ============================================================
# 10. PREDICTION
# ============================================================

def predict_land_price(
    latitude,
    longitude,
    bentuk_tapak,
    orientasi,
    kondisi_wilayah_sekitar
):

    # --------------------------------------------------------
    # Get spatial predictors
    # --------------------------------------------------------

    spatial_predictors = get_spatial_predictors(
        latitude,
        longitude
    )

    # --------------------------------------------------------
    # Location unavailable
    # --------------------------------------------------------

    if spatial_predictors is None:
        return None

    # --------------------------------------------------------
    # Prepare model input
    # --------------------------------------------------------

    X = prepare_prediction_input(
        spatial_predictors=spatial_predictors,

        bentuk_tapak=bentuk_tapak,

        orientasi=orientasi,

        kondisi_wilayah_sekitar=(
            kondisi_wilayah_sekitar
        )
    )

    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    predicted_ln_price = model.predict(X)[0]

    predicted_price = np.exp(
        predicted_ln_price
    )

    return float(predicted_price)