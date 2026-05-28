from fastapi import FastAPI, HTTPException, status, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

app = FastAPI(
    title="AeroCarbon API",
    description="API REST de monitoramento ambiental em tempo real integrando dados térmicos de satélites.",
    version="1.0.0"
)

# Configuração de CORS (Essencial para o Frontend Web e Mobile consumirem a API sem bloqueios)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite chamadas de qualquer origem (Web e Snack Expo Mobile)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------
# MODELOS DE DADOS (Pydantic Schemas)
# ----------------------------------------------------
class FocoQueimadaBase(BaseModel):
    regiao: str = Field(..., example="Amazônia - Setor Norte")
    latitude: float = Field(..., example=-3.4653)
    longitude: float = Field(..., example=-62.2154)
    nivel_risco: str = Field(..., example="Crítico")  # Baixo, Médio, Alto, Crítico
    carbono_estimado: float = Field(..., example=145.8, description="Quantidade de carbono estimada em toneladas")
    status: str = Field(default="Ativo", example="Ativo")  # Ativo, Controlado

class FocoQueimadaCreate(FocoQueimadaBase):
    pass

class FocoQueimadaResponse(FocoQueimadaBase):
    id: int
    data_deteccao: datetime

# ----------------------------------------------------
# BANCO DE DADOS EM MEMÓRIA (Simulação)
# ----------------------------------------------------
db_focos: List[FocoQueimadaResponse] = [
    FocoQueimadaResponse(
        id=1,
        regiao="Pantanal - Corumbá",
        latitude=-19.0031,
        longitude=-57.6536,
        nivel_risco="Alto",
        carbono_estimado=85.2,
        status="Ativo",
        data_deteccao=datetime.now()
    ),
    FocoQueimadaResponse(
        id=2,
        regiao="Cerrado - Matopiba",
        latitude=-10.2145,
        longitude=-45.8952,
        nivel_risco="Crítico",
        carbono_estimado=210.5,
        status="Ativo",
        data_deteccao=datetime.now()
    )
]

id_counter = 3

# ----------------------------------------------------
# ROTAS / ENDPOINTS (CRUD COMPLETO)
# ----------------------------------------------------

# Rota Inicial / Health Check
@app.get("/", tags=["Home"])
def home():
    return {
        "plataforma": "AeroCarbon",
        "status": "Online",
        "contexto": "Linha de defesa ecológica por monitoramento orbital"
    }

# 1. READ ALL (Listagem de registros - Usado no Mobile e no Web)
@app.get("/focos", response_model=List[FocoQueimadaResponse], tags=["Focos de Queimada"])
def listar_focos(status_filtro: Optional[str] = None):
    if status_filtro:
        return [f for f in db_focos if f.status.lower() == status_filtro.lower()]
    return db_focos

# 2. READ BY ID (Consulta de um registro específico)
@app.get("/focos/{foco_id}", response_model=FocoQueimadaResponse, tags=["Focos de Queimada"])
def obter_foco(foco_id: int):
    for foco in db_focos:
        if foco.id == foco_id:
            return foco
    raise HTTPException(status_code=404, detail="Foco de queimada não encontrado.")

# 3. CREATE (Cadastro de novos registros - Usado no formulário do Mobile e Web)
@app.post("/focos", response_model=FocoQueimadaResponse, status_code=status.HTTP_201_CREATED, tags=["Focos de Queimada"])
def criar_foco(novo_foco: FocoQueimadaCreate):
    global id_counter
    foco_salvo = FocoQueimadaResponse(
        id=id_counter,
        regiao=novo_foco.regiao,
        latitude=novo_foco.latitude,
        longitude=novo_foco.longitude,
        nivel_risco=novo_foco.nivel_risco,
        carbono_estimado=novo_foco.carbono_estimado,
        status=novo_foco.status,
        data_deteccao=datetime.now()
    )
    db_focos.append(foco_salvo)
    id_counter += 1
    return foco_salvo

# 4. UPDATE (Atualizar dados como mudar status para 'Controlado')
@app.put("/focos/{foco_id}", response_model=FocoQueimadaResponse, tags=["Focos de Queimada"])
def atualizar_foco(foco_id: int, foco_atualizado: FocoQueimadaCreate):
    for index, foco in enumerate(db_focos):
        if foco.id == foco_id:
            foco_alterado = FocoQueimadaResponse(
                id=foco_id,
                regiao=foco_atualizado.regiao,
                latitude=foco_atualizado.latitude,
                longitude=foco_atualizado.longitude,
                nivel_risco=foco_atualizado.nivel_risco,
                carbono_estimado=foco_atualizado.carbono_estimado,
                status=foco_atualizado.status,
                data_deteccao=db_focos[index].data_deteccao  # Mantém a data original
            )
            db_focos[index] = foco_alterado
            return foco_alterado
    raise HTTPException(status_code=404, detail="Foco de queimada não encontrado para atualização.")

# 5. DELETE (Remover registro em caso de falso positivo de calor)
@app.delete("/focos/{foco_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Focos de Queimada"])
def deletar_foco(foco_id: int):
    for index, foco in enumerate(db_focos):
        # Conversão preventiva para int garante que a comparação nunca falhe por tipo de dado
        if int(foco.id) == int(foco_id):
            db_focos.pop(index)
            
            # RETORNO CORRETO: Envia uma resposta HTTP 204 limpa e sem corpo
            return Response(status_code=status.HTTP_204_NO_CONTENT)
            
    raise HTTPException(status_code=404, detail="Foco de queimada não encontrado para exclusão.")