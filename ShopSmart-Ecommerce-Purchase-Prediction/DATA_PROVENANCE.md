# Data Provenance & Redistribution Notice — E-Commerce Customer Purchase Prediction

**Dataset File:** `Ecommerce_Purchase_Prediction_DataSet.csv`  
**Dimensions:** `10,000` rows × `19` columns (`1,004,190` bytes)  
**Verified SHA-256:** `6D8A176EEDA1CCB01840D04F2172457F4E2E83782D079762888B544AA202FF05`

---

## 1. Provenance & Redistribution Status (Unverified)

- **Original Source / License:** **Not independently verified.** No upstream citation, open-data license, or redistribution agreement accompanied the supplied CSV.
- **GitHub Exclusion Policy:** Because redistribution rights are unverified, `data/raw/*.csv` and `outputs/test_set_predictions.csv` are excluded via `.gitignore` and **must not be committed or pushed to public GitHub** unless redistribution permission is formally confirmed.
- **Local Retention:** The original source CSV is preserved untouched in the verified backup (`Ecommerce-Purchase-Prediction-Final-Backup`) and kept strictly local inside `data/raw/` for authorized local execution.

## 2. Privacy & Identifier Safeguards

- `Customer_ID` (`CUST00001`–`CUST10000`) is dropped prior to modeling (`ID_COL`) and is not exposed in documentation or figures.
- All outputs in `README.md` and `reports/MODEL_VALIDATION_REPORT.md` report aggregate statistics only.
