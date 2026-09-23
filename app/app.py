import os

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import dcc, html
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


# --- Distribuição de idade (Semana 2 — Ciência de Dados) -------------------
# NU_IDADE_N é só o valor numérico da idade — a unidade vem de TP_IDADE
# (dicionário oficial SIVEP-Gripe): 1-Dia, 2-Mês, 3-Ano. Sem converter pela
# unidade, idade_anos misturaria bebês de "5 dias" com pacientes de "5 anos"
# sob o mesmo número 5, então toda estatística aqui parte de idade_anos.
TP_IDADE_PARA_ANOS = {"1": 1 / 365, "2": 1 / 12, "3": 1}


def carregar_idades() -> pd.DataFrame:
    df = pd.read_sql(
        "SELECT nu_notific, nu_idade_n, tp_idade FROM notificacao", engine
    )
    fator = df["tp_idade"].map(TP_IDADE_PARA_ANOS)
    df["idade_anos"] = df["nu_idade_n"] * fator
    return df.dropna(subset=["idade_anos"])


def secao_distribuicao_idade():
    if engine is None:
        return dbc.Alert("DATABASE_URL não configurada.", color="warning")
    try:
        df = carregar_idades()
    except Exception as e:
        return dbc.Alert(f"Erro ao carregar dados de idade: {e}", color="danger")

    if df.empty:
        return dbc.Alert("Nenhum registro com idade válida ainda.", color="warning")

    resumo = df["idade_anos"].describe()
    media, mediana, desvio = resumo["mean"], resumo["50%"], resumo["std"]

    tabela_resumo = dbc.Table(
        [
            html.Thead(
                html.Tr(
                    [
                        html.Th(c)
                        for c in ["n", "média", "mediana", "desvio-padrão", "mín", "máx"]
                    ]
                )
            ),
            html.Tbody(
                html.Tr(
                    [
                        html.Td(f"{int(resumo['count'])}"),
                        html.Td(f"{media:.1f}"),
                        html.Td(f"{mediana:.1f}"),
                        html.Td(f"{desvio:.1f}"),
                        html.Td(f"{resumo['min']:.0f}"),
                        html.Td(f"{resumo['max']:.0f}"),
                    ]
                )
            ),
        ],
        bordered=True,
        size="sm",
        className="mt-2",
    )

    fig = px.histogram(
        df,
        x="idade_anos",
        nbins=20,
        labels={"idade_anos": "Idade (anos)"},
        title="Distribuição de idade dos casos de SRAG",
    )
    fig.add_vline(x=media, line_dash="dash", line_color="red", annotation_text="média")
    fig.add_vline(
        x=mediana, line_dash="dot", line_color="green", annotation_text="mediana"
    )

    return html.Div([tabela_resumo, dcc.Graph(figure=fig)])


app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY],
    url_base_pathname="/gripe/",
)
server = app.server  # necessário para o gunicorn (app:server)

app.layout = dbc.Container(
    [
        html.H1("Projeto SRAG — Painel de Vigilância", className="mt-4"),
        html.P("Dashboard em construção. Este é o esqueleto inicial do deploy."),
        dbc.Alert(testar_conexao(), color="info"),
        html.H3("Distribuição de idade", className="mt-4"),
        secao_distribuicao_idade(),
    ],
    fluid=True,
)

if __name__ == "__main__":
    # Modo dev local (sem gunicorn) — NÃO usar isso em produção no Coolify
    app.run(host="0.0.0.0", port=8050, debug=True)
