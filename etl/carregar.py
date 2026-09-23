"""Carga no banco (Semana 1): criação das tabelas e upsert genérico.

Não sabe nada do formato do CSV do SRAG — recebe registros já limpos
(ver limpar.py) e uma Table do schema.py, e faz
INSERT ... ON DUPLICATE KEY UPDATE (upsert nativo do MySQL).
"""

import logging

from sqlalchemy import create_engine, select
from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlalchemy.exc import SQLAlchemyError

from config import DATABASE_URL
from schema import metadata

engine = create_engine(DATABASE_URL, pool_pre_ping=True)


def criar_tabelas():
    try:
        metadata.create_all(engine)
    except SQLAlchemyError as e:
        logging.error(f"Falha ao conectar/criar tabelas no MySQL: {e}")
        raise
    logging.info(f"Tabelas verificadas/criadas: {list(metadata.tables.keys())}")


def upsert(tabela, registros: list[dict]) -> tuple[int, int]:
    """Insere/atualiza `registros` em `tabela`. Retorna (n_inseridos, n_atualizados)."""
    if not registros:
        return 0, 0

    pk_col = next(c for c in tabela.columns if c.primary_key)
    chaves = [r[pk_col.name] for r in registros]

    try:
        with engine.begin() as conn:
            existentes = {
                row[0]
                for row in conn.execute(select(pk_col).where(pk_col.in_(chaves)))
            }
            stmt = mysql_insert(tabela).values(registros)
            colunas_update = {
                c.name: stmt.inserted[c.name]
                for c in tabela.columns
                if not c.primary_key
            }
            stmt = stmt.on_duplicate_key_update(**colunas_update)
            conn.execute(stmt)
    except SQLAlchemyError as e:
        logging.error(f"Falha no upsert de '{tabela.name}': {e}")
        raise

    n_atualizados = len(existentes)
    n_inseridos = len(registros) - n_atualizados
    logging.info(
        f"{tabela.name}: upsert de {len(registros)} registros "
        f"({n_inseridos} inseridos, {n_atualizados} atualizados)"
    )
    return n_inseridos, n_atualizados


if __name__ == "__main__":
    criar_tabelas()
