# E-commerce Service

Microsserviço de backend em **Python (FastAPI)** com produtos e pedidos.

## Stack
- FastAPI + Uvicorn
- SQLAlchemy 2.0 (SQLite por padrão; troque via `DATABASE_URL`)
- Pydantic v2
- Pytest

## Rodando localmente
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Documentação interativa: http://localhost:8000/docs

## Testes
```bash
pytest -v
```

## Endpoints
| Método | Rota | Descrição |
|---|---|---|
| GET | `/health` | Healthcheck |
| POST | `/products` | Cria produto |
| GET | `/products?search=&skip=&limit=` | Lista/busca produtos |
| GET | `/products/{id}` | Detalha produto |
| PATCH | `/products/{id}` | Atualiza produto |
| DELETE | `/products/{id}` | Remove produto |
| POST | `/orders` | Cria pedido (valida e baixa estoque) |
| GET | `/orders?customer_email=` | Lista pedidos |
| GET | `/orders/{id}` | Detalha pedido |
| POST | `/orders/{id}/cancel` | Cancela pedido e devolve estoque |

## Exemplo
```bash
curl -X POST localhost:8000/products -H 'Content-Type: application/json' \
  -d '{"name":"Camiseta","price":"49.90","stock":10}'

curl -X POST localhost:8000/orders -H 'Content-Type: application/json' \
  -d '{"customer_email":"cliente@email.com","items":[{"product_id":1,"quantity":2}]}'
```

## Variáveis de ambiente
- `DATABASE_URL` (padrão: `sqlite:///./ecommerce.db`)
