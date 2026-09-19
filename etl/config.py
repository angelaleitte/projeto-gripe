"""Configuração de conexão com o banco (Semana 1 — Engenharia de Dados).

A string de conexão vem da variável de ambiente DATABASE_URL (lida de um
arquivo .env local, nunca versionado — ver .env.example na raiz do repo).

Banco compartilhado (mesmo usado pelo app do dashboard): MySQL "projDados",
provisionado no Coolify. Peça host/usuário/senha atuais se não tiver — não
deixe hardcoded aqui.
"""

import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL não definida. Copie .env.example para .env na raiz do "
        "repositório e preencha com a string de conexão real "
        "(mysql+pymysql://usuario:senha@host:porta/projDados)."
    )
