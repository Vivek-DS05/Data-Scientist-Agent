---
name: cleaning
description: How to handle missing values, duplicates, and outliers before analysis.
---

# Data Cleaning

Use this when the user asks to clean, fix, or prepare their data.

## Steps
1. Identify missing values: `df.isnull().sum()`.
2. Decide handling per column type:
   - Numeric: fill with median, or drop if <5% missing.
   - Categorical: fill with mode or "Unknown".
3. Remove exact duplicate rows: `df.drop_duplicates()`.
4. Detect outliers using IQR:
   `Q1, Q3 = df[col].quantile([0.25, 0.75])`
   `IQR = Q3 - Q1`
   flag values outside `[Q1 - 1.5*IQR, Q3 + 1.5*IQR]`.
5. Never silently modify data without explaining what you changed and why
   in the final `result` explanation.