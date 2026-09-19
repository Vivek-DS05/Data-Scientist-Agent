---
name: plotting
description: How to choose the right chart type and create clean matplotlib/seaborn visualizations.
---

# Visualization

Use this when the user asks to "show", "plot", "visualize", or "chart" something.

## Chart selection guide
- Single numeric distribution → `sns.histplot(df['col'], kde=True)`
- Compare numeric across categories → `sns.boxplot(x='cat_col', y='num_col', data=df)`
- Relationship between two numerics → `sns.scatterplot(x='a', y='b', data=df)`
- Correlation across many numerics → `sns.heatmap(df.corr(numeric_only=True), annot=True)`
- Category counts → `sns.countplot(x='col', data=df)`
- Trend over time → `df.plot(x='date_col', y='value_col')` (line chart)

## Rules
- Always add `plt.title(...)`, `plt.xlabel(...)`, `plt.ylabel(...)`.
- Call `plt.figure(figsize=(8,5))` before plotting to keep charts readable.
- Do NOT call `plt.show()` — the tool auto-saves the figure.
- Rotate x-tick labels with `plt.xticks(rotation=45)` if labels are long.