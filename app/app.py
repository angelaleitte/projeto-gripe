import os

import dash
import dash_bootstrap_components as dbc
from dash import html
from sqlalchemy import create_engine, text

# --- Conexão com o banco (lida da variável de ambiente DATABASE_URL) ---
DATABASE_URL = os.environ.get("DATABASE_URL")
engine = create_engine(DATABASE_URL, pool_pre_ping=True) if DATABASE_URL else None


def testar_conexao():
    if engine is None:
        return "DATABASE_URL não configurada."
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return "Conexão com o MySQL: OK ✅"
    except Exception as e:
        return f"Erro ao conectar no MySQL: {e}"


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
server = app.server  # necessário para o gunicorn (app:server)

app.layout = dbc.Container(
    [
        html.H1("Projeto SRAG — Painel de Vigilância", className="mt-4"),
        html.P("Dashboard em construção. Este é o esqueleto inicial do deploy."),
        dbc.Alert(testar_conexao(), color="info"),
    ],
    fluid=True,
)

if __name__ == "__main__":
    # Modo dev local (sem gunicorn) — NÃO usar isso em produção no Coolify
    app.run(host="0.0.0.0", port=8050, debug=True)
