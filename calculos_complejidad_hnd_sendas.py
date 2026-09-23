import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _(mo):
    mo.md(r"""
    # Complejidad económica de Honduras

    ## Identificación de industrias a partir de datos de empleo sectorial

    **Laboratorio de Desarrollo Regional de la Escuela de Gobierno y Transformación Pública del Tecnológico de Monterrey**

    **Sendas Think Tank**

    Año de referencia: 2019

    Clasificación industrial: Clasificador Internacional Industrial Uniforme (CIIU) Rev. 4 a cuatro dígitos

    ---

    Este documento reproduce, de principio a fin, el cálculo de las medidas de
    complejidad económica para Honduras y la construcción de los portafolios de
    política derivados de esas medidas.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    # 1. Introducción

    ## 1.1 Motivación y objetivo

    La pregunta que organiza este trabajo es operativa: **¿qué actividades
    económicas puede desarrollar Honduras a partir de las capacidades
    productivas que ya tiene?** El enfoque de complejidad económica responde
    observando qué produce cada país y con qué otras actividades coocurre lo que
    produce. Si dos actividades tienden a aparecer juntas en las mismas
    economías, es razonable suponer que exigen capacidades similares — insumos,
    destrezas, instituciones, infraestructura — y que quien domina una está más
    cerca de dominar la otra.

    El ejercicio tiene tres objetivos:

    1. Estimar los indicadores de complejidad económica (ECI, PCI, densidad,
       *complexity outlook gain*) para Honduras y un grupo de economías
       comparables.
    2. Validar que esas estimaciones, construidas sobre datos de **empleo**, son
       consistentes con las estimaciones estándar construidas sobre datos de
       **comercio exterior**.
    3. Derivar portafolios de industrias priorizadas bajo tres estrategias de
       diversificación con distintas escalas de riesgo, desde industrias cercanas hasta saltos largos.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 1.2 Definición de indicadores

    | Indicador | Definición | Lectura |
    |---|---|---|
    | `rca` | Ventaja comparativa revelada. | `rca > 1` indica especialización relativa. |
    | `mcp` | Matriz binaria de especialización. | Define qué actividades tiene cada país y si tiene especialización relativa. |
    | `diversity` | Número de actividades en las que el país está especializado. | Amplitud de la canasta productiva. |
    | `ubiquity` | Número de países especializados en una actividad. | Actividades poco ubicuas exigen más capacidades y viceversa. |
    | `eci` | Índice de complejidad económica del país. | Sofisticación de la estructura productiva. |
    | `pci` | Índice de complejidad de la actividad. | Sofisticación de las capacidades que exige una actividad económica. |
    | `proximity` | Coocurrencia entre pares de actividades. | Cercanía en el espacio de capacidades productivas. |
    | `density` | Proximidad promedio a las actividades que el país ya tiene. | Qué tan al alcance está una actividad dadas las capacidades actuales. |
    | `distance` | `1 - density`. | Qué tan lejos está una actividad. |
    | `cog` | Complexity outlook gain. | Valor estratégico u opción real. |
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1.3 Estructura del documento

    | Sección | Contenido |
    |---|---|
    | 2 | Entorno de trabajo: dependencias y conexión al catálogo |
    | 3 | Inventario de las tablas de datos utilizadas y productos de salida |
    | 4 | Carga, depuración y construcción de datos |
    | 5 | Cálculo de las medidas de complejidad |
    | 6 | Resultados generales: rankings de países y de actividades |
    | 7 | Pruebas de consistencia |
    | 8 | Portafolios de política |
    | 9 | Margen intensivo: lo que Honduras ya produce |
    | 10 | Margen extensivo: oportunidades de diversificación |
    | 11 | Exportación de resultados |
    | 12 | Anexos |

    ## 1.4 Reproducción

    ```bash
    uv sync
    export PYICEBERG_HOME=$(pwd)
    uv run marimo edit calculos_complejidad_hnd.py
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 2. Preparación del entorno

    ## 2.1 Dependencias

    Este bloque carga la librería `marimo`, que estructura el análisis en un entorno de notebook reactivo. El alias `mo` se usa a lo largo del documento para los componentes interactivos y los bloques de texto.
    """)
    return


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Este bloque prepara el entorno de trabajo cargando las dependencias necesarias para procesar datos, calcular indicadores de complejidad económica y presentar resultados en formatos gráficos y tabla.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    | Librería | Función en el análisis |
    |---|---|
    | `polars`, `polars.selectors` | Manipulación de datos |
    | `pandas` | Interoperabilidad con otras dependencias y escritura de Excel |
    | `numpy` | Operaciones numéricas |
    | `ecomplexity` | Cálculo de indicadores de complejidad y de proximidad |
    | `altair` | Visualizaciones |
    | `matplotlib` | Mapas de calor de diagnóstico de cobertura |
    | `great_tables` | Tablas con formato de publicación |
    | `pyiceberg` | Acceso al catálogo de datos del proyecto |
    """)
    return


@app.cell
def _():
    import polars as pl
    import pandas as pd
    import matplotlib.pyplot as plt
    import numpy as np
    from ecomplexity import ecomplexity
    from ecomplexity import proximity
    import altair as alt
    from great_tables import GT, html
    import polars.selectors as cs
    from pyiceberg.catalog import load_catalog


    return alt, cs, ecomplexity, load_catalog, np, pd, pl, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2.2 Conexión al catálogo de datos

    El proyecto almacena sus tablas en formato Apache Iceberg, con un catálogo SQLite local en `warehouse/pyiceberg_catalog.db`. Iceberg agrega una capa de metadatos sobre archivos Parquet, lo que permite tratar conjuntos de archivos como tablas relacionales versionadas.

    | Namespace | Contenido |
    |---|---|
    | `complejidad` | Insumos del análisis: empleo, PIB, población, rankings del Atlas. |
    | `diccionarios` | Catálogos de clasificación CIIU y tablas de recodificación. |
    | `viabilidad_atractivo` | Insumos del análisis complementario de viabilidad y atractivo. |
    """)
    return


@app.cell
def _(load_catalog):
    ### Instancia Catálogo
    warehouse_path = "warehouse"

    catalog = load_catalog(
        "default",
        **{
            'type': 'sql',
            "uri": f"sqlite:///{warehouse_path}/pyiceberg_catalog.db",
            "warehouse": f"{warehouse_path}",
        },
    )
    return (catalog,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2.3 Función auxiliar de carga

    `load_table()` encapsula el patrón de acceso al catálogo: recibe el namespace y el nombre de la tabla, y devuelve un DataFrame de polars ya materializado. Todas las cargas del documento pasan por esta función, salvo las que requieren evaluación diferida.
    """)
    return


@app.cell
def _(catalog, pl):
    ### Función que carga tabla de Apache Iceberg
    def load_table(
        namespace : str, 
        table : str
        ) -> pl.DataFrame:
        return catalog.load_table(f"{namespace}.{table}").to_polars().collect()


    return (load_table,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 3. Inventario de datos

    ## 3.1 Tablas del catálogo utilizadas en el análisis

    El inventario se declara de forma explícita para que cualquier persona que retome el ejercicio sepa, sin leer el código, qué datos se usan, de dónde vienen y en qué parte del análisis entran. Toda tabla nueva debe registrarse en la lista siguiente.
    """)
    return


@app.cell
def _(pl):
    ### Declaración explícita de las tablas que consume este notebook.
    TABLAS_PROYECTO = [
        {
            "namespace": "complejidad",
            "tabla": "ocde_sbs",
            "contenido": "Structural Business Statistics (SBS) de la OCDE: empleo por país, actividad CIIU, tamaño de empresa y año.",
            "rol": "Insumo principal de la matriz país-actividad",
            "seccion": "4.1",
        },
        {
            "namespace": "diccionarios",
            "tabla": "catalogo_ciiu_rev4",
            "contenido": "Catálogo CIIU Rev. 4 con jerarquía sección-división-clase y bandera 'incluye' de selección depurada.",
            "rol": "Define el universo de clases comparables",
            "seccion": "4.4, 9.1, 10.1",
        },
        {
            "namespace": "diccionarios",
            "tabla": "catalogo_ciiu_rev4_nombres",
            "contenido": "Tabla de recodificación entre clasificadores y nombres de actividad.",
            "rol": "Etiquetas de actividad y puente entre clasificadores",
            "seccion": "4.5",
        },
        {
            "namespace": "complejidad",
            "tabla": "actividades_transables",
            "contenido": "Razón de empleo transable por actividad económica.",
            "rol": "Identifica el subconjunto de actividades transables",
            "seccion": "4.5",
        },
        {
            "namespace": "complejidad",
            "tabla": "empleo_honduras_2019",
            "contenido": "Empleo por actividad CIIU a cuatro dígitos para Honduras, 2019.",
            "rol": "Incorpora Honduras a la matriz país-actividad",
            "seccion": "4.6",
        },
        {
            "namespace": "complejidad",
            "tabla": "empleo_slv_2019",
            "contenido": "Empleo por actividad CIIU a cuatro dígitos para El Salvador, 2019.",
            "rol": "País par centroamericano",
            "seccion": "4.6",
        },
        {
            "namespace": "complejidad",
            "tabla": "empleo_ecuador_2019",
            "contenido": "Empleo por actividad CIIU a cuatro dígitos para Ecuador, 2019.",
            "rol": "País par latinoamericano",
            "seccion": "4.6",
        },
        {
            "namespace": "complejidad",
            "tabla": "gdp_mmm_usd",
            "contenido": "PIB en miles de millones de dólares por país y año.",
            "rol": "Prueba de consistencia ECI vs ingreso",
            "seccion": "7.1",
        },
        {
            "namespace": "complejidad",
            "tabla": "population_gnrl_rural",
            "contenido": "Población rural por país y año.",
            "rol": "Denominador del PIB per cápita",
            "seccion": "7.1",
        },
        {
            "namespace": "complejidad",
            "tabla": "population_gnrl_urban",
            "contenido": "Población urbana por país y año.",
            "rol": "Denominador del PIB per cápita",
            "seccion": "7.1",
        },
        {
            "namespace": "complejidad",
            "tabla": "growth_proj_eci_rankings",
            "contenido": "Rankings e índices de complejidad del Atlas of Economic Complexity (Growth Lab, Harvard).",
            "rol": "Referencia externa de validación",
            "seccion": "7.2",
        },
    ]

    inventario_tablas = (
        pl.DataFrame(TABLAS_PROYECTO)
        .with_columns(
            (pl.col("namespace") + "." + pl.col("tabla")).alias("tabla_completa")
        )
        .select("tabla_completa", "contenido", "rol", "seccion")
    )

    inventario_tablas
    return (TABLAS_PROYECTO,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3.2 Metadatos registrados en el catálogo

    Las tablas de Iceberg llevan propiedades de metadatos escritas por `build_iceberg_warehouse.py` y actualizadas por `update_metadata.py` a partir de los archivos YAML del directorio `metadatos/`. El siguiente bloque las lee directamente del catálogo, de modo que la documentación del notebook y la del warehouse no puedan divergir.
    """)
    return


@app.cell
def _(TABLAS_PROYECTO, catalog, pl):
    ### Lee las propiedades de metadatos registradas en el catálogo Iceberg
    def describe_tabla(namespace: str, tabla: str) -> dict:
        clave = f"{namespace}.{tabla}"
        try:
            props = catalog.load_table(clave).properties
        except Exception as exc:
            return {
                "tabla_completa": clave,
                "longname": "No disponible",
                "descripcion": f"No disponible ({type(exc).__name__})",
                "url": "",
            }

        return {
            "tabla_completa": clave,
            "longname": props.get("longname", ""),
            "descripcion": props.get("description", ""),
            "url": props.get("url", ""),
        }


    catalogo_metadatos = pl.DataFrame(
        [describe_tabla(t["namespace"], t["tabla"]) for t in TABLAS_PROYECTO]
    )

    catalogo_metadatos
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3.3 Fuentes externas al catálogo

    | Ruta | Formato | Contenido |
    |---|---|---|
    | `datos/hs92_country_product_year_4` | Delta Lake | Exportaciones por país, producto HS92 a cuatro dígitos y año, del Atlas of Economic Complexity. |

    ## 3.4 Productos de salida

    | Ruta | Formato | Contenido |
    |---|---|---|
    | `complejidad.cdata` | Iceberg | Medidas de complejidad por país, actividad CIIU Rev. 4 y año: RCA, MCP, diversidad, ubicuidad, ECI, PCI, densidad, distancia, COI y COG. |
    | `datos/seleccion_final_complexity.xlsx` | XLSX | Universo de actividades, margen intensivo y margen extensivo. |
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 4. Carga y preparación de datos

    Este apartado va de la base original de la OCDE a una matriz país-actividad depurada y comparable, pasando por tres filtros sucesivos: cobertura temporal, universo de clases CIIU y condición de transabilidad.

    ## 4.1 Base de empleo: OCDE Structural Business Statistics

    La consulta permite filtrar la variable `Employees` y seleccionar las columnas relevantes antes de materializar los datos. Luego se conservan solo actividades codificadas a cuatro dígitos de la CIIU: se identifican los códigos `ACTIVITY` con una letra inicial de sección seguida de cuatro caracteres numéricos, la letra se guarda en `seccion` y el código se estandariza dejando los cuatro dígitos.
    """)
    return


