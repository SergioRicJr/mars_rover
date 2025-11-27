# Mars Rover API 🚀

API REST para controlar sondas exploradoras em Marte. Desenvolvida como desafio técnico utilizando Python, FastAPI e boas práticas de desenvolvimento.

## Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Tecnologias](#tecnologias)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Instalação e Execução](#instalação-e-execução)
  - [Execução local (sem Docker)](#execução-local-sem-docker)
  - [Execução com Docker](#execução-com-docker)
- [Documentação Interativa](#documentação-interativa)
- [Migrations (Alembic)](#migrations-alembic)
- [Endpoints da API](#endpoints-da-api)
- [Testes](#testes)
- [CI/CD](#cicd)
- [Exemplos de Uso](#exemplos-de-uso)

---

## Sobre o Projeto

O desafio consiste em uma API para controlar o movimento de sondas enviadas em missão para Marte. As sondas exploram um planalto retangular representado por uma malha 2D com coordenadas X e Y.

### Decisões de Arquitetura

- Endpoints síncronos: foram mantidos síncronos para evitar complexidade extra neste desafio. No dia a dia costumo aplicar soluções concorrentes (controllers async, gerenciadores de contexto e sessão de banco de dados assíncronos) para ganho de performance, porém aqui o custo de coordenação não se pagaria. Em cenários reais com maior carga ou requisitos de consistência, avaliaria o uso de locks pessimistas/otimistas ou filas para preservar integridade sem bloquear a API.
- Regras de negócio isoladas: toda a lógica vive no domínio (`app/domain`) de forma independente, mantendo controladores e serviços desacoplados.

### Regras

- Uma sonda sempre começa no canto inferior esquerdo (0, 0)
- A sonda nunca deve sair dos limites do planalto
- Comandos disponíveis:
  - `M` - Move 1 passo na direção atual
  - `L` - Rotaciona 90° para a esquerda
  - `R` - Rotaciona 90° para a direita

---

## Tecnologias

- **Python 3.11+**
- **FastAPI** - Framework web moderno e de alta performance
- **Pydantic** - Validação de dados
- **dependency-injector** - Injeção de dependências
- **pytest** - Framework de testes
- **Poetry** - Gerenciamento de dependências
- **Docker** - Containerização

### Padrões de Projeto Utilizados

- **State Pattern** - Para gerenciar as direções da sonda
- **Factory Pattern** - Para criar e executar comandos
- **Repository Pattern** - Para persistência de dados
- **Dependency Injection** - Para desacoplamento de componentes

---

## Estrutura do Projeto

```
mars_rover/
├── src/
│   ├── app/
│   │   ├── domain/              # Entidades e lógica de negócio
│   │   │   ├── direction.py     # Enum de direções (State Pattern)
│   │   │   ├── plateau.py       # Planalto com validação de limites
│   │   │   ├── rover.py         # Entidade Sonda
│   │   │   └── commands.py      # Factory de comandos
│   │   ├── endpoints/           # Controllers da API
│   │   │   └── rover/
│   │   │       ├── controllers.py
│   │   │       └── schemas.py   # Schemas Pydantic
│   │   ├── infrastructure/      # Infraestrutura
│   │   │   ├── exceptions.py    # Exceções customizadas
│   │   │   └── logger.py
│   │   ├── repositories/        # Camada de persistência
│   │   │   ├── irepository.py   # Interface do repositório
│   │   │   └── rover_repository.py
│   │   ├── services/            # Camada de serviços
│   │   │   └── rover_service.py
│   │   ├── config.py            # Configurações
│   │   └── containers.py        # Container de injeção de dependência
│   ├── tests/                   # Testes automatizados
│   │   ├── test_domain.py       # Testes unitários
│   │   └── test_api.py          # Testes de integração
│   ├── main.py                  # Ponto de entrada da aplicação
│   ├── pyproject.toml           # Configuração do Poetry
│   └── poetry.lock              # Lock file do Poetry
├── Dockerfile
├── Dockerfile.test
├── docker-compose.yml
└── README.md
```

---

## Instalação e Execução

### Execução local (sem Docker)

#### Pré-requisitos

- Python 3.11
- Poetry 1.8.3

#### Passos

1. Clone o repositório:

```bash
git clone https://github.com/seu-usuario/mars-rover.git
cd mars-rover
```

2. Instale as dependências (rodando dentro de `src/` onde está o `pyproject.toml`):

```bash
cd src
poetry install
```

3. Configure as variáveis de ambiente antes de iniciar a aplicação:

```bash
# Exemplo de configuração em shells compatíveis
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/mars_rover"
export SQL_ECHO=false
export SQL_POOL_SIZE=5
export SQL_MAX_OVERFLOW=10
```

No Windows PowerShell:

```powershell
$Env:DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/mars_rover"
$Env:SQL_ECHO = "false"
$Env:SQL_POOL_SIZE = "5"
$Env:SQL_MAX_OVERFLOW = "10"
```

4. Execute a aplicação (ainda dentro de `src/`):

```bash
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

A API ficará disponível em `http://localhost:8000`.

### Execução com Docker

```bash
# Construir e iniciar
docker-compose up --build

# Executar em background
docker-compose up -d

# Parar
docker-compose down
```

Para rodar os testes dentro do container:

```bash
docker-compose --profile test run test
```

Também é possível usar apenas o Dockerfile padrão:

```bash
docker build -t mars-rover-api .
docker run -p 8000:8000 mars-rover-api
```

### Documentação Interativa

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Migrations (Alembic)

- As migrations ficam em `src/alembic/versions` e são gerenciadas via Alembic.
- Para aplicar o estado mais recente no ambiente local (já dentro de `src/` e com as variáveis configuradas):

```bash
poetry run alembic upgrade head
```

- Para criar uma nova migration baseada no modelo atual:

```bash
poetry run alembic revision --autogenerate -m "descricao_da_migration"
```

- Ao subir via `docker-compose up`, o `docker-entrypoint.sh` roda `alembic upgrade head` automaticamente assim que o banco Postgres estiver saudável; detalhes em `MIGRATIONS_DOCKER.md`.
- Se preferir executar dentro do container: `docker-compose exec api poetry run alembic current` (status) e `docker-compose exec api poetry run alembic history` (histórico).

---

## Endpoints da API

### 1. Lançar Sonda

Cria uma nova sonda e configura o planalto.

```http
POST /probes
```

**Request:**
```json
{
    "x": 5,
    "y": 5,
    "direction": "NORTH"
}
```

**Response (201 Created):**
```json
{
    "id": "abc123",
    "x": 0,
    "y": 0,
    "direction": "NORTH"
}
```

### 2. Mover Sonda

Executa uma sequência de comandos na sonda.

```http
PUT /probes/{id}/commands
```

**Request:**
```json
{
    "commands": "MRM"
}
```

**Response (200 OK):**
```json
{
    "id": "abc123",
    "x": 1,
    "y": 1,
    "direction": "EAST"
}
```

**Erros:**
- `404 Not Found` - Sonda não encontrada
- `400 Bad Request` - Comando inválido ou movimento fora dos limites

### 3. Listar Sondas

Retorna todas as sondas cadastradas.

```http
GET /probes
```

**Response (200 OK):**
```json
{
    "probes": [
        {
            "id": "abc123",
            "x": 1,
            "y": 1,
            "direction": "EAST"
        },
        {
            "id": "xyz789",
            "x": 3,
            "y": 4,
            "direction": "NORTH"
        }
    ]
}
```

---

## Testes

### Postman Collection

Uma collection completa do Postman está disponível na pasta `postman/`:

1. Importe `Mars_Rover_API.postman_collection.json` no Postman
2. Importe `Mars_Rover_Local.postman_environment.json` como environment
3. Selecione o environment "Mars Rover Local"
4. Execute os testes individualmente ou use o Collection Runner

**Casos cobertos:**
- Lançamento de sondas (11 testes)
- Movimentação de sondas (13 testes)
- Listagem de sondas (2 testes)
- Cenários completos (2 fluxos)

### Executar todos os testes

```bash
poetry run pytest
```

### Executar com cobertura

```bash
poetry run pytest --cov=app --cov-report=html
```

### Executar testes específicos

```bash
# Apenas testes de domínio
poetry run pytest tests/test_domain.py

# Apenas testes de API
poetry run pytest tests/test_api.py
```

---

## CI/CD

- A pipeline está definida em `.github/workflows/tests.yml` e roda automaticamente no GitHub Actions em todos os pushes para a branch `master`.
- O workflow instala as dependências via Poetry e executa `poetry run pytest`, garantindo que a suíte complete sem falhas antes de aceitar alterações.
- Os resultados aparecem na aba **Actions** do repositório no GitHub, permitindo acompanhar logs, histórico de execuções e status dos testes.

---

## Exemplos de Uso

### Cenário completo via cURL

```bash
# 1. Lançar uma sonda em um planalto 5x5
curl -X POST http://localhost:8000/probes \
  -H "Content-Type: application/json" \
  -d '{"x": 5, "y": 5, "direction": "NORTH"}'

# Resposta: {"id":"a1b2c3d4","x":0,"y":0,"direction":"NORTH"}

# 2. Mover a sonda com a sequência MRM
curl -X PUT http://localhost:8000/probes/a1b2c3d4/commands \
  -H "Content-Type: application/json" \
  -d '{"commands": "MRM"}'

# Resposta: {"id":"a1b2c3d4","x":1,"y":1,"direction":"EAST"}

# 3. Listar todas as sondas
curl http://localhost:8000/probes

# Resposta: {"probes":[{"id":"a1b2c3d4","x":1,"y":1,"direction":"EAST"}]}
