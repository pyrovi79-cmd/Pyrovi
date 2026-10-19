import requests
import json
coord_zona = {"DMQ":(-0.275,-78.475) , "Junin":(-0.90,-80.175)}
resultado={}
for zona in coord_zona:
    req_meteo = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={coord_zona[zona][0]}&longitude={coord_zona[zona][1]}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&forecast_days=7&timezone=auto", timeout=6)
    datos = req_meteo.json()
    req_meteo.raise_for_status()
    datos_d = datos["daily"]
    datos_semanal = {"temp_max_semana":max(datos_d["temperature_2m_max"]),
        "temp_min_semana":sum(datos_d["temperature_2m_min"])/len(datos_d["temperature_2m_min"]),
         "precip_semana":sum(datos_d["precipitation_sum"]),
         "temp_prom_max_semana":sum(datos_d["temperature_2m_max"])/len(datos_d["temperature_2m_max"])}
    resultado[zona] = datos_semanal
with open("clima.json", "w") as archivo:
    json.dump(resultado, archivo)