@app.cell
def _(catalog, pl):
    ### Cargamos datos de OCDE SBS
    ocde_sbs = catalog.load_table("complejidad.ocde_sbs")

    df = (
        pl.scan_iceberg(ocde_sbs)
        .filter(pl.col("Measure") == "Employees")
        .select("REF_AREA", "ACTIVITY", "SIZE_CLASS", "OBS_VALUE", "TIME_PERIOD")
        .collect()
    )

    ### Lo convertimos a pandas
    df = df.to_pandas()

    ### Nos quedamos con las actividades a 4 dígitos del CIIU
    df = df[df["ACTIVITY"].apply(lambda x: len(x) == 5)]

    ### Define función que evalúa si los últimos 4 caracteres son numéricos
    test_numericos = lambda cadena: all([i.isnumeric() for i in list(cadena)])

    df = df[df["ACTIVITY"].apply(lambda x: test_numericos(x[1:]))]

    ### Obtén sección
    df["seccion"] = df["ACTIVITY"].apply(lambda x: x[0])
    df["ACTIVITY"] = df["ACTIVITY"].apply(lambda x: x[1:])

    df
    return (df,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4.2 Análisis de cobertura de los datos
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    En el siguiente bloque se construye un resumen anual de la cobertura de la base `df`, contando el número de registros disponibles por sección de actividad económica. Para ello, identifica el rango de años en `TIME_PERIOD`, filtra la base año por año y calcula la frecuencia de observaciones asociadas a cada valor de `seccion`.

    Como resultado, se obtiene el DataFrame `resumen_seccion_conteos`, donde cada fila representa un año, las columnas de secciones indican el número de registros observados por sección económica y la columna `Total` resume el número total de registros disponibles en ese año. Esta tabla sirve como control de calidad para evaluar la cobertura temporal y sectorial de la información antes de continuar con el análisis.
    """)
    return


@app.cell
def _(df, pd):
    ### Resume conteos de registros por sección
    acumula = []

    anio_min = df["TIME_PERIOD"].min()
    anio_max = df["TIME_PERIOD"].max()

    for i in range(anio_min, anio_max+1):
        consulta = df.query(f"TIME_PERIOD=={i}")["seccion"].value_counts().to_frame().T
        consulta["Total"] = consulta.sum(axis = 1)
        consulta["year"] = i
        acumula.append(consulta)

    resumen_seccion_conteos = pd.concat(acumula)
    resumen_seccion_conteos
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    La tabla `resumen_seccion_conteos` permite evaluar la cobertura anual de la base por sección económica. Los valores `NaN` indican que en ese año no se encontraron registros para una sección específica, mientras que la columna `Total` resume el número total de observaciones disponibles para cada año.

    Aunque los años 2021 y 2022 presentan un mayor número total de registros, 2019 puede considerarse el año con mejor cobertura sectorial balanceada dentro del período reciente. Esto se debe a que combina un volumen alto de observaciones con una distribución más estable entre secciones económicas, evitando que la cobertura esté concentrada en pocas secciones específicas.

    Además, al ser un año reciente previo a las posibles alteraciones observadas después de 2020, ofrece una base más adecuada para realizar comparaciones sectoriales y continuar el análisis con mayor consistencia.

    La siguiente visualización con presenta los valores de la tabla anterior en forma de mapa de calor, usando una transformación logarítmica para facilitar la comparación visual entre sectores con distintos niveles de empleo.

    El gráfico resultante permite revisar la distribución temporal y sectorial del empleo agregado, identificar años con mayor cobertura efectiva y detectar secciones económicas con valores relativamente altos o bajos dentro de la base.
    """)
    return


@app.cell
def _(df, np, plt):
    ## Resumen de empleo total por seccion

    resumen_empleo_anios = df.groupby(
        ["TIME_PERIOD", "seccion"]
    ).agg({"OBS_VALUE": "sum"}).reset_index().pivot(
        index="TIME_PERIOD",
        columns="seccion",
        values="OBS_VALUE"
    )

    plt.figure(figsize=(10, 8))

    plt.imshow(np.log(resumen_empleo_anios.to_numpy()))

    plt.xticks(
        ticks=np.arange(len(resumen_empleo_anios.columns)),
        labels=resumen_empleo_anios.columns
    )

    plt.yticks(
        ticks=np.arange(len(resumen_empleo_anios.index)),
        labels=resumen_empleo_anios.index
    )

    plt.xlabel("Sección económica")
    plt.ylabel("Año")
    plt.title("Empleo agregado por año y sección económica")
    plt.colorbar(label="Logaritmo del empleo agregado")

    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4.3 Cobertura por país

    La cobertura se mide como el número de actividades a cuatro dígitos con empleo positivo en cada combinación país-año. Se filtran las observaciones con `OBS_VALUE > 0`, se agrupa por año, país y actividad, y se cuenta el número de actividades distintas por país y año.

    Luego, la información se agrupa por `TIME_PERIOD`, `REF_AREA` y `ACTIVITY` para consolidar los registros de cada actividad dentro de un mismo país y año. Posteriormente, se cuenta el número de actividades distintas por país y año, generando el DataFrame `cobertura_pais_anio`. En esta tabla, la variable `cobertura` indica cuántas actividades económicas presentan empleo positivo para cada combinación país-año.

    A partir de esta tabla, se construye una matriz donde las filas representan países, las columnas representan años y los valores corresponden al número de actividades económicas con empleo positivo. Esta matriz se visualiza mediante un mapa de calor, lo que permite revisar de manera directa la evolución de la cobertura de la base en el tiempo y entre países.
    """)
    return


@app.cell
def _(df):
    # Calcula cobertura por año, país y sección
    # Cobertura = número de actividades económicas con empleo positivo
    cobertura_pais_anio = (
        df.query("OBS_VALUE > 0")
        .groupby(["TIME_PERIOD", "REF_AREA", "ACTIVITY"])
        .agg({"OBS_VALUE": "sum"})
        .reset_index()
        .groupby(["TIME_PERIOD", "REF_AREA"])
        .agg({"ACTIVITY": "count"})
        .reset_index()
        .rename(columns={"ACTIVITY": "cobertura"})
    )

    cobertura_pais_anio
    return (cobertura_pais_anio,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    El mapa de calor muestra que la cobertura no es homogénea durante todo el período. Antes de 2008, la información aparece de forma limitada y concentrada en pocos países. A partir de 2008, la cobertura aumenta considerablemente y se observa una mayor cantidad de países con un número alto de actividades reportadas. Sin embargo, los años posteriores a 2020 muestran cambios importantes en la cobertura, con reducciones en el número de actividades económicas reportadas para la mayoría de países.

    Con base en estos resultados, 2019 se selecciona como año de referencia porque combina una cobertura alta con una estructura relativamente estable entre países.
    """)
    return


@app.cell
def _(cobertura_pais_anio, np, plt):
    # Matriz país-año para el mapa de calor

    matriz_cobertura_pais_anio = (
        cobertura_pais_anio
        .pivot(
            index="REF_AREA",
            columns="TIME_PERIOD",
            values="cobertura"
        )
        .sort_index()
    )

    plt.figure(figsize=(14, 10))

    plt.imshow(
        matriz_cobertura_pais_anio.to_numpy(),
        aspect="auto"
    )

    plt.xticks(
        ticks=np.arange(len(matriz_cobertura_pais_anio.columns)),
        labels=matriz_cobertura_pais_anio.columns,
        rotation=90
    )

    plt.yticks(
        ticks=np.arange(len(matriz_cobertura_pais_anio.index)),
        labels=matriz_cobertura_pais_anio.index
    )

    plt.xlabel("Año")
    plt.ylabel("País")
    plt.title("Cobertura de actividades económicas con empleo positivo por país y año")

    plt.colorbar(label="Número de actividades con empleo positivo")

    plt.tight_layout()
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4.4 Universo de clases CIIU comparables

    Se carga la selección depurada desde `diccionarios.catalogo_ciiu_rev4`, filtrando las clases con `incluye == 1`.

    Esta selección excluye actividades con baja comparabilidad entre países. En particular, se retiran actividades que aparecen listadas únicamente en la información de Honduras o actividades reportadas por un número muy reducido de países de la OCDE. Con ello, se define un universo de clases CIIU más consistente para el análisis comparativo. Debido a lo anterior, salen del análisis las secciones:

    A) Agricultura, ganadería, silvicultura y pesca

    B) Explotación de minas y canteras (parcialmente)

    K) Actividades financieras y de seguros

    O) Administración pública y defensa; planes de seguridad social de afiliación obligatoria

    P) Enseñanza

    Q) Actividades de atención de la salud humana y de asistencia social

    R) Actividades artísticas, de entretenimiento y recreativas

    S) Otras actividades de servicios (parcialmente)

    T) Actividades de los hogares como empleadores y actividades no diferenciadas de los hogares como productores de bienes y servicios para uso propio

    U) Actividades de organizaciones y órganos extraterritoriales.


    Los códigos se estandarizan a cuatro dígitos con ceros a la izquierda, para que sean compatibles con la variable `ACTIVITY` de la base principal. El resultado son 305 actividades económicas.
    """)
    return


@app.cell
def _(load_table):
    ### Cargamos selección de industrias 
    ciiu_industrias_seleccionadas = load_table(
                    "diccionarios", "catalogo_ciiu_rev4"
                    ).to_pandas().query("incluye==1")[
                        ["clase_codigo", "clase_titulo"]
                    ]
    ### Formato de clave ciiu 04d
    ciiu_industrias_seleccionadas["clase_codigo"] = ciiu_industrias_seleccionadas["clase_codigo"].apply(lambda x : f"{x:04}")

    ### Lista de Actividades CIIU a considerar
    ciiu_seleccion = ciiu_industrias_seleccionadas["clase_codigo"].to_list()

    ciiu_industrias_seleccionadas
    return (ciiu_seleccion,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4.5 Actividades transables y cobertura por país

    La definición de transables proviene de `complejidad.actividades_transables`, conservando las que tienen `razon_emp_transables > 0`, lo que da 263 actividades. Estos códigos se cruzan con la tabla de recodificación `diccionarios.catalogo_ciiu_rev4_nombres` y se estandarizan a cuatro dígitos.

    Luego la base se filtra a 2019, a las actividades transables y a observaciones con `OBS_VALUE > 0`; se agrega por país y actividad, y se cuenta cuántas actividades transables reporta cada país. La columna `ACTIVITY` del resultado expresa esa cuenta como proporción del total de actividades transables consideradas.
    """)
    return


