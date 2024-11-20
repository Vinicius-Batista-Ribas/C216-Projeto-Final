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
@app.get("/api/v1/home/list/category/{categoria}", response_model=List[Mods])
async def listar_mods_por_categoria(categoria: str):
    conn = await get_database()
    try:
        query = "SELECT * FROM mods WHERE LOWER(categoria) ILIKE LOWER($1)"
        rows = await conn.fetch(query, f"%{categoria}%")  # Uso de % para buscar similaridades
        results = [dict(row) for row in rows]
        
        if not results:
            raise HTTPException(status_code=404, detail=f"Nenhum mod encontrado para a categoria: {categoria}")
        
        return results
    
    finally:
        await conn.close()


@app.get("/api/v1/home/list/game/{jogo}", response_model=List[Mods])
async def listar_mods_por_jogo(jogo: str):
    conn = await get_database()
    try:
        query = "SELECT * FROM mods WHERE LOWER(jogo) ILIKE LOWER($1)"
        rows = await conn.fetch(query, f"%{jogo}%")  # Uso de % para buscar similaridades
        results = [dict(row) for row in rows]
        
        if not results:
            raise HTTPException(status_code=404, detail=f"Nenhum mod encontrado para o jogo: {jogo}")
        
        return results
    
    finally:
        await conn.close()


### Buscar por id
@app.get("/api/v1/home/mod/{nome}", response_model=List[Mods])
async def listar_mods_filtrados(nome: str):
    conn = await get_database()
    try:
        query = "SELECT * FROM mods WHERE LOWER(nome) ILIKE LOWER($1)"
        results = await conn.fetch(query, f"%{nome}%")
        if not results:
            raise HTTPException(status_code=404, detail="MOD NAO ENCONTRADO")
        mods_list = [Mods(**dict(record)) for record in results]
        return mods_list
    
    
    finally: await conn.close()

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
        update_fields = []
        params = []

        if mod_atualizado.nome is not None:
            update_fields.append("nome = $2")
            params.append(mod_atualizado.nome)
        if mod_atualizado.jogo is not None:
            update_fields.append("jogo = $3")
            params.append(mod_atualizado.jogo)
        if mod_atualizado.descricao is not None:
            update_fields.append("descricao = $4")
            params.append(mod_atualizado.descricao)
        if mod_atualizado.versao is not None:
            update_fields.append("versao = $5")
            params.append(mod_atualizado.versao)
        if mod_atualizado.autores is not None:
            update_fields.append("autores = $6")
            params.append(mod_atualizado.autores)
        if mod_atualizado.categoria is not None:
            update_fields.append("categoria = $7")
            params.append(mod_atualizado.categoria)
        if mod_atualizado.tamanho is not None:
            update_fields.append("tamanho = $8")
            params.append(mod_atualizado.tamanho)

        # Se houver campos para atualizar, executa a query
        if update_fields:
            update_query = f"UPDATE mods SET {', '.join(update_fields)} WHERE id = $1 RETURNING *"
            params.insert(0, mod_id)  # Adiciona o mod_id como o primeiro parâmetro
            updated_mod = await conn.fetchrow(update_query, *params)

            if updated_mod:
                return {"message": "MOD atualizado com sucesso!", "MOD": dict(updated_mod)}
            else:
                raise HTTPException(status_code=404, detail="Falha ao atualizar o MOD")
        else:
            return {"message": "Nenhuma alteração encontrada."}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar mod: {str(e)}")
    
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