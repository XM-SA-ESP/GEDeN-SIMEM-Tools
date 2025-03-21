# Obtener colección de variables

Esta función le permite al usuario obtener el listado de variables disponibles que se pueden usar dentro de la clase VariableSIMEM.

## Uso

Para obtener los datos se debe ejecutar la siguiente instrucción:

```bash

from pydataxm.pydatasimem import VariableSIMEM

listado_variables = VariableSIMEM.get_collection()
print(listado_variables)

```

## Ejemplo

El dataframe que se le devuelve al usuario viene de la siguiente forma:

| CodigoVariable | Nombre                   |
|----------------|--------------------------|
| PB_Nal         | Precio de bolsa nacional |
| PrecioEscasez  | Precio de escasez        |
| .............. | ........................ |