@app.cell
def _(df, load_table, pl):
    ### Consulta para verificar la cantidad de actividades en 2019 con valores mayores a 0
    # Cargamos recodificación
    recod = load_table("diccionarios", "catalogo_ciiu_rev4_nombres").to_pandas()

    ## Diccionario CIIU 4 a nombres
    mapp_ciiu = pl.from_pandas(recod.query("clasificador=='ciiu_rev_4'")[["codigo", "nombre_actividad"]].astype(str))

    # Cargamos transables 
    transables = load_table("complejidad", "actividades_transables").to_pandas().query("razon_emp_transables > 0")

    recod = recod[recod["codigo_nuevo"].isin(transables["actividad"])]
    ciiu_transable = recod.query("clasificador =='ciiu_rev_4'")["codigo"].unique()
    ciiu_transable = [f"{i:04}" for i in ciiu_transable]

    ## Nos quedamos con las actividades transables
    df_actividades_transables = (
                            df
                            .query("TIME_PERIOD == 2019")
                            .query(f"ACTIVITY in {ciiu_transable}")
                            .query("OBS_VALUE>0")
                            .groupby(["REF_AREA", "ACTIVITY"])
                            .agg({"OBS_VALUE" : "sum"})
                            .reset_index()
                            .groupby("REF_AREA")
                            .agg({"ACTIVITY" : "count"})    
    )



    df_actividades_transables["ACTIVITY"] = df_actividades_transables["ACTIVITY"]/len(ciiu_transable)

    df_actividades_transables
    return ciiu_transable, df_actividades_transables, mapp_ciiu


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Se observa que varios países presentan una cobertura alta, como `ROU`, `DEU`, `HRV`, `LVA`, `ITA`, `NOR`, `ESP` y `KOR`, con valores cercanos o superiores al 80% del total de actividades transables. Esto indica que estos países reportan información para una parte amplia del universo transable, lo que favorece su uso en análisis comparativos.

    En contraste, países como `EST`, `JPN`, `CRI` y `LUX` presentan coberturas reducidas. Estos casos reportan una proporción baja de actividades transables con empleo positivo, por lo que su inclusión en comparaciones debe evaluarse con cuidado. Una cobertura limitada puede afectar la representatividad del análisis y generar resultados menos comparables frente a países con mayor disponibilidad de información.
    """)
    return


@app.cell
def _(df_actividades_transables):
    df_actividades_transables.sort_values(by="ACTIVITY", ascending=False).plot.bar()
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 4.6 Construcción de la tabla de insumos

    Este bloque aplica en secuencia todos los filtros y arma la matriz país-actividad definitiva: conserva los países cuya cobertura de transables supera el umbral de 0.69, filtra al año de análisis, mantiene las actividades que están tanto en la selección depurada como en el universo transable, retira la CIIU 1910 y se queda con los registros de `SIZE_CLASS == '_T'`, el total de la actividad. Quedan 213 actividades.

    Sobre ese universo se incorporan las bases propias de Honduras, El Salvador y Ecuador, estandarizando sus códigos a cuatro dígitos y restringiéndolas a las actividades presentes en la muestra. El resultado final es el DataFrame `insumos_complejidad`, que contiene una base consolidada de empleo por país y actividad económica para 2019 para 21 economías y 213 actividades.
    """)
    return


@app.cell
def _(
    ciiu_seleccion,
    ciiu_transable,
    df,
    df_actividades_transables,
    load_table,
    pd,
):
    ### Haremos el análisis de complejidad modificando la muestra de paises de acuerdo al umbral de la razón de actividades que reportan empleo vs total de actividades transables

    ### Que actividades no tenemos datos para los paises? Dato atípico
    ciiu_na = [
        "1910", # Fabricación de productos de hornos de coque
    ]

    ### Define umbral para la selección de la muestra de países
    umbral = 0.69
    anio_analisis = 2019

    ### Obten países por encima del umbral
    paises_muestra = df_actividades_transables.reset_index().query(f"ACTIVITY>{umbral}")["REF_AREA"].to_list()

    ### Filtra los datos que cumplen con el criterio
    insumos_complejidad = (
                    df
                        # Filtra periodo de análisis
                        .query(f"TIME_PERIOD == {anio_analisis}")
                        # Filtra selección
                        .query(f"ACTIVITY in {ciiu_seleccion}")
                        # Filtra por actividades transables
                        .query(f"ACTIVITY in {ciiu_transable}")
                        # Filtra países muestra
                        .query(f"REF_AREA in {paises_muestra}")
                        # Excluye industrias seleccionadas manualmente
                        .query(f"ACTIVITY not in {ciiu_na}")    
                        # Filtramos por el total de la actividad
                        .query(f"SIZE_CLASS == '_T'")      
    )

    insumos_complejidad = insumos_complejidad[["TIME_PERIOD", "REF_AREA", "ACTIVITY", "OBS_VALUE"]]

    muestra_actividades = list(insumos_complejidad["ACTIVITY"].unique())

    ### Cargamos Honduras
    hnd = load_table("complejidad", "empleo_honduras_2019").to_pandas()
    hnd["ACTIVITY"] = hnd["ACTIVITY"].apply(lambda x : f"{x:04}")
    hnd = hnd.query(f"ACTIVITY in {muestra_actividades}")

    ### Cargamos a El Salvador
    slv = load_table("complejidad", "empleo_slv_2019").to_pandas()
    slv["ACTIVITY"] = slv["ACTIVITY"].astype(str)
    slv = slv.query(f"ACTIVITY in {muestra_actividades}")

    ### Cargamos a Ecuador
    ecu = load_table("complejidad", "empleo_ecuador_2019").to_pandas()
    ecu["ACTIVITY"] = ecu["ACTIVITY"].astype(str)
    ecu = ecu.query(f"ACTIVITY in {muestra_actividades}")

    ### Concatenamos datos de paises no considerados en los datos de OCDE 
    insumos_complejidad = pd.concat([insumos_complejidad, hnd, slv, ecu])

    insumos_complejidad
    return anio_analisis, insumos_complejidad, paises_muestra


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 5. Cálculo de las medidas de complejidad

    ## 5.1 Indicadores de complejidad económica

    El diccionario `trade_cols` indica a `ecomplexity()` qué columnas corresponden al año, país, actividad y valor observado. La función construye la matriz país-actividad a partir del empleo y estima los indicadores descritos en la Sección 1.2. El resultado se convierte a polars y se eliminan observaciones nulas, para conservar únicamente combinaciones con indicadores completos.

    Se agrega `distance` como `1 - density`: valores bajos indican actividades cercanas a las capacidades existentes del país, valores altos indican actividades más alejadas.

    El resultado es el DataFrame `cdata`, que contiene indicadores de complejidad económica por país y actividad. Esta tabla sirve como base para identificar actividades con mayor o menor complejidad, así como oportunidades productivas más cercanas o más distantes para cada país.
    """)
    return


@app.cell
def _(ecomplexity, insumos_complejidad, pl):
    # Calculate complexity
    trade_cols = {'time':"TIME_PERIOD", 'loc': "REF_AREA",  'prod': "ACTIVITY",  'val': "OBS_VALUE"}
    cdata = pl.from_pandas(ecomplexity(insumos_complejidad, trade_cols)).drop_nulls()
    cdata = cdata.with_columns(
        distance = 1 -pl.col("density")
    )
    cdata
    return (cdata,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 6. Resultados generales

    ## 6.1 Ranking de países según el ECI

    Se selecciona una observación única por país, se ordenan los valores de `eci` de mayor a menor y se asigna una posición ordinal.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    A partir de los indicadores calculados en `cdata`, se construye un ranking de países según el índice de complejidad económica (`eci`). Para ello, se selecciona una observación única por país, se ordenan los valores de `eci` de mayor a menor y se asigna una posición ordinal mediante `rank()`.

    El resultado es el DataFrame `eci_paises`, que contiene el código de país (`REF_AREA`), el valor del índice de complejidad económica y su posición en el ranking. Esta tabla permite identificar qué países presentan estructuras productivas más complejas dentro de la muestra analizada. El país que ocupa el primer lugar en el ranking es Alemania, mientras que Honduras ocupa la posición 20 (el penúltimo de la lista).
    """)
    return


