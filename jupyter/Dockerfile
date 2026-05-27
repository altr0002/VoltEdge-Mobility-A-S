FROM jupyter/scipy-notebook:python-3.11

USER root

RUN pip install --no-cache-dir \
    SQLAlchemy==2.0.36 \
    psycopg2-binary==2.9.10 \
    joblib==1.4.2

USER ${NB_UID}
