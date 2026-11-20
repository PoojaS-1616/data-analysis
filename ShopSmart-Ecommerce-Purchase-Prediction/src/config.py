"""Project-relative paths, feature definitions, and modeling constants."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_RAW_PATH = BASE_DIR / "data" / "raw" / "Ecommerce_Purchase_Prediction_DataSet.csv"
MODEL_DIR = BASE_DIR / "models"
MODEL_PATH = MODEL_DIR / "logistic_regression_pipeline.joblib"
OUTPUTS_DIR = BASE_DIR / "outputs"
FIGURES_DIR = OUTPUTS_DIR / "figures"
METRICS_PATH = OUTPUTS_DIR / "metrics_summary.json"
PREDICTIONS_PATH = OUTPUTS_DIR / "test_set_predictions.csv"
REPORTS_DIR = BASE_DIR / "reports"

RANDOM_STATE = 42
TEST_SIZE = 0.20
CV_FOLDS = 5

ID_COL = "Customer_ID"
TARGET_COL = "Purchase"

CAT_COLS = [
    "Gender",
    "Device_Type",
    "Traffic_Source",
    "Membership_Type",
    "Payment_Method",
]

NUM_COLS = [
    "Age",
    "Session_Duration_Min",
    "Pages_Viewed",
    "Products_Viewed",
    "Cart_Items",
    "Cart_Value_INR",
    "Discount_Percent",
    "Previous_Orders",
    "Days_Since_Last_Visit",
    "Email_Open_Rate",
    "Customer_Rating",
    "Returns_Last_Year",
]

# 5 continuous features exhibiting severe right-tail spikes in EDA
CAP_COLS = [
    "Session_Duration_Min",
    "Pages_Viewed",
    "Cart_Value_INR",
    "Discount_Percent",
    "Days_Since_Last_Visit",
]

PLAIN_NUM_COLS = [c for c in NUM_COLS if c not in CAP_COLS]

# Feature availability groups for leakage / prediction-time audit:
# Pre-checkout features available during browsing before payment selection
PRE_CHECKOUT_CAT_COLS = [c for c in CAT_COLS if c != "Payment_Method"]
# Pre-cart features available before items/cart value/payment are finalized
PRE_CART_NUM_COLS = [c for c in NUM_COLS if c not in {"Cart_Items", "Cart_Value_INR", "Discount_Percent"}]