@app.cell
def _(cdata, pl):
    ### Ranking de Países de acuerdo a ECI
    eci_paises = cdata.select("REF_AREA", "eci").unique().sort("eci", descending=True)
    eci_paises = eci_paises.with_columns(
        eci_rank = pl.col("eci").rank("ordinal", descending=True)
    )
    eci_paises
    return (eci_paises,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6.2 Ranking de actividades según el PCI

    El mismo ejercicio para actividades económicas: `pci` las ordena según su nivel relativo de complejidad dentro de la matriz país-actividad. El resultado se cruza con el diccionario CIIU para incorporar nombres y con la base original para agregar la sección económica.

    El resultado es el DataFrame `pci_industrias`, que contiene las actividades económicas ordenadas de mayor a menor complejidad. Esta tabla sirve para identificar las industrias más complejas del universo analizado y para relacionar los resultados de complejidad con la clasificación sectorial CIIU. La industria más compleja del listado es "fabricación de vehículos automotores", mientras que la menos compleja es "fabricación de otros productos de madera".
    """)
    return


@app.cell
def _(cdata, df, mapp_ciiu, pl):
    pci_industrias = (
        cdata.select("ACTIVITY", "pci")
        .with_columns(
            pl.col("ACTIVITY")
            .cast(pl.Utf8)
            .str.zfill(4)
        )
        .join(
            mapp_ciiu.with_columns(
                pl.col("codigo")
                .cast(pl.Utf8)
                .str.zfill(4)
            ),
            left_on="ACTIVITY",
            right_on="codigo"
        )
        .unique()
        .drop_nulls()
        .join(
            pl.from_pandas(df)
            .with_columns(
                pl.col("ACTIVITY")
                .cast(pl.Utf8)
                .str.zfill(4)
            )
            .select("ACTIVITY", "seccion")
            .unique(),
            on="ACTIVITY",
        )
        .sort("pci", descending=True)
    )

    pci_industrias
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 7. Pruebas de consistencia

    El uso de empleo en lugar de exportaciones es una de las decisiones metodológicas más fuertes del ejercicio.

    Esta sección la somete a tres pruebas: la relación del ECI con el ingreso per cápita, la comparación con el ECI del Atlas de Complejidad Económica, y el recálculo de los indicadores con exportaciones para la misma muestra de países.

    ## 7.1 Complejidad e ingreso per cápita

    La población total es la suma de la población rural y urbana, y se integra con la base de PIB usando `Year`, `Nation` e `iso_code3` como llaves. El PIB per cápita divide el PIB en dólares entre la población total, por lo que `gdp_mmm_usd` se multiplica por 1 000 000 antes de la división.

    El resultado es el DataFrame `gdp`, que contiene el PIB, la población total y el PIB per cápita para cada país disponible. El PIB per cápita se calcula dividiendo el PIB expresado en dólares entre la población total, por lo que se multiplica `gdp_mmm_usd` por `1_000_000` antes de realizar la división.
    """)
    return


@app.cell
def _(anio_analisis, load_table):
    ## Cargamos GDP
    gdp = load_table("complejidad", "gdp_mmm_usd").to_pandas().query(f"Year=={anio_analisis}")

    ## Cargamos poblacion rural
    pob_rural = load_table("complejidad", "population_gnrl_rural").to_pandas().query(f"Year=={anio_analisis}")

    ## Cargamos poblacion urbana
    pob_urbana = load_table("complejidad", "population_gnrl_urban").to_pandas().query(f"Year=={anio_analisis}")

    ## Reunimos población
    pob = pob_rural.merge(
        pob_urbana,
        on = ["Year","Nation","iso_code3"], 
    )
    pob["poblacion"] = pob["population_gnrl_rural"] + pob["population_gnrl_urban"]

    gdp = gdp.merge(
        pob, 
        on = ["Year","Nation","iso_code3"], 
    )
    gdp["gdp_percapita"] = (gdp["gdp_mmm_usd"]/gdp["poblacion"])*1_000_000
    gdp
    return (gdp,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    El siguiente gráfico muestra la correlación positiva que existe entre el `eci` y el `PIB per cápita`.

    La correlación entre ECI y PIB per cápita es positiva, como predice la teoría. Honduras, entre las economías pares y aspiracionales comparadas, ocupa la última posición en ingreso por habitante y la penúltima en complejidad económica.
    """)
    return


@app.cell
def _(alt, eci_paises, gdp, pl):
    ### Gráficas de dispersion para GDP
    eci_paises_gdp = eci_paises.join(
        pl.from_pandas(gdp),
        left_on="REF_AREA", 
        right_on = "iso_code3"
    )

    gdp_vs_eci = (
        alt.Chart(eci_paises_gdp)
        .mark_circle(
            opacity=0.99,
            stroke="black",
            strokeWidth=1.2,
            strokeOpacity=0.9,
            size=180
        )
        .encode(
            x=alt.X("gdp_percapita:Q").title(
                "GDP Per Cápita [Miles de Dólares por persona]"
            ),
            y=alt.Y("eci:Q").title("ECI"),
            color=alt.ColorValue("red"),
            tooltip=[
                "REF_AREA",
                "gdp_percapita",
                "eci"
            ]
        )
    )

    gdp_vs_eci_reg_line = (
        gdp_vs_eci
        .transform_regression(
            "gdp_percapita",
            "eci"
        )
        .mark_line(size=5)
        .transform_calculate(
            Fit='"LinReg"'
        )
        .encode(
            stroke="Fit:N"
        )
    )

    labels_iso_code3 = gdp_vs_eci.mark_text(
        align="left",
        baseline="middle",
        dx=10,
        fontSize=12
    ).encode(
        text="REF_AREA",
        color=alt.ColorValue("black")
    )

    gdp_vs_eci_chart = (
        (
            gdp_vs_eci
            + gdp_vs_eci_reg_line
            + labels_iso_code3
        )
        .properties(
            width=900,
            height=600,
            title=alt.TitleParams(
                "GDP per cápita vs ECI",
                subtitle="Datos de Empleo de OECD SBS 2019",
                subtitleColor="gray"
            )
        )
        .interactive()
        .configure_legend(
            strokeColor="gray",
            fillColor="#EEEEEE",
            padding=6,
            cornerRadius=6,
            orient="top-left",
            labelFontSize=10,
            titleFontSize=11,
            symbolSize=80,
            labelLimit=120
        )
    )

    gdp_vs_eci_chart
    return (eci_paises_gdp,)


@app.cell
def _(mo):
    mo.md(r"""
    ## 7.2 Contraste con el Atlas de Complejidad Económica

    Se carga `complejidad.growth_proj_eci_rankings`, del Atlas of Economic Complexity del Growth Lab de Harvard, filtrada al año de referencia. Es la referencia externa contra la cual se contrastan los resultados obtenidos con datos de empleo.

    El resultado es el DataFrame `atlas`, que contiene rankings e indicadores de complejidad económica reportados por el Atlas para 2019. Esta base se utiliza como referencia externa para contrastar los resultados obtenidos con la metodología aplicada sobre los datos de empleo por actividad económica.
    """)
    return


@app.cell
def _(load_table, pl):
    ### Carga datos del atlas del ranking
    atlas = load_table("complejidad", "growth_proj_eci_rankings").filter(
        pl.col("year") == 2019
    )
    atlas
    return (atlas,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Se construye una base comparativa que integra dos medidas de complejidad económica: el `ECI` calculado a partir de empleo en actividades económicas de `OECD SBS` y el `ECI` reportado por el Atlas de Complejidad Económica. Ambas medidas se integran usando el código ISO3 del país como llave.

    La información se transforma a formato largo mediante `unpivot()`, lo que permite representar ambas fuentes de `ECI` dentro de una misma estructura de datos. Posteriormente, se incorpora el PIB per cápita calculado previamente, generando una base con país, fuente del indicador, valor de `ECI` y nivel de ingreso por persona.

    La visualización compara el PIB per cápita con el `ECI` para ambas fuentes. Los resultados muestran que los cálculos de complejidad usando información de empleo guardan consistencia con los que se nutren de datos de comercio exterior. Aunque los primeros, de manera sistemática arrojan puntajes más bajos.
    """)
    return


@app.cell
def _(alt, atlas, cs, eci_paises_gdp, gdp, pl):
    ### Dibujemos los puntos de acuerdo al GDP y el ECI de empleo y del atlas
    ## Pegamos ECI del atlas
    eci_paises_gdp_empleo_atlas = (
        eci_paises_gdp.select("REF_AREA", "eci")
        .rename({"REF_AREA": "country_iso3_code", "eci": "ECI Empleo OECD SBS"})
        .join(
            atlas.select("country_iso3_code", "eci_hs12").rename({"eci_hs12": "ECI Atlas"}),
            on="country_iso3_code",
        )
        .unpivot(cs.numeric(), index="country_iso3_code")
        .join(
            pl.from_pandas(gdp)
            .select("iso_code3", "gdp_percapita")
            .rename({"iso_code3": "country_iso3_code"}),
            on="country_iso3_code",
        )
    )

    # 1. Define the base chart with encodings
    base = (
        alt.Chart(eci_paises_gdp_empleo_atlas)
        .encode(
            x=alt.X("gdp_percapita:Q").title("GDP Percapita [Miles de Dólares por persona]"),
            y=alt.Y("value:Q").title("ECI"),
            color=alt.Color("variable:N").title("Datos"),
        )
        .properties(
            title=alt.TitleParams(
                "GDP percapita vs ECI",
                subtitle="Datos de Empleo de OECD SBS 2019 y Atlas de Complejidad",
                subtitleColor="gray",
            )
        )
    )

    # Gráfico 1: PIB per cápita vs indicador de complejidad

    chart = (
        base.mark_circle(
            opacity=0.99,
            stroke="black",
            strokeWidth=1.2,
            strokeOpacity=0.9,
            size=280,
        )
        .encode(
            tooltip=[
                "country_iso3_code",
                "gdp_percapita",
                "value",
                "variable",
            ]
        )
        +
        base.transform_regression(
            "gdp_percapita",
            "value",
            groupby=["variable"]
        ).mark_line()
    )

    labels_iso_code3_eci = base.mark_text(
        align="left",
        baseline="middle",
        dx=15,
        fontSize=12,
    ).encode(
        text="country_iso3_code",
        color=alt.ColorValue("black"),
    )

    all_chart = (
        (chart + labels_iso_code3_eci)
        .properties(
            width=900,
            height=600
        )
        .interactive()
        .configure_legend(
            strokeColor="gray",
            fillColor="#EEEEEE",
            padding=6,
            cornerRadius=6,
            orient="top-left",
            labelFontSize=10,
            titleFontSize=11,
            symbolSize=80,
            labelLimit=120
        )
    )

    all_chart
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7.3 Recálculo del ECI con exportaciones

    La siguiente prueba consiste en recalcular la complejidad con datos de exportaciones, manteniendo la misma muestra de países. Se carga la base Delta `datos/hs92_country_product_year_4` y se filtra a los países seleccionados por cobertura, incorporando a Honduras, Ecuador y El Salvador, lo que deja la muestra final de 21 economías.

    `ecomplexity()` se aplica sobre la matriz país-producto construida con valores de exportación. El resultado se depura y se reduce a una observación única por país, con `eci` renombrado como `eci_atlas`.
    """)
    return


@app.cell
def _(ecomplexity, paises_muestra, pl):
    ### Cacularemos las medidas de complejidad usando los datos del Atlas
    ### PARA LA MUESTRA DE 21 PAISES
    atlas_export = pl.scan_delta("datos/hs92_country_product_year_4").filter(
        pl.col("country_iso3_code").is_in(paises_muestra + ['HND', 'ECU', 'SLV'])
    )
    atlas_export = atlas_export.collect().to_pandas()

    # Calculate complexity
    trade_cols_export = {'time':"year", 'loc': "country_iso3_code",  'prod': "product_hs92_code",  'val': "export_value"}
    cdata_export = pl.from_pandas(ecomplexity(atlas_export, trade_cols_export)).drop_nulls()
    cdata_export = cdata_export.select("country_iso3_code", "eci").unique().rename({"eci" : "eci_atlas"})
    cdata_export
    return (cdata_export,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7.4 Comparación de rankings

    Para cada fuente se construye un ranking ordinal, lo que permite comparar la posición relativa de cada país bajo ambos enfoques. La tabla `cdata_atlas_estimado` reúne el código del país, el `eci` con su ranking basado en empleo, y el `eci_atlas` con su ranking basado en exportaciones.

    La figura compara ambos rankings mediante un diagrama de dispersión. El eje horizontal muestra el ranking de complejidad basado en `OECD SBS`, mientras que el eje vertical muestra el ranking derivado del Atlas. Cada punto representa un país y se incorpora una línea de identidad como referencia visual. Los países ubicados cerca de esa línea presentan posiciones similares en ambos rankings, mientras que los casos alejados reflejan discrepancias entre la complejidad estimada a partir del empleo y la complejidad estimada a partir de exportaciones.

    El resultado corrobora la existencia de una correlación positiva entre ambos rankings.
    """)
    return


