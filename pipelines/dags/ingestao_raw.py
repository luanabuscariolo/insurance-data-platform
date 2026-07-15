"""DAG da Fase 2: carrega os parquet da raw zone para o schema raw do PostgreSQL."""
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook

RAW_DIR = Path(os.environ.get("RAW_DIR", "/opt/airflow/data/raw"))

ENTIDADES = ["clientes", "corretores", "apolices", "coberturas", "sinistros", "pagamentos"]

@dag(
    dag_id = "ingestao_raw",
    description = "Carrega os parquet da raw zone para o schema raw do warehouse.",
    start_date = datetime(2024, 1, 1),
    schedule = "@daily",
    catchup = False,
    tags = ["fase2", "ingestao", "raw"],
)

def ingestao_raw():

    @task
    def criar_schema_raw() -> None:
        hook = PostgresHook(postgres_conn_id = "warehouse")
        hook.run("CREATE SCHEMA IF NOT EXISTS raw;")

    @task
    def carregar_entidade(nome: str) -> dict:
        caminho = RAW_DIR / f"{nome}.parquet"
        df = pd.read_parquet(caminho)

        hook = PostgresHook(postgres_conn_id = "warehouse")
        engine = hook.get_sqlalchemy_engine()

        df.to_sql(nome, engine, schema="raw", if_exists="replace", index=False)

        return {"entidade": nome, "linhas": len(df)}
    
    schema = criar_schema_raw()
    for entidade in ENTIDADES:
        carga = carregar_entidade.override(task_id=f"carregar_{entidade}")(entidade)
        schema >> carga

ingestao_raw()
