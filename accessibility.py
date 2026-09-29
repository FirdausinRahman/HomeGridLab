from pathlib import Path

import numpy as np
import rasterio
from pyproj import Transformer


# ============================================================
# PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

KDE_DIR = BASE_DIR / "Data" / "KDE"
COST_DIR = BASE_DIR / "Data" / "Cost"

# ============================================================
# COORDINATE TRANSFORMATION
# WGS84 (latitude/longitude) → UTM 48S
# ============================================================

TRANSFORMER = Transformer.from_crs(
    "EPSG:4326",
    "EPSG:32748",
    always_xy=True
)


# ============================================================
# AMENITY RASTERS
# ============================================================

AMENITIES = {

    "Leisure": {
        "kde": "XA_Entertainment.tif",
        "cost": "1_Culture_Entertain_Cost.tif",
    },

    "Education": {
        "kde": "XB_Education.tif",
        "cost": "2_Education_Cost.tif",
    },

    "Finance": {
        "kde": "XC_Finances.tif",
        "cost": "3_Finances_Cost.tif",
    },

    "Culinary": {
        "kde": "XD_Gastronomy.tif",
        "cost": "4_Gastronomy_Cost.tif",
    },

    "Government Office": {
        "kde": "XE_Government.tif",
        "cost": "5_Gov_Cost.tif",
    },

    "Health": {
        "kde": "XF_Health.tif",
        "cost": "6_Health_Cost.tif",
    },

    "Worshiping Place": {
        "kde": "XI_Religion.tif",
        "cost": "9_Religion_Cost.tif",
    },

    "Retail / Store": {
        "kde": "XJ_Retail.tif",
        "cost": "10_Retail_Cost.tif",
    },

    "Sport & Park": {
        "kde": "XM_Sport.tif",
        "cost": "13_Sport_Cost.tif",
    },

    "Tourism Accommodation": {
        "kde": "XN_Tourism.tif",
        "cost": "14_Tourism_Cost.tif",
    },
}


# ============================================================
# RASTER UTILITIES
# ============================================================

def get_valid_min_max(path):
    """
    Get minimum and maximum valid values from a raster.

    NoData and non-finite values are excluded.
    """

    with rasterio.open(path) as src:

        data = src.read(1, masked=True)

        values = data.compressed()

        values = values[np.isfinite(values)]

        if len(values) == 0:
            return None, None

        return float(values.min()), float(values.max())


def sample_raster(path, x, y):
    """
    Sample a raster at projected coordinates.

    Returns:
        float : valid raster value
        None  : outside raster coverage or NoData
    """

    with rasterio.open(path) as src:

        bounds = src.bounds

        # Outside raster coverage
        if not (
            bounds.left <= x <= bounds.right
            and bounds.bottom <= y <= bounds.top
        ):
            return None

        value = next(
            src.sample([(x, y)])
        )[0]

        # Handle NoData
        if src.nodata is not None:

            if np.isclose(value, src.nodata):
                return None

        # Handle NaN / infinity
        if not np.isfinite(value):
            return None

        return float(value)


# ============================================================
# CHOICE VARIETY SCORE
# ============================================================

def calculate_choice_variety_score(
    raw_value,
    minimum,
    maximum
):
    """
    Convert raw KDE into a 0–100 Choice Variety Score.

    Higher KDE = higher Choice Variety.

    Formula:

        ((KDE - KDE_min) /
         (KDE_max - KDE_min)) × 100
    """

    if minimum is None or maximum is None:
        return None

    if maximum == minimum:
        return 0.0

    score = (
        (raw_value - minimum)
        / (maximum - minimum)
    ) * 100

    return float(
        np.clip(score, 0, 100)
    )


# ============================================================
# ACCESSIBILITY SCORE
# ============================================================

def calculate_accessibility_score(raw_value):
    """
    Cost raster is already an Accessibility Score.

    Raster convention:

        0   = lowest accessibility
        100 = highest accessibility

    Therefore no transformation is applied.
    """

    return float(
        np.clip(raw_value, 0, 100)
    )


# ============================================================
# GENERIC 1–5 SCORE
# ============================================================

def score_to_level(score):
    """
    Convert a 0–100 score into five levels.

        1 = 0–<20
        2 = 20–<40
        3 = 40–<60
        4 = 60–<80
        5 = 80–100
    """

    if score < 20:
        return 1

    if score < 40:
        return 2

    if score < 60:
        return 3

    if score < 80:
        return 4

    return 5