@app.cell
def _(alt, cdata, cdata_export, pl):
    ### Reunimos los datos
    cdata_atlas_estimado = cdata.select(
        "REF_AREA", "eci"
    ).unique().rename(
        {"REF_AREA" : "country_iso3_code"}
    ).with_columns(
        eci_rank = pl.col("eci").rank("ordinal", descending=True)
    ).join(
        cdata_export.with_columns(
        eci_rank_atlas = pl.col("eci_atlas").rank("ordinal", descending=True)
    ), 
        on = "country_iso3_code"
    )

    ### Dibujamos la figura
    # Gráfico de comparación de rankings

    base_rankings = (
        alt.Chart(cdata_atlas_estimado)
        .mark_circle(
            opacity=0.99,
            stroke="black",
            strokeWidth=1.2,
            strokeOpacity=0.9,
            size=220
        )
        .encode(
            x=alt.X("eci_rank:Q").title("Ranking ECI OECD SBS"),
            y=alt.Y("eci_rank_atlas:Q").title("Ranking ECI Atlas"),
            color=alt.ColorValue("red"),
            tooltip=[
                "country_iso3_code",
                "eci_rank",
                "eci_rank_atlas"
            ]
        )
    )

    base_rankings_reg_line = (
        base_rankings
        .transform_regression(
            "eci_rank",
            "eci_rank_atlas"
        )
        .mark_line(size=5)
        .transform_calculate(
            Fit='"LinReg"'
        )
        .encode(
            stroke="Fit:N"
        )
    )

    labels_iso_code3_rankings = base_rankings.mark_text(
        align="left",
        baseline="middle",
        dx=10,
        fontSize=12,
    ).encode(
        text="country_iso3_code",
        color=alt.ColorValue("black"),
    )

    line_red = (
        alt.Chart()
        .mark_rule(
            color="red",
            size=5
        )
        .transform_calculate(
            Fit='"Identidad f(x) = x"'
        )
        .encode(
            x=alt.value(0),
            x2=alt.value("width"),
            y=alt.value("height"),
            y2=alt.value(0),
            stroke="Fit:N",
        )
    )

    gdp_vs_eci_chart_rankings = (
        (
            base_rankings
            + base_rankings_reg_line
            + line_red
            + labels_iso_code3_rankings
        )
        .properties(
            width=900,
            height=600,
            title=alt.TitleParams(
                "Comparación de Rankings de Países",
                subtitle="Datos de Empleo de OECD SBS y Atlas de Complejidad 2019",
                subtitleColor="gray"
            )
        )
        .interactive()
        .configure_legend(
            strokeColor="gray",
            fillColor="#EEEEEE",
            padding=6,
            cornerRadius=6,
            orient="top-left",
            labelFontSize=10,
            titleFontSize=11,
            symbolSize=80,
            labelLimit=120
        )
    )

    gdp_vs_eci_chart_rankings
    return


@app.cell
def _(mo):
    mo.md(r"""
    # 8. Portafolios de política

    Validados los indicadores, la pregunta pasa a ser de política: qué actividades priorizar. La respuesta depende del apetito de riesgo.

    ## 8.1 Criterios de priorización y ponderadores

    | Portafolio | Prefijo | `density` | `pci` | `cog` | Lógica |
    |---|---|---|---|---|---|
    | Low-hanging Fruit | `lhf` | 0.80 | 0.05 | 0.15 | Prioriza lo alcanzable con las capacidades actuales. |
    | Balanced Portfolio | `bp` | 0.50 | 0.25 | 0.25 | Equilibra cercanía, complejidad y opción futura. |
    | Long Jumps | `lj` | 0.20 | 0.35 | 0.45 | Favorece complejidad y potencial, aun a mayor distancia. |

    `calcula_score()` aplica estos pesos sobre las actividades filtradas para Honduras y restringidas a `mcp == 0`, es decir, las que el país aún no desarrolla de manera revelada. El score final es la media ponderada de `density_norm`, `pci` y `cog`.
    """)
    return


@app.cell
def _(np, pl):
    ## Calcula promedio ponderado de density, PCI y GO
    ### Define ponderadores
    product_selection_criteria = {
        "Low-hanging Fruit" : {"cog" : 0.15, "pci" : 0.05, "density" : 0.8},
        "Balanced Portfolio" : {"cog" : 0.25, "pci" : 0.25, "density" : 0.5},
        "Long Jumps" : {"cog" : 0.45, "pci" : 0.35, "density" : 0.2},
    }

    ### Mapeo portafolios - prefijos
    mapp_portafolios = {
        "lhf" : "Low-hanging Fruit", 
        "bp" : "Balanced Portfolio", 
        "lj" : "Long Jumps"
    }

    ### Creamos score como una media ponderada
    def calcula_score(portafolio : str, 
                      df_portafolios : pl.DataFrame
                     ) -> pl.DataFrame:

        df_portafolios = df_portafolios.filter(
            (pl.col("mcp") == 0) & 
            (pl.col("REF_AREA") == "HND")
        )
        df_portafolios_score = df_portafolios.with_columns(
            df_portafolios.select(
                pl.struct("density_norm", "pci", "cog").map_elements(
                    lambda s: np.average(
                        a = [s["density_norm"], s["pci"], s["cog"]],
                        weights = [
                            product_selection_criteria[mapp_portafolios[portafolio]]["density"],
                            product_selection_criteria[mapp_portafolios[portafolio]]["pci"], 
                            product_selection_criteria[mapp_portafolios[portafolio]]["cog"]
                        ]
                    ), 
                    return_dtype=pl.Float64
                ).alias(portafolio)
            )
        ).select("REF_AREA", "ACTIVITY", "mcp", portafolio)

        return df_portafolios_score

    return calcula_score, mapp_portafolios, product_selection_criteria


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 8.2 Normalización de la densidad

    `density`, `pci` y `cog` están en escalas distintas, de modo que promediarlas directamente daría un peso implícito arbitrario. `calcula_density_z()` normaliza `density` mediante una transformación z-score: valores positivos representan densidades superiores al promedio y valores negativos, inferiores. También recalcula `distance` como `1 - density`.

    El resultado de esa función es un DataFrame con las columnas adicionales `density_norm` y `distance`. Esta transformación prepara los indicadores para construir scores de priorización y comparar actividades económicas bajo distintos criterios de selección.
    """)
    return


@app.cell
def _(pl):
    ## Calculamos densidad normalizada para cada conjunto de datos
    def calcula_density_z(df : pl.DataFrame
        ) -> pl.DataFrame:

        ### Normalizamos density
        df = df.with_columns(
            density_norm = (pl.col("density") - pl.col("density").mean())/pl.col("density").std(), 
            distance = 1 - pl.col("density")
        )

        return df 

    return (calcula_density_z,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    La función `calcula_density_z()` se aplica al DataFrame `cdata` para generar una versión normalizada de los indicadores de complejidad. El resultado se almacena en `cdata_norm`.

    Esta transformación incorpora la variable `density_norm`, que expresa la densidad productiva en una escala estandarizada, y recalcula `distance` como `1 - density`. La normalización permite comparar la densidad con otros indicadores usados en la priorización de actividades económicas, especialmente dentro de los scores definidos para los distintos portafolios.

    El DataFrame `cdata_norm` conserva la información de complejidad económica original y añade variables preparadas para el cálculo de oportunidades productivas.
    """)
    return


@app.cell
def _(calcula_density_z, cdata):
    cdata_norm = calcula_density_z(cdata)
    cdata_norm
    return (cdata_norm,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 8.3 Construcción de rankings

    La función `obten_ranking()` automatiza la construcción de rankings de actividades económicas para una estrategia de portafolio específica. A partir del identificador del portafolio, calcula el score correspondiente con `calcula_score()`, incorpora el nombre de cada actividad mediante el cruce con `mapp_ciiu` y agrega la etiqueta desde la base original.

    Las actividades se ordenan de mayor a menor puntaje y se asigna un ranking ordinal. Posteriormente, se conservan las primeras 20 actividades mejor posicionadas y se renombran las columnas de salida de acuerdo con el portafolio seleccionado.

    El resultado es una tabla con el ranking, el código CIIU y el nombre de las actividades priorizadas. Esta función permite generar salidas comparables para distintos portafolios, como `lhf`, `bp` o `lj`, manteniendo una estructura uniforme para el análisis de oportunidades productivas.
    """)
    return


@app.cell
def _(calcula_score, cdata_norm, df, mapp_ciiu, pl):
    def obten_ranking(portafolio_cat : str, 
                      datos : pl.DataFrame, ) -> pl.DataFrame:

        return calcula_score(portafolio_cat, cdata_norm).join(
            mapp_ciiu,
            left_on="ACTIVITY", 
            right_on="codigo"
        ).unique().drop_nulls().join(
            pl.from_pandas(df).select("ACTIVITY", "seccion").unique(),
            on = "ACTIVITY"
        ).sort(
            portafolio_cat, descending=True
        ).select(
                portafolio_cat, "ACTIVITY", "nombre_actividad"
            ).with_columns(
                pl.col(portafolio_cat).rank("ordinal", descending=True).alias("rank")
            ).drop(portafolio_cat).head(20).select("rank", "ACTIVITY", "nombre_actividad").rename({
                "nombre_actividad" : f"nombre_actividad_{portafolio_cat}", 
                "rank" : f"rank_{portafolio_cat}", 
                "ACTIVITY" : f"ciiu_{portafolio_cat}"
        })

    return (obten_ranking,)


@app.cell
def _(mo):
    mo.md(r"""
    A continuación, se muestra el top 20 de cada uno de los portafolios:
    """)
    return


@app.cell
def _(cdata_norm, mapp_portafolios, obten_ranking, pl):
    ### Creamos portafolios 
    portafolios_categorias = [obten_ranking(portafolio,  cdata_norm) for portafolio in mapp_portafolios]
    portafolios_categorias = pl.concat(portafolios_categorias,  how = "horizontal")
    portafolios_categorias
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 9. Margen intensivo

    El margen intensivo agrupa las actividades en las que Honduras ya muestra presencia productiva. La pregunta aquí no es qué añadir, sino qué tan complejo y qué tan bien conectado está lo que el país ya tiene.

    ## 9.1 Diagrama Distancia-PCI de Honduras

    La muestra se restringe a actividades con `rca > 0`. En el eje horizontal, `distance` mide la distancia productiva respecto a las capacidades existentes: valores bajos indican actividades cercanas a la estructura actual. En el vertical, `pci` representa la complejidad relativa. El color y el tamaño reflejan el `rca` en escala logarítmica, y la forma identifica el estado de `mcp`.

    Antes de construir la figura, se ajusta la clasificación sectorial para agrupar las divisiones de fabricación de prendas de vestir y fabricación de productos textiles bajo la categoría `Industria Textil`. Esta reclasificación permite representar de forma más clara un conjunto de actividades relevantes dentro de la estructura productiva hondureña.

    En la visualización, el color identifica la sección económica ajustada y el tamaño del punto representa el empleo observado en escala logarítmica. El resultado permite identificar actividades existentes en Honduras que combinan mayor complejidad, cercanía productiva y peso laboral, aportando una lectura de las capacidades actuales del país y su posición relativa frente al nivel de complejidad nacional.
    """)
    return


