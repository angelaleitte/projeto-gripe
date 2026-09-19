"""Schema do banco (Semana 1, Dias 1-3 do plano) — SQLAlchemy Core.

Nomes de campo, tipos e domínios de valores confirmados no dicionário de
dados oficial do SIVEP-Gripe (Ministério da Saúde, versão 25/05/2023,
"dicionario-de-dados-2019-a-2025.pdf", baixado de
https://dadosabertos.saude.gov.br/dataset/srag-2019-a-2026).
Cópia local em MATERIAIS/dicionario/ (fora do repositório Git — não
versionada, só referência).

`notificacao` NÃO modela as ~194 colunas do dataset bruto — é um subconjunto
curado com os campos usados ao longo do plano de 34 dias (identificação,
localização, sintomas/comorbidades principais, vacinação, internação/UTI e
desfecho). Dá pra ampliar depois, coluna a coluna, sempre conferindo o nome
real no dicionário.

Desvios de tipo em relação ao dicionário (documentados aqui de propósito):
- nu_idade_n: o dicionário declara Varchar2(3), mas é um valor numérico
  (idade) usado em contas/agregações nas Semanas 2 e 3 do plano — modelado
  como Integer. Combinado com tp_idade (dia/mês/ano) pra interpretar certo.
"""

from sqlalchemy import Column, Date, Integer, MetaData, String, Table

metadata = MetaData()

# --- Tabela fato: uma notificação de SRAG por linha -----------------------
notificacao = Table(
    "notificacao",
    metadata,
    # Identificação / tempo
    Column("nu_notific", String(12), primary_key=True),  # NU_NOTIFIC
    Column("dt_notific", Date),  # DT_NOTIFIC
    Column("sem_not", String(6)),  # SEM_NOT
    Column("dt_sin_pri", Date),  # DT_SIN_PRI — data dos primeiros sintomas
    Column("sem_pri", String(6)),  # SEM_PRI
    # Localização (notificação)
    Column("sg_uf_not", String(2)),  # SG_UF_NOT
    Column(
        "id_municip", String(6), index=True
    ),  # ID_MUNICIP (alias CO_MUN_NOT) — FK lógica p/ dim_municipio
    # Demográficos
    Column("cs_sexo", String(1)),  # CS_SEXO — 1-M / 2-F / 9-Ignorado
    Column("dt_nasc", Date),  # DT_NASC
    Column("nu_idade_n", Integer),  # NU_IDADE_N — ver nota de desvio acima
    Column("tp_idade", String(1)),  # TP_IDADE — 1-Dia / 2-Mês / 3-Ano
    Column("cs_gestant", String(1)),  # CS_GESTANT
    Column("cs_raca", String(2)),  # CS_RACA
    # Sintomas (subconjunto — campo 34 do dicionário)
    Column("febre", String(1)),  # FEBRE
    Column("tosse", String(1)),  # TOSSE
    Column("garganta", String(1)),  # GARGANTA
    Column("dispneia", String(1)),  # DISPNEIA
    Column("desc_resp", String(1)),  # DESC_RESP
    Column("saturacao", String(1)),  # SATURACAO
    Column("diarreia", String(1)),  # DIARREIA
    Column("vomito", String(1)),  # VOMITO
    # Comorbidades (subconjunto — campo 35 do dicionário)
    Column("cardiopati", String(1)),  # CARDIOPATI
    Column("diabetes", String(1)),  # DIABETES
    Column("asma", String(1)),  # ASMA
    Column("obesidade", String(1)),  # OBESIDADE
    Column("renal", String(1)),  # RENAL
    Column("imunodepre", String(1)),  # IMUNODEPRE
    # Vacinação
    Column("vacina", String(1)),  # VACINA — vacina de gripe (campo 40)
    Column("vacina_cov", String(1)),  # VACINA_COV — vacina covid-19 (campo 36)
    # Internação / UTI
    Column("hospital", String(1)),  # HOSPITAL — houve internação?
    Column("dt_interna", Date),  # DT_INTERNA
    Column("uti", String(1)),  # UTI — internado em UTI?
    Column("dt_entuti", Date),  # DT_ENTUTI
    Column("dt_saiduti", Date),  # DT_SAIDUTI
    # Classificação / desfecho
    Column("classi_fin", String(1)),  # CLASSI_FIN — 1 a 5 (ver dicionário)
    Column("evolucao", String(1)),  # EVOLUCAO — 1-Cura / 2-Óbito / 9-Ignorado
    Column("dt_evoluca", Date),  # DT_EVOLUCA — data de alta ou óbito
)

# --- Dimensão: município ----------------------------------------------------
# id_municip / sg_uf vêm do próprio dicionário SIVEP-Gripe (campo 4 — código
# IBGE do município de notificação). nome_municipio NÃO está no dicionário
# do SIVEP (que só traz o código) — precisa ser populado a partir da tabela
# oficial de municípios do IBGE (ex: servicodados.ibge.gov.br/api/v1/localidades)
# antes de usar em relatórios/gráficos.
dim_municipio = Table(
    "dim_municipio",
    metadata,
    Column("id_municip", String(6), primary_key=True),  # ID_MUNICIP (IBGE)
    Column("sg_uf", String(2)),  # UF do município (padrão IBGE)
    Column("nome_municipio", String(100)),  # fonte: tabela IBGE, não o SIVEP
)
