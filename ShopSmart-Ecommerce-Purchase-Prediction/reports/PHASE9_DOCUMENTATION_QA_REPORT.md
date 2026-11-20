# PHASE 9 — DOCUMENTATION & PORTFOLIO PRESENTATION QA REPORT
## ShopSmart — E-Commerce Customer Purchase Prediction

**Review Date:** 2026-11-21  
**Reviewer Perspective:** Senior Technical Recruiter & Senior ML Engineer  
**Target Folder:** `PoojaS-1616/data-analysis/ShopSmart-Ecommerce-Purchase-Prediction/`  
**Base Commit:** `6c85f26af787fc8d0f13d8494bbf608f8a1e269c`

---

## 1. Before / After Portfolio Assessment

| Evaluation Dimension | Before Phase 9 | After Phase 9 | Key Improvement |
|---|---:|---:|---|
| **First Impression (60–120s Scan)** | 8.5 / 10 | **9.5 / 10** | Hero badges, Table of Contents, Project Highlights KPI table, and 8 genuine light-theme UI screenshots |
| **README Clarity & Navigation** | 8.5 / 10 | **9.5 / 10** | 19 structured sections + dedicated `docs/` suite (`QUICKSTART.md`, `TECHNICAL_WALKTHROUGH.md`, `PROJECT_SUMMARY.md`, `DEMO_VIDEO_STORYBOARD.md`) |
| **Visual Quality** | 8.0 / 10 | **9.2 / 10** | Fixed live Streamlit dark-theme contrast (`.streamlit/config.toml` light theme), fixed Page 1 4-tier segment mapping, captured all 8 real UI pages |
| **Technical Credibility** | 9.5 / 10 | **9.7 / 10** | Explicitly audited `C=0.1` benchmark vs. `C=1.0` local artifact rather than hiding the `0.0006` ROC-AUC difference; fixed real `app.py` package-shadowing startup bug caught during live browser testing |
| **Reproducibility & Governance** | 9.0 / 10 | **9.3 / 10** | 11-step PowerShell Quickstart with troubleshooting table; zero raw CSVs, `.joblib`, `.venv`, credentials, or personal paths |

---

## 2. Technical Inconsistencies & Live Bugs Found and Resolved

1. **Live Startup Import Bug (`app/app.py`):** Launching `streamlit run app\app.py` caused `app/app.py` to shadow the `app` package (`ModuleNotFoundError: No module named 'app.components'`). Fixed by removing `APP_DIR` from `sys.path` and pinning `PROJECT_ROOT` at `sys.path[0]`.
2. **Duplicate Auto-Sidebar & Dark-Theme Contrast (`.streamlit/config.toml`):** Added `showSidebarNavigation = false` and `base = "light"` matching ShopSmart's Deep Navy / White / Blue visual identity.
3. **Page 1 Intent Segment Mismatch (`app/pages/executive_overview.py`):** Computed 4-tier segments directly from `Purchase_Probability` via `assign_marketing_segment` so all `2,000` test rows display cleanly across all 4 bars (`687`, `860`, `372`, `81`).
4. **Benchmark `C=0.1` vs. Artifact `C=1.0` Audit:** Documented transparently in `README.md` (`Model Version & Evaluation Protocol Note`) without altering historical metrics.
5. **Parent `data-analysis/README.md` Sync:** Updated only ShopSmart's two outdated counts (`seven-page -> eight-page`, `9/9 -> 16/16`); the other four projects remain 100% untouched.

---

## 3. Genuine Screenshots Verified (`8 / 8`)

All 8 PNGs in `docs/screenshots/` (`01_executive_overview.png` through `08_business_impact_simulator.png`) were captured from the live running Streamlit server at `http://localhost:8520` (`1440×900` light theme) and verified visually.

---

## 4. Remaining Limitations (Why Score Is Not 10.0 / 10)

- **No Synthetic Demo Mode Yet:** Clones without the excluded raw CSV still cannot launch the Streamlit app without supplying an authorized local CSV first.
- **No GitHub Actions CI Workflow Yet:** Automated `pytest` (`16/16`) runs locally rather than via live GitHub Actions badges.
- **Minor Narrow-Viewport Wrapping on Page 8 Screenshot:** `08_business_impact_simulator.png` wraps long INR KPI digits slightly on 4-column cards; readable and genuine, but could be tightened with wider viewport CSS in a future pass.
- **No Public Cloud Deployment or Recorded Demo Video Yet:** Storyboard prepared (`docs/DEMO_VIDEO_STORYBOARD.md`); no video or deployment URL fabricated.

---

## 5. Final Presentation Score

**Final Score:** **`9.4 / 10`** (Recruiter & Senior ML Engineer Portfolio Standard) — **Status: `READY FOR APPROVAL GATE`**
