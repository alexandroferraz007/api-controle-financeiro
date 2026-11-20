import os
from typing import Literal
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
security = HTTPBearer()

app = FastAPI(
    title="API de Controle Financeiro",
    description="API REST com autenticação JWT e banco de dados PostgreSQL (Supabase).",
    version="2.0.0"
)


# --- MODELOS DE DADOS ---
class UsuarioAuth(BaseModel):
    email: str = Field(..., example="alex@email.com")
    password: str = Field(..., min_length=6, example="123456")


class TransacaoSchema(BaseModel):
    descricao: str = Field(..., min_length=2, example="Salário Mensal")
    valor: float = Field(..., gt=0, example=3500.00)
    tipo: Literal["receita", "despesa"] = Field(..., example="receita")


# --- SEGURANÇA: Verifica o Token do usuário logado ---
def obter_usuario_atual(credenciais: HTTPAuthorizationCredentials = Depends(security)):
    token = credenciais.credentials
    try:
        resposta = supabase.auth.get_user(token)
        if not resposta or not resposta.user:
            raise HTTPException(status_code=401, detail="Token inválido ou expirado.")
        return resposta.user
    except Exception:
        raise HTTPException(status_code=401, detail="Não autorizado. Faça login novamente.")


# --- ROTAS DE AUTENTICAÇÃO ---
@app.post("/registrar", status_code=201, tags=["Autenticação"])
def registrar_usuario(usuario: UsuarioAuth):
    try:
        resposta = supabase.auth.sign_up({
            "email": usuario.email,
            "password": usuario.password
        })
        if not resposta.user:
            raise HTTPException(status_code=400, detail="Não foi possível cadastrar o usuário.")
        return {"mensagem": "Usuário cadastrado com sucesso!", "email": resposta.user.email}
    except Exception as erro:
        raise HTTPException(status_code=400, detail=f"Erro ao registrar: {str(erro)}")


@app.post("/login", tags=["Autenticação"])
def fazer_login(usuario: UsuarioAuth):
    try:
        resposta = supabase.auth.sign_in_with_password({
            "email": usuario.email,
            "password": usuario.password
        })
        return {
            "mensagem": "Login realizado com sucesso!",
            "access_token": resposta.session.access_token,
            "token_type": "bearer"
        }
    except Exception:
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos.")


# --- ROTAS DE TRANSAÇÕES (PROTEGIDAS POR LOGIN) ---
@app.post("/transacoes", status_code=201, tags=["Transações"])
def criar_transacao(transacao: TransacaoSchema, usuario=Depends(obter_usuario_atual)):
    dados = transacao.model_dump()
    dados["user_id"] = usuario.id  # Vincula ao usuário logado
    resposta = supabase.table("transacoes").insert(dados).execute()
    return {"mensagem": "Transação registrada!", "dados": resposta.data}

@app.get("/", include_in_schema=False)
def redirecionar_para_docs():
    return RedirectResponse(url="/docs")

@app.get("/transacoes", tags=["Transações"])
def listar_transacoes(usuario=Depends(obter_usuario_atual)):
    resposta = (
        supabase.table("transacoes")
        .select("*")
        .eq("user_id", usuario.id)
        .order("id", desc=True)
        .execute()
    )
    return resposta.data


@app.put("/transacoes/{transacao_id}", tags=["Transações"])
def atualizar_transacao(transacao_id: int, transacao: TransacaoSchema, usuario=Depends(obter_usuario_atual)):
    dados = transacao.model_dump()
    resposta = (
        supabase.table("transacoes")
        .update(dados)
        .eq("id", transacao_id)
        .eq("user_id", usuario.id)
        .execute()
    )
    if not resposta.data:
        raise HTTPException(status_code=404, detail="Transação não encontrada.")
    return {"mensagem": "Transação atualizada!", "dados": resposta.data}


@app.delete("/transacoes/{transacao_id}", tags=["Transações"])
def deletar_transacao(transacao_id: int, usuario=Depends(obter_usuario_atual)):
    resposta = (
        supabase.table("transacoes")
        .delete()
        .eq("id", transacao_id)
        .eq("user_id", usuario.id)
        .execute()
    )
    if not resposta.data:
        raise HTTPException(status_code=404, detail="Transação não encontrada.")
    return {"mensagem": f"Transação {transacao_id} removida!"}


@app.get("/saldo", tags=["Resumo"])
def calcular_saldo(usuario=Depends(obter_usuario_atual)):
    resposta = (
        supabase.table("transacoes")
        .select("valor, tipo")
        .eq("user_id", usuario.id)
        .execute()
    )
    transacoes = resposta.data

    total_receitas = sum(item["valor"] for item in transacoes if item["tipo"] == "receita")
    total_despesas = sum(item["valor"] for item in transacoes if item["tipo"] == "despesa")
    saldo_atual = total_receitas - total_despesas

    return {
        "usuario": usuario.email,
        "total_receitas": round(total_receitas, 2),
        "total_despesas": round(total_despesas, 2),
        "saldo_atual": round(saldo_atual, 2)
    }