FROM python:3.11-slim

WORKDIR /app

# Dependências de sistema mínimas (necessárias para mysqlclient/pyarrow, se usado)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8050

# gunicorn serve o Dash em produção (não use o servidor de dev do Dash aqui)
CMD ["gunicorn", "--bind", "0.0.0.0:8050", "--workers", "2", "--timeout", "120", "app:server"]
