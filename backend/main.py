from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional
import time
import asyncpg
import os

async def get_database():
    DATABASE_URL = os.environ.get("PGURL", "postgresql://postgres:postgres@db:5432/mods") 
    return await asyncpg.connect(DATABASE_URL)

app = FastAPI()

class Mods(BaseModel):
    id: Optional[int] = None
    nome: str
    jogo: str
    descricao: str
    versao: str
    autores: str
    categoria: str
    tamanho: str


class AtualizarMods(BaseModel):
    nome: Optional[str] = None
    jogo: Optional[str] = None
    descricao: Optional[str] = None
    versao: Optional[str] = None
    autores: Optional[str] = None
    categoria: Optional[str] = None
    tamanho: Optional[str] = None



@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    print(f"Path: {request.url.path}, Method: {request.method}, Process Time: {process_time:.4f}s")
    return response


### Verificar se o produto existe
async def exist(nome: str, conn: asyncpg.Connection):
    try:
        query = "SELECT * FROM mods WHERE LOWER(nome) = LOWER($1)"
        result = await conn.fetchval(query, nome)
        return result is not None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"falha ao verificar se o mod existe: {str(e)}")

### CRIAR MOD
@app.post("/api/v1/home/", status_code=201)
async def add_mod(mod: Mods):
    conn = await get_database()
    try:
        if await exist(mod.nome, conn):
            raise HTTPException(status_code=400, detail="error ao adicionar, o nome do mod ja esta sendo usado.")
        query = "INSERT INTO mods (nome, jogo, descricao, categoria, versao, autores, tamanho) VALUES ($1, $2, $3, $4, $5, $6, $7)"
        async with conn.transaction():
            await conn.execute(query, mod.nome, mod.jogo, mod.descricao, mod.categoria, mod.versao, mod.autores, mod.tamanho)
            return {"message": "MOD cadastrado com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"falha ao adicionar mod: {str(e)}")  
    
    finally: await conn.close()  

### Listar todos
@app.get("/api/v1/home/", response_model=List[Mods])
async def listar_mods():
    conn = await get_database()
    try:
        query = "SELECT * FROM mods"
        rows = await conn.fetch(query)
        mods = [dict(row) for row in rows]
        return mods
    
    finally: await conn.close()

### Listar por filtros
@app.get("/api/v1/home/list/{type}", response_model=List[Mods])
async def listar_mods_por_jogo(type: str):
    conn = await get_database()
    try:
        # Consulta SQL com correção
        query = """
            SELECT * FROM mods 
            WHERE LOWER(jogo) ILIKE LOWER($1)
               OR LOWER(nome) ILIKE LOWER($1)  
               OR LOWER(categoria) ILIKE LOWER($1)
        """
        # Realiza a busca com o tipo, usando '%' para encontrar similaridades
        rows = await conn.fetch(query, f"%{type}%")
        
        # Converter os resultados em uma lista de dicionários
        results = [dict(row) for row in rows]
        
        # Verifica se algum resultado foi encontrado
        if not results:
            raise HTTPException(status_code=404, detail=f"Nenhum mod encontrado para o tipo: {type}")
        
        return results
    
    finally:
        await conn.close()



### Buscar por id
@app.get("/api/v1/home/mod/{mod_id}")
async def listar_mods_filtrados(mod_id: int):

    conn = await get_database()
    try:
        query = "SELECT * FROM mods WHERE id = $1"
        results = await conn.fetchrow(query, mod_id)
        if not results:
            raise HTTPException(status_code=404, detail="MOD NAO ENCONTRADO")
        return dict(results)
    
    
    finally: 
        await conn.close()

### ATUALIZAR
@app.patch("/api/v1/home/mod/{mod_id}", response_model=dict)
async def atualizar(mod_id: int, mod_atualizado: AtualizarMods):
    conn = await get_database()
    try:
        # Verifica se o mod existe pelo ID
        query = "SELECT * FROM mods WHERE id = $1"
        mod = await conn.fetchrow(query, mod_id)
        if mod is None:
            raise HTTPException(status_code=404, detail="Mod não encontrado")
        
        # Lista de campos a serem atualizados
        update_query = """
            UPDATE mods
            SET nome = COALESCE($1, nome),
                jogo = COALESCE($2, jogo),
                descricao = COALESCE($3, descricao),
                versao = COALESCE($4, versao),
                autores = COALESCE($5, autores),
                categoria = COALESCE($6, categoria),
                tamanho = COALESCE($7, tamanho)
            WHERE id = $8
        """

        await conn.execute(
            update_query,
            mod_atualizado.nome,
            mod_atualizado.jogo,
            mod_atualizado.descricao,
            mod_atualizado.versao,
            mod_atualizado.autores,
            mod_atualizado.categoria,
            mod_atualizado.tamanho,
            mod_id
        )
        
        # Busca o mod atualizado
        updated_mod = await conn.fetchrow(query, mod_id)
        
        # Retorna o mod atualizado na resposta
        return {
            "message": "MOD atualizado com sucesso!",
            "MOD": dict(updated_mod)
        }
    finally:
        await conn.close()

### REMOVER        
@app.delete("/api/v1/home/mod/{mod_id}")
async def remove(mod_id: int):

    conn = await get_database()
    try:
        query = "SELECT * FROM mods WHERE id = $1"
        mod = await conn.fetchrow(query, mod_id)

        if mod is None:
            raise HTTPException(status_code=404, detail="Mod não encontrado.")
        
        delete_query = "DELETE FROM mods WHERE id = $1"
        await conn.execute(delete_query, mod_id)

        return{"message": "Mod removido com sucesso"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao remover mod: {str(e)}")
    
    finally: await conn.close()


### RESET DATABASE
@app.delete("/api/v1/home/reset/")
async def reset():
    init_sql = os.getenv("INIT_SQL", "db/db.sql")
    conn = await get_database()
    try:
        with open(init_sql, 'r') as file:
            sql_comands = file.read()
            print(sql_comands)
        await conn.execute(sql_comands)
        return {"message": "Banco de dados limpo com sucesso!"}    
    
    finally: await conn.close()