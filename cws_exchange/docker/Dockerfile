FROM quay.io/jupyter/datascience-notebook:python-3.12.7

# set up jupyter
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONUTF8=1 \
    PYTHONIOENCODING=UTF-8

# install packages with conda
RUN echo Y | mamba install -c conda-forge xgboost shap tableone openpyxl jupyterlab-git ipython-sql pingouin optuna joblib tqdm lightgbm imbalanced-learn

CMD jupyter lab --ip=0.0.0.0 --port=8888 --allow-root
