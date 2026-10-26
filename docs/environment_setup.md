# Retail Sales Analytics — Environment Setup Guide

This guide provides end-to-end instructions for configuring the Python environment required for the Retail Sales Analytics project.

---

## 1. Prerequisites
- **Python**: Version `3.10`, `3.11`, `3.12`, or `3.13`.
- **Package Manager**: Either `pip` (standard) or `conda` / `miniconda` / `anaconda`.
- **Git** (optional, for version control).

---

## 2. Setup Option A: Conda Environment (Recommended for Data Science)

### Step 1: Open Terminal / Anaconda Prompt
Navigate to your project root directory:
```powershell
cd c:\Users\chand\OneDrive\Desktop\data
```

### Step 2: Create Conda Environment
Use the provided `environment.yml` configuration:
```bash
conda env create -f environment.yml
```

### Step 3: Activate the Environment
```bash
conda activate retail-sales-analytics
```

---

## 3. Setup Option B: Python Standard `venv`

### Step 1: Navigate to Workspace Root
```powershell
cd c:\Users\chand\OneDrive\Desktop\data
```

### Step 2: Create Virtual Environment
On Windows (PowerShell):
```powershell
py -m venv .venv
```
*(On macOS/Linux, run `python3 -m venv .venv`)*

### Step 3: Activate the Virtual Environment
On Windows (PowerShell):
```powershell
.\.venv\Scripts\Activate.ps1
```

> **Note for Windows PowerShell Users**: If you encounter an execution policy restriction (`running scripts is disabled on this system`), run:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

On macOS/Linux:
```bash
source .venv/bin/activate
```

### Step 4: Upgrade Pip and Install Dependencies
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 4. Verification and Sanity Testing

After activating your environment, run these commands to verify that your environment, dataset, and testing suite are functional:

### 1. Generate / Refresh the Dataset
```bash
python -m src.data_generator
```
*Expected Output: Generates 2,500 records saved to `data/raw/retail_sales.csv`.*

### 2. Run the Data Quality Validator
```bash
python -m src.validator
```
*Expected Output: `Overall Status: [PASS] PASSED (22 checks passed, 0 failed)`.*

### 3. Run Automated Unit & Integration Tests
```bash
pytest tests/test_validation.py -v
```
*Expected Output: `11 passed in ~3s`.*

---

## 5. IDE Setup (VS Code / Antigravity IDE)

1. **Select Interpreter**:
   - Press `Ctrl + Shift + P` (or `Cmd + Shift + P` on Mac).
   - Type `Python: Select Interpreter`.
   - Choose either:
     - The Conda environment (`retail-sales-analytics`)
     - Or the virtual environment (`./.venv/Scripts/python.exe`).
2. **Jupyter Notebooks**:
   - Ensure the `Jupyter` extension is enabled.
   - When opening files in `notebooks/`, select the active Python kernel at the top-right corner.
