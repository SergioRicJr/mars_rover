# Dockerfile para Mars Rover API
FROM python:3.11-slim

# Metadata
LABEL maintainer="Sergio Nascimento <sergioricjr7@gmail.com>"
LABEL description="API para controlar sondas exploradoras em Marte"

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.3 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

# Adiciona poetry ao PATH
ENV PATH="$POETRY_HOME/bin:$PATH"

# Instala dependências do sistema
RUN apt-get -y update && \
    apt-get install -y --no-install-recommends wget && \
    rm -rf /var/lib/apt/lists/* && \
    pip install "poetry==$POETRY_VERSION" && poetry --version


# Copia toda a estrutura do projeto
WORKDIR /workspace
COPY src/ ./src/

# Instala dependências (executa de dentro de src/)
WORKDIR /workspace/src
RUN poetry install --no-root --only main

# Copia e torna executável o entrypoint
COPY src/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
# Converte finais de linha para Unix (caso o arquivo tenha sido salvo em Windows) e garante permissão
RUN sed -i 's/\r$//' /usr/local/bin/docker-entrypoint.sh && \
    chmod +x /usr/local/bin/docker-entrypoint.sh

# Configura PYTHONPATH para imports funcionarem
ENV PYTHONPATH=/workspace/src

# Exponha a porta 8000
EXPOSE 8000

# Comando para rodar migration e iniciar a aplicação (executa de dentro de src/)
WORKDIR /workspace/src
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["python", "main.py"]
