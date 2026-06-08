from fastapi import FastAPI, HTTPException, status, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI(
    title="AeroCarbon API",
    description="API de Monitoramento Ambiental e Detecção de Queimadas por Satélite",
    version="1.0.0"
)

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. MODELO DE DADOS
class FocoQueimada(BaseModel):
    id: int
    regiao: str = Field(..., example="Pantanal - Corumbá")
    latitude: float = Field(..., example=-19.0031)
    longitude: float = Field(..., example=-57.6536)
    nivel_risco: str = Field(..., example="Crítico") # Crítico, Alto, Médio
    carbono_estimado: float = Field(..., example=85.2) # Em toneladas de CO2
    status: str = Field(default="Ativo", example="Ativo") # Ativo / Resolvido

class FocoQueimadaUpdate(BaseModel):
    regiao: Optional[str] = Field(None, example="Pantanal - Corumbá")
    latitude: Optional[float] = Field(None, example=-19.0031)
    longitude: Optional[float] = Field(None, example=-57.6536)
    nivel_risco: Optional[str] = Field(None, example="Crítico")
    carbono_estimado: Optional[float] = Field(None, example=85.2)
    status: Optional[str] = Field(None, example="Ativo")

# 2. BANCO DE DADOS EM MEMÓRIA
db_focos: List[FocoQueimada] = [
    FocoQueimada(id=1, regiao="Pantanal - Corumbá", latitude=-19.0031, longitude=-57.6536, nivel_risco="Alto", carbono_estimado=85.2, status="Ativo"),
    FocoQueimada(id=2, regiao="Cerrado - Matopiba", latitude=-10.2145, longitude=-45.8952, nivel_risco="Crítico", carbono_estimado=210.5, status="Ativo"),
    FocoQueimada(id=3, regiao="Amazônia - São Félix", latitude=-6.6447, longitude=-51.9945, nivel_risco="Médio", carbono_estimado=45.0, status="Ativo")
]

# 3. ROTAS DA API (FRAMEWORK FASTAPI)

@app.get("/", tags=["Home"])
def read_root():
    return {"message": "Bem-vindo à API AeroCarbon de Monitoramento Ambiental!"}

# GET - Listar todos os focos ativos
@app.get("/focos", response_model=List[FocoQueimada], tags=["Focos de Queimada"])
def listar_focos():
    return db_focos

# POST - Criar um novo alerta de queimada
@app.post("/focos", status_code=status.HTTP_201_CREATED, response_model=FocoQueimada, tags=["Focos de Queimada"])
def criar_foco(foco: FocoQueimada):
    # Verifica se já existe o ID para evitar duplicidade
    if any(f.id == foco.id for f in db_focos):
        raise HTTPException(status_code=400, detail="Já existe um registro com este ID.")
    db_focos.append(foco)
    return foco

# PUT - Atualizar um foco existente
@app.put("/focos/{foco_id}", response_model=FocoQueimada, tags=["Focos de Queimada"])
def atualizar_foco(foco_id: int, dados: FocoQueimadaUpdate):
    for index, foco in enumerate(db_focos):
        if foco.id == foco_id:
            atualizado = foco.model_copy(update=dados.model_dump(exclude_none=True))
            db_focos[index] = atualizado
            return atualizado
    raise HTTPException(status_code=404, detail="Foco de queimada não encontrado.")

# DELETE
@app.delete("/focos/{foco_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Focos de Queimada"])
def deletar_foco(foco_id: int):
    for index, foco in enumerate(db_focos):
        if int(foco.id) == int(foco_id):
            db_focos.pop(index)
            return Response(status_code=status.HTTP_204_NO_CONTENT)
            
    raise HTTPException(status_code=404, detail="Foco de queimada não encontrado para exclusão.")