# Inicialización de un objeto de la clase

Para poder acceder a las funcionalidades de la clase primero se debe inicializar un objeto de la clase.

## Parámetros

- Dataset_id: Id del conjunto de datos que se desea explorar.
- Fecha_Inicio: Fecha desde la cual se necesita la información.
- Fecha_Fin: Fecha hasta la que se necesita la información.
- Column_destiny (Opcional): Nombre de la columna a la cual se le desea aplicar filtro.
- Var_values (Opcional): Valores del filtro que se desea aplicar.

## Uso

Para inicializar un objeto de la clase hay 2 formas:

1. Inicializar un conjunto de datos sin filtro:

```bash
from pydataxm.pydatasimem import ReadSIMEM

Dataset_id = "EC6945"
Fecha_Inicio = "2024-01-01"
Fecha_Fin = "2024-12-31"

simem = ReadSIMEM(Dataset_id, Fecha_Inicio, Fecha_Fin)
```

2. Inicializar un conjunto de datos con filtros:

```bash
from pydataxm.pydatasimem import ReadSIMEM

Dataset_id = "EC6945"
Fecha_Inicio = "2024-01-01"
Fecha_Fin = "2024-12-31"
Column = "CodigoVariable"
Values = "PB_Nal"

simem = ReadSIMEM(Dataset_id, Fecha_Inicio, Fecha_Fin, Column, Values)
```