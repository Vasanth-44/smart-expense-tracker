# Installing ML Dependencies on Windows

## Issue
scikit-learn requires Microsoft Visual C++ Build Tools on Windows.

## Solutions

### Option 1: Install Pre-built Wheel (Easiest)
```bash
pip install scikit-learn joblib
```
This usually works with the latest pip version.

### Option 2: Use Conda (Recommended for Windows)
```bash
# Install Miniconda from https://docs.conda.io/en/latest/miniconda.html
conda install scikit-learn joblib
```

### Option 3: Install Build Tools (If needed)
1. Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Install "Desktop development with C++"
3. Then run: `pip install scikit-learn joblib`

### Option 4: Use Without ML (Fallback)
The system works perfectly fine without the ML model using keyword-based categorization. Just skip the ML installation and the system will automatically use the keyword fallback.

## After Installation

Train the model:
```bash
python train_model.py
```

The backend will automatically load the model on startup.
