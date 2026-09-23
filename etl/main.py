"""Ponto de entrada do pipeline de carga (Semana 1): extrai -> limpa -> carrega.

Roda com `python main.py` de dentro de etl/. Log completo em pipeline.log
(configurado em config.py, importado indiretamente via carregar.py).
"""

import logging

from carregar import criar_tabelas, upsert
from extrair import ler_amostra
from limpar import limpar_registros
from schema import dim_municipio, notificacao


def main():
    logging.info("Pipeline iniciado")

    criar_tabelas()

    linhas = ler_amostra()
    registros_notif, municipios = limpar_registros(linhas)

    n_ins_mun, n_upd_mun = upsert(dim_municipio, municipios)
    n_ins_notif, n_upd_notif = upsert(notificacao, registros_notif)

    n_inseridos = n_ins_mun + n_ins_notif
    n_atualizados = n_upd_mun + n_upd_notif
    logging.info(f"Pipeline concluído: {n_inseridos} inseridos, {n_atualizados} atualizados")


if __name__ == "__main__":
    main()
