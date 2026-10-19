# Pyrovi
## Ver en línea
https://pyrovi79-cmd.github.io/Pyrovi/

**Estimación de riesgo de incendios en Ecuador**

## Limitaciones

### Del modelo

- Se priorizó el recall (detectar incendios reales) con un umbral de 0.4, lo que puede generar falsas alarmas.
- El umbral de 0.4 se eligió mirando el conjunto de prueba, por lo que el rendimiento real puede ser menor.
- El modelo no conoce la zona: solo ve el clima de la semana.
- El nivel "medio" (desde 0.25) es una decisión de diseño, no un resultado del modelo.
- la primera carga puede tardar hasta un minuto mientras el servidor despierta

### De los datos

- El conjunto de datos es pequeño: 602 filas (una por zona y semana) con el clima de ambas zonas.
- El clima de entrenamiento es el observado en la misma semana, y en la app se usa un pronóstico.
- Las zonas son rectángulos aproximados, no los límites oficiales.
- No se consideran fenómenos como El Niño y La Niña, entre otros, que pueden alterar el clima.

## Créditos

* **Mapa de fondo:** © [OpenStreetMap](https://www.openstreetmap.org/copyright) contributors.
* **Clima, histórico y pronóstico:** [Weather data by Open-Meteo.com](https://open-meteo.com/), bajo licencia [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Los datos se procesaron en un resumen semanal por zona.
* **Focos de calor:** [NASA FIRMS](https://firms.modaps.eosdis.nasa.gov/) (VIIRS NOAA-20 y S-NPP), usados para entrenar el modelo.
* **Librería del mapa:** [Leaflet](https://leafletjs.com/).
