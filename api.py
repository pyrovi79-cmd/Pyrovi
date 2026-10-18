from fastapi import FastAPI
from pydantic import BaseModel, Field
from torch import nn
import torch
import requests
from fastapi import HTTPException 
from fastapi.middleware.cors import CORSMiddleware
import time
class clima_semanal(BaseModel):
    temp_max_semana: float
    temp_min_semana: float
    precip_semana : float = Field(ge=0)
    temp_prom_max_semana: float

paquete = torch.load("modelo_riesgo.pt", weights_only= False)
red = nn.Sequential(
    nn.Linear(4,8),
    nn.ReLU(),
    nn.Linear(8,1)
)
red.load_state_dict(paquete["pesos"])
red.eval()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"],
    allow_methods=["GET"],
) 

@app.post("/riesgo")
def prediccion(datos: clima_semanal):
    return calcular_riesgos(datos.temp_max_semana,
datos.temp_min_semana,
datos.precip_semana,
datos.temp_prom_max_semana)


coord_zona = {"DMQ":(-0.275,-78.475) , "Junin":(-0.90,-80.175)}
cache_clima = {}
def clima_zona(zona):
    if zona in cache_clima and time.time() - cache_clima[zona][0] < 1800:
            print("usando la libreta")
            return cache_clima[zona][1]
    try:
        
        req_meteo = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={coord_zona[zona][0]}&longitude={coord_zona[zona][1]}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&forecast_days=7&timezone=auto", timeout=6)
        req_meteo.raise_for_status()
        datos = req_meteo.json()
        datos_d = datos["daily"]
        datos_semanal = {"temp_max_semana":max(datos_d["temperature_2m_max"]),
        "temp_min_semana":sum(datos_d["temperature_2m_min"])/len(datos_d["temperature_2m_min"]),
         "precip_semana":sum(datos_d["precipitation_sum"]),
         "temp_prom_max_semana":sum(datos_d["temperature_2m_max"])/len(datos_d["temperature_2m_max"])}
        cache_clima[zona] = (time.time(), datos_semanal)
        return datos_semanal
    except (requests.RequestException, KeyError):
        raise HTTPException(status_code=502, detail="No se pudo obtener el clima") 
def calcular_riesgos(temp_max, temp_min, precip, temp_prom_max):
    datos_ordenados = [temp_max,temp_min,precip,temp_prom_max]
    tensor = torch.tensor([datos_ordenados], dtype= torch.float32)
    media = torch.tensor(paquete["media"])
    desv = torch.tensor(paquete["desv"])
    normalizar = (tensor-media)/desv
    with torch.no_grad():
        logits = red(normalizar)
        probs = torch.sigmoid(logits)
        probabilidad = probs.item()
        pred = (probs > paquete["umbral"])
        riesgo_alto = pred.item()
    if probabilidad > paquete["umbral"]:
        prob_riesgo = "alto"
    elif probabilidad <= paquete["umbral"] and probabilidad >= 0.25:
        prob_riesgo = "medio"
    else :
        prob_riesgo = "bajo"
    return{"probabilidad":round(probabilidad, 3), "riesgo_alto": riesgo_alto, "semaforo": prob_riesgo}

@app.get("/riesgo/{zona}")
def riesgo_zona(zona:str):
    if zona not in coord_zona:
        raise HTTPException(status_code=404, detail="zona no encontrada")  
    datos_zonas = clima_zona(zona)
    riesgos = calcular_riesgos(datos_zonas["temp_max_semana"],datos_zonas["temp_min_semana"],datos_zonas["precip_semana"],datos_zonas["temp_prom_max_semana"])
    return {"zona":zona,"clima":datos_zonas,"riesgo":riesgos}

