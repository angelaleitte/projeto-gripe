"""Ponto de entrada do pipeline de carga (Semana 1).

Por enquanto só cria a estrutura das tabelas no banco (Dias 1-3 do plano).
A carga dos dados reais do INFLUD26 entra nos próximos dias (limpeza,
decodificação, tratamento de inconsistências — Dias 3-7).
"""

from sqlalchemy import create_engine

from config import DATABASE_URL
from schema import metadata

engine = create_engine(DATABASE_URL, pool_pre_ping=True)


if __name__ == "__main__":
    metadata.create_all(engine)
    print("Tabelas criadas com sucesso:", list(metadata.tables.keys()))