@app.cell
def _(alt, cdata, load_table, mapp_ciiu, pl):
    cdata_intensivo = cdata.filter(
        (pl.col("REF_AREA") == "HND") & 
        (pl.col("rca") > 0) & 
        (pl.col("mcp") == 1)
    )

    hline = alt.Chart().mark_rule(color="red").encode(
        y=alt.datum(-1.14)
    )

    ciiu_textil = load_table("diccionarios", "catalogo_ciiu_rev4").to_pandas().query("incluye == 1")

    ciiu_textil["clase_codigo"] = ciiu_textil["clase_codigo"].apply(lambda x: f"{x:04}")

    ciiu_textil = ciiu_textil[
        ["clase_codigo", "clase_titulo", "seccion_codigo", "seccion_titulo", "division_titulo"]
    ]

    ciiu_textil.loc[
        ciiu_textil["division_titulo"] == "Fabricación de prendas de vestir",
        "seccion_titulo"
    ] = "Industria Textil"

    ciiu_textil.loc[
        ciiu_textil["division_titulo"] == "Fabricación de productos textiles",
        "seccion_titulo"
    ] = "Industria Textil"

    ciiu_textil = pl.from_pandas(ciiu_textil)

    plot_intensivo = alt.Chart(
        cdata_intensivo
        .join(
            mapp_ciiu,
            left_on="ACTIVITY", 
            right_on="codigo"
        )
        .join(
            ciiu_textil,
            left_on="ACTIVITY", 
            right_on="clase_codigo"
        )
    ).mark_circle(
        opacity=0.99,
        stroke="black",
        strokeWidth=1.2,
        strokeOpacity=0.9,
        size=180
    ).encode(
        x=alt.X("distance").scale(zero=False).title("Distancia"),
        y=alt.Y("pci").title("PCI").scale(
            domain=(
                cdata_intensivo["pci"].min() - 1.5,
                cdata_intensivo["pci"].max() + 0.4
            )
        ),
        color=alt.Color("seccion_titulo").title("Sección"),
        size=alt.Size("OBS_VALUE").scale(type="log").title("Empleo"),
        tooltip=["nombre_actividad", "division_titulo", "OBS_VALUE"]
    )

    plot_intensivo = plot_intensivo + hline

    plot_intensivo.properties(
        title=alt.TitleParams(
            "Diagrama Distancia-PCI (Intensivo)",
            subtitle="Honduras. Datos de Empleo de OECD SBS 2019",
            subtitleColor="gray"
        )
    )
    return cdata_intensivo, ciiu_textil, hline


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 9.2 Empleo y complejidad

    La siguiente figura relaciona el empleo observado con la complejidad de las actividades intensivas de Honduras. La muestra se restringe a actividades con `rca > 0` y `mcp == 1`, lo que permite concentrar el análisis en actividades donde el país ya presenta una capacidad productiva revelada.

    El eje horizontal muestra `OBS_VALUE`, interpretado como empleo observado, en escala logarítmica. Esta transformación facilita comparar actividades con tamaños laborales muy distintos. El eje vertical muestra el `PCI`, que representa la complejidad relativa de cada actividad económica.

    El color de los puntos identifica la sección económica ajustada y el tamaño representa el `RCA` en escala logarítmica. Además, se incorpora una línea horizontal asociada al `ECI` de Honduras, que permite comparar la complejidad de cada actividad con el nivel agregado de complejidad del país.

    El resultado permite identificar actividades que combinan una base laboral existente y relativamente amplia con mayor complejidad económica, así como actividades intensivas en empleo pero con menor complejidad relativa.
    """)
    return


@app.cell
def _(alt, cdata_intensivo, ciiu_textil, hline, mapp_ciiu):
    #### Plot intensivo Logaritmo Empleo vs PCI

    plot_intensivo_empleo = alt.Chart(
        cdata_intensivo.join(
            mapp_ciiu,
            left_on="ACTIVITY", 
            right_on="codigo"
        ).join(
            ciiu_textil,
            left_on="ACTIVITY", 
            right_on="clase_codigo"
        )
    ).mark_circle(
        opacity=0.99,
        stroke="black",
        strokeWidth=1.2,
        strokeOpacity=0.9, 
        size=180,     
    ).encode(
        x=alt.X("OBS_VALUE").scale(type="log", zero=False).title("Empleo"),
        y=alt.Y("pci").title("PCI").scale(
            domain=(
                cdata_intensivo["pci"].min() - 1.5,
                cdata_intensivo["pci"].max() + 0.4
            )
        ),
        color=alt.Color("seccion_titulo").title("Sección"),
        size=alt.Size("rca").scale(type="log").title("RCA"),
        tooltip=["nombre_actividad", "division_titulo", "OBS_VALUE"]
    )

    plot_intensivo_empleo = plot_intensivo_empleo + hline

    plot_intensivo_empleo.properties(
        title=alt.TitleParams(
            "Logaritmo de empleo vs PCI (Intensivo)",
            subtitle="Honduras. Datos de Empleo de OECD SBS 2019",
            subtitleColor="gray"
        )
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 10. Margen extensivo

    El margen extensivo agrupa las actividades que Honduras aún no desarrolla de manera revelada, es decir, con `mcp == 0`.

    ## 10.1 Consolidación de los portafolios

    `agrega_col()` añade una columna `portafolio` que identifica la estrategia de cada recomendación. Para cada portafolio se ejecuta `obten_ranking()` y los resultados se renombran a una estructura común — `ranking`, `clase_codigo`, `clase_titulo` — lo que permite concatenarlos en una sola tabla larga. Finalmente se cruza con las secciones económicas del catálogo CIIU, con los códigos formateados a cuatro dígitos para garantizar consistencia en el join.
    """)
    return


@app.cell
def _(cdata_norm, load_table, mapp_portafolios, obten_ranking, pl):
    def agrega_col(df, columna): 
        return df.with_columns(
            portafolio=pl.lit(columna)
        )

    portafolios = pl.concat(
        [
            agrega_col(
                obten_ranking(portafolio, cdata_norm).rename(
                    {
                        f"rank_{portafolio}": "ranking", 
                        f"ciiu_{portafolio}": "clase_codigo", 
                        f"nombre_actividad_{portafolio}": "clase_titulo", 
                    }
                ), 
                portafolio
            )
            for portafolio in mapp_portafolios
        ]  
    )

    ciiu_secciones = load_table("diccionarios", "catalogo_ciiu_rev4").to_pandas().query("incluye == 1")

    ciiu_secciones["clase_codigo"] = ciiu_secciones["clase_codigo"].apply(lambda x: f"{x:04}")

    ciiu_secciones = pl.from_pandas(
        ciiu_secciones[["clase_codigo", "seccion_codigo", "seccion_titulo"]]
    )

    portafolios = portafolios.join(
        ciiu_secciones,
        on="clase_codigo"
    )

    portafolios
    return (portafolios,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 10.2 Base de visualización

    `cdata_hnd` reúne los indicadores normalizados de Honduras restringidos a `mcp == 0`, con los códigos CIIU a cuatro dígitos y las etiquetas de clase y sección incorporadas mediante un join por la izquierda.
    """)
    return


@app.cell
def _(cdata_norm, load_table, pl):
    ### Preparamos df para visualizacion
    ciiu_actividades = load_table("diccionarios", "catalogo_ciiu_rev4").to_pandas().query("incluye == 1")

    ciiu_actividades["clase_codigo"] = ciiu_actividades["clase_codigo"].apply(lambda x: f"{x:04}")

    ciiu_actividades = pl.from_pandas(
        ciiu_actividades[
            [
                "clase_codigo",
                "clase_titulo",
                "seccion_codigo",
                "seccion_titulo"
            ]
        ]
    )

    cdata_hnd = (
        cdata_norm
        .with_columns(
            pl.col("ACTIVITY").cast(pl.Utf8).str.zfill(4)
        )
        .filter(
            (pl.col("REF_AREA") == "HND") &
            (pl.col("mcp") == 0)
        )
        .join(
            ciiu_actividades,
            left_on="ACTIVITY", 
            right_on="clase_codigo",
            how="left"
        )
    )

    cdata_hnd
    return cdata_hnd, ciiu_actividades


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 10.3 Controles del explorador interactivo

    `complexity_metric` vincula nombres descriptivos con las columnas de la base: `Complexity` corresponde a `pci` y `Opportunity Gain` a `cog`. Los dos menús desplegables permiten elegir la estrategia de priorización y la métrica del eje vertical, y recalculan la figura sin modificar el código.
    """)
    return


@app.cell
def _(mo):
    ### Complexity metrics
    complexity_metric = {
        "Complexity" : "pci",
        "Opportunity Gain" : "cog"
    }

    ### Definimos Dropdowns

    #### Selection criteria dropdown
    drop_product_selection_criteria = mo.ui.dropdown(
        options=["Low-hanging Fruit", "Balanced Portfolio" , "Long Jumps"],
        value="Low-hanging Fruit",
        label="Choose Product Selection Criteria",
        searchable=True,
    )

    #### Complexity metric dropdown
    drop_complexity_metric =  mo.ui.dropdown(
        options=["Complexity", "Opportunity Gain"],
        value="Complexity",
        label="Choose Complexity Metric",
        searchable=True,
    )
    return (
        complexity_metric,
        drop_complexity_metric,
        drop_product_selection_criteria,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 10.4 Separación entre actividades priorizadas y resto

    `mapp_portafolios_inv` invierte el mapeo entre nombres descriptivos y códigos internos, para traducir la selección del menú al prefijo usado en la tabla `portafolios`. A partir del portafolio elegido se extraen las clases CIIU priorizadas y `cdata_hnd` se divide en dos subconjuntos.

    Esta separación permite comparar visualmente las actividades priorizadas frente al conjunto restante de oportunidades, facilitando la interpretación de los resultados según el criterio de selección elegido por el usuario.
    """)
    return


@app.cell
def _(
    cdata_hnd,
    drop_product_selection_criteria,
    mapp_portafolios,
    pl,
    portafolios,
):
    ### Subset productos priorizados y no priorizados
    ### Mapeo portafolios - prefijos
    mapp_portafolios_inv = {v:k for k,v in mapp_portafolios.items()}

    ### Clases a priorizar
    clases_ciiu_priorizar = portafolios.filter(portafolio=mapp_portafolios_inv[drop_product_selection_criteria.value])["clase_codigo"].to_numpy()

    #### Priorizados
    points_prioriza = cdata_hnd.filter(
                (pl.col("ACTIVITY").is_in(clases_ciiu_priorizar)) 
    )

    #### No Priorizados
    points_resto = cdata_hnd.filter(
                ~pl.col("ACTIVITY").is_in(clases_ciiu_priorizar)   
    )
    return points_prioriza, points_resto


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 10.5 Capas del diagrama

    | Capa | Contenido |
    |---|---|
    | `relateness_plot_prioriza` | Actividades del portafolio seleccionado, con puntos grandes y borde negro. |
    | `text` | Etiquetas con el nombre de cada actividad priorizada. |
    | `relateness_plot` | Resto de actividades, con menor opacidad, como contexto. |

    `selection_weigths` construye una etiqueta que resume los pesos del criterio seleccionado y se muestra en el subtítulo. El eje horizontal es `distance`; el vertical, la métrica elegida en el menú. El color distingue la sección económica.
    """)
    return


