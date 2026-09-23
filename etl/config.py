"""Configuração de conexão com o banco (Semana 1 — Engenharia de Dados).

A string de conexão vem da variável de ambiente DATABASE_URL (lida de um
arquivo .env local, nunca versionado — ver .env.example na raiz do repo).

Banco compartilhado (mesmo usado pelo app do dashboard): MySQL "projDados",
provisionado no Coolify. Peça host/usuário/senha atuais se não tiver — não
deixe hardcoded aqui.

Também centraliza a configuração de logging do pipeline: os outros módulos
só precisam `import logging` e usar `logging.info(...)` / `logging.error(...)`
— o basicConfig abaixo já vale pro processo inteiro a partir do momento em
que config.py é importado (é sempre o primeiro import, direto ou indireto,
de qualquer script do pipeline).
"""

import logging
import os

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    filename="pipeline.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8",
)

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL não definida. Copie .env.example para .env na raiz do "
        "repositório e preencha com a string de conexão real "
        "(mysql+pymysql://usuario:senha@host:porta/projDados)."
    )
