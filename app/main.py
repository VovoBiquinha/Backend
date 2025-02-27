from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from fastapi.encoders import jsonable_encoder 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

@app.on_event("startup")
async def startup_db():
    try:
        app.mongodb_client = AsyncIOMotorClient("mongodb+srv://guiglreis:F9iyvikkE0s39L79@vovobiquinha.d3sry.mongodb.net/").Create_New_Students
        app.mongodb = app.mongodb_client
        print("Banco de dados conectado")
    except Exception as e:
        print(f"Erro ao conectar com o banco de dados: {e}")

@app.on_event("shutdown")
async def shutdown_db():
    app.mongodb_client.close()

class Aluno(BaseModel):
    nome: str
    sobrenome: str
    dataNascimento: str
    endereco: str
    escola: str
    diagnostico: str
    usoMedicamento: bool
    nomeMedicamento: str = None
    posologia: str = None
    servicos: str

@app.post("/alunos/")
async def cadastrar_aluno(aluno: Aluno):
    aluno_dict = aluno.dict()
    print(f"Inserindo aluno: {aluno_dict}") 
    try:
        result = await app.mongodb.New_Students.insert_one(aluno_dict)
        if result.acknowledged:
            print(f"Documento inserido com sucesso: {result.inserted_id}")
        else:
            print("Falha ao inserir o documento.")
    except Exception as e:
        print(f"Erro ao inserir aluno: {e}")
        return {"error": str(e)} 
    aluno_dict["_id"] = str(result.inserted_id)
    return aluno_dict


@app.get("/alunos/", response_model=List[Aluno])
async def listar_alunos():
    alunos = await app.mongodb.New_Students.find().to_list(100)  
  
    for aluno in alunos:
        aluno["_id"] = str(aluno["_id"])    
    return alunos

@app.get("/")
def home():
    return {"message": "API rodando com sucesso!"}