@app.cell
def _(
    alt,
    cdata_hnd,
    complexity_metric,
    drop_complexity_metric,
    drop_product_selection_criteria,
    points_prioriza,
    points_resto,
    product_selection_criteria,
):
    # Create an Altair chart
    selection_weigths = ", ".join([f"{i} = {j}" for i,j in product_selection_criteria[drop_product_selection_criteria.value].items()])
    selection_weigths = "Weights : " + selection_weigths



    ### Priorized product plots
    relateness_plot_prioriza = alt.Chart(points_prioriza).mark_point(filled=True, size=230, stroke = "black").encode(
        alt.X('distance', title="Distancia").scale(domain=(cdata_hnd["distance"].min()-0.02,cdata_hnd["distance"].max() + 0.02)), # Encoding along the x-axis
        alt.Y(complexity_metric[drop_complexity_metric.value], title=drop_complexity_metric.value).scale(domain=(-4,8)), # Encoding along the y-axis
        color='seccion_titulo', # Category encoding by color
        tooltip=['clase_titulo', 'seccion_titulo', 'distance', complexity_metric[drop_complexity_metric.value]]
    ).properties(
        title = [f"Relatedness-complexity diagram - HND - Year : 2019", 
                 f"{drop_product_selection_criteria.value}", 
                selection_weigths],

    )
    ### Priorized product plots (Para el texto en negro)
    relateness_plot_prioriza_negro = alt.Chart(points_prioriza).mark_point().encode(
        alt.X('distance', title="Distancia").scale(domain=(cdata_hnd["distance"].min()-0.02,cdata_hnd["distance"].max() + 0.02)), # Encoding along the x-axis
        alt.Y(complexity_metric[drop_complexity_metric.value], title=drop_complexity_metric.value), # Encoding along the y-axis
        #color='Sector', # Category encoding by color
        tooltip=['clase_titulo', 'seccion_titulo', 'distance', complexity_metric[drop_complexity_metric.value]]
    ).properties(
        title = [f"Relatedness-complexity diagram - HND - Year : 2019", 
                 f"{drop_product_selection_criteria.value}", 
                selection_weigths],

    )

    # 3. Create a separate text layer
    text = relateness_plot_prioriza_negro.mark_text(
        align='left',
        baseline='middle',
        fontSize = 7,
        fontStyle = "bold",
        #fontWeight = "bold",
        dx=7 # Offset the text slightly to the right of the point
    ).encode(
        text='clase_titulo:N' # Nominal data type for labels
    )


    ### Unpriorized product plots
    relateness_plot = alt.Chart(points_resto).mark_point(filled=True, size=230, opacity=0.3).encode(
        alt.X('distance', title="Distancia").scale(domain=(cdata_hnd["distance"].min(),cdata_hnd["distance"].max())), # Encoding along the x-axis
        alt.Y(complexity_metric[drop_complexity_metric.value], title=drop_complexity_metric.value), # Encoding along the y-axis
        color=alt.Color('seccion_titulo', title = "Seccion"), # Category encoding by color
        tooltip=['clase_titulo', 'seccion_titulo', 'distance', complexity_metric[drop_complexity_metric.value]]
    )
    return relateness_plot, relateness_plot_prioriza


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 10.6 Explorador interactivo

    Los menús permiten alternar entre criterios de portafolio y métricas de complejidad sin modificar el código.
    """)
    return


@app.cell
def _(
    complexity_metric,
    drop_complexity_metric,
    drop_product_selection_criteria,
    mo,
    relateness_plot,
    relateness_plot_mo,
    relateness_plot_prioriza,
    relateness_plot_prioriza_mo,
):
    # In a new cell, display the chart and its data filtered by the selection

    if complexity_metric[drop_complexity_metric.value] == "ICI_UE":
        stack_plots = [
                    drop_product_selection_criteria,drop_complexity_metric,
                    relateness_plot_prioriza_mo + relateness_plot_mo ,
                    #points_prioriza.select("Sector", "Subsector", "rama_id", "Industria", "score").sort(by="score", descending=False)
            ]
    else:
        stack_plots = [
                    drop_product_selection_criteria,drop_complexity_metric,
                    relateness_plot_prioriza + relateness_plot,
                    #points_prioriza.select("Sector", "Subsector", "rama_id", "Industria", "score").sort(by="score", descending=False)
            ]

    mo.vstack(stack_plots)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 11. Exportación de resultados

    Se exportan los resultados en el archivo `datos/seleccion_final_complexity.xlsx` dividido en tres hojas:
    1. Total de actividades
    2. Margen intensivo
    3. Margen extensivo
    """)
    return


@app.cell
def _(cdata, cdata_norm, ciiu_actividades, pd, pl, portafolios):
    from pathlib import Path

    # Crear carpeta de salida
    output_dir = Path("datos")
    output_dir.mkdir(parents=True, exist_ok=True)

    archivo_salida = output_dir / "resultados_complexity_final.xlsx"


    def to_pandas_safe(tabla):
        if isinstance(tabla, pl.DataFrame):
            return tabla.to_pandas()
        return tabla


    def asegura_ciiu_4d(tabla, columna):
        if isinstance(tabla, pl.DataFrame):
            return tabla.with_columns(
                pl.col(columna).cast(pl.Utf8).str.zfill(4)
            )
        else:
            tabla[columna] = tabla[columna].astype(str).str.zfill(4)
            return tabla


    # Usar ciiu_actividades ya existente
    # No se redefine para evitar error en marimo

    ciiu_actividades_reporte = (
        ciiu_actividades
        .with_columns(
            pl.col("clase_codigo").cast(pl.Utf8).str.zfill(4)
        )
        .unique()
    )


    # Preparar bases de complejidad con códigos CIIU en cuatro dígitos

    cdata_export_reporte = (
        cdata
        .with_columns(
            pl.col("ACTIVITY").cast(pl.Utf8).str.zfill(4).alias("ACTIVITY")
        )
    )

    cdata_norm_export_reporte = (
        cdata_norm
        .with_columns(
            pl.col("ACTIVITY").cast(pl.Utf8).str.zfill(4).alias("ACTIVITY")
        )
    )


    # Hoja 1: 213 act

    reporte_213_act = (
        cdata_export_reporte
        .filter(pl.col("REF_AREA") == "HND")
        .join(
            ciiu_actividades_reporte,
            left_on="ACTIVITY",
            right_on="clase_codigo",
            how="left"
        )
        .select(
            pl.col("REF_AREA").alias("ISO 3"),
            pl.lit("Honduras").alias("País"),
            pl.col("ACTIVITY").alias("ciiu4_cod"),
            pl.col("clase_titulo").alias("ciiu4_actividad"),
            pl.col("seccion_codigo"),
            pl.col("seccion_titulo"),
            pl.col("OBS_VALUE").alias("Empleo"),
            pl.col("TIME_PERIOD").alias("Año"),
            "rca",
            "mcp",
            "diversity",
            "ubiquity",
            "eci",
            "pci",
            "density"
        )
        .sort("ciiu4_cod")
    )


    # Hoja 2: Intensivo

    ### Actividades incorporadas manualmente a la hoja Intensivo
    ciiu_intensivo_manual = [
        "2930",  # Fabricación de partes y accesorios para vehículos automotores
    ]

    reporte_intensivo = (
        cdata_export_reporte
        .filter(
            (pl.col("REF_AREA") == "HND") &
            (
                ((pl.col("rca") > 0) & (pl.col("mcp") == 1)) |
                pl.col("ACTIVITY").is_in(ciiu_intensivo_manual)
            )
        )
        .join(
            ciiu_actividades_reporte,
            left_on="ACTIVITY",
            right_on="clase_codigo",
            how="left"
        )
        .select(
            pl.col("REF_AREA").alias("ISO 3"),
            pl.lit("Honduras").alias("País"),
            pl.col("ACTIVITY").alias("ciiu4_cod"),
            pl.col("clase_titulo").alias("ciiu4_actividad"),
            pl.col("seccion_codigo"),
            pl.col("seccion_titulo"),
            pl.col("OBS_VALUE").alias("Empleo"),
            pl.col("TIME_PERIOD").alias("Año"),
            "rca",
            "mcp",
            "diversity",
            "ubiquity",
            "eci",
            "pci",
            "density"
        )
        .sort("pci", descending=True)
    )

    # Hoja 3: Extensivo

    mapp_nombre_portafolios = {
        "lhf": "Oportunidades cercanas",
        "bp": "Portafolio balanceado",
        "lj": "Saltos largos"
    }

    portafolios_export_reporte = (
        portafolios
        .with_columns(
            pl.col("clase_codigo").cast(pl.Utf8).str.zfill(4).alias("clase_codigo")
        )
    )

    reporte_extensivo = (
        portafolios_export_reporte
        .join(
            cdata_norm_export_reporte
            .filter(pl.col("REF_AREA") == "HND")
            .select(
                "ACTIVITY",
                "cog",
                "pci",
                "density"
            ),
            left_on="clase_codigo",
            right_on="ACTIVITY",
            how="left"
        )
        .with_columns(
            source=pl.lit("ladder"),
            Portafolio=pl.col("portafolio").replace(mapp_nombre_portafolios)
        )
        .select(
            "source",
            pl.col("portafolio").alias("portfolio"),
            "Portafolio",
            "ranking",
            pl.col("clase_codigo").alias("ciiu4_cod"),
            pl.col("clase_titulo").alias("Clase CIIU"),
            pl.col("seccion_codigo"),
            pl.col("seccion_titulo"),
            pl.col("cog").alias("COG"),
            pl.col("pci").alias("PCI"),
            pl.col("density").alias("Density")
        )
        .sort(["portfolio", "ranking"])
    )


    # Asegurar códigos CIIU de cuatro dígitos

    reporte_213_act = asegura_ciiu_4d(reporte_213_act, "ciiu4_cod")
    reporte_intensivo = asegura_ciiu_4d(reporte_intensivo, "ciiu4_cod")
    reporte_extensivo = asegura_ciiu_4d(reporte_extensivo, "ciiu4_cod")


    # Verificación de etiquetas faltantes

    verifica_etiquetas_faltantes_213 = (
        reporte_213_act
        .filter(pl.col("ciiu4_actividad").is_null())
        .select("ciiu4_cod")
        .unique()
        .sort("ciiu4_cod")
    )

    verifica_etiquetas_faltantes_intensivo = (
        reporte_intensivo
        .filter(pl.col("ciiu4_actividad").is_null())
        .select("ciiu4_cod")
        .unique()
        .sort("ciiu4_cod")
    )

    print("Etiquetas faltantes en 213 act:")
    print(verifica_etiquetas_faltantes_213)

    print("Etiquetas faltantes en Intensivo:")
    print(verifica_etiquetas_faltantes_intensivo)


    # Exportar reporte

    with pd.ExcelWriter(archivo_salida, engine="openpyxl") as writer:

        to_pandas_safe(reporte_213_act).to_excel(
            writer,
            sheet_name="213 act",
            index=False
        )

        to_pandas_safe(reporte_intensivo).to_excel(
            writer,
            sheet_name="Intensivo",
            index=False
        )

        to_pandas_safe(reporte_extensivo).to_excel(
            writer,
            sheet_name="Extensivo",
            index=False
        )

        for sheet_name in ["213 act", "Intensivo", "Extensivo"]:
            ws = writer.book[sheet_name]

            for cell in ws[1]:
                if cell.value == "ciiu4_cod":
                    col_letter = cell.column_letter

                    for row in range(2, ws.max_row + 1):
                        ws[f"{col_letter}{row}"].number_format = "@"
                        ws[f"{col_letter}{row}"].value = str(ws[f"{col_letter}{row}"].value).zfill(4)

    archivo_salida
    return reporte_213_act, reporte_extensivo, reporte_intensivo


