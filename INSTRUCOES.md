# Guia de Deploy — Projeto SRAG no Coolify

## Ponto de atenção importante ⚠️

Você escolheu colar o `docker-compose.yml` direto no Coolify (sem repositório
Git). Isso funciona bem para o **MySQL** e o **Adminer**, porque usam imagens
prontas do Docker Hub.

Mas o serviço **`app`** (Python/Dash) usa `build: context: ./app` — ou seja,
o Coolify precisa achar uma pasta `app/` com `Dockerfile`, `requirements.txt`
e `app.py` dentro, no mesmo lugar onde ele guarda o compose no servidor.

Você tem duas opções:

### Opção A (recomendada): criar um repositório Git rapidinho
Mesmo sem querer usar Git como "workflow" do projeto, um repositório privado
grátis no GitHub só para guardar `app/` resolve isso em 2 minutos e o Coolify
faz o build sozinho a cada deploy. Aí no compose você trocaria:
```yaml
build:
  context: ./app
```
por apontar o serviço para o repo (o Coolify tem um campo específico pra isso
quando você adiciona o "Resource" como Docker Compose + Git).

### Opção B: usar o gerenciador de arquivos do Coolify
Versões recentes do Coolify têm uma aba **"Storage" / "Files"** dentro do
recurso Docker Compose, onde dá pra criar/colar arquivos direto pela
interface web, sem Git. Nesse caso:
1. Crie o recurso "Docker Compose" no Coolify e cole o `docker-compose.yml`.
2. Na aba de arquivos do recurso, crie a pasta `app/` e cole dentro:
   `Dockerfile`, `requirements.txt`, `app.py` (conteúdo abaixo).
3. Deploy.

Se seu Coolify não tiver essa aba disponível, a Opção A é o caminho mais
simples.

---

## Passo a passo no painel do Coolify

1. **Acesse o painel** do Coolify no seu VPS (a URL que você configurou pra
   ele — geralmente algo como `https://SEU-DOMINIO:8000` ou um subdomínio).

2. **Crie um novo Project** (ou use um existente) → **New Resource** →
   **Docker Compose** (não escolha "Application" nem "Database" avulsos —
   escolha a opção de colar/gerenciar um compose completo).

3. **Cole o conteúdo de `docker-compose.yml`** (arquivo anexo).

4. **Configure as variáveis de ambiente** (aba "Environment Variables" do
   recurso) — NUNCA deixe hardcoded no compose:
   - `MYSQL_ROOT_PASSWORD` → gere uma senha forte
   - `MYSQL_PASSWORD` → gere outra senha forte (diferente da root)

5. **Resolva o build do `app/`** conforme Opção A ou B acima.

6. **Domínio (`dados.angelaleite.com`)**:
   - No seu provedor de DNS, crie um registro **CNAME** ou **A** apontando
     `dados.angelaleite.com` → `76.13.168.152` (IP do seu VPS).
   - O compose já tem os labels do Traefik configurados para esse domínio
     e SSL automático via Let's Encrypt (`certresolver=letsencrypt`) — o
     Coolify deve reconhecer isso automaticamente. Se o Coolify tiver um
     campo próprio de "Domains" na UI para o serviço `app`, prefira
     configurar por lá (mais confiável que labels manuais) e pode remover
     os labels do Traefik do compose.

7. **Deploy.** Acompanhe os logs de build — a primeira build do MySQL +
   app deve levar alguns minutos.

8. **Teste**: acesse `https://dados.angelaleite.com` — deve aparecer a
   página inicial do Dash com "Conexão com o MySQL: OK ✅".

---

## Depois que estiver no ar

- **Swap file**: se ainda não tiver, adicione 2-4GB de swap no VPS (via
  SSH, com uma senha nova — não reaproveite a que foi exposta no chat):
  ```bash
  fallocate -l 4G /swapfile
  chmod 600 /swapfile
  mkswap /swapfile
  swapon /swapfile
  echo '/swapfile none swap sw 0 0' >> /etc/fstab
  ```

- **Monitorar recursos**: depois de 1-2 dias rodando, vale checar de novo
  o uso de RAM/CPU do VPS pra confirmar que está estável (posso puxar essas
  métricas de novo quando quiser).

- **Semana 3 (ML) e Semana 4 (Agents SDK/OpenAI)**: quando chegar lá, adicione
  as libs comentadas no `requirements.txt` e a variável `OPENAI_API_KEY` como
  environment variable no Coolify (nunca no código).
