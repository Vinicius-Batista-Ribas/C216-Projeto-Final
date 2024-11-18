from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional
import time
import asyncpg
import os

async def get_database():
    DATABASE_URL = os.environ.get("PGURL", "postgresql://postgres:postgres@db:5432/produtos") 
    return await asyncpg.connect(DATABASE_URL)

app = FastAPI()

class Mods(BaseModel):
    id: Optional[int] = None
    nome = str
    jogo = str
    descricao = str
    versao = str
    autores = str
    categoria = str
    tamanho = str


class AtualizarMods(BaseModel):
    nome = Optional[str] = None
    jogo = Optional[str] = None
    descricao = Optional[str] = None
    versao = Optional[str] = None
    autores = Optional[str] = None
    categoria = Optional[str] = None
    tamanho = Optional[str] = None



@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    print(f"Path: {request.url.path}, Method: {request.method}, Process Time: {process_time:.4f}s")
    return response


### Listar todos
@app.get("/api/v1/home", response_model=List[Mods])
async def listar_mods():
    conn = await get_database()
    try:
        query = "SELECT * FROM mods"
        rows = await conn.fetch(query)
        mods = [dict(row) for row in rows]
        return mods
    finally:
        await conn.close()


### Listar por filtros
@app.get("/api/v1/home/list/{categoria}", response_model=List[Mods])
async def listar_mods_filtrados(tipo: str, valor: str):
    conn = await get_database()
    try:
        if tipo.lower() == "categoria":
            query = "SELECT * FROM mods WHERE LOWER(categoria) = LOWER($1)"
        elif tipo.lower() == "jogo":
            query = "SELECT * FROM mods WHERE LOWER(jogo) = LOWER($1)"
        else:
            raise HTTPException(status_code=400, detail="Tipo de filtro inválido. Use 'categoria' ou 'jogo'.")
        
        rows = await conn.fetch(query, valor)
        results = [dict(row) for row in rows]
        
        if not results:
            raise HTTPException(status_code=404, detail=f"Nenhum mod encontrado para {tipo}: {valor}")
        
        return results
    finally:
        await conn.close()



### Buscar por nome
@app.get("/api/v1/home/mod/{nome}", response_model=List[Mods])
async def listar_mods_filtrados(nome: str):
    conn = await get_database()
    try:
        query = "SELECT * FROM mods WHERE LOWER(nome) = LOWER($1)"
        results = await conn.fetch(query, nome)
        if not results:
            raise HTTPException(status_code=404, detail="MOD NAO ENCONTRADO")
        return results
    finally:
        await conn.close()


### Verificar se o produto existe
async def exist(nome: str, conn: asyncpg.Connection):
    try:
        query = "SELECT * FROM mods WHERE LOWER(nome) = LOWER($1)"
        result = await conn.fetchval(query, nome)
        return result is not None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"falha ao verificar se o mod existe: {str(e)}")


### CRIAR MOD
@app.post("/api/v1/home", status_code=201)
async def add_mod(mod: Mods):
    conn = await get_database()
    try:
        if await exist(mod.nome, conn):
            raise HTTPException(status_code=400, detail="error ao adicionar, o nome do mod ja esta sendo usado.")
        query = "INSERT INTO mods (nome, jogo, descricao, categoria, versao, autores, tamanho) VALUES ($1, $2, $3, $4, $5, $6)"
        async with conn.transaction():
            await conn.execute(query, mod.nome, mod.jogo, mod.descricao, mod.categoria, mod.versao, mod.autores, mod.tamanho)
            return {"message": "MOD cadastrado com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"falha ao adicionar mod: {str(e)}")  
    finally: 
        await conn.close()  

