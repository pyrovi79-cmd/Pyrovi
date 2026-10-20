from fastapi import FastAPI
from pydantic import BaseModel, Field
from torch import nn
import torch
import requests
from fastapi import HTTPException 
from fastapi.middleware.cors import CORSMiddleware
import time


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
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500","https://pyrovi79-cmd.github.io"],
    allow_methods=["GET"],
) 


coord_zona = {"DMQ":(-0.275,-78.475) , "Junin":(-0.90,-80.175)}
cache_clima = {}
def clima_zona(zona):
    if zona in cache_clima and time.time() - cache_clima[zona][0] < 1800:

            return cache_clima[zona][1]
    try:
        req_meteo = requests.get("https://raw.githubusercontent.com/pyrovi79-cmd/Pyrovi/main/clima.json", timeout=6)
        req_meteo.raise_for_status()
        datos = req_meteo.json()
        datos_semanal = datos[zona]
        cache_clima[zona] = (time.time(), datos_semanal)
        return datos_semanal
    except (requests.RequestException, KeyError)as error:
        print("Error clima:", repr(error))
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

