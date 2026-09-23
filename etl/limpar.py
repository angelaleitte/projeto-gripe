"""Limpeza e transformação das linhas brutas do CSV do SRAG.

Recebe as linhas cruas de extrair.py (dicts com as ~194 colunas originais,
tudo string) e devolve registros já no formato das tabelas de schema.py.
"""

import logging
from datetime import date, datetime

CAMPOS_DATA = ["DT_NOTIFIC", "DT_SIN_PRI", "DT_NASC", "DT_INTERNA",
               "DT_ENTUTI", "DT_SAIDUTI", "DT_EVOLUCA"]
CAMPOS_TEXTO = ["SEM_NOT", "SEM_PRI", "SG_UF_NOT", "CS_SEXO", "TP_IDADE",
                "CS_GESTANT", "CS_RACA", "FEBRE", "TOSSE", "GARGANTA",
                "DISPNEIA", "DESC_RESP", "SATURACAO", "DIARREIA",
                "VOMITO", "CARDIOPATI", "DIABETES", "ASMA", "OBESIDADE",
                "RENAL", "IMUNODEPRE", "VACINA", "VACINA_COV",
                "HOSPITAL", "UTI", "CLASSI_FIN", "EVOLUCAO"]


def parse_data(valor: str) -> date | None:
    """'2026-01-14T00:00:00.000Z' -> date(2026, 1, 14). Vazio -> None."""
    if not valor:
        return None
    return datetime.strptime(valor[:10], "%Y-%m-%d").date()


def parse_int(valor: str) -> int | None:
    return int(valor) if valor else None


def vazio_para_none(valor: str) -> str | None:
    return valor if valor else None


def montar_registro_notificacao(linha: dict) -> dict:
    registro = {"nu_notific": linha["NU_NOTIFIC"], "id_municip": linha["CO_MUN_NOT"]}
    for campo in CAMPOS_DATA:
        registro[campo.lower()] = parse_data(linha.get(campo, ""))
    for campo in CAMPOS_TEXTO:
        registro[campo.lower()] = vazio_para_none(linha.get(campo, ""))
    registro["nu_idade_n"] = parse_int(linha.get("NU_IDADE_N", ""))
    return registro


def montar_registro_municipio(linha: dict) -> dict:
    return {
        "id_municip": linha["CO_MUN_NOT"],
        "sg_uf": linha["SG_UF_NOT"],
        "nome_municipio": linha["ID_MUNICIP"],
    }


def limpar_registros(linhas: list[dict]) -> tuple[list[dict], list[dict]]:
    """Linhas brutas -> (registros de notificacao, registros de dim_municipio)."""
    logging.info(f"Início da limpeza: {len(linhas)} linhas recebidas")

    registros_notif = [montar_registro_notificacao(l) for l in linhas]
    # dedup por id_municip (várias notificações podem ser do mesmo município)
    municipios_por_codigo = {
        l["CO_MUN_NOT"]: montar_registro_municipio(l) for l in linhas
    }
    municipios = list(municipios_por_codigo.values())

    logging.info(
        f"Fim da limpeza: {len(registros_notif)} notificações e "
        f"{len(municipios)} municípios (após dedup) prontos para carga"
    )
    return registros_notif, municipios
