# Obtener datos

Esta función le permite al usuario obtener los datos como un dataframe de la librería pandas. Este dataframe puede venir indexado de 2 formas según las columnas del conjunto de datos.

## Tipos de dataframe según el índice

1. Indexado por versión y por fecha: Este dataframe contiene las columnas originales que vienen desde el portal SIMEM, pero la columna fecha y la columna versión vienen como índices, además de que la información viene con la versión que el usuario solicito al momento de inicializar el objeto de la clase.
2. Indexado por fecha: En esta caso se devuelve la misma información que en el dataframe con 2 índices anteriormente mencionado, la gran diferencia está en que el conjunto de datos que viene del portal SIMEM no cuenta con una columna versión, por lo que en este caso solamente se indexa por la columna fecha.

## Uso

Para obtener los datos se debe ejecutar la siguiente instrucción:

```bash

CodigoVariable = "PrecioEscasez"
Fecha_Inicio = "2024-01-01"
Fecha_Fin = "2024-12-31"

var = VariableSIMEM(CodigoVariable, Fecha_Inicio, Fecha_Fin)
var.get_data()

```

## Ejemplo

El dataframe que se le devuelve al usuario tiene 2 formatos de salida que dependen del valor que se le asigne al parámetro esCalidad al momento de inicializar el objeto.

1. esCalidad = True: Con este valor el dataframe vendrá con la siguiente estructura

| fecha      | maestra | codigoVariable | codMaestra | valor |
|------------|---------|----------------|------------|-------|
| 2024-12-01 | SISTEMA | PrecioEscasez  | SISTEMA    | 100   |

2. esCalidad = False: Con este valor el dataframe vendrá indexado de la siguiente forma

|            |         | CodigoVariable | Valor | ..... |
|------------|---------|----------------|-------|-------|
| Fecha      | Version |                |       |       |
| 2024-12-01 | TXF     | GReal          | 0.0   | ..... |