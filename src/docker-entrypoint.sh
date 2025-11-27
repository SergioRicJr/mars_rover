#!/bin/bash
set -e

# Executa migrations do Alembic
echo "Executando migrations do Alembic..."
cd /workspace/src
poetry run alembic upgrade head
echo "Migrations concluídas!"

# Inicia a aplicação
exec "$@"
