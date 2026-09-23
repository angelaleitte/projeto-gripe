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

    saida = Path(__file__).resolve().parent / "estatisticas_idade.json"
    saida.write_text(
        json.dumps(
            {"media": media, "mediana": mediana, "moda": moda, "desvio_padrao": desvio},
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"\nEstatísticas salvas em {saida} (para o histograma de amanhã)")
