# Complejidad Económica Honduras
Repositorio de la Identificación de Industrias para Honduras

## Descarga del repositorio

Para descargar el repositorio utiliza la instrucción:

```
https://github.com/milocortes/complejidad_economica_honduras.git
```
## Precondiciones de ejecución
El proyecto utiliza [uv](https://docs.astral.sh/uv/) como administrador de proyectos y paquetes. En la siguiente [liga](https://docs.astral.sh/uv/getting-started/installation/) se encuentra los metodos de instalación de uv para los sistemas operativos Windows, macOS y Linux.


## Sincronización del ambiente virtual

Sincronizamos las dependencias en nuestro ambiente virtual con la instrucción:

```bash 
uv sync
```
>Sincronizar (Syncing) es el proceso de instalar las versiones correctas de las dependencias de un lockfile en el ambiente del proyecto.

## Replicación de programas

Para replicar el programa de cálculos de medidas de complejidad ejecuta la siguiente instrucción:

```bash 
uv run marimo edit calculos_complejidad_hnd.py
```

Para replicar el programa de cálculos de los factores de viabilidad y atractivo ejecuta la siguiente instrucción:

```bash 
uv run marimo edit viabilidad_atractivo.py
```

## Catálogo de datos
El proyecto utiliza [Apache Iceberg](https://iceberg.apache.org/) como formato de almacenamiento de tablas. Apache Iceberg define la organización, versionamiento y acceso a un data lake. No cambia la forma como los datos son almacenados a nivel de archivo. En su lugar, agrega una capa de metadatos sobre archivos almacenados (tipicamente en formato Parquet) lo que permite tratar conjuntos de archivos como tablas relacionales coherentes, manteniéndolos al mismo tiempo en almacenamiento de objetos de bajo coste.

Podemos interactuar con la capa de metadatos mediante [PyIceberg](https://py.iceberg.apache.org/), el cual es el cliente oficial de Python de Apache Iceberg. Con PyIceberg, es posible conectarte a un catálogo de Iceberg, crear y gestionar tablas, y realizar operaciones como añadir, sobrescribir y escanear datos, todo ello en Python nativo.

Para consultar los namespace del catálogo, ejecutamos la siguiente instrucción:
> [!IMPORTANT]
> Antes de ejecutar la instrucción es necesario exportar la variable de ambiente ```PYICEBERG_HOME``` a la ruta del repositorio.
> En sistemas operativos macOS y Linux, ejecuta la instrucción:
>
> ```bash
> export PYICEBERG_HOME=$(pwd)
> ```
> En Windows, ejecuta en Powershell la instrucción:
> ```powershell
> $env:PYICEBERG_HOME = $pwd.Path
> ```



> [!NOTE]
>
> Un namespace es una ubicación lógica que agrupa tablas. Es un concepto similar al de un schema en una base de datos.

```bash 
uv run pyiceberg list
```

Para consultar los metadatos de una tabla en un namespace, usa la instrucción:

```bash 
uv run pyiceberg describe complejidad.ocde_sbs
```

### Inspección de Tablas con [TableSleuth](https://tablesleuth.com/)

[TableSleuth](https://tablesleuth.com/) es una herramienta para analizar la estructura de archivos, metadatos, evolución de tablas, etc, para Apache Iceberg.

Para abrir el navegador de TableSleuth como una aplicación web, ejecuta la instrucción : 
```bash 
uv run tablesleuth web
```


