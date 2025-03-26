# Obtener datos de un conjunto

Esta función le permite al usuario obtener los datos de un conjunto como un dataframe de la librería pandas.

## Uso

Para obtener los datos de algún conjunto se debe ejecutar una de las siguientes instrucción:

1. Con un conjunto de datos sin filtro:

```bash

from pydataxm.pydatasimem import ReadSIMEM

Dataset_id = "EC6945"
Fecha_Inicio = "2024-01-01"
Fecha_Fin = "2024-12-31"

simem = ReadSIMEM(Dataset_id, Fecha_Inicio, Fecha_Fin)
data = simem.main()
```

2. Con un conjunto de datos con filtros:

```bash

from pydataxm.pydatasimem import ReadSIMEM

Dataset_id = "EC6945"
Fecha_Inicio = "2024-01-01"
Fecha_Fin = "2024-12-31"
Column = "CodigoVariable"
Values = "PB_Nal"

simem = ReadSIMEM(Dataset_id, Fecha_Inicio, Fecha_Fin, Column, Values)
data = simem.main(filter=True)
```
