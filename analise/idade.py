"""Análise exploratória: distribuição de idade dos casos de SRAG (Semana 2).

NU_IDADE_N é só o valor numérico da idade — a unidade vem de TP_IDADE
(dicionário oficial SIVEP-Gripe): 1-Dia, 2-Mês, 3-Ano. Sem converter pela
unidade, idade_anos misturaria bebês de "5 dias" com pacientes de "5 anos"
sob o mesmo número 5 — por isso toda estatística aqui parte de idade_anos
(sempre em anos), nunca de nu_idade_n bruto.

Reaproveita a engine/config de etl/carregar.py (mesma conexão MySQL usada
na carga) em vez de duplicar a lógica de conexão aqui.
"""

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "etl"))

import pandas as pd

from carregar import engine

# Fator de conversão de nu_idade_n para anos, conforme TP_IDADE
TP_IDADE_PARA_ANOS = {
    "1": 1 / 365,  # 1-Dia
    "2": 1 / 12,  # 2-Mês
    "3": 1,  # 3-Ano
}


def carregar_idades() -> pd.DataFrame:
    df = pd.read_sql(
        "SELECT nu_notific, nu_idade_n, tp_idade FROM notificacao", engine
    )
    fator = df["tp_idade"].map(TP_IDADE_PARA_ANOS)
    df["idade_anos"] = df["nu_idade_n"] * fator
    return df


if __name__ == "__main__":
    df = carregar_idades()

    total = len(df)
    sem_idade = int(df["idade_anos"].isna().sum())
    if sem_idade:
        print(
            f"{sem_idade} de {total} registros sem nu_idade_n/tp_idade "
            "válidos (fora das estatísticas abaixo)"
        )

    print(df["idade_anos"].describe())
    print()

    media = df["idade_anos"].mean()
    mediana = df["idade_anos"].median()
    moda = df["idade_anos"].mode().iloc[0]
    desvio = df["idade_anos"].std()

    print(f"média:         {media:.2f}")
    print(f"mediana:       {mediana:.2f}")
    print(f"moda:          {moda:.2f}")
    print(f"desvio-padrão: {desvio:.2f}")
    print()

    diferenca = abs(media - mediana)
    if diferenca > 0.1 * mediana:
        print(
            f"Média e mediana distantes ({diferenca:.2f} anos de diferença) "
            "-> distribuição assimétrica (uma cauda de idades puxa a média "
            "para longe do valor central)."
        )
    else:
        print(
            f"Média e mediana próximas ({diferenca:.2f} anos de diferença) "
            "-> distribuição aproximadamente simétrica em torno do centro."
        )

    # Quartis calculados de forma independente, para conferir com o describe()
    quartis = df["idade_anos"].quantile([0.25, 0.5, 0.75])
    resumo = df["idade_anos"].describe()
    bate = (
        abs(quartis[0.25] - resumo["25%"]) < 1e-9
        and abs(quartis[0.5] - resumo["50%"]) < 1e-9
        and abs(quartis[0.75] - resumo["75%"]) < 1e-9
    )
    print("quantile([0.25, 0.5, 0.75]):")
    print(quartis.to_string())
    print(f"Bate com o describe()? {'sim' if bate else 'NÃO'}")

    # Histograma (backend sem janela: só salva o arquivo)
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ax = df["idade_anos"].hist(bins=20, edgecolor="white")
    ax.axvline(media, color="red", linestyle="--", label=f"média = {media:.1f}")
    ax.axvline(mediana, color="green", linestyle=":", label=f"mediana = {mediana:.1f}")
    ax.set_title("Distribuição de idade dos casos de SRAG")
    ax.set_xlabel("Idade (anos)")
    ax.set_ylabel("Nº de casos")
    ax.legend()
    png = Path(__file__).resolve().parent / "histograma_idade.png"
    ax.figure.savefig(png, dpi=120, bbox_inches="tight")
    print(f"\nHistograma salvo em {png}")

    saida = Path(__file__).resolve().parent / "estatisticas_idade.json"
    saida.write_text(
        json.dumps(
            {"media": media, "mediana": mediana, "moda": moda, "desvio_padrao": desvio},
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Estatísticas salvas em {saida}")

    # config.py (importado via carregar.py) já configurou o logging -> pipeline.log
    logging.info(
        f"Análise de idade: n={int(resumo['count'])}, média={media:.2f}, "
        f"mediana={mediana:.2f}, moda={moda:.2f}, desvio={desvio:.2f}, "
        f"quartis={quartis.round(2).tolist()} (bate com describe: {bate})"
    )
