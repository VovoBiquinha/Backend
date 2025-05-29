from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List
from fastapi.encoders import jsonable_encoder 
from typing import Optional
from app.report import router as report_router
from fastapi import HTTPException
from bson import ObjectId

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

app.include_router(report_router)

@app.on_event("startup")
async def startup_db():
    try:
        app.mongodb_client = AsyncIOMotorClient("mongodb+srv://guiglreis:Maçadoamor33440388@vovobiquinha.d3sry.mongodb.net/")
        app.mongodb = app.mongodb_client["Create_New_Students"]
        print("Banco de dados conectado")
    except Exception as e:
        print(f"Erro ao conectar com o banco de dados: {e}")

@app.on_event("shutdown")
async def shutdown_db():
    app.mongodb_client.close()

class Aluno(BaseModel):
    first_name: str
    last_name: str
    birth_date: str
    address: str
    school: str
    diagnosis: str
    medication_usage: bool
    medication_name: Optional[str] = None
    dosage: Optional[str] = None
    services: str

class AlunoComId(Aluno):
    id: Optional[str]

    class Config:
        orm_mode = True

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


@app.get("/alunos/", response_model=List[AlunoComId])
async def listar_alunos():
    alunos = await app.mongodb.New_Students.find().to_list(100)  
    
    for aluno in alunos:
        aluno["id"] = str(aluno["_id"])    
        del aluno["_id"]
    return alunos

@app.get("/")
def home():
    return {"message": "API rodando com sucesso!"}