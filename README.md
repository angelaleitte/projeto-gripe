# Projeto SRAG — Vigilância de Síndrome Respiratória Aguda Grave

Pipeline completo (Engenharia de Dados → Ciência de Dados → Machine Learning
→ IA/Automação) construído sobre dados públicos reais do SIVEP-Gripe (SRAG),
com dashboard interativo e atualização semanal automatizada.

> Projeto de portfólio documentado publicamente no LinkedIn, dia a dia,
> como parte de um plano de 34 dias.

## Fonte de dados

- **Dataset**: SRAG 2019 a 2026 (`INFLUD26`), recurso "Banco vivo" atualizado
  semanalmente — [dadosabertos.saude.gov.br](https://dadosabertos.saude.gov.br)
- Complementar: [InfoGripe (Fiocruz)](https://gitlab.procc.fiocruz.br/mave/repo)

## Stack

| Camada | Tecnologia |
|---|---|
| Linguagem | Python 3.11 |
| Dados | pandas, pyarrow |
| Banco de dados | MySQL 8 |
| Dashboard | Dash + Plotly + Dash Bootstrap Components |
| Machine Learning | scikit-learn, XGBoost, SHAP |
| IA/Automação | OpenAI Agents SDK |
| Infraestrutura | Docker Compose, deploy via Coolify |
| Servidor de produção | Gunicorn |

## Estrutura do repositório

```
.
├── docker-compose.yml   # MySQL + app + adminer
├── app/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py            # Dashboard Dash
├── .env.example          # Modelo de variáveis de ambiente (não commitar .env real)
└── INSTRUCOES.md          # Guia de deploy no Coolify
```

## Como rodar localmente (desenvolvimento)

```bash
cp .env.example .env
# edite o .env com senhas locais de teste
docker compose up --build
```

Acesse `http://localhost:8050`.

## Deploy em produção

Ver [`INSTRUCOES.md`](./INSTRUCOES.md) para o passo a passo completo de
deploy via Coolify, incluindo configuração de domínio e SSL.

## Roadmap do projeto

- **Semana 1** — Engenharia de Dados (limpeza, decodificação, tratamento de
  inconsistências)
- **Semana 2** — Ciência de Dados (análise exploratória, estatística, mapa
  coroplético, dashboard)
- **Semana 3** — Machine Learning (classificação, regressão, clusterização)
- **Semana 4** — IA/Automação (pipeline completo com LLM gerando boletins)

## Licença

A definir.
