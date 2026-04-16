# Data Science for Engineers - Lab Course

Welcome to the lab exercises for the Data Science for Engineers course.

## Course Overview

This course bridges the gap between traditional engineering measurement analysis and modern machine learning. Throughout the semester, we will explore how to extract robust insights from data by combining statistical rigor with advanced algorithms.

Key topics covered include:

- **Error Analysis & Statistics:** Fundamentals of measurement error analysis, error propagation, and statistical techniques like Principal Component Analysis (PCA).
- **Optimization & Modeling:** Methods for linear and nonlinear optimization, and adapting univariate and multivariate model functions to measured data.
- **Uncertainty Quantification:** Classical and Bayesian approaches to determining error intervals and parameter dependencies.
- **Machine Learning:** Connecting nonlinear model adaptation to supervised learning, and applying unsupervised learning (clustering) to real-world measurements.

## Environment Setup

To ensure complete reproducibility and avoid dependency conflicts across different operating systems, we manage our lab environments using [**uv**](https://docs.astral.sh/uv/), a lightning-fast Python package installer and resolver.

Instead of dealing with global Python installations or manually creating virtual environments, `uv` allows us to define our environment declaratively.

### Prerequisites

If you haven't already, install `uv` on your machine: <https://docs.astral.sh/uv/getting-started/installation/>

### 1. Initialize the Project Environment

Navigate to the root directory of this repository. We will use `uv sync` to automatically read the `uv.lock` file, create an isolated virtual environment (`.venv`), and install all necessary dependencies (including Jupyter, Pandas, Plotly, and Scikit-Learn).

```bash
# Run this inside the course repository root
uv sync
```

### (1.5 activate environment)

To use `uv`, we need to prepend each command with `uv run`. If that is too tedious for you, activate the environment like any other environment in python using `source .venv/bin/activate` (if you are using a different shell, like `nu` or `fish`, use the appropriate activation script like `activate.nu` or `activate.fish`). This step is optional and the rest of the docs will use the `uv run` method!

### 2. Launching Jupyter Notebook

Once the environment is synced, you can launch Jupyter Notebook directly through uv. This ensures Jupyter is running entirely within the isolated course environment, guaranteeing access to the correct package versions.

```bash
uv run jupyter notebook
```
