"""Extração dos dados brutos do SRAG.

Por enquanto lê a amostra local (etl/amostra/amostra_srag.csv, 30 registros
reais extraídos do arquivo oficial 2026 — ver nota em carregar_amostra.py
do histórico do repo). Quando o pipeline avançar para o arquivo completo
(INFLUD26, ~237MB, "Banco vivo" em dadosabertos.saude.gov.br), este módulo
passa a baixar o CSV oficial — a função ler_amostra() abaixo já isola essa
fronteira do resto do pipeline (limpar.py e carregar.py não sabem de onde
as linhas vieram).
"""

import csv
import logging

AMOSTRA_CSV = "amostra/amostra_srag.csv"


def ler_amostra(caminho: str = AMOSTRA_CSV) -> list[dict]:
    logging.info(f"Início da extração: lendo {caminho}")
    with open(caminho, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";", quotechar='"')
        linhas = list(reader)
    logging.info(f"Fim da extração: {len(linhas)} linhas lidas de {caminho}")
    return linhas
