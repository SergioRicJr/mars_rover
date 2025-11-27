# Como as Migrations são Aplicadas no Docker Compose

## Fluxo de Execução

Quando você executa `docker-compose up`, o seguinte processo acontece:

### 1. Inicialização dos Serviços

```yaml
services:
  db:          # PostgreSQL inicia primeiro
  api:         # API aguarda o banco estar saudável (healthcheck)
```

### 2. Healthcheck do Banco de Dados

O serviço `db` tem um healthcheck que verifica se o PostgreSQL está pronto:

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres"]
  interval: 10s
  timeout: 5s
  retries: 5
```

O serviço `api` só inicia **depois** que o banco está saudável:

```yaml
depends_on:
  db:
    condition: service_healthy
```

### 3. Entrypoint do Container API

Quando o container `api` inicia, o `docker-entrypoint.sh` é executado:

```bash
#!/bin/bash
# 1. Verifica se USE_POSTGRES=true
# 2. Aguarda o banco estar pronto (verificação adicional)
# 3. Executa: poetry run alembic upgrade head
# 4. Inicia a aplicação: uvicorn main:app
```

### 4. Execução das Migrations

O Alembic executa automaticamente:

```bash
cd /workspace/src
poetry run alembic upgrade head
```

Isso aplica **todas as migrations pendentes** no banco de dados.

## Comportamento

### Primeira Execução

1. Banco de dados inicia vazio
2. API aguarda banco estar pronto
3. Entrypoint executa `alembic upgrade head`
4. Migration `001_initial_migration_create_rovers_table.py` é aplicada
5. Tabela `rovers` é criada
6. API inicia normalmente

### Execuções Subsequentes

1. Banco de dados já tem as tabelas
2. API aguarda banco estar pronto
3. Entrypoint executa `alembic upgrade head`
4. Alembic verifica que não há migrations pendentes
5. API inicia normalmente

### Com Novas Migrations

1. Você adiciona uma nova migration em `alembic/versions/`
2. Ao fazer `docker-compose up`, o entrypoint detecta a nova migration
3. Alembic aplica automaticamente a nova migration
4. API inicia com o schema atualizado

## Logs

Você verá nos logs do container `api`:

```
Aguardando banco de dados estar pronto (db:5432)...
Banco de dados está pronto!
Executando migrations do Alembic...
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 001, Initial migration: create rovers table
✓ Migrations aplicadas com sucesso!
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## Execução Manual (Opcional)

Se precisar executar migrations manualmente dentro do container:

```bash
# Entrar no container
docker-compose exec api bash

# Executar migrations manualmente
cd /workspace/src
poetry run alembic upgrade head

# Ver status
poetry run alembic current

# Ver histórico
poetry run alembic history
```

## Troubleshooting

### Migrations não são aplicadas

1. Verifique se `USE_POSTGRES=true` está definido
2. Verifique os logs do container: `docker-compose logs api`
3. Verifique se o banco está acessível: `docker-compose exec api nc -z db 5432`

### Erro de conexão

O entrypoint aguarda até 30 tentativas (60 segundos). Se o banco demorar mais, verifique:
- Healthcheck do banco está funcionando?
- `depends_on` está configurado corretamente?

### Migrations já aplicadas

O Alembic mantém um registro na tabela `alembic_version`. Se precisar resetar:

```bash
docker-compose exec api poetry run alembic downgrade base
docker-compose exec api poetry run alembic upgrade head
```

**⚠️ CUIDADO**: Isso apagará todas as tabelas!

