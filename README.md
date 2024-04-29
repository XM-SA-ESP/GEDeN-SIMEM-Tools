
# PyDataSIMEM 
![Logo SIMEM](/assets/SIMEM_logo_3.png?raw=true)

## Qué es?
pyDataSIMEM es una herramienta del Sistema de Información del Mercado de Energía Mayorista (SIMEM), que permite al usuario consumir los registros de los catálogos de datos publicados de forma programatica utilizando python. Utilizar esta herramienta simplifica el trabajo para la obtención de información a través del SIMEM.

## Índice <!-- Documentacion de libreria, instalacion de libreria para uso -->
1. Información disponible
2. Parámetros
3. Ejemplo de uso
4. Documentación API

### Información disponible
Los catálogos de datos disponibles se encentran publicados en ["Catálogo de datos y API"](https://www.simem.co/pages/catalogodatos/51FC0A59-3A00-462C-B449-9CB8D5E007FB), cada uno contiene su propio conjunto de variables y rangos de fechas. 

### Parámetros
Para realizar una descarga de información se requieren 3 variables:
* datasetId = identificador único de un conjunto de datos, se puede encontrar en la sección API del conjunto.
* startDate = fecha inicial de la que se desea obtener información
* endDate = fecha finale de la que se desea obtener información
    
    > [!IMPORTANT]
    > Formato de fecha: **YYYY-MM-DD**

### Ejemplo de uso
Crea un objeto de interacción con la API y guarda los registros del conjunto de datos entre las fechas en un archivo CSV
```python
conjunto = PyDataSimem("e007fb", "2024-04-14", "2024-04-16")
dataset_df = conjunto.main()
path = os.getcwd + os.sep + r'demos' + os.sep + f'{object.dataset_id}.csv'
dataset_df.to_csv(path, index=False)
```

### Documentación API
También se puede realizar la consulta utilizando directamente la API. Descarga la [documentación](https://www.simem.co/recursos/Documentacion%20API%20SIMEM.pdf) para ver los ejemplos