import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Viabilidad y atractivo de industrias

    ## Priorización multicriterio para Honduras

    **Laboratorio de Desarrollo Regional de la Escuela de Gobierno y Transformación Pública del Tecnológico de Monterrey**

    **Sendas Think Tank**

    ---

    Este documento construye dos índices sintéticos para cada industria candidata de Honduras — uno de atractivo y otro de viabilidad — y los combina en un diagrama de cuadrantes que ordena las industrias por fase de intervención. Es la continuación del análisis de complejidad económica: toma su salida como universo de industrias y le añade características adicionales que los resultados de complejidad no capturan por si solos.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 1. Introducción

    ## 1.1 Motivación

    El análisis de complejidad económica responde qué industrias están al alcance de las capacidades productivas de Honduras y cuáles son sofisticadas. No obstante, no responde si el mundo está invirtiendo en ellas, si el país tiene los insumos, ni si dependen de restricciones que Honduras no puede levantar en el corto plazo.

    Este ejercicio agrega esas dimensiones. Para cada industria se calculan factores de atractivo y viabilidad, se agregan en dos índices mediante el método TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution), y el resultado se representa en un plano donde cada cuadrante corresponde a una fase de intervención.

    ## 1.2 Método de agregación

    TOPSIS ordena alternativas por su distancia a una solución ideal. Con una matriz de industrias por factores, normaliza cada columna, construye una alternativa ideal — el mejor valor de cada factor — y una anti-ideal, y puntúa cada industria por su cercanía relativa a la primera.

    Cada factor se declara como beneficio o como costo. Un factor de beneficio mejora la posición de la industria cuando es alto; uno de costo la empeora. La dependencia de energía, por ejemplo, entra como costo: cuanto mayor es, menos viable resulta la industria en un país con restricciones de suministro.

    Los pesos son uniformes dentro de cada índice. Sin evidencia sobre la importancia relativa de los factores, repartirlos por igual evita introducir un juicio no documentado.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1.3 Factores de atractivo

    | Factor | Variable | Fuente | Sección |
    |---|---|---|---|
    | Inversión acumulada en LAC | `cumulative_investment_lac` | fDi Markets | 5.1 |
    | Crecimiento de la inversión en LAC | `cagr_investment_lac` | fDi Markets | 5.2 |
    | Elasticidad empleo-inversión en LAC | `elasticidad_empleo_fdi_lac` | fDi Markets | 5.3 |
    | Crecimiento de la producción | `cagr_production` | OCDE SBS | 5.4 |
    | Crecimiento de las exportaciones mundiales | `cagr_exports` | Atlas HS12 | 5.5 |
    | Sustitución de importaciones de China | `share_imports_china` | Atlas HS12 | 5.6 |
    | Elasticidad empleo-producto | `elasticidad_empleo_producto` | OCDE SBS | 5.7 |

    Todos entran como factores de beneficio.

    ## 1.4 Factores de viabilidad

    | Factor | Variable | Fuente | Tipo | Sección |
    |---|---|---|---|---|
    | RCA en países pares | `rca_peers` | Complejidad | Beneficio | 6.1 |
    | Disponibilidad de insumos | `razon_insumos_presentes` | AIPNET y Atlas | Beneficio | 6.2 |
    | Dependencia energética | `share_energy` | OCDE SBS | Costo | 6.3 |
    | Dependencia eléctrica | `razon_electricidad_gasto_total` | SAIC México | Costo | 6.4 |
    | Intensidad institucional | `institutional_intensity` | Nunn | Costo | 6.5 |

    ## 1.5 Lectura de los cuadrantes

    El diagrama cruza ambos índices en sus medias. Los cuatro cuadrantes se etiquetan como fases de intervención: la Fase I reúne las industrias de alto atractivo y alta viabilidad, y la Fase IV las de bajo atractivo y baja viabilidad.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1.6 Estructura del documento

    | Sección | Contenido |
    |---|---|
    | 2 | Entorno de trabajo |
    | 3 | Inventario de las tablas de datos utilizadas |
    | 4 | Datos base de producción y empleo de la OCDE SBS |
    | 5 | Construcción de factores de atractivo |
    | 6 | Construcción de factores de viabilidad |
    | 7 | Consolidación de factores e imputación de faltantes |
    | 8 | Cálculo de los índices TOPSIS|
    | 9 | Diagramas de viabilidad y atractivo en los márgenes intensivo y extensivo |
    | 10 | Análisis específico de productos textiles a nivel HS12 |
    | 11 | Anexos |

    ## 1.7 Reproducción

    ```bash
    uv sync
    export PYICEBERG_HOME=$(pwd)
    uv run marimo edit viabilidad_atractivo.py
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 2. Entorno de trabajo

    ## 2.1 Dependencias

    Este bloque carga la librería marimo, que estructura el análisis en un entorno de notebook reactivo. El alias mo se usa a lo largo del documento para los componentes interactivos y los bloques de texto.
    """)
    return


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    | Librería | Función en el análisis |
    |---|---|
    | `polars` | Manipulación de datos |
    | `pandas` | Interoperabilidad y lectura de datos |
    | `numpy` | Pesos y tipos de criterio para TOPSIS |
    | `pymcdm` | Implementación de TOPSIS y del ranking |
    | `scikit-learn` | Imputación de faltantes por vecinos más cercanos |
    | `altair` | Diagramas de viabilidad y atractivo |
    | `pyiceberg` | Acceso al catálogo de datos del proyecto |

    Los imports están repartidos a lo largo del notebook, en el punto donde se usan por primera vez.
    """)
    return


@app.cell
def _():
    import polars as pl
    import pandas as pd
    from pyiceberg.catalog import load_catalog

    return load_catalog, pd, pl


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2.2 Conexión al catálogo de datos

    | Namespace | Contenido |
    |---|---|
    | `viabilidad_atractivo` | Insumos propios de este análisis: AIPNET, electricidad, intensidad institucional, textiles. |
    | `complejidad` | Salidas del análisis de complejidad y datos del Atlas. |
    | `diccionarios` | Catálogos CIIU y tablas de correspondencia entre clasificadores. |
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

    Este notebook consume diecisiete tablas del catálogo, repartidas en tres namespaces, más tres fuentes externas.

    Una dependencia merece atención especial: la tabla `complejidad.cdata` es la salida del notebook de complejidad económica. Este documento no puede ejecutarse si aquel no se ha corrido antes.
    """)
    return


@app.cell
def _(pl):
    ### Declaración explícita de las tablas que consume este notebook.
    TABLAS_PROYECTO = [
        {
            "namespace": "diccionarios",
            "tabla": "fdi_subsectores_iso_code3",
            "contenido": "Proyectos de inversión extranjera directa por subsector y país, de fDi Markets.",
            "factor": "Inversión y empleo FDI",
            "seccion": "5.1",
        },
        {
            "namespace": "diccionarios",
            "tabla": "paises_iso_code",
            "contenido": "Catálogo de países con código ISO3 y subregión de Naciones Unidas.",
            "factor": "Agrupación regional de FDI",
            "seccion": "5.1",
        },
        {
            "namespace": "diccionarios",
            "tabla": "correspondencia_fdi_ciiu_rev4",
            "contenido": "Correspondencia entre los subsectores de fDi Markets y las clases CIIU Rev. 4.",
            "factor": "Puente FDI-CIIU",
            "seccion": "5.1",
        },
        {
            "namespace": "complejidad",
            "tabla": "hs12_country_product_year_4",
            "contenido": "Exportaciones e importaciones por país, producto HS12 a cuatro dígitos y año, del Atlas.",
            "factor": "Crecimiento exportador y RCA",
            "seccion": "5.5, 6.1, 6.2",
        },
        {
            "namespace": "diccionarios",
            "tabla": "ponderadores_ciiu_hs12_concordance",
            "contenido": "Correspondencia ponderada entre clases CIIU Rev. 4 y productos HS12.",
            "factor": "Puente CIIU-HS12",
            "seccion": "5.5",
        },
        {
            "namespace": "viabilidad_atractivo",
            "tabla": "importaciones_usa_china_hs12",
            "contenido": "Participación de China en las importaciones de Estados Unidos por producto HS12.",
            "factor": "Sustitución de importaciones",
            "seccion": "5.6",
        },
        {
            "namespace": "complejidad",
            "tabla": "cdata",
            "contenido": "Indicadores de complejidad por país y actividad. Salida del notebook de complejidad económica.",
            "factor": "Universo de industrias y RCA de pares",
            "seccion": "6.1",
        },
        {
            "namespace": "viabilidad_atractivo",
            "tabla": "aipnet_hs12_4d",
            "contenido": "Cadena de producción entre productos HS12, generada por AIPNET.",
            "factor": "Disponibilidad de insumos",
            "seccion": "6.2",
        },
        {
            "namespace": "diccionarios",
            "tabla": "ponderadores_ciiu_naics2017_concordance",
            "contenido": "Correspondencia ponderada entre clases CIIU Rev. 4 y el clasificador NAICS 2017.",
            "factor": "Puente CIIU-NAICS",
            "seccion": "6.4",
        },
        {
            "namespace": "viabilidad_atractivo",
            "tabla": "electricidad_saic_2003-2023",
            "contenido": "Gasto en energía eléctrica y gasto total por actividad económica, del SAIC de México.",
            "factor": "Dependencia eléctrica",
            "seccion": "6.4",
        },
        {
            "namespace": "diccionarios",
            "tabla": "ciiu-rev-2_to_ciiu-rev-4",
            "contenido": "Correspondencia ponderada entre CIIU Rev. 2 a tres dígitos y CIIU Rev. 4 a cuatro dígitos.",
            "factor": "Puente entre revisiones CIIU",
            "seccion": "6.5",
        },
        {
            "namespace": "viabilidad_atractivo",
            "tabla": "institutional_intensity",
            "contenido": "Índice de intensidad institucional por actividad, en CIIU Rev. 2.",
            "factor": "Intensidad institucional",
            "seccion": "6.5",
        },
        {
            "namespace": "diccionarios",
            "tabla": "catalogo_ciiu_rev4_nombres",
            "contenido": "Tabla de recodificación entre clasificadores y nombres de actividad.",
            "factor": "Etiquetas de actividad",
            "seccion": "9.1",
        },
        {
            "namespace": "diccionarios",
            "tabla": "catalogo_ciiu_rev4",
            "contenido": "Catálogo CIIU Rev. 4 con jerarquía sección-división-clase.",
            "factor": "Clasificación sectorial",
            "seccion": "9.1",
        },
        {
            "namespace": "viabilidad_atractivo",
            "tabla": "productos_textiles",
            "contenido": "Selección de productos textiles a nivel HS12 con su actividad asociada.",
            "factor": "Universo del análisis textil",
            "seccion": "10.1",
        },
        {
            "namespace": "viabilidad_atractivo",
            "tabla": "productos_textiles_cw_hs12_ciiu4",
            "contenido": "Correspondencia ponderada entre los productos textiles HS12 y las clases CIIU Rev. 4.",
            "factor": "Puente textiles HS12-CIIU",
            "seccion": "10.1",
        },
        {
            "namespace": "complejidad",
            "tabla": "product_hs12",
            "contenido": "Catálogo de productos HS12 con nombres cortos por capítulo.",
            "factor": "Etiquetas de producto",
            "seccion": "10.4",
        },
    ]

    inventario_tablas = (
        pl.DataFrame(TABLAS_PROYECTO)
        .with_columns(
            (pl.col("namespace") + "." + pl.col("tabla")).alias("tabla_completa")
        )
        .select("tabla_completa", "contenido", "factor", "seccion")
    )

    inventario_tablas
    return (TABLAS_PROYECTO,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3.2 Metadatos registrados en el catálogo

    El siguiente bloque lee las propiedades escritas por `build_iceberg_warehouse.py` y actualizadas por `update_metadata.py`.
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
    ---|---|---|
    | `datos/oecd_sbp_produccion_gasto_insumos` | Delta Lake | Producción, valor agregado y compras de bienes, servicios  de la OCDE SBS.
    | `datos/oecd_sbp_empleo_energia` | Delta Lake | Empleo total, empleo femenino y productividad laboral por actividad, de la OCDE SBS.
    | `datos/seleccion_final_complexity.xlsx` | XLSX | Selección final de industrias por margen, con su asignación a clusters. Hojas `intensivo` y `extensivo`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 4. Datos base de la OCDE SBS

    Dos bases de la Structural Business Statistics alimentan los factores construidos con datos de la OCDE. Ambas se leen en formato Delta desde `datos/` y comparten la misma rutina de limpieza.

    ## 4.1 Códigos de medida

    | Código | Medida | Base | Usado en |
    |---|---|---|---|
    | `PROD` | Production | Producción | 5.4 Crecimiento de la producción |
    | `INGS` | Total purchases of goods and services | Producción | 6.3 Dependencia energética, denominador |
    | `INEN` | Purchases of energy products | Producción | 6.3 Dependencia energética, numerador |
    | `EMPN` | Total employment (persons employed) | Empleo | 5.7 Elasticidad empleo-producto |
    """)
    return


@app.cell
def _():
    ## Códigos de medida de la OCDE SBS
    produccion = {
        "PROD": "Production",
        "INGS": "Total purchases of goods and services",
        "INEN": "Purchases of energy products",
    }

    empleo = {
        "EMPN": "Total employment (persons employed)",
    }
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4.2 Rutina de carga y depuración

    `obten_datos()` aplica a cualquiera de las dos bases el mismo tratamiento: consulta diferida sobre el archivo Delta, agregación por actividad, período y medida, y filtrado a las clases CIIU de cuatro dígitos. Los códigos de la OCDE llegan con una letra de sección al inicio, que se descarta para dejar solo los cuatro dígitos.

    El resultado se pivotea de formato largo a ancho, con una columna por código de medida. De esta estructura de datos se nutren los análisis posteriores.
    """)
    return


@app.cell
def _(pd, pl):
    ### Define consulta tipo lazy para el acceso a los datos
    def obten_datos(dataset : str) -> pd.DataFrame: 
        q = pl.scan_delta(f'datos/{dataset}').select("ACTIVITY", "OBS_VALUE", "MEASURE", "TIME_PERIOD").group_by("ACTIVITY", "TIME_PERIOD", "MEASURE").sum()
        ### Recolectamos la informacion
        df = q.collect()

        ### Lo convertimos a pandas
        df = df.to_pandas()

        ### Nos quedamos con las actividades a 4 digitos del CIIU
        df = df[df["ACTIVITY"].apply(lambda x : len(x)==5)]

        ### Define funcion que evalua si los últimos 4 caracteres son numéricos
        test_numericos = lambda cadena : all([i.isnumeric() for i in list(cadena)])

        df = df[df["ACTIVITY"].apply(lambda x : test_numericos(x[1:]))]

        ### Obten seccion
        df["ACTIVITY"] = df["ACTIVITY"].apply(lambda x : x[1:])

        df = df.pivot(index=['TIME_PERIOD', 'ACTIVITY'], columns='MEASURE', values='OBS_VALUE')

        return df.reset_index()

    return (obten_datos,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4.3 Producción, insumos y gasto en energía
    """)
    return


@app.cell
def _(obten_datos):
    ### Cargamos datos de produccion
    df_produccion = obten_datos("oecd_sbp_produccion_gasto_insumos")
    df_produccion
    return (df_produccion,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4.4 Empleo
    """)
    return


@app.cell
def _(obten_datos):
    ### Cargamos datos de empleo
    df_empleo = obten_datos("oecd_sbp_empleo_energia")
    df_empleo
    return (df_empleo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 5. Factores de atractivo

    Se analizan factores que cuantifican qué tan atractiva es cada industria como destino de política pública. Todos entran a TOPSIS como criterios de beneficio: cuanto mayor el valor, mejor la posición de la industria.

    ## 5.1 Preparación de los datos de inversión extranjera

    Los proyectos de fDi Markets llegan con su subsector propietario, que se traduce a clases CIIU Rev. 4 mediante la tabla de correspondencia. A cada proyecto se le asigna además la subregión de su país de destino, lo que permite separar el universo mundial del subconjunto de América Latina y el Caribe.

    Los países sin subregión asignada se imputan como Western Asia, y la fecha del proyecto se reduce al año.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # PENDIENTE DE ARREGLAR
    """)
    return


@app.cell
def _(load_table):
    ## Carga FDI
    fdi = load_table("diccionarios", "fdi_subsectores_iso_code3").to_pandas()

    ## Carga regiones 
    regiones = load_table("diccionarios", "paises_iso_code").to_pandas()

    ## Carga crosswalk de los subsectores fdi - CIIU
    fdi_ciiu = load_table("diccionarios", "correspondencia_fdi_ciiu_rev4").to_pandas()
    fdi_ciiu["CIIU"] = fdi_ciiu["CIIU"].apply(lambda x  : f"{x:04d}")

    ## Agregamos regiones del mundo a datos de fdi
    fdi  = fdi.merge(regiones[["iso_alpha_3", "un_sub_region"]], left_on="iso_code3", right_on="iso_alpha_3", how="left")
    fdi["un_sub_region"] = fdi["un_sub_region"].fillna("Western Asia")

    ## Cambiamos a entero el año de inicio del proyecto
    fdi["Project date"] = fdi["Project date"].apply(lambda x : x.split("/")[-1]).astype(int)

    ## Agregamos la correspondencia de actividad CIIU y subsector fdi
    fdi = fdi.merge(fdi_ciiu[["Nombre fDi (Subsector)_duplicated_0", "CIIU"]], left_on="Sub-sector", right_on="Nombre fDi (Subsector)_duplicated_0", how="left")

    ## Filtramos dataset a la región de LAC
    fdi_lac = fdi.query("un_sub_region == 'Latin America and the Caribbean'")
    return (fdi_lac,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5.2 Inversión acumulada y empleo generado

    Se agrupan los proyectos por clase CIIU para obtener el monto total de inversión en capital y el empleo generado entre 2019 y 2024, en dos versiones: mundo y América Latina y el Caribe.
    """)
    return


@app.cell
def _(fdi_lac):
    ## Agrupamos por actividad CIIU para tener el monto acumulado de inversión en capital y creacion de empleo entre 2019 y 2024
    fdi_lac_capital_investment = fdi_lac[["CIIU", "Capital investment", "Jobs created"]].groupby("CIIU").sum().reset_index()
    return (fdi_lac_capital_investment,)


@app.cell
def _(fdi_lac_capital_investment):
    fdi_lac_capital_investment
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5.3 Tasa de crecimiento compuesta de la inversión

    La tasa compuesta anual se calcula sobre la inversión acumulada, no sobre el flujo anual. Para cada clase CIIU se ordenan los proyectos por año, se acumula la inversión y se toma el primer y el último valor de la serie.
    """)
    return


@app.cell
def _(fdi_lac, pl):
    ## Tasa de crecimiento compuesta para inversión de industrias en lac
    fdi_lac_cagr_investment = pl.from_pandas(fdi_lac[["CIIU", "Project date", "Capital investment"]]).sort(
        ["Project date", "CIIU"], maintain_order=True
    ).group_by("Project date", "CIIU",maintain_order=True).sum().select(
        pl.col("Project date", "CIIU", "Capital investment"),
        pl.col("Capital investment").cum_sum().over("CIIU").alias("investment_cum_sum"),
    ).group_by("CIIU", maintain_order=True).agg(
            beginning_val = pl.col("investment_cum_sum").first(),
            ending_val = pl.col("investment_cum_sum").last(),
            n_years = pl.col("Project date").max() - pl.col("Project date").min(),
        ).with_columns(
        cagr_investment = ((pl.col("ending_val") / pl.col("beginning_val")) ** (1 / pl.col("n_years")) - 1)*100
    )

    fdi_lac_cagr_investment
    return (fdi_lac_cagr_investment,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Calculamos la tasa de crecimiento compuesta del empleo entre 2019 y 2024 para cada industria.
    """)
    return


@app.cell
def _(fdi_lac, pl):
    ## Tasa de crecimiento compuesta para inversión de industrias en lac
    fdi_lac_cagr_empleo = pl.from_pandas(fdi_lac[["CIIU", "Project date", "Jobs created"]]).sort(
        ["Project date", "CIIU"], maintain_order=True
    ).group_by("Project date", "CIIU",maintain_order=True).sum().select(
        pl.col("Project date", "CIIU", "Jobs created"),
        pl.col("Jobs created").cum_sum().over("CIIU").alias("empleo_cum_sum"),
    ).group_by("CIIU", maintain_order=True).agg(
            beginning_val = pl.col("empleo_cum_sum").first(),
            ending_val = pl.col("empleo_cum_sum").last(),
            n_years = pl.col("Project date").max() - pl.col("Project date").min(),
        ).with_columns(
        cagr_empleo = ((pl.col("ending_val") / pl.col("beginning_val")) ** (1 / pl.col("n_years")) - 1)*100
    )

    fdi_lac_cagr_empleo
    return (fdi_lac_cagr_empleo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5.4 Elasticidad del empleo a la inversión

    La elasticidad mide cuánto responde el empleo a cambios en la inversión extranjera dentro de un sector: cuánto crece el empleo por cada punto porcentual de crecimiento de la FDI.

    $$\epsilon = \frac{\%\ \text{cambio en empleo}}{\%\ \text{cambio en FDI}}$$

    Un valor entre cero y uno indica que el sector crea empleo pero la inversión crece más rápido. Un valor mayor que uno indica un sector intensivo en trabajo, que genera mucho empleo por unidad de inversión.

    Referencia: [Economic Growth and Sectoral Capacity for Employment](https://infonomics-society.org/wp-content/uploads/ijcdse/published-papers/volume-6-2015/Economic-Growth-and-Sectoral-Capacity-for-Employment.pdf)
    """)
    return


@app.cell
def _(fdi_lac_cagr_empleo, fdi_lac_cagr_investment, pl):
    elasticidad_lac_empleo_fdi = fdi_lac_cagr_investment.select("CIIU", "cagr_investment").join(
        fdi_lac_cagr_empleo.select("CIIU", "cagr_empleo"), 
        on = "CIIU",
    ).with_columns(
        elasticidad = pl.col("cagr_empleo")/pl.col("cagr_investment")
    )
    elasticidad_lac_empleo_fdi
    return (elasticidad_lac_empleo_fdi,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5.5 Crecimiento de la producción

    El crecimiento de la industria se mide como la tasa compuesta anual de la producción (`PROD`) entre 2018 y 2019, con datos de la OCDE SBS.
    """)
    return


@app.cell
def _(df_produccion, pl):
    industry_growth_rate = pl.from_pandas(
        df_produccion[
            ["TIME_PERIOD", "ACTIVITY", "PROD"]
        ].query(
            f"TIME_PERIOD in {[2018, 2019]}"
        )
    ).sort(
        ["ACTIVITY", "TIME_PERIOD"]
    ).group_by("ACTIVITY", maintain_order=True).agg(
            beginning_val = pl.col("PROD").first(),
            ending_val = pl.col("PROD").last(),
            n_years = pl.col("TIME_PERIOD").max() - pl.col("TIME_PERIOD").min(),
            #pl.col("PROD").pct_change().alias("Growth_Rate")
        ).with_columns(
        cagr_production = ((pl.col("ending_val") / pl.col("beginning_val")) ** (1 / pl.col("n_years")) - 1)*100
    )

    industry_growth_rate
    return (industry_growth_rate,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5.6 Crecimiento exportador mundial

    Una industria CIIU se descompone en los productos HS12 que la integran, ponderados por el peso relativo de cada producto dentro de la industria. Con esos ponderadores se construye, sobre los datos del Atlas, un indicador del crecimiento exportador de la industria en el mundo entre 2019 y 2024.

    La tabla de correspondencia descarta los registros cuyo ponderador viene como texto `NA` y convierte el resto a numérico.
    """)
    return


@app.cell
def _(load_table):
    ## Cargamos datos del atlas
    atlas_hs12 = load_table("complejidad", "hs12_country_product_year_4")
    atlas_hs12
    return (atlas_hs12,)


@app.cell
def _(atlas_hs12, pl):
    ## Valor de exportaciones de HS12 de 2012 a 2024
    exportaciones_hs = atlas_hs12.group_by("product_hs12_code", "year").agg(
        pl.col("export_value").sum()
    ).filter(
        pl.col("year").is_in([2019,2024])
    )
    exportaciones_hs
    return (exportaciones_hs,)


@app.cell
def _(load_table, pl):
    ## Cargamos crosswalk entre CIIU y HS12
    ciiu_hs12 = load_table("diccionarios", "ponderadores_ciiu_hs12_concordance")
    ciiu_hs12 = ciiu_hs12.filter(pl.col("weight")!='NA').with_columns(
        pl.col("hs12").cast(pl.Int64), 
        pl.col("weight").cast(pl.Float64), 
    )
    ciiu_hs12
    return (ciiu_hs12,)


@app.cell
def _(ciiu_hs12, exportaciones_hs, pl):
    ## Reunimos datos de exportaciones por producto HS12 y el crosswalk CIIU-HS12
    industry_growth_rate_exports = exportaciones_hs.join(
        ciiu_hs12, 
        left_on="product_hs12_code", 
        right_on="hs12"
    ).with_columns(
        (pl.col("export_value")*pl.col("weight")).alias("export_value")
    ).group_by("ciiu", "year").agg(
        pl.col("export_value").sum()
    ).sort(
        ["ciiu", "year"]
    ).group_by("ciiu", maintain_order=True).agg(
            beginning_val = pl.col("export_value").first(),
            ending_val = pl.col("export_value").last(),
            n_years = pl.col("year").max() - pl.col("year").min(),
            #pl.col("PROD").pct_change().alias("Growth_Rate")
        ).with_columns(
        cagr_exports = ((pl.col("ending_val") / pl.col("beginning_val")) ** (1 / pl.col("n_years")) - 1)*100
    )

    industry_growth_rate_exports
    return (industry_growth_rate_exports,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Nos queda como resultado una tabla con 136 industrias.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5.7 Sustitución de importaciones estadounidenses desde China

    La participación de China en las importaciones de Estados Unidos, medida por producto HS12, se agrega a nivel de industria CIIU como media ponderada por los mismos pesos de la correspondencia.

    Una participación alta señala una industria donde China concentra el abastecimiento del mercado estadounidense, y por tanto donde existe margen para que Honduras sustituya parte de ese flujo. El factor entra a TOPSIS como beneficio, bajo el supuesto de que mayor concentración china implica mayor oportunidad de relocalización.

    Ese supuesto es discutible: una participación china alta también puede reflejar una ventaja de costos difícil de disputar.
    """)
    return


@app.cell
def _(load_table):
    ## Carga datos
    china_imports = load_table("viabilidad_atractivo", "importaciones_usa_china_hs12").select("product_hs12_code", "share_imports_china")
    china_imports
    return (china_imports,)


@app.cell
def _(china_imports, ciiu_hs12, pl):
    ### Reunimos datos de share import of china con la correspondencia CIIU y HS12
    ciiu_china_intensiveness = ciiu_hs12.join(
        china_imports, 
        left_on="hs12", 
        right_on="product_hs12_code"
    ).group_by("ciiu").agg(
        share_imports_china = (pl.col("share_imports_china") * pl.col("weight")).sum() / pl.col("weight").sum()
    )
    ciiu_china_intensiveness
    return (ciiu_china_intensiveness,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5.8 Elasticidad del empleo al producto

    La misma lógica de la Sección 5.4, aplicada ahora al crecimiento de la producción en lugar del crecimiento de la inversión: cuánto crece el empleo del sector por cada punto porcentual de crecimiento de su producto.

    $$\epsilon = \frac{\%\ \text{cambio en empleo}}{\%\ \text{cambio en producto}}$$

    Un valor mayor que uno indica un sector intensivo en trabajo. Ese es el sentido en que el factor captura la capacidad de generar empleo, que era el propósito declarado del indicador.

    La formulación original mencionaba la capacidad de crear empleo entre grupos específicos — mujeres, jóvenes, baja calificación. El cálculo actual no distingue grupos: usa empleo total (`EMPN`). La base tiene `EMPF`, empleo femenino, que permitiría construir esa versión desagregada.
    """)
    return


@app.cell
def _(df_empleo, pl):
    employment_growth_rate = pl.from_pandas(
        df_empleo[
            ["TIME_PERIOD", "ACTIVITY", "EMPN"]
        ].query(
            f"TIME_PERIOD in {[2018, 2019]}"
        )
    ).sort(
        ["ACTIVITY", "TIME_PERIOD"]
    ).group_by("ACTIVITY", maintain_order=True).agg(
            beginning_val = pl.col("EMPN").first(),
            ending_val = pl.col("EMPN").last(),
            n_years = pl.col("TIME_PERIOD").max() - pl.col("TIME_PERIOD").min(),
            #pl.col("PROD").pct_change().alias("Growth_Rate")
        ).with_columns(
            cagr_employment = ((pl.col("ending_val") / pl.col("beginning_val")) ** (1 / pl.col("n_years")) - 1)*100
    )

    employment_growth_rate
    return (employment_growth_rate,)


@app.cell
def _(employment_growth_rate, industry_growth_rate, pl):
    employment_elasticity = industry_growth_rate.select(
                                  "ACTIVITY", "cagr_production"
                            ).join(
                                employment_growth_rate.select(
                                    "ACTIVITY", "cagr_employment"
                                ), 
                                on = "ACTIVITY"
                            ).with_columns(
                                elasticity = pl.col("cagr_employment")/pl.col("cagr_production")
                            )
    employment_elasticity
    return (employment_elasticity,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 6. Factores de viabilidad

    Cinco factores miden qué tan alcanzable es cada industria para Honduras. A diferencia de los de atractivo, no todos entran como beneficio: tres son criterios de costo, donde un valor alto empeora la posición de la industria.

    ## 6.1 Fortaleza en países pares

    Se usa el RCA promedio de El Salvador y Ecuador como señal de que una industria es viable en economías de estructura comparable a la hondureña. La tabla de origen es `complejidad.cdata`, la salida del análisis de complejidad económica.
    """)
    return


@app.cell
def _(load_table, pl):
    ## Cargamos datos de complejidad y nos quedamos con los registros de honduras
    cdata = load_table("complejidad", "cdata")

    ## Analizamos solo los pares
    ## Calculamos el rca promedio entre los pares
    rca_peers = cdata.filter(
        pl.col("REF_AREA").is_in(["SLV", "ECU"])
    ).group_by("ACTIVITY").agg(
        pl.col("rca").mean().alias("rca_peers")
    ).rename({"ACTIVITY" : "ciiu"})

    rca_peers
    return cdata, rca_peers


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6.2 Disponibilidad de insumos

    Una industria es más viable si los insumos que necesita ya están al alcance del país. Para determinarlo se usa la red de producción de [AIPNET](https://aipnet.io/), que identifica qué productos entran como insumo de qué otros productos, cruzada con los flujos comerciales de Honduras en el Atlas.

    Un insumo se considera disponible si se cumple alguna de dos condiciones. Que Honduras lo exporte con ventaja comparativa revelada, señal de que el país lo produce en volumen competitivo. O que lo importe con intensidad, definida como representar al menos el 20% de las importaciones que implica la cadena de producción del producto, señal de que existe un canal de abastecimiento establecido.

    El factor final es la proporción de insumos disponibles sobre el total de insumos de la industria, ponderada por el peso de cada producto dentro de la clase CIIU.
    """)
    return


@app.cell
def _(load_table):
    ## Cargamos cadena de producción de los productos hs12 de aipnet
    aipnet = load_table("viabilidad_atractivo", "aipnet_hs12_4d")
    aipnet
    return (aipnet,)


@app.cell
def _(aipnet, ciiu_hs12):
    ## Reunimos datos de AIPNET con el crosswalk de CIIU-HS12
    nodo_madre = "hs2012_code_downstream"
    nodo_hijo = "hs2012_code_upstream"

    aipnet_ciiu = aipnet.join(
        ciiu_hs12, 
        left_on=nodo_hijo,
        right_on="hs12",
    ).select(
        "ciiu", "weight", nodo_hijo, nodo_madre
    ).rename(
        {
            nodo_hijo : "hs12"
        }
    )
    aipnet_ciiu
    return aipnet_ciiu, nodo_madre


@app.cell
def _(ciiu_hs12):
    ciiu_hs12
    return


@app.cell
def _(atlas_hs12, pl):
    ### Filtramos datos de HND
    atlas_hs12_hnd = atlas_hs12.filter(
        (pl.col("country_iso3_code")=="HND") &
        (pl.col("year")==2024)
    )
    atlas_hs12_hnd
    return (atlas_hs12_hnd,)


@app.cell
def _(aipnet_ciiu, atlas_hs12_hnd, nodo_madre, pl):
    ## Creamos dataframe que contiene el porcentaje de insumos presentes para la producción del producto hs12
    threshold_intensidad_importacion = 0.2 

    aipnet_ciiu_razon_insumos = aipnet_ciiu.join(
        atlas_hs12_hnd.select("product_hs12_code", "export_rca", "import_value"), 
        left_on=nodo_madre, 
        right_on="product_hs12_code", 
        how = "left"
    ).fill_null(0).with_columns(
        ## Etiquetamos con 1 los productos que se exportan con ventaja comparativa
        M = pl.when(
            pl.col("export_rca")>=1
        ).then(
            pl.lit(1)
        ).otherwise(
            pl.lit(0)
        ),
        ## Calculamos el porcentaje de importación por producto que importa cada cada producto para el total de importación que implica su cadena de producción
        razon_importacion = pl.col("import_value")/pl.col("import_value").sum().over("ciiu","hs12")
    ).with_columns(
        ## Variable que indica si el producto se importa con intensidad (el insumo representa el 20% de las importaciones totales con las que se produce el producto)
        se_importa = pl.when(
            pl.col("razon_importacion") >= threshold_intensidad_importacion
        ).then(
            pl.lit(1)
        ).otherwise(
            0
        )
    ).with_columns(
        ## Un insumo está disponible por dos condiciones : 
        ## 1) Lo exporta con ventaja comparativa o 
        ## 2) lo importa con intensidad 
        disponible = pl.when(
            (pl.col("M")==1) | (pl.col("se_importa")==1)
        ).then(
            pl.lit(1)
        ).otherwise(
            pl.lit(0)
        )
    ).group_by("ciiu","hs12", "weight").agg(
        pl.col("disponible").sum().alias("inputs_presentes"),
        pl.col("disponible").count().alias("inputs_totales"),
    ).with_columns(
        razon_insumos_presentes = pl.col("inputs_presentes")/pl.col("inputs_totales")
    ).with_columns(
        weight__insumos_presentes = pl.col("weight")*pl.col("razon_insumos_presentes")
    )
    aipnet_ciiu_razon_insumos
    return aipnet_ciiu_razon_insumos, threshold_intensidad_importacion


@app.cell
def _(aipnet_ciiu_razon_insumos, pl):
    ### Calculamos la razón de insumos presentes para cada industria CIIU
    ciiu_insumos_presentes = aipnet_ciiu_razon_insumos.group_by(
        "ciiu"
    ).agg(
        pl.col("weight__insumos_presentes").sum().alias("razon_insumos_presentes")
    )
    ciiu_insumos_presentes
    return (ciiu_insumos_presentes,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6.3 Dependencia energética

    La participación del gasto en productos energéticos (`INEN`) dentro del total de compras de bienes y servicios (`INGS`), para el año 2019.

    Entra a TOPSIS como criterio de costo: una industria que destina buena parte de su gasto a energía es más vulnerable en un país con restricciones de suministro y precios altos, así que una participación alta reduce su viabilidad.
    """)
    return


@app.cell
def _(df_produccion, pl):
    share_energy = pl.from_pandas(
        df_produccion
    ).filter(
        TIME_PERIOD=2019
    ).with_columns(
        share_energy = pl.col("INEN")/pl.col("INGS")
    ).select(
        "ACTIVITY", "share_energy"
    )
    share_energy
    return (share_energy,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6.4 Dependencia eléctrica

    La OCDE no desagrega el gasto eléctrico del gasto energético total, así que este factor se construye con datos mexicanos del Sistema Automatizado de Información Censal, que sí lo separan. La razón entre gasto en energía eléctrica y gasto total en bienes y servicios se toma para 2023 y se traduce de NAICS a CIIU mediante la tabla de correspondencia ponderada.

    El supuesto es que la intensidad eléctrica de una industria es una característica tecnológica, comparable entre países. Es un supuesto fuerte: la misma industria puede operar con tecnologías distintas en México y en Honduras. Entra como criterio de costo.
    """)
    return


@app.cell
def _(load_table):
    ## Cargamos crosswalk entre CIIU y NAICS
    ciiu_naics = load_table("diccionarios", "ponderadores_ciiu_naics2017_concordance")
    ciiu_naics
    return (ciiu_naics,)


@app.cell
def _(load_table):
    ## Cargamos consumo de energia electrica
    electricidad = load_table("viabilidad_atractivo", "electricidad_saic_2003-2023").to_pandas()
    electricidad["actividad"] = electricidad["actividad"].apply(lambda x : x.split()[1])

    electricidad_colname = "K412A Gasto por consumo de energía eléctrica (millones de pesos)"
    total_colname = "K000A Total de gastos por consumo de bienes y servicios (millones de pesos)"

    electricidad["razon_electricidad_gasto_total"] = electricidad[electricidad_colname]/electricidad[total_colname]
    electricidad = electricidad.drop(columns=[electricidad_colname, total_colname])
    electricidad = electricidad.pivot(index="actividad", columns="anio", values="razon_electricidad_gasto_total").reset_index()
    electricidad
    return (electricidad,)


@app.cell
def _(electricidad, pl):
    electricidad_share = pl.from_pandas(
        electricidad[["actividad", 2023]].rename(
            columns = {
                2023 : "razon_electricidad_gasto_total", 
                "actividad" : "naics"
            }
        )
    ).with_columns(
        pl.col("naics").cast(pl.Int32)
    )
    electricidad_share
    return (electricidad_share,)


@app.cell
def _(ciiu_naics, electricidad_share, pl):
    ### Reunimos razon de consumo de electricidad y el crosswalk CIIU-NAICS
    ### y calculamos la media ponderada por industria CIIU
    ciiu_razon_electricidad_gasto_total = ciiu_naics.join(
        electricidad_share, 
        on = "naics", 
        how="left"
    ).group_by("ciiu").agg(
        razon_electricidad_gasto_total = (pl.col("razon_electricidad_gasto_total") * pl.col("weight")).sum() / pl.col("weight").sum()
    )
    ciiu_razon_electricidad_gasto_total
    return (ciiu_razon_electricidad_gasto_total,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6.5 Intensidad institucional

    Cuantifica qué tanto depende una industria de la calidad del entorno institucional — cumplimiento de contratos, protección de la propiedad, resolución de disputas. Las industrias con contratos complejos y relaciones de largo plazo con proveedores son más sensibles a instituciones débiles.

    El índice viene en CIIU Rev. 2 a tres dígitos y se traduce a CIIU Rev. 4 a cuatro dígitos mediante una correspondencia ponderada. El peso de cada clase Rev. 4 se normaliza dentro del conjunto de correspondencias de su clase Rev. 2.

    Entra como criterio de costo: mayor dependencia institucional implica menor viabilidad en un contexto de instituciones débiles.
    """)
    return


@app.cell
def _(load_table, pl):
    ## Cargamos correspondencia CIIU Rev 2 (3 Digitos) a CIIU Rev 4 (4 Dígitos)
    cw_ciiu_rev_2_ciiu_rev_4 = load_table("diccionarios", "ciiu-rev-2_to_ciiu-rev-4")

    ## Calculamos el peso relativo de la actividad CIIU Rev 4 (4 Dígitos) en las correspondencias totales de actividades CIIU Rev 2 (3 Digitos) para posteriormente usarlas como pesos en el cálculo de la media ponderada de la actividad
    cw_ciiu_rev_2_ciiu_rev_4 = cw_ciiu_rev_2_ciiu_rev_4.with_columns(
        ( 
            pl.col("weight")/pl.col("weight").sum().over("ciiu4")
        ).alias("composicion")
    )

    ## Cargamos Datos de Institutional Intensity en CIIU Rev 2 (3 Digitos)
    inst_intensity = load_table("viabilidad_atractivo", "institutional_intensity")

    ### Reunimos el valor de institutional intensity y el crosswalk CIIU-Rev-2-CIIU-Rev-4
    ### y calculamos la media ponderada por industria CIIU
    df_institutional_intensity = cw_ciiu_rev_2_ciiu_rev_4.join(
        inst_intensity.select("ISIC", "Institutional Intensity"), 
        left_on="ciiu2", 
        right_on="ISIC", 
        how="left"
    ).group_by("ciiu4").agg(
            institutional_intensity = (pl.col("Institutional Intensity") * pl.col("composicion")).sum() / pl.col("composicion").sum()
        ).rename(
        {
            "ciiu4" : "ciiu"
        }
        )

    df_institutional_intensity
    return (df_institutional_intensity,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 7. Consolidación de factores

    Hasta aquí, cada factor se calculó por su cuenta, con su propia fuente, su propia unidad de análisis y su propio camino hasta la clase CIIU. La inversión extranjera llegó por subsectores de fDi Markets traducidos con un crosswalk. El crecimiento exportador llegó por productos HS12 ponderados dentro de cada industria. La dependencia eléctrica llegó desde el clasificador NAICS mexicano. La intensidad institucional llegó desde una revisión anterior de la CIIU.

    Esta sección junta esos caminos en una sola matriz: una fila por industria hondureña, una columna por factor. Es el paso donde se hacen visibles los huecos, porque ninguna de las quince fuentes cubre exactamente el mismo conjunto de industrias.

    El orden de operaciones importa. Primero se normalizan llaves y nombres, porque las tablas llegan con la industria llamada `CIIU`, `ACTIVITY` o `ciiu`, y con tipos distintos. Luego se unen. Después se recorta al universo hondureño. Y solo al final se imputan los faltantes, cuando ya se sabe cuáles son huecos reales y no artefactos de la unión.

    ## 7.1 Normalización de llaves y nombres

    Cada tabla se reduce a dos columnas, la industria y el factor, y se renombra a la convención que usarán las listas de TOPSIS en la Sección 8.
    """)
    return


@app.cell
def _(
    ciiu_china_intensiveness,
    ciiu_insumos_presentes,
    ciiu_razon_electricidad_gasto_total,
    elasticidad_lac_empleo_fdi,
    employment_elasticity,
    fdi_lac_cagr_investment,
    fdi_lac_capital_investment,
    industry_growth_rate,
    industry_growth_rate_exports,
    pl,
    share_energy,
):
    # Attractiveness
    ## Capacidad para movilizar FDI (region)

    ###  Monto acumulado de inversión en capital y creacion de empleo entre 2019 y 2024
    fdi_lac_capital_investment_final = pl.from_pandas(fdi_lac_capital_investment).select("CIIU", "Capital investment").rename({"CIIU":"ciiu", "Capital investment" : "cumulative_investment_lac"}).with_columns(
        pl.col("ciiu").cast(pl.Int64)
    )
    ### Tasa de crecimiento compuesta de la inversión entre 2019 y 2024 para cada industria
    fdi_lac_cagr_investment_final = fdi_lac_cagr_investment.select("CIIU", "cagr_investment").rename({"CIIU" : "ciiu", "cagr_investment" : "cagr_investment_lac"}).with_columns(
        pl.col("ciiu").cast(pl.Int64)
    )

    ### Elasticidad del crecimiento del empleo al crecimiento de FDI
    elasticidad_lac_empleo_fdi_final = elasticidad_lac_empleo_fdi.select("CIIU", "elasticidad").rename({"CIIU" : "ciiu", "elasticidad" : "elasticidad_empleo_fdi_lac"}).with_columns(
        pl.col("ciiu").cast(pl.Int64)
    )

    ## Industry growth worldwide (past five years)
    industry_growth_rate_final = industry_growth_rate.select("ACTIVITY","cagr_production").rename({"ACTIVITY" : "ciiu"}).with_columns(
        pl.col("ciiu").cast(pl.Int64)
    )

    ## Industry growth worldwide (past five years-Atlas export growth)
    industry_growth_rate_exports_final = industry_growth_rate_exports.select("ciiu", "cagr_exports").with_columns(
        pl.col("ciiu").cast(pl.Int64)
    )

    ## Possibility to substitute US imports from Asia (China)
    ciiu_china_intensiveness_final = ciiu_china_intensiveness.clone().with_columns(
        pl.col("ciiu").cast(pl.Int64)
    )

    ## Capacity to create employment 
    employment_elasticity_final = employment_elasticity.select("ACTIVITY", "elasticity").rename({"ACTIVITY" : "ciiu", "elasticity" : "elasticidad_empleo_producto"}).with_columns(
        pl.col("ciiu").cast(pl.Int64)
    )

    # Viability
    ## Strength in countries like Honduras (RCA in peer group)
    ## Availability of inputs (doble razor, let us talk)
    ciiu_insumos_presentes_final = ciiu_insumos_presentes.clone().with_columns(
        pl.col("ciiu").cast(pl.Int64)
    )

    ## Reliance on a constraint or potential constraint (energy, security)
    share_energy_final = share_energy.rename({"ACTIVITY" : "ciiu"}).with_columns(
        pl.col("ciiu").cast(pl.Int64)
    )

    ## Reliance on a constraint or potential constraint (electricity-SCIAN México)
    ciiu_razon_electricidad_gasto_total_final = ciiu_razon_electricidad_gasto_total.clone().with_columns(
        pl.col("ciiu").cast(pl.Int64)
    )
    return (
        ciiu_china_intensiveness_final,
        ciiu_insumos_presentes_final,
        ciiu_razon_electricidad_gasto_total_final,
        elasticidad_lac_empleo_fdi_final,
        employment_elasticity_final,
        fdi_lac_cagr_investment_final,
        fdi_lac_capital_investment_final,
        industry_growth_rate_exports_final,
        industry_growth_rate_final,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7.2 Universo de industrias

    El conjunto de industrias a evaluar sale de Honduras en la tabla de complejidad. Todo factor que no corresponda a una de esas industrias se descarta.
    """)
    return


@app.cell
def _(cdata):
    ## Cargamos datos de complejidad y nos quedamos con los registros de honduras
    cdata_hnd = cdata.filter(REF_AREA="HND")
    cdata_hnd
    return (cdata_hnd,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7.3 Matriz de factores

    `pl.concat(how="align")` une las quince tablas por su columna común, `ciiu`, conservando todas las industrias que aparezcan en cualquiera de ellas. Es equivalente a una cadena de uniones externas: una industria presente en una sola tabla aparece en el resultado con nulos en el resto.

    Por eso el filtro final es necesario. Sin él, la matriz incluiría industrias que existen en los datos de inversión extranjera o en el crosswalk de productos, pero que no están en el universo hondureño.
    """)
    return


@app.cell
def _(
    cdata_hnd,
    ciiu_china_intensiveness_final,
    ciiu_insumos_presentes_final,
    ciiu_razon_electricidad_gasto_total_final,
    df_institutional_intensity,
    elasticidad_lac_empleo_fdi_final,
    employment_elasticity_final,
    fdi_lac_cagr_investment_final,
    fdi_lac_capital_investment_final,
    industry_growth_rate_exports_final,
    industry_growth_rate_final,
    pl,
    rca_peers,
):
    ## Obtenemos las actividades CIIU a analizar
    ciiu_analiza = cdata_hnd.select("ACTIVITY").rename({"ACTIVITY" : "ciiu"})

    ## Concatena con los indicadores calculados
    factores = pl.concat(
        [
            ciiu_analiza, 
            fdi_lac_capital_investment_final,
            fdi_lac_cagr_investment_final,
            elasticidad_lac_empleo_fdi_final,
            industry_growth_rate_final,
            industry_growth_rate_exports_final,
            ciiu_china_intensiveness_final,
            employment_elasticity_final,
            rca_peers,
            ciiu_insumos_presentes_final,
            ciiu_razon_electricidad_gasto_total_final, 
            df_institutional_intensity
        ], how="align"
    ).filter(
        pl.col("ciiu").is_in(cdata_hnd["ACTIVITY"])
    )
    factores
    return (factores,)


@app.cell
def _(factores):
    ### Cobertura de cada factor antes de imputar
    total = len(factores)
    print(f"Industrias en la matriz: {total}\n")
    for col in factores.columns:
        if col == "ciiu":
            continue
        nulos = factores[col].null_count()
        print(f"  {col:38s}  faltantes: {nulos:4d}  ({nulos/total:5.1%})")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7.4 Imputación de faltantes

    No todas las industrias tienen valor en los diferentes factores de viabilidad y atractivo: la base de inversión extranjera no cubre todas las clases CIIU, y las tablas de correspondencia dejan huecos. TOPSIS no admite faltantes, así que se imputan con el método de los k vecinos más cercanos, con k igual a dos.

    El método busca, para cada industria con un dato faltante, las dos industrias más parecidas según los factores que sí tiene, y le asigna el promedio de esas dos.
    """)
    return


@app.cell
def _(factores, pd, pl):
    ## Imputamos datos con K vecinos más cercanos
    from sklearn.impute import KNNImputer

    # Initialize the imputer (setting K=2 neighbors)
    imputer = KNNImputer(n_neighbors=2, weights="uniform")

    # Fit and transform the data
    factores_imputados = pl.from_pandas(
        pd.DataFrame(imputer.fit_transform(factores.to_pandas()), columns=factores.columns)
    )
    factores_imputados
    return KNNImputer, factores_imputados, imputer


@app.cell
def _(KNNImputer, factores, imputer, pd, pl):
    ### La llave de industria no participa en el cálculo de distancias
    columnas_factores = [c for c in factores.columns if c != "ciiu"]

    imputer_1 = KNNImputer(n_neighbors=2, weights="uniform")

    factores_imputados_1 = pl.concat(
        [
            factores.select("ciiu"),
            pl.from_pandas(
                pd.DataFrame(
                    imputer.fit_transform(factores.select(columnas_factores).to_pandas()),
                    columns=columnas_factores,
                )
            ),
        ],
        how="horizontal",
    )

    factores_imputados_1
    return (factores_imputados_1,)


@app.cell
def _(factores_imputados, factores_imputados_1):
    ### Celda temporal: diferencia entre imputaciones
    def _compara_imputaciones(nuevo, viejo):
        filas = []
        for c in nuevo.columns:
            if c == "ciiu":
                continue
            filas.append((c, int((nuevo[c] != viejo[c]).sum())))

        filas.sort(key=lambda x: -x[1])

        salida = [f"{'Factor':38s}  valores que cambian"]
        for c, n in filas:
            salida.append(f"  {c:38s}  {n}")
        return "\n".join(salida)


    print(_compara_imputaciones(factores_imputados, factores_imputados_1))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 8. Cálculo de los índices

    Los factores ya están en una matriz completa. Falta reducirlos a dos números por industria: uno de atractivo y uno de viabilidad.

    TOPSIS lo hace midiendo distancias. Normaliza cada columna para que las escalas sean comparables, construye una industria ideal — la que tendría el mejor valor en cada factor — y una anti-ideal, y puntúa cada industria real por su cercanía relativa a la primera. El resultado va de cero a uno.

    Cada factor se declara como beneficio o como costo, y eso determina qué extremo cuenta como ideal. Los diez factores de atractivo entran como beneficio. En viabilidad, el RCA de países pares y la disponibilidad de insumos son beneficio; la dependencia energética, la eléctrica y la intensidad institucional son costo.

    Los pesos son uniformes dentro de cada índice. Es una decisión deliberada: sin evidencia sobre la importancia relativa de los factores, repartirlos por igual evita introducir un juicio no documentado y es un punto de partida razonable ante la ausencia de un criterio de ponderación robusto.
    """)
    return


@app.cell
def _():
    import numpy as np
    from pymcdm.methods import TOPSIS
    from pymcdm.helpers import rrankdata, normalize_matrix

    return TOPSIS, np, rrankdata


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 8.1 Índice de atractivo

    Se aplica TOPSIS a los factores de la Sección 5, todos como criterios de beneficio y con peso uniforme cada uno.
    """)
    return


@app.cell
def _(TOPSIS, factores_imputados, np, rrankdata):
    # TOPSIS atractivo
    atractivo_factores = [
        "cumulative_investment_lac",
        "cagr_investment_lac",
        "elasticidad_empleo_fdi_lac",
        "cagr_production",
        "cagr_exports",
        "share_imports_china", 
        "elasticidad_empleo_producto"
    ]

    alts_atractivo = factores_imputados.select(atractivo_factores).to_numpy()

    # Define criteria weights (should sum up to 1)
    weights_atractivo = np.array([1/len(atractivo_factores)]*len(atractivo_factores))

    # Define criteria types (1 for profit, -1 for cost)
    types_atractivo = np.array([1]*len(atractivo_factores))

    # Create object of the method
    # Note, that default normalization method for TOPSIS is minmax
    topsis_atractivo = TOPSIS()

    # Determine preferences and ranking for alternatives
    pref_atractivo = topsis_atractivo(alts_atractivo, weights_atractivo, types_atractivo)
    ranking_atractivo = rrankdata(pref_atractivo)

    # If you want to inspect computation process in details
    results_atractivo = topsis_atractivo(alts_atractivo, weights_atractivo, types_atractivo, verbose=True)
    return pref_atractivo, topsis_atractivo


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 8.2 Índice de viabilidad

    Se aplica TOPSIS a los factores de la Sección 6, con peso uniforme de un quinto cada uno. A diferencia del atractivo, aquí los tipos de criterio no son todos iguales. Los primeros dos tienen un criterio de suma, mientras que los de electricidad y calidad institucional a mayores valores, restan.
    """)
    return


@app.cell
def _(TOPSIS, factores_imputados, np, rrankdata):
    # TOPSIS Viabilidad
    viabilidad_factores = [
        "rca_peers",
        "razon_insumos_presentes", 
        "razon_electricidad_gasto_total",
        "institutional_intensity"
    ]

    alts_viabilidad = factores_imputados.select(viabilidad_factores).to_numpy()

    # Define criteria weights (should sum up to 1)
    weights_viabilidad = np.array([1/len(viabilidad_factores)]*len(viabilidad_factores))

    # Define criteria types (1 for profit, -1 for cost)
    types_viabilidad = np.array([1, 1, -1, -1])

    # Create object of the method
    # Note, that default normalization method for TOPSIS is minmax
    topsis_viabilidad = TOPSIS()

    # Determine preferences and ranking for alternatives
    pref_viabilidad = topsis_viabilidad(alts_viabilidad, weights_viabilidad, types_viabilidad)
    ranking_viabilidad = rrankdata(pref_viabilidad)
    return (pref_viabilidad,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 8.3 Tabla de scores

    Los dos vectores de preferencia se pegan a la llave de industria. Esta tabla es lo que consumen los diagramas de la Sección 9 y, más adelante, el análisis textil.

    El orden de las filas importa: `pref_atractivo` y `pref_viabilidad` son arreglos de numpy sin llave propia, y se asignan por posición. Coinciden con `factores_imputados` porque salen de esa misma matriz sin reordenarla.
    """)
    return


@app.cell
def _(factores_imputados, pl, pref_atractivo, pref_viabilidad):
    ### Creamos data frame con los scores de viabilidad y atractivo
    scores_viabilidad_atractivo = factores_imputados.select("ciiu").with_columns(
            topsis_atractivo = pref_atractivo, 
            topsis_viabilidad = pref_viabilidad, 
    ).with_columns(
        pl.col("ciiu").cast(pl.Int64)
    )
    scores_viabilidad_atractivo
    return (scores_viabilidad_atractivo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 9. Diagramas de viabilidad y atractivo

    Los dos índices se cruzan en un plano. Cada industria es un punto, las líneas punteadas marcan las medias de cada eje, y los cuatro cuadrantes se leen como fases de intervención: la Fase I reúne lo atractivo y viable, la Fase IV lo que no es ninguna de las dos cosas.

    El ejercicio se hace por separado en los dos márgenes. El intensivo son industrias donde Honduras ya tiene presencia, y la pregunta es cuáles conviene profundizar. El extensivo son industrias que el país no desarrolla actualmente con cierto grado de especialización, y la pregunta es cuáles conviene abrir.

    El color distingue el cluster de política al que pertenece cada industria. Esa asignación no se calcula aquí: viene del archivo `datos/seleccion_final_complexity.xlsx`.

    ## 9.1 Insumos de etiquetado y selección final

    Tres cargas: los nombres de actividad, el catálogo CIIU con su jerarquía sectorial, y la selección final de industrias por margen con su cluster asignado.
    """)
    return


@app.cell
def _(load_table, pd, pl):
    # Cargamos recodificación
    recod = load_table("diccionarios", "catalogo_ciiu_rev4_nombres").to_pandas()

    ## Diccionario CIIU 4 a nombres
    mapp_ciiu = pl.from_pandas(recod.query("clasificador=='ciiu_rev_4'")[["codigo", "nombre_actividad"]])

    ### Cargamos selección de industrias
    ciiu_industrias = pl.from_pandas(
        load_table("diccionarios", "catalogo_ciiu_rev4").to_pandas().query("incluye==1")
    )

    ### Resultados finales Intensivo
    #resultados_finales_intensivo = pd.read_excel("datos/viabilidad_atractivo/Resultados Complexity_final.xlsx", sheet_name="Intensivo")
    resultados_finales_intensivo = pd.read_excel("datos/seleccion_final_complexity.xlsx", sheet_name="intensivo")

    ### Resultados finales Extensivo
    #resultados_finales_extensivo = pd.read_excel("datos/viabilidad_atractivo/Resultados Complexity_final.xlsx", sheet_name="Extensivo")
    resultados_finales_extensivo = pd.read_excel("datos/seleccion_final_complexity.xlsx", sheet_name="extensivo")
    return (
        ciiu_industrias,
        mapp_ciiu,
        resultados_finales_extensivo,
        resultados_finales_intensivo,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Margen intensivo:
    """)
    return


@app.cell
def _(resultados_finales_intensivo):
    resultados_finales_intensivo
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Margen extensivo:
    """)
    return


@app.cell
def _(resultados_finales_extensivo):
    resultados_finales_extensivo
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 9.2 Paleta de clusters

    Se identificaron seis clusters de industrias, con colores fijos para que ambos diagramas sean comparables entre sí y con cualquier material que los acompañe.
    """)
    return


@app.cell
def _():
    import altair as alt 

    color_cat = [
      "C1 Manufactura avanzada y metalmecánica",
      "C2 Química, materiales y farmacéutica",
      "C3 Agroindustria y alimentos procesados",
      "C4 Servicios empresariales intensivos en conocimiento (KIBS)",
      "C5 Turismo, conectividad y logística",
      "C6 Textiles, confección y materiales flexibles"
    ]

    color_hexa = ["#4E79A7", "#F28E2B", "#E15759", "#76B7B2", "#59A14F", "#EDC948"]
    return alt, color_cat, color_hexa


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 9.3 Margen intensivo

    Qué industrias pertenecen a este margen lo define la hoja `intensivo` de `datos/seleccion_final_complexity.xlsx`. Luego se agregan los datos en una matriz final que incorpora el puntaje de viabilidad y atractivo. Posteriormente, se diagrama una estrategia basada en los puntajes de viabilidad y atractivo en cuatro fases.
    """)
    return


@app.cell
def _(
    cdata_hnd,
    ciiu_industrias,
    mapp_ciiu,
    pl,
    resultados_finales_intensivo,
    scores_viabilidad_atractivo,
):
    ### Datos del margen intensivo
    cdata_intensivo = cdata_hnd.filter(
        pl.col("ACTIVITY").is_in(resultados_finales_intensivo["ciiu4_cod"])
    )

    cdata_intensivo = cdata_intensivo.join(
        mapp_ciiu,
        left_on="ACTIVITY",
        right_on="codigo",
    ).join(
        ciiu_industrias.select(
            "clase_codigo", "clase_titulo", "seccion_codigo", "seccion_titulo",
            "division_titulo",
        ),
        left_on="ACTIVITY",
        right_on="clase_codigo",
    )

    cdata_intensivo = cdata_intensivo.join(
        scores_viabilidad_atractivo,
        left_on="ACTIVITY",
        right_on="ciiu",
    ).join(
        pl.from_pandas(resultados_finales_intensivo[["Clusters", "ciiu4_cod"]]),
        left_on="ACTIVITY",
        right_on="ciiu4_cod",
    )

    cdata_intensivo
    return (cdata_intensivo,)


@app.cell
def _(alt, cdata_intensivo, color_cat, color_hexa, pd):
    ### Diagrama de cuadrantes, margen intensivo
    plot_intensivo = (
        alt.Chart(cdata_intensivo)
        .mark_circle(
            opacity=0.99,
            stroke="black",
            strokeWidth=1.2,
            strokeOpacity=0.9,
            size=180,
        )
        .encode(
            x=alt.X("topsis_viabilidad").scale(zero=False).title("Viabilidad"),
            y=alt.Y("topsis_atractivo").scale(zero=False).title("Atractivo"),
            color=alt.Color(
                "Clusters", scale=alt.Scale(domain=color_cat, range=color_hexa)
            ).title("Cluster"),
            tooltip=[
                alt.Tooltip("nombre_actividad", title="Actividad"),
                alt.Tooltip("division_titulo", title="División CIIU Rev 4"),
                alt.Tooltip("OBS_VALUE", title="Empleo"),
            ],
        )
    )

    ### Líneas divisorias en la media de cada eje
    rule_atractivo = (
        alt.Chart(pd.DataFrame({"y": [cdata_intensivo["topsis_atractivo"].mean()]}))
        .mark_rule(color="gray", strokeDash=[4, 4], strokeWidth=3)
        .encode(y="y:Q")
    )
    rule_viabilidad = (
        alt.Chart(pd.DataFrame({"x": [cdata_intensivo["topsis_viabilidad"].mean()]}))
        .mark_rule(color="gray", strokeDash=[4, 4], strokeWidth=3)
        .encode(x="x:Q")
    )

    ### Etiquetas de fase, una por cuadrante
    quadrant_labels_intensivo = pd.DataFrame(
        {
            "y_pos": [
                cdata_intensivo["topsis_atractivo"].max(),
                cdata_intensivo["topsis_atractivo"].min(),
                cdata_intensivo["topsis_atractivo"].max(),
                cdata_intensivo["topsis_atractivo"].min(),
            ],
            "x_pos": [
                cdata_intensivo["topsis_viabilidad"].max() * 0.95,
                cdata_intensivo["topsis_viabilidad"].max() * 0.95,
                cdata_intensivo["topsis_viabilidad"].min() * 1.05,
                cdata_intensivo["topsis_viabilidad"].min() * 1.05,
            ],
            "label": ["Fase I", "Fase II", "Fase III", "Fase IV"],
        }
    )

    text_layer_intensivo = (
        alt.Chart(quadrant_labels_intensivo)
        .mark_text(size=14, fontStyle="bold", color="black")
        .encode(x="x_pos:Q", y="y_pos:Q", text="label:N")
    )

    (plot_intensivo + rule_atractivo + rule_viabilidad + text_layer_intensivo).properties(
        title=alt.TitleParams(
            "Diagrama Viabilidad-Atractivo",
            subtitle="Margen Intensivo",
            subtitleColor="gray",
        )
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 9.4 Margen extensivo

    Industrias que Honduras no desarrolla hoy. La pregunta aquí es de apertura: cuáles de las oportunidades identificadas por el análisis de complejidad valen el esfuerzo una vez que se consideran el atractivo del mercado y la viabilidad de entrar. Posteriormente, se diagrama una estrategia basada en los puntajes de viabilidad y atractivo en cuatro fases.
    """)
    return


@app.cell
def _(
    cdata_hnd,
    ciiu_industrias,
    mapp_ciiu,
    pl,
    resultados_finales_extensivo,
    scores_viabilidad_atractivo,
):
    ### Datos del margen extensivo
    cdata_extensivo = cdata_hnd.filter(
        pl.col("ACTIVITY").is_in(resultados_finales_extensivo["ciiu4_cod"])
    )

    cdata_extensivo = cdata_extensivo.join(
        mapp_ciiu,
        left_on="ACTIVITY",
        right_on="codigo",
    ).join(
        ciiu_industrias.select(
            "clase_codigo",
            "clase_titulo",
            "seccion_codigo",
            "seccion_titulo",
            "division_titulo",
        ),
        left_on="ACTIVITY",
        right_on="clase_codigo",
    )

    cdata_extensivo = cdata_extensivo.join(
        scores_viabilidad_atractivo,
        left_on="ACTIVITY",
        right_on="ciiu",
    ).join(
        pl.from_pandas(resultados_finales_extensivo[["Clusters", "ciiu4_cod"]]),
        left_on="ACTIVITY",
        right_on="ciiu4_cod",
    )

    cdata_extensivo
    return (cdata_extensivo,)


@app.cell
def _(alt, cdata_extensivo, color_cat, color_hexa, pd):
    ### Diagrama de cuadrantes, margen extensivo
    plot_extensivo = (
        alt.Chart(cdata_extensivo)
        .mark_circle(
            opacity=0.99,
            stroke="black",
            strokeWidth=1.2,
            strokeOpacity=0.9,
            size=180,
        )
        .encode(
            x=alt.X("topsis_viabilidad").scale(zero=False).title("Viabilidad"),
            y=alt.Y("topsis_atractivo").scale(zero=False).title("Atractivo"),
            color=alt.Color(
                "Clusters", scale=alt.Scale(domain=color_cat, range=color_hexa)
            ).title("Cluster"),
            tooltip=[
                alt.Tooltip("nombre_actividad", title="Actividad"),
                alt.Tooltip("division_titulo", title="División CIIU Rev 4"),
                alt.Tooltip("OBS_VALUE", title="Empleo"),
            ],
        )
    )

    ### Líneas divisorias en la media de cada eje
    rule_extensivo_atractivo = (
        alt.Chart(pd.DataFrame({"y": [cdata_extensivo["topsis_atractivo"].mean()]}))
        .mark_rule(color="gray", strokeDash=[4, 4], strokeWidth=3)
        .encode(y="y:Q")
    )
    rule_extensivo_viabilidad = (
        alt.Chart(pd.DataFrame({"x": [cdata_extensivo["topsis_viabilidad"].mean()]}))
        .mark_rule(color="gray", strokeDash=[4, 4], strokeWidth=3)
        .encode(x="x:Q")
    )

    ### Etiquetas de fase, una por cuadrante
    quadrant_labels = pd.DataFrame(
        {
            "y_pos": [
                cdata_extensivo["topsis_atractivo"].max(),
                cdata_extensivo["topsis_atractivo"].min(),
                cdata_extensivo["topsis_atractivo"].max(),
                cdata_extensivo["topsis_atractivo"].min(),
            ],
            "x_pos": [
                cdata_extensivo["topsis_viabilidad"].max() * 0.95,
                cdata_extensivo["topsis_viabilidad"].max() * 0.95,
                cdata_extensivo["topsis_viabilidad"].min() * 1.05,
                cdata_extensivo["topsis_viabilidad"].min() * 1.05,
            ],
            "label": ["Fase I", "Fase II", "Fase III", "Fase IV"],
        }
    )

    text_layer = (
        alt.Chart(quadrant_labels)
        .mark_text(size=14, fontStyle="bold", color="black")
        .encode(x="x_pos:Q", y="y_pos:Q", text="label:N")
    )

    (
        plot_extensivo + rule_extensivo_atractivo + rule_extensivo_viabilidad + text_layer
    ).properties(
        title=alt.TitleParams(
            "Diagrama Viabilidad-Atractivo",
            subtitle="Margen Extensivo",
            subtitleColor="gray",
        )
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 10. Productos textiles

    El análisis de las secciones anteriores opera sobre industrias CIIU. Este bloque repite el ejercicio de viabilidad y atractivo sobre productos HS12 a cuatro dígitos, porque en el sector textil las decisiones de política se definen por producto y la agregación a clase industrial borra distinciones relevantes.

    Los factores son los mismos, traducidos de CIIU rev 4 a HS12 mediante una correspondencia ponderada: cada producto hereda el valor de las industrias con las que corresponde, pesado por el peso de esa correspondencia. Dos factores se calculan directamente sobre productos, sin pasar por CIIU: el crecimiento exportador y la participación china en las importaciones estadounidenses.

    El alcance geográfico es más estrecho que en el análisis principal.

    ## 10.1 Universo de productos

    La selección de productos textiles y su correspondencia con clases CIIU provienen de dos tablas del namespace `viabilidad_atractivo`.
    """)
    return


@app.cell
def _(load_table, pl):
    # Cargamos productos seleccionados de Textiles
    textiles = load_table(
                    "viabilidad_atractivo", "productos_textiles"
                ).with_columns(
                    pl.col("HS12").cast(pl.String)
                ).rename(
                    {"HS12":"hs12"}
                )
    textiles
    return (textiles,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Se cargan las correspondencias entre CIIU y HS12 y los pesos:
    """)
    return


@app.cell
def _(load_table):
    # Cargamos CW de productos textiles
    cw_textiles = load_table("viabilidad_atractivo", "productos_textiles_cw_hs12_ciiu4")
    cw_textiles
    return (cw_textiles,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 10.2 Factores de atractivo

    Se toman los siguientes criterios:
    1. Monto acumulado de inversión en capital (LAC) (+)
    2. Tasa de crecimiento de la inversión (LAC) (+)
    3. Elasticidad Empleo/Inversión (LAC) (+)
    4. Crecimiento de la Producción mundial (+)
    5. Crecimiento de las Exportaciones mundiales (+)
    6. Dependencia de EU de importaciones desde China (+)
    7. Capacidad para crear empleo (+)


    Los siguientes bloques de código presentan, de manera ordenada, la preparación de cada uno de los indicadores mencionados.
    """)
    return


@app.cell
def _(cw_textiles, fdi_lac_capital_investment, pl):
    ## Capacidad para movilizar FDI (LAC)
    ## Agrupamos por actividad CIIU para tener el monto acumulado de inversión en capital y creacion de empleo entre 2019 y 2024

    textiles_fdi_lac_capital_investment = cw_textiles.with_columns(
        pl.col("ISIC4").cast(pl.String)
    ).join(
        pl.from_pandas(fdi_lac_capital_investment),
        left_on="ISIC4", 
        right_on="CIIU", 
        how="left"
    ).with_columns(
        pl.col("Capital investment")*pl.col("weight"),
        pl.col("Jobs created")*pl.col("weight"),
    ).drop(
        "ISIC4", "weight"
    ).group_by("hs12").sum().with_columns(
        pl.col("hs12").map_elements(lambda x : f"{x:04d}")
    ).rename(
        {"Capital investment" : "cumulative_investment_lac"}
    )

    textiles_fdi_lac_capital_investment
    return (textiles_fdi_lac_capital_investment,)


@app.cell
def _(cw_textiles, fdi_lac_cagr_investment, pl):
    ## Tasa de crecimiento compuesta para inversión de industrias en todo el mundo
    textiles_fdi_lac_cagr_investment = cw_textiles.with_columns(
        pl.col("ISIC4").cast(pl.String)
    ).join(
        fdi_lac_cagr_investment,
        left_on="ISIC4", 
        right_on="CIIU", 
        how="left"
    ).with_columns(
        pl.col("beginning_val")*pl.col("weight"),
        pl.col("ending_val")*pl.col("weight"),
    ).group_by("hs12").agg(
        pl.col("beginning_val").sum(),  
        pl.col("ending_val").sum(),  
        (pl.col("n_years").sum()/pl.col("n_years").count()).alias("n_years")
    ).fill_nan(0.0).with_columns(
        cagr_investment = ((pl.col("ending_val") / pl.col("beginning_val")) ** (1 / pl.col("n_years")) - 1)*100
    ).select("hs12", "cagr_investment").with_columns(
        pl.col("hs12").cast(pl.String)
    )


    textiles_fdi_lac_cagr_investment
    return (textiles_fdi_lac_cagr_investment,)


@app.cell
def _(cw_textiles, fdi_lac_cagr_empleo, pl):
    ## Tasa de crecimiento compuesta para inversión de industrias en lac
    textiles_fdi_lac_cagr_empleo = cw_textiles.with_columns(
        pl.col("ISIC4").cast(pl.String)
    ).join(
        fdi_lac_cagr_empleo,
        left_on="ISIC4", 
        right_on="CIIU", 
        how="left"
    ).with_columns(
        pl.col("beginning_val")*pl.col("weight"),
        pl.col("ending_val")*pl.col("weight"),
    ).group_by("hs12").agg(
        pl.col("beginning_val").sum(),  
        pl.col("ending_val").sum(),  
        (pl.col("n_years").sum()/pl.col("n_years").count()).alias("n_years")
    ).fill_nan(0.0).with_columns(
        cagr_empleo = ((pl.col("ending_val") / pl.col("beginning_val")) ** (1 / pl.col("n_years")) - 1)*100
    ).select("hs12", "cagr_empleo").with_columns(
        pl.col("hs12").cast(pl.String)
    )

    textiles_fdi_lac_cagr_empleo 
    return (textiles_fdi_lac_cagr_empleo,)


@app.cell
def _(pl, textiles_fdi_lac_cagr_empleo, textiles_fdi_lac_cagr_investment):
    ### Elasticidad del empleo a la inversión extranjera directa
    textiles_elasticidad_lac_empleo_fdi = textiles_fdi_lac_cagr_investment.select("hs12", "cagr_investment").join(
        textiles_fdi_lac_cagr_empleo.select("hs12", "cagr_empleo"), 
        on = "hs12",
    ).with_columns(
        elasticidad_empleo_fdi = pl.col("cagr_empleo")/pl.col("cagr_investment")
    ).select("hs12", "elasticidad_empleo_fdi")
    textiles_elasticidad_lac_empleo_fdi
    return (textiles_elasticidad_lac_empleo_fdi,)


@app.cell
def _(pl, textiles_fdi_lac_cagr_empleo, textiles_industry_growth_rate):
    ### Elasticidad del empleo al crecimiento de la producción de la industria
    textiles_elasticidad_empleo_producto = textiles_industry_growth_rate.select("hs12", "cagr_production").join(
        textiles_fdi_lac_cagr_empleo.select("hs12", "cagr_empleo"), 
        on = "hs12",
    ).with_columns(
        elasticidad_empleo_producto = pl.col("cagr_empleo")/pl.col("cagr_production")
    ).select("hs12", "elasticidad_empleo_producto")
    textiles_elasticidad_empleo_producto
    return (textiles_elasticidad_empleo_producto,)


@app.cell
def _(cw_textiles, industry_growth_rate, pl):
    ## ⁠Industry growth worldwide (2019 vs 2018) como en la sección 5
    textiles_industry_growth_rate = cw_textiles.with_columns(
        pl.col("ISIC4").cast(pl.String)
    ).join(
        industry_growth_rate.drop("cagr_production"),
        left_on="ISIC4", 
        right_on="ACTIVITY", 
        how="left"
    ).with_columns(
        pl.col("beginning_val")*pl.col("weight"),
        pl.col("ending_val")*pl.col("weight"),
    ).group_by("hs12").agg(
        pl.col("beginning_val").sum(),  
        pl.col("ending_val").sum(),  
        (pl.col("n_years").sum()/pl.col("n_years").count()).alias("n_years")
    ).fill_nan(0.0).with_columns(
        cagr_production = ((pl.col("ending_val") / pl.col("beginning_val")) ** (1 / pl.col("n_years")) - 1)*100
    ).select("hs12", "cagr_production").with_columns(
        pl.col("hs12").cast(pl.String)
    )

    textiles_industry_growth_rate
    return (textiles_industry_growth_rate,)


@app.cell
def _(exportaciones_hs, pl):
    ## ⁠Industry growth worldwide (past five years-Atlas export growth)
    textiles_industry_growth_rate_exports = exportaciones_hs.sort(
        ["product_hs12_code", "year"]
    ).group_by("product_hs12_code", maintain_order=True).agg(
            beginning_val = pl.col("export_value").first(),
            ending_val = pl.col("export_value").last(),
            n_years = pl.col("year").max() - pl.col("year").min(),
            #pl.col("PROD").pct_change().alias("Growth_Rate")
        ).with_columns(
        cagr_exports = ((pl.col("ending_val") / pl.col("beginning_val")) ** (1 / pl.col("n_years")) - 1)*100
    ).with_columns(
        pl.col("product_hs12_code").map_elements(lambda x : f"{x:04d}")
    ).rename(
        {"product_hs12_code" : "hs12"}
    ).select("hs12", "cagr_exports")
    textiles_industry_growth_rate_exports
    return (textiles_industry_growth_rate_exports,)


@app.cell
def _(china_imports, pl):
    ## ⁠Possibility to substitute US imports from Asia (China) 
    textiles_china_imports = china_imports.with_columns(
        pl.col("product_hs12_code").map_elements(lambda x : f"{x:04d}")
    ).rename(
        {"product_hs12_code" : "hs12"}
    )
    textiles_china_imports
    return (textiles_china_imports,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 10.3 Factores de viabilidad

    Se toman los siguientes criterios:
    1. Fortaleza en países como Honduras (RCA entre pares) (+)
    2. Disponibilidad de Insumos (+)
    3. Dependencia o restricción potencial (Electricidad) (+)
    4. Intensidad institucional (-)

    Los siguientes bloques de código presentan, de manera ordenada, la preparación de cada uno de los indicadores mencionados.
    """)
    return


@app.cell
def _(atlas_hs12, pl):
    ## Strength in countries like Honduras (RCA in peer group)
    import polars.selectors as cs

    paises_pares_lac = ["SLV", "ECU"]

    textiles_rca_peers = atlas_hs12.filter(
        (pl.col("country_iso3_code").is_in(paises_pares_lac)) &
        (pl.col("year")==2024)
    ).select(
        "product_hs12_code", "country_iso3_code", "export_rca"
    ).fill_null(0).with_columns(
        ## Etiquetamos con 1 los productos que se exportan con ventaja comparativa
        M = pl.when(
            pl.col("export_rca")>=1
        ).then(
            pl.lit(1)
        ).otherwise(
            pl.lit(0)
        ),
    ).pivot(
        index="product_hs12_code",
        on="country_iso3_code",
        values="M",
        aggregate_function="sum",
    ).with_columns(
        (
             pl.sum_horizontal(paises_pares_lac).alias("rca_peers") / 3   
        )
        , 
        pl.col("product_hs12_code").map_elements(lambda x : f"{x:04d}")
    ).rename(
        {
            "product_hs12_code" : "hs12"
        }
    ).select("hs12", "rca_peers")
    textiles_rca_peers
    return (textiles_rca_peers,)


@app.cell
def _(
    aipnet_ciiu,
    atlas_hs12_hnd,
    nodo_madre,
    pl,
    threshold_intensidad_importacion,
):
    ## Availability of inputs
    textiles_availability_inputs = aipnet_ciiu.drop("ciiu", "weight").join(
        atlas_hs12_hnd.select("product_hs12_code", "export_rca", "import_value"), 
        left_on=nodo_madre, 
        right_on="product_hs12_code", 
        how = "left"
    ).fill_null(0).with_columns(
        ## Etiquetamos con 1 los productos que se exportan con ventaja comparativa
        M = pl.when(
            pl.col("export_rca")>=1
        ).then(
            pl.lit(1)
        ).otherwise(
            pl.lit(0)
        ),
        ## Calculamos el porcentaje de importación por producto que importa cada cada producto para el total de importación que implica su cadena de producción
        razon_importacion = pl.col("import_value")/pl.col("import_value").sum().over("hs12")
    ).with_columns(
        ## Variable que indica si el producto se importa con intensidad (el insumo representa el 20% de las importaciones totales con las que se produce el producto)
        se_importa = pl.when(
            pl.col("razon_importacion") >= threshold_intensidad_importacion
        ).then(
            pl.lit(1)
        ).otherwise(
            0
        )
    ).with_columns(
        ## Un insumo está disponible por dos condiciones : 
        ## 1) Lo exporta con ventaja comparativa o 
        ## 2) lo importa con intensidad 
        disponible = pl.when(
            (pl.col("M")==1) | (pl.col("se_importa")==1)
        ).then(
            pl.lit(1)
        ).otherwise(
            pl.lit(0)
        )
    ).group_by("hs12").agg(
        pl.col("disponible").sum().alias("inputs_presentes"),
        pl.col("disponible").count().alias("inputs_totales"),
    ).with_columns(
        razon_insumos_presentes = pl.col("inputs_presentes")/pl.col("inputs_totales")
    ).select("hs12", "razon_insumos_presentes").with_columns(
        pl.col("hs12").map_elements(lambda x : f"{x:04d}")
    )
    textiles_availability_inputs
    return (textiles_availability_inputs,)


@app.cell
def _(cw_textiles, pl, share_energy):
    ## Reliance on a constraint or potential constraint (energy, security)
    textiles_share_energy = cw_textiles.with_columns(
        pl.col("ISIC4").cast(pl.String)
    ).join(
        share_energy,
        left_on="ISIC4", 
        right_on="ACTIVITY", 
        how="left"
    ).group_by("hs12").agg(
                share_energy = (pl.col("share_energy") * pl.col("weight")).sum() / pl.col("weight").sum()
    ).with_columns(
        pl.col("hs12").cast(pl.String)
    )

    textiles_share_energy
    return (textiles_share_energy,)


@app.cell
def _(ciiu_razon_electricidad_gasto_total, cw_textiles, pl):
    ## Reliance on a constraint or potential constraint (electricity-SCIAN México)
    textiles_ciiu_razon_electricidad_gasto_total = cw_textiles.with_columns(
        pl.col("ISIC4").cast(pl.String)
    ).join(
        ciiu_razon_electricidad_gasto_total.with_columns(
            pl.col("ciiu").cast(pl.String)
        ),
        left_on="ISIC4", 
        right_on="ciiu", 
        how="left"
    ).group_by("hs12").agg(
                razon_electricidad_gasto_total = (pl.col("razon_electricidad_gasto_total") * pl.col("weight")).sum() / pl.col("weight").sum()
    ).with_columns(
        pl.col("hs12").cast(pl.String)
    )
    textiles_ciiu_razon_electricidad_gasto_total
    return (textiles_ciiu_razon_electricidad_gasto_total,)


@app.cell
def _(cw_textiles, df_institutional_intensity, pl):
    ## Institutional Intensity
    textiles_df_institutional_intensity = cw_textiles.with_columns(
        pl.col("ISIC4").cast(pl.String)
    ).join(
        df_institutional_intensity.with_columns(
            pl.col("ciiu").cast(pl.String)
        ),
        left_on="ISIC4", 
        right_on="ciiu", 
        how="left"
    ).group_by("hs12").agg(
                institutional_intensity = (pl.col("institutional_intensity") * pl.col("weight")).sum() / pl.col("weight").sum()
    ).with_columns(
        pl.col("hs12").cast(pl.String)
    )
    textiles_df_institutional_intensity
    return (textiles_df_institutional_intensity,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 10.4 Consolidación e imputación

    Las tablas de factores se unen por `hs12` y el resultado se cruza con la selección de productos textiles. Ese cruce es una unión interna: solo sobreviven los productos que están en la selección y tienen al menos un factor calculado.

    La tabla `textiles` aporta además tres columnas que no son factores construidos aquí — `Distance`, `PCI` y `Opportunity Gain` — provenientes del análisis de complejidad. Se usan en la Sección 10.6 para construir un tercer índice.

    La imputación reutiliza el mismo objeto `KNNImputer` definido previamente. Cada llamada a `fit_transform` ajusta el modelo desde cero sobre los datos que recibe, de modo que la imputación textil se calcula con vecinos textiles, no con industrias del análisis principal.
    """)
    return


@app.cell
def _(
    imputer,
    pd,
    pl,
    textiles,
    textiles_availability_inputs,
    textiles_china_imports,
    textiles_ciiu_razon_electricidad_gasto_total,
    textiles_df_institutional_intensity,
    textiles_elasticidad_empleo_producto,
    textiles_elasticidad_lac_empleo_fdi,
    textiles_fdi_lac_cagr_empleo,
    textiles_fdi_lac_cagr_investment,
    textiles_fdi_lac_capital_investment,
    textiles_industry_growth_rate,
    textiles_industry_growth_rate_exports,
    textiles_rca_peers,
    textiles_share_energy,
):
    ## Consolidamos tablas

    textiles_consolida = pl.concat([
        textiles_fdi_lac_capital_investment, 
        textiles_fdi_lac_cagr_investment, 
        textiles_fdi_lac_cagr_empleo,
        textiles_elasticidad_lac_empleo_fdi,
        textiles_elasticidad_empleo_producto,
        textiles_industry_growth_rate, 
        textiles_industry_growth_rate_exports, 
        textiles_china_imports, 
        textiles_rca_peers, 
        textiles_availability_inputs, 
        textiles_share_energy, 
        textiles_ciiu_razon_electricidad_gasto_total, 
        textiles_df_institutional_intensity
    ],  how = "align")

    textiles_factores = textiles.join(
        textiles_consolida, 
        on = "hs12",
        how = "inner"
    ).with_columns(
        pl.col("hs12").cast(pl.Int32)
    ).drop("Actividad")

    ## Imputamos datos con Kmedias
    # Fit and transform the data
    textiles_factores_imputados = pl.from_pandas(
        pd.DataFrame(imputer.fit_transform(textiles_factores.to_pandas()), columns=textiles_factores.columns)
    )
    textiles_factores_imputados

    textiles_factores_imputados
    return (textiles_factores_imputados,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 10.5 Índices de viabilidad y atractivo

    El procedimiento es el mismo aplicado a la matriz de productos. Los pesos son uniformes dentro de cada índice y los tipos de criterio se mantienen.
    """)
    return


@app.cell
def _(TOPSIS, np, rrankdata, textiles_factores_imputados, topsis_atractivo):
    # TOPSIS atractivo
    textiles_atractivo_factores = [
        "cumulative_investment_lac",
        "cagr_investment",
        "elasticidad_empleo_fdi",
        "elasticidad_empleo_producto",
        "cagr_production",
        "cagr_exports",
        "share_imports_china", 
    ]
    textiles_alts_atractivo = textiles_factores_imputados.select(textiles_atractivo_factores).to_numpy()

    # Define criteria weights (should sum up to 1)
    textiles_weights_atractivo = np.array([1/len(textiles_atractivo_factores)]*len(textiles_atractivo_factores))

    # Define criteria types (1 for profit, -1 for cost)
    textiles_types_atractivo = np.array([1]*len(textiles_atractivo_factores))

    # Create object of the method
    # Note, that default normalization method for TOPSIS is minmax
    textiles_topsis_atractivo = TOPSIS()

    # Determine preferences and ranking for alternatives
    textiles_pref_atractivo = topsis_atractivo(textiles_alts_atractivo, textiles_weights_atractivo, textiles_types_atractivo)
    textiles_ranking_atractivo = rrankdata(textiles_pref_atractivo)

    # If you want to inspect computation process in details
    textiles_results_atractivo = topsis_atractivo(textiles_alts_atractivo, textiles_weights_atractivo, textiles_types_atractivo, verbose=True)
    return (textiles_pref_atractivo,)


@app.cell
def _(TOPSIS, np, rrankdata, textiles_factores_imputados):
    # TOPSIS Viabilidad
    textiles_viabilidad_factores = [
        "rca_peers",
        "razon_insumos_presentes",
        "share_energy",
        "razon_electricidad_gasto_total",
        "institutional_intensity",
    ]

    textiles_alts_viabilidad = textiles_factores_imputados.select(
        textiles_viabilidad_factores
    ).to_numpy()

    # Pesos uniformes, suman 1
    textiles_weights_viabilidad = np.array(
        [1 / len(textiles_viabilidad_factores)] * len(textiles_viabilidad_factores)
    )

    # Tipos de criterio: 1 beneficio, -1 costo
    textiles_types_viabilidad = np.array([1, 1, -1, -1, -1])

    # La normalización por defecto de TOPSIS es minmax
    textiles_topsis_viabilidad = TOPSIS()

    # Preferencias y ranking
    textiles_pref_viabilidad = textiles_topsis_viabilidad(
        textiles_alts_viabilidad, textiles_weights_viabilidad, textiles_types_viabilidad
    )
    textiles_ranking_viabilidad = rrankdata(textiles_pref_viabilidad)
    return (textiles_pref_viabilidad,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 10.6 Índice de complejidad

    A diferencia del análisis principal, el bloque textil construye un tercer índice a partir de las variables de complejidad que vienen en la tabla de productos seleccionados.

    | Factor | Tipo | Lectura |
    |---|---|---|
    | `Distance` | Costo | Mayor distancia a las capacidades actuales reduce la prioridad |
    | `PCI` | Beneficio | Mayor complejidad del producto la aumenta |
    | `Opportunity Gain` | Beneficio | Mayor ganancia de oportunidades la aumenta |

    Este índice ordena los productos por atractivo desde la perspectiva de complejidad económica.
    """)
    return


@app.cell
def _(TOPSIS, np, rrankdata, textiles_factores_imputados):
    # TOPSIS Complejidad
    complejidad_factores = [
        "Distance",
        "PCI", 
        "Opportunity Gain"
    ]


    textiles_alts_complejidad = textiles_factores_imputados.select(complejidad_factores).to_numpy()

    # Define criteria weights (should sum up to 1)
    textiles_weights_complejidad = np.array([1/len(complejidad_factores)]*len(complejidad_factores))

    # Define criteria types (1 for profit, -1 for cost)
    textiles_types_complejidad = np.array([-1, 1, 1])

    # Create object of the method
    # Note, that default normalization method for TOPSIS is minmax
    textiles_topsis_complejidad = TOPSIS()

    # Determine preferences and ranking for alternatives
    textiles_pref_complejidad = textiles_topsis_complejidad(textiles_alts_complejidad, textiles_weights_complejidad, textiles_types_complejidad)
    textiles_ranking_complejidad = rrankdata(textiles_pref_complejidad)
    return (textiles_pref_complejidad,)


@app.cell
def _(
    pl,
    textiles,
    textiles_factores_imputados,
    textiles_pref_atractivo,
    textiles_pref_complejidad,
    textiles_pref_viabilidad,
):
    ### Creamos data frame con los scores de viabilidad y atractivo
    textiles_scores_viabilidad_atractivo = textiles_factores_imputados.select(
        "hs12"
        ).with_columns(
            pl.col("hs12").cast(pl.Int32).cast(pl.String)
        ).join(
        textiles.select("hs12", "Actividad"),
        on = "hs12"

    ).with_columns(
            topsis_atractivo = textiles_pref_atractivo, 
            topsis_viabilidad = textiles_pref_viabilidad,
            topsis_complejidad = textiles_pref_complejidad
    )
    textiles_scores_viabilidad_atractivo
    return (textiles_scores_viabilidad_atractivo,)


@app.cell
def _(textiles_scores_viabilidad_atractivo):
    textiles_scores_viabilidad_atractivo.sort(["topsis_complejidad", "topsis_viabilidad", "topsis_atractivo"], descending = True)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 10.7 Etiquetas de producto

    El catálogo HS12 aporta nombres cortos por capítulo, que se usan como categoría de color en el diagrama final. El capítulo se obtiene truncando el código de producto a sus dos primeros dígitos.
    """)
    return


@app.cell
def _(load_table):
    ## Cargamos productos HS12
    productos_hs12 = load_table("complejidad", "product_hs12")
    productos_hs12
    return (productos_hs12,)


@app.cell
def _(
    pl,
    productos_hs12,
    textiles,
    textiles_factores_imputados,
    textiles_pref_complejidad,
):
    ## Guardamos factores imputados con topsis de complejidad

    textiles_factores_imputados_topsis_complejidad = textiles_factores_imputados.with_columns(
        topsis_complejidad = textiles_pref_complejidad
    )
    textiles_factores_imputados_topsis_complejidad = textiles_factores_imputados_topsis_complejidad.with_columns(
        pl.col("hs12").map_elements(lambda x : str(x)[:2]).alias("hs_12_2d").cast(pl.Int32)
    ).join(
        productos_hs12.select("product_name_short", "product_hs12_code"), 
        left_on="hs_12_2d", 
        right_on="product_hs12_code"
    )
    textiles_factores_imputados_topsis_complejidad = textiles_factores_imputados_topsis_complejidad.with_columns(
        pl.col("hs12").cast(pl.Int32).cast(pl.String)
    ).join(
            textiles.select("hs12", "Actividad"),
            on = "hs12"
        )
    textiles_factores_imputados_topsis_complejidad
    return (textiles_factores_imputados_topsis_complejidad,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 10.8 Explorador interactivo

    Esta sección permite variar el corte del análisis: en lugar de graficar todos los productos textiles, se toman los primeros según el índice de complejidad y se recalculan atractivo y viabilidad únicamente sobre ese subconjunto.

    El recálculo importa porque TOPSIS normaliza cada criterio contra el mínimo y el máximo observados en la matriz. Restringir las alternativas cambia esos rangos y, con ellos, las posiciones relativas. La lectura de la figura es siempre relativa al top seleccionado.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### La función de recálculo

    La función ordena los productos por índice de complejidad, se queda con los primeros `top_n` y vuelve a correr los dos TOPSIS sobre ese subconjunto. Las listas de factores y los tipos de criterio se toman del ámbito global para que el explorador use una sola especificación. Devuelve el código HS12, los tres índices y las etiquetas de clúster y actividad que la figura necesita.
    """)
    return


@app.cell
def _(TOPSIS, np, pd, pl, rrankdata):
    def textiles_topsis_viabilidad_atractivo(
        data : pd.DataFrame, 
        top_n : int
        ) -> pl.DataFrame:

        data = data.sort("topsis_complejidad", descending=True).head(top_n)

        # TOPSIS atractivo
        textiles_atractivo_factores = [
            "cumulative_investment_lac",
            "cagr_investment",
            "elasticidad_empleo_fdi",
            "elasticidad_empleo_producto",
            "cagr_production",
            "cagr_exports",
            "share_imports_china", 
        ]
        textiles_alts_atractivo = data.select(textiles_atractivo_factores).to_numpy()

        # Define criteria weights (should sum up to 1)
        textiles_weights_atractivo = np.array([1/len(textiles_atractivo_factores)]*len(textiles_atractivo_factores))

        # Define criteria types (1 for profit, -1 for cost)
        textiles_types_atractivo = np.array([1]*len(textiles_atractivo_factores))

        # Create object of the method
        # Note, that default normalization method for TOPSIS is minmax
        textiles_topsis_atractivo = TOPSIS()

        # Determine preferences and ranking for alternatives
        textiles_pref_atractivo = textiles_topsis_atractivo(textiles_alts_atractivo, textiles_weights_atractivo, textiles_types_atractivo)
        textiles_ranking_atractivo = rrankdata(textiles_pref_atractivo)

        # If you want to inspect computation process in details
        textiles_results_atractivo = textiles_topsis_atractivo(textiles_alts_atractivo, textiles_weights_atractivo, textiles_types_atractivo, verbose=True)

        # TOPSIS Viabilidad
        textiles_viabilidad_factores = [
            "rca_peers",
            "razon_insumos_presentes", 
            #"share_energy",
            "razon_electricidad_gasto_total",
            "institutional_intensity"
        ]


        textiles_alts_viabilidad = data.select(textiles_viabilidad_factores).to_numpy()

        # Define criteria weights (should sum up to 1)
        textiles_weights_viabilidad = np.array([1/len(textiles_viabilidad_factores)]*len(textiles_viabilidad_factores))

        # Define criteria types (1 for profit, -1 for cost)
        textiles_types_viabilidad = np.array([1, 1, -1, -1])

        # Create object of the method
        # Note, that default normalization method for TOPSIS is minmax
        textiles_topsis_viabilidad = TOPSIS()

        # Determine preferences and ranking for alternatives
        textiles_pref_viabilidad = textiles_topsis_viabilidad(textiles_alts_viabilidad, textiles_weights_viabilidad, textiles_types_viabilidad)
        textiles_ranking_viabilidad = rrankdata(textiles_pref_viabilidad)

        ### Creamos data frame con los scores de viabilidad y atractivo
        data = data.select(
            "hs12"
            ).with_columns(
                pl.col("hs12").cast(pl.Int32).cast(pl.String)
            ).with_columns(
                topsis_atractivo = textiles_pref_atractivo, 
                topsis_viabilidad = textiles_pref_viabilidad,
                topsis_complejidad = data["topsis_complejidad"],
                cluster = data["product_name_short"], 
                Actividad = data["Actividad"]
        )

        return data

    return (textiles_topsis_viabilidad_atractivo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Selector del corte

    El control fija cuántos productos entran al recálculo. Al modificarlo, la figura se reconstruye de forma automática: si la posición de un producto se mantiene entre el top 10 y el top 20, la señal es robusta; si se desplaza, depende del conjunto de comparación.
    """)
    return


@app.cell
def _(mo):
    dropdown = mo.ui.dropdown(options=[10, 15, 20], value=10, label="Escoge Top")
    dropdown
    return (dropdown,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Diagrama de viabilidad y atractivo

    Cada producto se ubica según su viabilidad (eje horizontal) y su atractivo (eje vertical), con el color indicando el clúster. Las líneas punteadas cruzan en las medias de cada índice dentro del corte seleccionado y definen las cuatro fases: la Fase I reúne los productos altos en ambos índices, la Fase IV los bajos en ambos, y las fases II y III los casos asimétricos, donde el cuello de botella está identificado y admite una entrada de política más clara.
    """)
    return


@app.cell
def _(
    alt,
    dropdown,
    pd,
    textiles_factores_imputados_topsis_complejidad,
    textiles_topsis_viabilidad_atractivo,
):
    textiles_topsis = textiles_topsis_viabilidad_atractivo(textiles_factores_imputados_topsis_complejidad, dropdown.value)

    plot_textiles = alt.Chart(
            textiles_topsis
            ).mark_circle(
                opacity=0.99,
                stroke='black',
                strokeWidth=1.2,
                strokeOpacity=0.9, 
                size=180,     
            ).encode(
        y=alt.Y('topsis_atractivo').scale(zero=False).title("Atractivo"),
        x=alt.X('topsis_viabilidad').scale(zero=False).title("Viabilidad"),#.scale(type ="log"),
        color = alt.Color("cluster").title("Cluster"),
        #size = alt.Size("topsis_atractivo"),
        tooltip=[

                alt.Tooltip('Actividad', title='Actividad'), 
        ] 
    ).properties(
        title=alt.TitleParams(
            "Diagrama Complejidad-Viabilidad-Atractivo",
            #subtitle="Honduras. Datos de Empleo de OECD SBS 2019",
            subtitleColor="gray"
        )
    )

    # Create a horizontal line at y = -1.14
    textiles_rule_atractivo = alt.Chart(pd.DataFrame({'y': [textiles_topsis["topsis_atractivo"].mean()]})).mark_rule(color='gray', strokeWidth=3, strokeDash=[4,4]).encode(y='y:Q')
    textiles_rule_viabilidad = alt.Chart(pd.DataFrame({'x': [textiles_topsis["topsis_viabilidad"].mean()]})).mark_rule(color='gray', strokeWidth=3, strokeDash=[4,4]).encode(x='x:Q')

    # 2. Quadrant labels dataframe with custom coordinates
    # Change these values to position text exactly where you want it
    textiles_quadrant_labels = pd.DataFrame({
        'y_pos': [textiles_topsis["topsis_atractivo"].max(), 
                textiles_topsis["topsis_atractivo"].min()*1.05, 
                textiles_topsis["topsis_atractivo"].max(),
                textiles_topsis["topsis_atractivo"].min()*1.05],     # X coordinates for text
        'x_pos': [textiles_topsis["topsis_viabilidad"].max()*0.95,
                textiles_topsis["topsis_viabilidad"].max()*0.95,
                textiles_topsis["topsis_viabilidad"].min()*1.05,
                textiles_topsis["topsis_viabilidad"].min()*1.05],     # Y coordinates for text
        'label': ['Fase I', 'Fase II', 'Fase III', 'Fase IV'],
        'align': ['right', 'left', 'left', 'right'] # Optional: aligns text inside boundaries
    })

    # 5. Quadrant text layer
    textiles_text_layer = alt.Chart(textiles_quadrant_labels).mark_text(
        size=16,
        fontStyle='bold',
        color='black'
    ).encode(
        x='x_pos:Q',
        y='y_pos:Q',
        text='label:N'
    )

    plot_textiles = (plot_textiles + textiles_rule_atractivo + textiles_rule_viabilidad + textiles_text_layer).properties(
    #plot_intensivo.properties(
            title=alt.TitleParams(
                "Diagrama Viabilidad-Atractivo",
                subtitle="Productos Textiles",
                subtitleColor="gray"
            )
    )
    plot_textiles
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Anexos

    ## Limitaciones

    **Asimetría de horizontes.** Los factores de inversión cubren varios años, mientras que el crecimiento de la producción se calcula entre dos años consecutivos. Al entrar ambos con el mismo peso, una variación interanual pesa tanto como una tendencia de mediano plazo.

    **Ponderadores uniformes.** TOPSIS reparte el peso por igual entre los criterios de cada dimensión. Es una decisión normativa, no un resultado del modelo, y determina el orden de los productos tanto como los datos mismos.

    **Imputación de valores faltantes.** El imputador por vecinos más cercanos mide distancias sobre las columnas que recibe. Los códigos de clasificación tienen una escala mucho mayor que la de los factores y, si se incluyen, dominan el cálculo de vecindad. Los factores tampoco están estandarizados entre sí, de modo que los de escala más amplia pesan más en la distancia.
    """)
    return


if __name__ == "__main__":
    app.run()