@app.cell
def _(reporte_213_act):
    reporte_213_act
    return


@app.cell
def _(reporte_intensivo):
    reporte_intensivo
    return


@app.cell
def _(reporte_extensivo):
    reporte_extensivo
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 11.2 Publicación de `cdata` en el catálogo

    Los indicadores de complejidad son insumo del análisis de viabilidad y atractivo, que los lee desde el catálogo como `complejidad.cdata`. Este bloque cierra el circuito entre ambos notebooks: escribe la tabla al warehouse, de modo que trabajen sobre el mismo resultado.

    | Aspecto | Valor |
    |---|---|
    | Tabla | `complejidad.cdata` |
    | Filas esperadas | 4,473 — veintiún economías por doscientas trece actividades |
    | Llave de actividad | `ACTIVITY` como entero, sin ceros a la izquierda |
    | Modo de escritura | Reemplazo completo del contenido |
    """)
    return


@app.cell
def _(catalog, cdata, pl):
    ### ---------------------------------------------------------------------------
    ### Publica cdata en el catálogo para el análisis de viabilidad y atractivo.
    ### Reemplaza el contenido completo de la tabla.
    ### ---------------------------------------------------------------------------
    TABLA_CDATA = "complejidad.cdata"

    ### Orden y tipos exactos que espera el catálogo
    ESQUEMA_CDATA = {
        "REF_AREA": pl.String,
        "ACTIVITY": pl.Int64,
        "OBS_VALUE": pl.Float64,
        "TIME_PERIOD": pl.Int64,
        "diversity": pl.Int64,
        "ubiquity": pl.Int64,
        "mcp": pl.Int64,
        "eci": pl.Float64,
        "pci": pl.Float64,
        "density": pl.Float64,
        "coi": pl.Float64,
        "cog": pl.Float64,
        "rca": pl.Float64,
        "distance": pl.Float64,
    }

    ### Verifica que cdata tenga todas las columnas requeridas
    faltantes = [c for c in ESQUEMA_CDATA if c not in cdata.columns]
    if faltantes:
        raise ValueError(f"cdata no tiene las columnas: {faltantes}")

    ### Selecciona en el orden del catálogo y ajusta tipos.
    ### ACTIVITY pasa de texto con ceros a la izquierda a entero.
    cdata_catalogo = cdata.select(
        [pl.col(nombre).cast(tipo) for nombre, tipo in ESQUEMA_CDATA.items()]
    )

    print(f"Filas a escribir: {len(cdata_catalogo)}")
    print(f"Economías: {cdata_catalogo['REF_AREA'].n_unique()}")
    print(f"Actividades: {cdata_catalogo['ACTIVITY'].n_unique()}")

    datos_arrow = cdata_catalogo.to_arrow()

    if catalog.table_exists(TABLA_CDATA):
        tabla_cdata = catalog.load_table(TABLA_CDATA)

        ### Compara el esquema antes de sobrescribir
        columnas_catalogo = [c.name for c in tabla_cdata.schema().fields]
        if columnas_catalogo != list(ESQUEMA_CDATA.keys()):
            raise ValueError(
                "El esquema del catálogo no coincide con el esperado.\n"
                f"Catálogo: {columnas_catalogo}\n"
                f"Esperado: {list(ESQUEMA_CDATA.keys())}"
            )

        ### Reemplaza el contenido completo, no agrega filas
        tabla_cdata.overwrite(datos_arrow)
        print(f"{TABLA_CDATA} actualizada.")
    else:
        tabla_cdata = catalog.create_table(TABLA_CDATA, schema=datos_arrow.schema)
        tabla_cdata.append(datos_arrow)
        print(f"{TABLA_CDATA} creada.")

    with tabla_cdata.transaction() as transaction:
        transaction.set_properties(
            name="cdata",
            longname="Indicadores de complejidad económica por país y actividad",
            url="",
            namespace="complejidad",
            description=(
                "Salida del notebook calculos_complejidad_hnd.py. Contiene rca, mcp, "
                "diversity, ubiquity, eci, pci, density, coi, cog y distance para la "
                "muestra de 21 economías y 213 actividades CIIU Rev. 4, con año de "
                "referencia 2019. Insumo del análisis de viabilidad y atractivo."
            ),
        )

    verificacion = catalog.load_table(TABLA_CDATA).to_polars().collect()
    print(f"Verificación: {len(verificacion)} filas en el catálogo")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 12. Anexos

    ## 12.1 Comparativa de Honduras y Alemania

    La siguiente figura presenta un diagrama Distancia-PCI para Honduras a partir de los indicadores de complejidad calculados con datos de empleo de `OECD SBS` para 2019. La visualización se restringe a actividades con `rca > 0`, lo que permite concentrar el análisis en actividades con presencia relativa positiva en el país.

    En el eje horizontal se muestra la variable `distance`, que mide la distancia productiva de cada actividad respecto a las capacidades existentes. Valores más bajos indican actividades más cercanas a la estructura productiva actual. En el eje vertical se presenta el `pci`, que representa la complejidad relativa de cada actividad económica.

    El color y el tamaño de los puntos reflejan el valor de `rca` en escala logarítmica, mientras que la forma identifica el estado de `mcp`. De esta manera, el gráfico permite analizar simultáneamente cercanía productiva, complejidad económica e intensidad relativa de las actividades observadas.

    Esta visualización sirve para identificar actividades existentes en Honduras que combinan mayor complejidad, cercanía a las capacidades actuales y una presencia relativa más fuerte. También funciona como diagnóstico inicial para comparar la estructura productiva observada con las oportunidades priorizadas en los portafolios.
    """)
    return


@app.cell
def _(alt, cdata, mapp_ciiu, pl):

    alt.Chart(cdata.filter(
        (pl.col("REF_AREA")=="HND") & 
        (pl.col("rca")>0)

    ).join(
        mapp_ciiu,
        left_on="ACTIVITY", 
        right_on="codigo"
    )
             ).mark_circle(
                opacity=0.99,
                stroke='black',
                strokeWidth=1.2,
                strokeOpacity=0.9, 
                size=180,     
             ).encode(
        x=alt.X('distance').scale(zero=False).title("Distancia"),
        y=alt.Y('pci').title("PCI"),#.scale(type ="log"),
        shape = alt.Shape("mcp:N").title("M"),
        color = alt.Color("rca").scale(type ="log", scheme='redblue', domainMid=1.0).title("RCA"),
        size = alt.Size("rca").scale(type ="log"),
        tooltip=["nombre_actividad","rca"]
    ).properties(
        title=alt.TitleParams(
            "Diagrama Distancia-PCI",
            subtitle="Honduras. Datos de Empleo de OECD SBS 2019",
            subtitleColor="gray"
        )
    ).configure_legend(
        strokeColor='gray',
        fillColor='white',
        padding=10,
        cornerRadius=10,
        orient='top-left', 
        titleFontSize=18,
        labelFontSize=16,

    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    El siguiente gráfico sirve como referencia comparativa frente al caso de Honduras, ya que permite observar cómo se distribuyen las actividades de una economía con mayor complejidad en el espacio Distancia-PCI.
    """)
    return


@app.cell
def _(alt, cdata, mapp_ciiu, pl):
    alt.Chart(cdata.filter(
        (pl.col("REF_AREA")=="DEU") & 
        (pl.col("rca")>0)

    ).join(
        mapp_ciiu,
        left_on="ACTIVITY", 
        right_on="codigo"
    )
             ).mark_circle(
                opacity=0.99,
                stroke='black',
                strokeWidth=1.2,
                strokeOpacity=0.9, 
                size=180,     
             ).encode(
        x=alt.X('distance').scale(zero=False).title("Distancia"),
        y=alt.Y('pci').title("PCI"),#.scale(type ="log"),
        shape = alt.Shape("mcp:N").title("M"),
        color = alt.Color("rca").scale(type ="log", scheme='redblue', domainMid=1.0).title("RCA"),
        size = alt.Size("rca").scale(type ="log"),
        tooltip=["nombre_actividad","rca"]
    ).properties(
        title=alt.TitleParams(
            "Diagrama Distancia-PCI",
            subtitle="Alemania. Datos de Empleo de OECD SBS 2019",
            subtitleColor="gray"
        )
    ).configure_legend(
        strokeColor='gray',
        fillColor='white',
        padding=10,
        cornerRadius=10,
        orient='bottom-left', 
        titleFontSize=18,
        labelFontSize=18,

    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 12.2 Limitaciones

    1. Las bases de Honduras, El Salvador y Ecuador provienen de levantamientos distintos a la SBS de la OCDE. Aunque se armonizan a la misma clasificación y al mismo año, las diferencias de cobertura y de definición de la unidad de observación no se corrigen.

    2. El umbral de 0.69 determina la muestra de países y, por esa vía, los valores de `pci` y `eci`. El ejercicio no incluye por ahora un análisis de sensibilidad frente a umbrales alternativos.

    3. Los ponderadores de los portafolios son una elección normativa, no basada en criterios estadísticos.

    4. Los datos de Honduras son suscepcitibles a errores de clasificación en los registros administraticos que añaden ruido a los cálculos.
    """)
    return


if __name__ == "__main__":
    app.run()
