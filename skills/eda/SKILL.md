---
name: eda
description: How to perform exploratory data analysis - summary stats, missing values, distributions, correlations.
---

# Exploratory Data Analysis (EDA)

Use this when the user asks general questions about their dataset
("what does this data look like?", "summarize this dataset", "any patterns?").

## Steps
1. Check `df.shape`, `df.dtypes`, and `df.isnull().sum()` first.
2. For numeric columns, use `df.describe()` for central tendency and spread.
3. For categorical columns, use `df['col'].value_counts()`.
4. Check for correlations between numeric columns with `df.corr(numeric_only=True)`.
5. Flag any columns with >30% missing values or obvious outliers (use
   `df['col'].quantile([0.01, 0.99])` to spot extreme values).
6. Always summarize findings in `result` as a readable string, not just raw
   dataframes.