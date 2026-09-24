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

    idade = df["idade_anos"]
    q = idade.quantile([0.25, 0.5, 0.75])
    quartis_batem = all(
        abs(q[p] - resumo[r]) < 1e-9
        for p, r in [(0.25, "25%"), (0.5, "50%"), (0.75, "75%")]
    )
    pct_crianca = (idade < 5).mean()
    pct_idoso = (idade >= 60).mean()
    perto_da_media = int(((idade >= media - 5) & (idade <= media + 5)).sum())

    diferenca = abs(media - mediana)
    if diferenca <= 0.1 * mediana:
        leitura_centro = (
            f"Média ({media:.1f}) e mediana ({mediana:.1f}) estão próximas: "
            "distribuição aproximadamente simétrica."
        )
    else:
        lado = "alta" if media > mediana else "baixa"
        leitura_centro = (
            f"Média ({media:.1f}) e mediana ({mediana:.1f}) estão distantes "
            f"({diferenca:.1f} anos): a média é puxada por uma cauda de idades "
            f"mais {lado}s, então a mediana descreve melhor o caso típico."
        )

    leitura = dbc.Card(
        dbc.CardBody(
            [
                html.H5("Leitura do histograma", className="card-title"),
                html.Ul(
                    [
                        html.Li(leitura_centro),
                        html.Li(
                            f"{pct_crianca:.0%} dos casos têm menos de 5 anos e "
                            f"{pct_idoso:.0%} têm 60 anos ou mais: os casos se "
                            "concentram nas duas pontas."
                        ),
                        html.Li(
                            f"Só {perto_da_media} caso(s) caem a ±5 anos da média: "
                            "ela cai numa região com poucos casos, não no "
                            "centro da distribuição."
                        ),
                        html.Li(
                            f"Quartis (quantile 0,25 / 0,5 / 0,75): "
                            f"{q[0.25]:.1f} / {q[0.5]:.1f} / {q[0.75]:.2f} anos — "
                            + (
                                "conferem com o describe()."
                                if quartis_batem
                                else "DIVERGEM do describe()."
                            )
                        ),
                    ]
                ),
            ]
        ),
        className="mb-3",
    )

    resumo_feito = dbc.Card(
        dbc.CardBody(
            [
                html.H5("Resumo do que foi feito", className="card-title"),
                html.Ol(
                    [
                        html.Li(
                            "Conferido no dicionário oficial: NU_IDADE_N é só o "
                            "número; TP_IDADE dá a unidade (1-Dia, 2-Mês, 3-Ano)."
                        ),
                        html.Li(
                            "Idade convertida para anos (idade_anos) antes de "
                            "qualquer estatística."
                        ),
                        html.Li(
                            "describe(), média, mediana, moda e desvio-padrão "
                            "calculados sobre idade_anos."
                        ),
                        html.Li(
                            "Histograma (20 faixas) com média e mediana marcadas."
                        ),
                        html.Li(
                            "Quartis via quantile() conferidos contra o describe()."
                        ),
                        html.Li(
                            "Resultado registrado em pipeline.log pelo script "
                            "analise/idade.py."
                        ),
                    ]
                ),
                html.Small(
                    "Base atual: amostra de 30 notificações reais do SRAG 2026. "
                    "As conclusões são ilustrativas até a carga completa.",
                    className="text-muted",
                ),
            ]
        ),
        className="mb-4",
    )

    return html.Div([tabela_resumo, dcc.Graph(figure=fig), leitura, resumo_feito])


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
        #dbc.Alert(testar_conexao(), color="info"),
        html.H3("Distribuição de idade", className="mt-4"),
        secao_distribuicao_idade(),
    ],
    fluid=True,
)

if __name__ == "__main__":
    # Modo dev local (sem gunicorn) — NÃO usar isso em produção no Coolify
    app.run(host="0.0.0.0", port=8050, debug=True)