# ============================================================
# CHOICE VARIETY LABEL
# ============================================================

def choice_level_label(level):
    """
    User-facing interpretation for Choice Variety.

    Levels 1 and 2 intentionally share the same
    neutral wording.
    """

    labels = {

        1: "Less Choice Variety Bonus",

        2: "Less Choice Variety Bonus",

        3: "Moderate Choice Variety Bonus",

        4: "Good Choice Variety Bonus",

        5: "Excellent Choice Variety Bonus",
    }

    return labels[level]


# ============================================================
# ACCESSIBILITY LABEL
# ============================================================

def accessibility_level_label(level):

    labels = {

        1: "Very bad",

        2: "Bad",

        3: "Moderate",

        4: "Good",

        5: "Excellent",
    }

    return labels[level]


# ============================================================
# OVERALL ACCESS SCORE LABEL
# ============================================================

def overall_level_label(level):

    labels = {

        1: "Very low",

        2: "Low",

        3: "Moderate",

        4: "Good",

        5: "Excellent",
    }

    return labels[level]


# ============================================================
# MAIN FUNCTION
# ============================================================

def get_accessibility_profile(
    latitude,
    longitude
):
    """
    Generate the complete amenity profile
    for a selected location.

    Returns:

        {
            "Education": {
                "choice_variety": ...,
                "accessibility": ...,
                "overall": ...,
                ...
            },
            ...
        }

    Returns None only if the coordinate transformation
    itself cannot be performed.
    """

    # --------------------------------------------------------
    # Convert WGS84 → UTM 48S
    # --------------------------------------------------------

    x, y = TRANSFORMER.transform(
        longitude,
        latitude
    )

    profile = {}

    # --------------------------------------------------------
    # Process each amenity category
    # --------------------------------------------------------

    for category, files in AMENITIES.items():

        kde_path = KDE_DIR / files["kde"]

        cost_path = COST_DIR / files["cost"]

        # ----------------------------------------------------
        # Check raster existence
        # ----------------------------------------------------

        if not kde_path.exists():

            profile[category] = None

            continue

        if not cost_path.exists():

            profile[category] = None

            continue

        # ----------------------------------------------------
        # Sample KDE
        # ----------------------------------------------------

        kde_raw = sample_raster(
            kde_path,
            x,
            y
        )

        # ----------------------------------------------------
        # Sample Accessibility
        # ----------------------------------------------------

        cost_raw = sample_raster(
            cost_path,
            x,
            y
        )

        # ----------------------------------------------------
        # Handle unavailable location
        # ----------------------------------------------------

        if kde_raw is None or cost_raw is None:

            profile[category] = None

            continue

        # ----------------------------------------------------
        # KDE → Choice Variety Score
        # ----------------------------------------------------

        kde_min, kde_max = get_valid_min_max(
            kde_path
        )

        choice_variety = calculate_choice_variety_score(
            raw_value=kde_raw,
            minimum=kde_min,
            maximum=kde_max
        )

        # ----------------------------------------------------
        # Cost → Accessibility Score
        # ----------------------------------------------------

        accessibility = calculate_accessibility_score(
            cost_raw
        )

        # ----------------------------------------------------
        # Overall Access Score
        # ----------------------------------------------------

        overall = (
            choice_variety
            + accessibility
        ) / 2

        # ----------------------------------------------------
        # Convert scores to levels
        # ----------------------------------------------------

        choice_level = score_to_level(
            choice_variety
        )

        accessibility_level = score_to_level(
            accessibility
        )

        overall_level = score_to_level(
            overall
        )

        # ----------------------------------------------------
        # Store result
        # ----------------------------------------------------

        profile[category] = {

            # Raw values
            "kde_raw": kde_raw,
            "cost_raw": cost_raw,

            # 0–100 scores
            "choice_variety": round(
                choice_variety,
                2
            ),

            "accessibility": round(
                accessibility,
                2
            ),

            "overall": round(
                overall,
                2
            ),

            # Choice Variety
            "choice_level": choice_level,

            "choice_label": choice_level_label(
                choice_level
            ),

            # Accessibility
            "accessibility_level": (
                accessibility_level
            ),

            "accessibility_label": (
                accessibility_level_label(
                    accessibility_level
                )
            ),

            # Overall
            "overall_level": overall_level,

            "overall_label": overall_level_label(
                overall_level
            ),
        }

    return profile