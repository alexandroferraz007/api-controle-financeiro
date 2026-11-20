# 💰 API de Controle Financeiro Pessoal

API RESTful desenvolvida em **Python** com **FastAPI** e banco de dados **PostgreSQL (Supabase)** para gerenciamento de receitas, despesas e cálculo de saldo individual por usuário.

## 🚀 Funcionalidades
- **Autenticação de Usuários:** Cadastro (`/registrar`) e login (`/login`) com geração de token JWT.
- **Isolamento de Dados:** Cada usuário autenticado visualiza, cria, edita e exclui apenas as próprias transações.
- **CRUD Completo:** Criação, listagem, atualização e exclusão de receitas e despesas com validação de dados (Pydantic).
- **Resumo Financeiro:** Rota `/saldo` que calcula automaticamente o total de receitas, total de despesas e saldo atual.
- **Documentação Interativa:** Swagger UI gerado automaticamente em `/docs`.

## 🛠️ Tecnologias Utilizadas
- **Python 3.12**
- **FastAPI**
- **Supabase (PostgreSQL & Auth)**
- **Pydantic**

## ⚙️ Como Rodar Localmente

1. Clone o repositório:
```bash
git clone https://github.com
cd finance-api
```

2. Crie e ative o ambiente virtual:
```bash
python -m venv venv
.\venv\Scripts\activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Crie um arquivo `.env` na raiz do projeto com suas credenciais do Supabase:
```env
SUPABASE_URL=sua_url_do_supabase
SUPABASE_KEY=sua_chave_anon_public
```

5. Inicie o servidor:
```bash
python -m fastapi dev main.py
```

Acesse `http://127.0.0` no navegador para testar os endpoints.
