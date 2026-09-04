import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Métricas de Viabilidad y Atractivo por industria (CIIU Rev. 4)

    **Paquete de replicabilidad — Sendas Think Tank / EGTP Tecnológico de Monterrey**

    Esta rutina construye, para cada industria de la CIIU Rev. 4 a 4 dígitos, dos índices sintéticos:

    - **Atractivo**: qué tan deseable es promover/atraer la industria (mercado, inversión, crecimiento, potencial de empleo, sustitución de importaciones desde Asia).
    - **Viabilidad**: qué tan factible es desarrollarla en Honduras dadas las capacidades existentes y las restricciones (energía, disponibilidad de insumos).

    Cada índice se obtiene combinando varios factores con el método **TOPSIS**. El resultado final son dos diagramas Viabilidad–Atractivo (margen intensivo y extensivo).

    **Flujo:** (1) carga de datos → (2) factores de atractivo → (3) factores de viabilidad → (4) reunión e imputación de faltantes (KNN) → (5) agregación con TOPSIS → (6) diagramas → (7) exportación.

    **Fuentes:** OECD SDBS (producción, insumos, energía, empleo); fDi Markets (inversión extranjera por subsector); Atlas of Economic Complexity (exportaciones HS12, RCA); AIPNET (red de producción); Censos Económicos / SAIC de México (intensidad eléctrica); participación de China en importaciones de EE. UU.; concordancias CIIU↔HS12, CIIU↔NAICS y CIIU↔subsectores fDi; y datos de complejidad del proyecto.

    **Requisitos:** Python 3.11+ y los paquetes `marimo`, `polars`, `pandas`, `numpy`, `scikit-learn`, `pymcdm`, `altair`, `pyarrow`, `openpyxl`. No requiere hardware especializado. La rutina es **determinista**.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Preparación del entorno
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    Cargamos las librerías principales de la rutina.
    """)
    return


@app.cell
def _():
    import marimo as mo
    import pathlib
    import numpy as np
    import pandas as pd
    import polars as pl
    import altair as alt
    from sklearn.impute import KNNImputer
    from pymcdm.methods import TOPSIS
    from pymcdm.helpers import rrankdata

    return KNNImputer, TOPSIS, alt, mo, np, pathlib, pd, pl, rrankdata


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Configuración

    Todos los supuestos del análisis están centralizados aquí: rutas (relativas a la carpeta del proyecto), años de referencia, países pares, número de vecinos del imputador y los pesos y la orientación de los criterios de TOPSIS. Cualquier usuario puede auditarlos o modificarlos sin tocar la lógica de cálculo.
    """)
    return


@app.cell
def _(np, pathlib):
    # --- Rutas (relativas a la carpeta donde se ejecuta el notebook) ---
    DATA_DIR = pathlib.Path("datos")
    VA_DIR = DATA_DIR         # insumos del ejercicio
    FDI_DIR = VA_DIR               # datos de fDi Markets
    RECOD_DIR = DATA_DIR            # concordancias / ponderadores
    OUTPUT_DIR = pathlib.Path("datos/viabilidad_atractivo")           # salidas
    OUTPUT_DIR.mkdir(exist_ok=True)

    # --- Supuestos del análisis ---
    PAISES_PEERS = ["SLV", "ECU"]      # países pares para la criterio de viabilidad de ventaja comparativa (RCA)

    # Años de referencia para las tasas de crecimiento compuesto (CAGR).
    # NOTA: producción usa solo 2018-2019; si se busca una ventana de cinco años, ampliar.
    ANIOS_PRODUCCION = [2018, 2019]    # crecimiento de la producción (OECD SDBS)
    ANIOS_EMPLEO = [2018, 2022]        # crecimiento del empleo (OECD SDBS)
    ANIOS_EXPORT = [2019, 2024]        # crecimiento exportador (Atlas)
    ANIO_SHARE_ENERGY = 2019           # participación de energía en insumos (OECD SDBS)
    ANIO_ELECTRICIDAD = 2023           # intensidad eléctrica (SAIC México)
    ANIO_ATLAS_HND = 2024              # foto de RCA de Honduras en el Atlas

    KNN_N_NEIGHBORS = 2                # vecinos para la imputación de faltantes

    # --- Criterios de TOPSIS (+1 = más es mejor; -1 = más es peor) ---
    ATRACTIVO_FACTORES = [
        "cumulative_investment_world",
        "cumulative_investment_lac",
        "cagr_investment_world",
        "cagr_investment_lac",
        "elasticidad_empleo_fdi_world",
        "elasticidad_empleo_fdi_lac",
        "cagr_production",
        "cagr_exports",
        "share_imports_china",
        "elasticidad_empleo_producto",
    ]
    ATRACTIVO_TYPES = np.array([1] * len(ATRACTIVO_FACTORES))

    VIABILIDAD_FACTORES = [
        "rca_peers",                       # fortaleza en países pares (+)
        "razon_insumos_presentes",         # disponibilidad local de insumos (+)
        "share_energy",                    # dependencia de energía (restricción, -)
        "razon_electricidad_gasto_total",  # dependencia de electricidad (restricción, -)
    ]
    VIABILIDAD_TYPES = np.array([1, 1, -1, -1])
    return (
        ANIOS_EMPLEO,
        ANIOS_EXPORT,
        ANIOS_PRODUCCION,
        ANIO_ATLAS_HND,
        ANIO_ELECTRICIDAD,
        ANIO_SHARE_ENERGY,
        ATRACTIVO_FACTORES,
        ATRACTIVO_TYPES,
        FDI_DIR,
        KNN_N_NEIGHBORS,
        OUTPUT_DIR,
        PAISES_PEERS,
        RECOD_DIR,
        VA_DIR,
        VIABILIDAD_FACTORES,
        VIABILIDAD_TYPES,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Referencia de variables OECD SDBS

    Códigos de columna usados en los archivos de OECD SDBS (solo para interpretar):

    **Producción / insumos:** `VAFC` = valor agregado a costo de factores; `INGS` = compras totales de bienes y servicios; `INEN` = compras de productos energéticos; `PROD` = producción.

    **Empleo / energía:** `EMPN` = empleo total; `EMPF` = empleadas mujeres; `INEN` = compras de productos energéticos; `VAPE` = productividad laboral; `EMPE` = empleados.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Funciones auxiliares
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    Definimos una función para cargar y preparar las bases de OECD SDBS. La función lee el archivo parquet correspondiente, conserva las columnas necesarias y suma los valores por actividad, año y medida.

    Luego filtra las actividades CIIU a cuatro dígitos. En la base original, los códigos vienen precedidos por una letra de sección, por lo que se verifica que el código tenga el formato esperado y se elimina esa letra inicial. Finalmente, la base se transforma a formato ancho, dejando cada medida como una columna distinta para facilitar los cálculos posteriores.
    """)
    return


@app.cell
def _(VA_DIR, pl):
    def obten_datos(dataset: str):
        """Lee un parquet de OECD SDBS y lo deja en formato ancho por medida.

        1. Lectura diferida (lazy). 2. Suma por actividad, anio y medida.
        3. Conserva solo actividades a 4 digitos del CIIU (la actividad viene como
           '<letra de seccion><4 digitos>', p. ej. 'C1234'); quita la letra inicial.
        4. Pivotea las medidas a columnas.
        """
        consulta = (
            pl.scan_delta(VA_DIR / f"{dataset}")
            .select("ACTIVITY", "OBS_VALUE", "MEASURE", "TIME_PERIOD")
            .group_by("ACTIVITY", "TIME_PERIOD", "MEASURE")
            .sum()
        )
        df = consulta.collect().to_pandas()

        df = df[df["ACTIVITY"].apply(lambda x: len(x) == 5)]
        es_numerico = lambda cadena: all(c.isnumeric() for c in cadena)
        df = df[df["ACTIVITY"].apply(lambda x: es_numerico(x[1:]))]
        df["ACTIVITY"] = df["ACTIVITY"].apply(lambda x: x[1:])

        df = df.pivot(
            index=["TIME_PERIOD", "ACTIVITY"], columns="MEASURE", values="OBS_VALUE"
        )
        return df.reset_index()

    return (obten_datos,)


@app.cell
def _(mo):
    mo.md(r"""
    Definimos una función para calcular la tasa de crecimiento compuesta a partir de variables que son flujos anuales, como inversión o empleo de proyectos FDI. Como estos datos no son stocks, primero se agregan por año y grupo, y luego se acumulan en el tiempo.

    A partir de la serie acumulada se toma el valor inicial, el valor final y el número de años disponibles para estimar el crecimiento promedio anual compuesto. Cuando solo existe un año de información, el CAGR queda nulo para evitar divisiones por cero y puede tratarse posteriormente en la rutina.
    """)
    return


@app.cell
def _(pl):
    def cagr_desde_flujo(df, grupo, anio_col, valor_col, salida):
        """CAGR sobre el STOCK ACUMULADO de un flujo anual (inversion/empleo FDI).

        Los proyectos de FDI son flujos; primero se acumulan en el tiempo y luego
        se calcula la tasa compuesta entre el primer y el ultimo anio:
        CAGR = (valor_final / valor_inicial) ** (1 / n anios) - 1.
        Si la industria tiene un solo anio (n anios = 0), el CAGR queda nulo y se
        imputa despues; asi se evita la division por cero.
        """
        return (
            df.sort([anio_col, grupo], maintain_order=True)
            .group_by(anio_col, grupo, maintain_order=True)
            .sum()
            .select(
                pl.col(anio_col, grupo, valor_col),
                pl.col(valor_col).cum_sum().over(grupo).alias("_acumulado"),
            )
            .group_by(grupo, maintain_order=True)
            .agg(
                beginning_val=pl.col("_acumulado").first(),
                ending_val=pl.col("_acumulado").last(),
                n_years=pl.col(anio_col).max() - pl.col(anio_col).min(),
            )
            .with_columns(
                pl.when(pl.col("n_years") > 0)
                .then(
                    ((pl.col("ending_val") / pl.col("beginning_val")) ** (1 / pl.col("n_years")) - 1)
                    * 100
                )
                .otherwise(None)
                .alias(salida)
            )
        )

    return (cagr_desde_flujo,)


@app.cell
def _(mo):
    mo.md(r"""
    Definimos una función para calcular la tasa de crecimiento compuesta de variables que ya vienen expresadas como niveles, como producción, empleo o exportaciones. En estos casos no se acumulan los valores, sino que se compara el nivel observado al inicio y al final de la ventana de años seleccionada.

    La función filtra los años definidos, agrupa por actividad o grupo de análisis, y calcula el crecimiento promedio anual compuesto a partir del valor inicial, el valor final y el número de años entre ambos. Cuando solo existe un año de información, el resultado queda nulo para evitar divisiones por cero.
    """)
    return


@app.cell
def _(pl):
    def cagr_desde_nivel(df, grupo, anio_col, valor_col, salida, anios):
        """CAGR sobre un NIVEL ya observado (produccion, empleo, exportaciones).

        A diferencia de los flujos de FDI, cada anio ya es un nivel; se toma el
        valor del primer y del ultimo anio de la ventana `anios`.
        """
        return (
            df.filter(pl.col(anio_col).is_in(anios))
            .sort([grupo, anio_col], maintain_order=True)
            .group_by(grupo, maintain_order=True)
            .agg(
                beginning_val=pl.col(valor_col).first(),
                ending_val=pl.col(valor_col).last(),
                n_years=pl.col(anio_col).max() - pl.col(anio_col).min(),
            )
            .with_columns(
                pl.when(pl.col("n_years") > 0)
                .then(
                    ((pl.col("ending_val") / pl.col("beginning_val")) ** (1 / pl.col("n_years")) - 1)
                    * 100
                )
                .otherwise(None)
                .alias(salida)
            )
        )

    return (cagr_desde_nivel,)


@app.cell
def _(mo):
    mo.md(r"""
    Definimos una función auxiliar para estandarizar la columna `ciiu` como entero. Esto evita problemas al unir tablas cuando una base trae los códigos CIIU como texto y otra como número. Al asegurar un mismo tipo de dato, los cruces posteriores se hacen de forma más consistente.
    """)
    return


@app.cell
def _(pl):
    def a_entero_ciiu(df):
        """Asegura que la columna `ciiu` sea entera, para unir tablas sin choques de tipo."""
        return df.with_columns(pl.col("ciiu").cast(pl.Int64))

    return (a_entero_ciiu,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Carga de datos
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    OECD SDBS: produccion/insumos y empleo/energia (formato ancho)
    """)
    return


@app.cell
def _(obten_datos):
    df_produccion = obten_datos("oecd_sbp_produccion_gasto_insumos")
    df_empleo = obten_datos("oecd_sbp_empleo_energia")
    df_produccion
    return df_empleo, df_produccion


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### fDi Markets

    Proyectos de inversion por subsector. Se agrega la subregion del mundo a cada proyecto, se extrae el anio de inicio y se traduce el subsector fDi a CIIU mediante la concordancia. `fdi_lac` es el subconjunto de America Latina y el Caribe.
    """)
    return


@app.cell
def _(FDI_DIR, pl):
    fdi = pl.read_delta(FDI_DIR / "fdi_subsectores_iso_code3").to_pandas()
    regiones = pl.read_delta(FDI_DIR / "paises_iso_code").to_pandas()
    fdi_ciiu = pl.read_delta(FDI_DIR / "correspondencia_fdi_ciiu_rev4").to_pandas()
    fdi_ciiu["CIIU"] = fdi_ciiu["CIIU"].apply(lambda x: f"{x:04d}")

    fdi = fdi.merge(
        regiones[["iso_alpha_3", "un_sub_region"]],
        left_on="iso_code3", right_on="iso_alpha_3", how="left",
    )
    fdi["un_sub_region"] = fdi["un_sub_region"].fillna("Western Asia")

    fdi["Project date"] = fdi["Project date"].apply(lambda x: x.split("/")[-1]).astype(int)
    fdi = fdi.merge(
        fdi_ciiu[["Nombre fDi (Subsector)_duplicated_0", "CIIU"]],
        left_on="Sub-sector", right_on="Nombre fDi (Subsector)_duplicated_0", how="left",
    )

    fdi_lac = fdi.query("un_sub_region == 'Latin America and the Caribbean'")
    fdi
    return fdi, fdi_lac


@app.cell
def _():
    return


@app.cell
def _(VA_DIR, pl):
    # Atlas de Complejidad: exportaciones por producto HS12, pais y anio
    atlas_hs12 = pl.read_delta(VA_DIR / "hs12_country_product_year_4")
    atlas_hs12
    return (atlas_hs12,)


@app.cell
def _(mo):
    mo.md(r"""
    Cargamos la tabla de concordancia entre actividades CIIU y productos HS12. Esta base permite vincular ambas clasificaciones usando ponderadores, lo que es útil cuando una actividad CIIU se relaciona con varios productos.

    Se eliminan los registros sin ponderador válido y se ajustan los tipos de datos de las columnas principales. Con esto, `hs12` queda como entero y `weight` como número decimal, dejando la tabla lista para cruces y cálculos ponderados.
    """)
    return


@app.cell
def _(RECOD_DIR, pl):
    # Concordancia CIIU <-> HS12 (con ponderadores)
    ciiu_hs12 = pl.read_delta(RECOD_DIR / "ponderadores_ciiu_hs12_concordance")
    ciiu_hs12 = ciiu_hs12.filter(pl.col("weight") != "NA").with_columns(
        pl.col("hs12").cast(pl.Int64),
        pl.col("weight").cast(pl.Float64),
    )

    ciiu_hs12
    return (ciiu_hs12,)


@app.cell
def _(mo):
    mo.md(r"""
    Cargamos la participación de China en las importaciones de Estados Unidos por producto HS12. La base conserva el código del producto y la variable `share_imports_china`, que mide qué proporción de las importaciones estadounidenses proviene de China.

    Esta información permite aproximar la exposición de cada producto a la competencia o dependencia china en el mercado de Estados Unidos.
    """)
    return


@app.cell
def _(VA_DIR, pl):
    # Participacion de China en importaciones de EE. UU. por producto HS12
    china_imports = pl.read_delta(VA_DIR / "importaciones_usa_china_hs12").select(
        "product_hs12_code", "share_imports_china"
    )

    china_imports
    return (china_imports,)


@app.cell
def _(mo):
    mo.md(r"""
    Cargamos la tabla de concordancia entre actividades CIIU y la clasificación NAICS 2017.
    """)
    return


@app.cell
def _(RECOD_DIR, pl):
    # Concordancia CIIU <-> NAICS 2017 (con ponderadores)
    ciiu_naics = pl.read_delta(RECOD_DIR / "ponderadores_ciiu_naics2017_concordance")
    ciiu_naics
    return (ciiu_naics,)


@app.cell
def _(mo):
    mo.md(r"""
    Importamos la tabla de datos con las estimaciones de complejidad para la selección de 21 países.
    """)
    return


@app.cell
def _(VA_DIR, pl):
    # Datos de complejidad del proyecto (RCA y MCP por pais-actividad)
    cdata = pl.read_delta(VA_DIR / "cdata")
    cdata
    return (cdata,)


@app.cell
def _(mo):
    mo.md(r"""
    Cargamos la red de producción AIPNET a nivel de productos HS12. Esta base permite identificar relaciones de insumo-producto entre bienes, lo que ayuda a aproximar encadenamientos dentro de las cadenas productivas.
    """)
    return


@app.cell
def _(VA_DIR, pl):
    # Red de produccion AIPNET (cadena de insumos entre productos HS12)
    aipnet = pl.read_delta(VA_DIR / "aipnet_hs12_4d")
    aipnet
    return (aipnet,)


@app.cell
def _(mo):
    mo.md(r"""
    Cargamos las tablas de recodificación y selección de industrias utilizadas en el proyecto. La base `recodificacion_hnd_usa.csv` permite construir el mapeo de actividades CIIU Rev. 4 con sus respectivos nombres, mientras que `seleccion_manual_preliminar.csv` conserva la selección depurada de industrias incluidas en el análisis.

    También importamos los resultados finales del análisis de complejidad desde el archivo `Resultados Complexity_final.xlsx`, separando las actividades intensivas y extensivas. Estas bases sirven como insumo para combinar los resultados de complejidad con indicadores adicionales de viabilidad y atractivo productivo.
    """)
    return


@app.cell
def _(VA_DIR, pd, pl):
    # Recodificacion y seleccion de industrias del proyecto
    recod = pl.read_delta(VA_DIR / "catalogo_ciiu_rev4_nombres").to_pandas()
    mapp_ciiu = pl.from_pandas(
        recod.query("clasificador=='ciiu_rev_4'")[["codigo", "nombre_actividad"]]
    )
    ciiu_pedro = pl.from_pandas(
        pl.read_delta(VA_DIR / "catalogo_ciiu_rev4").to_pandas().query("incluye==1")
    )
    resultados_finales_intensivo = pd.read_excel(
        VA_DIR / "Resultados Complexity_final.xlsx", sheet_name="Intensivo"
    )
    resultados_finales_extensivo = pd.read_excel(
        VA_DIR / "Resultados Complexity_final.xlsx", sheet_name="Extensivo"
    )

    return (
        ciiu_pedro,
        mapp_ciiu,
        resultados_finales_extensivo,
        resultados_finales_intensivo,
    )


@app.cell
def _(resultados_finales_extensivo):
    resultados_finales_extensivo
    return


@app.cell
def _(resultados_finales_intensivo):
    resultados_finales_intensivo
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Factores de Atractivo
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Capacidad para movilizar inversion (mundo y LAC)

    Inversion de capital y empleos creados acumulados por industria, en todo el mundo y en America Latina y el Caribe.
    """)
    return


@app.cell
def _(fdi, fdi_lac):
    fdi_capital_investment = (
        fdi[["CIIU", "Capital investment", "Jobs created"]].groupby("CIIU").sum().reset_index()
    )
    fdi_lac_capital_investment = (
        fdi_lac[["CIIU", "Capital investment", "Jobs created"]].groupby("CIIU").sum().reset_index()
    )
    fdi_capital_investment
    return fdi_capital_investment, fdi_lac_capital_investment


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Tasa de crecimiento compuesta (CAGR) de la inversion
    """)
    return


@app.cell
def _(cagr_desde_flujo, fdi, pl):
    fdi_cagr_investment = cagr_desde_flujo(
        pl.from_pandas(fdi[["CIIU", "Project date", "Capital investment"]]),
        grupo="CIIU", anio_col="Project date", valor_col="Capital investment",
        salida="cagr_investment",
    )
    fdi_cagr_investment
    return (fdi_cagr_investment,)


@app.cell
def _(cagr_desde_flujo, fdi_lac, pl):
    fdi_lac_cagr_investment = cagr_desde_flujo(
        pl.from_pandas(fdi_lac[["CIIU", "Project date", "Capital investment"]]),
        grupo="CIIU", anio_col="Project date", valor_col="Capital investment",
        salida="cagr_investment",
    )
    fdi_lac_cagr_investment
    return (fdi_lac_cagr_investment,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### CAGR del empleo creado por FDI
    """)
    return


@app.cell
def _(cagr_desde_flujo, fdi, pl):
    fdi_cagr_empleo = cagr_desde_flujo(
        pl.from_pandas(fdi[["CIIU", "Project date", "Jobs created"]]),
        grupo="CIIU", anio_col="Project date", valor_col="Jobs created",
        salida="cagr_empleo",
    )
    fdi_cagr_empleo
    return (fdi_cagr_empleo,)


@app.cell
def _(cagr_desde_flujo, fdi_lac, pl):
    fdi_lac_cagr_empleo = cagr_desde_flujo(
        pl.from_pandas(fdi_lac[["CIIU", "Project date", "Jobs created"]]),
        grupo="CIIU", anio_col="Project date", valor_col="Jobs created",
        salida="cagr_empleo",
    )
    fdi_lac_cagr_empleo
    return (fdi_lac_cagr_empleo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Elasticidad empleo-inversion

    Mide cuantos empleos se crean por cada punto de crecimiento de la inversion:

    \begin{equation}
    \text { Elasticity }(\epsilon)=\frac{\% \text { Change in Employment }}{\% \text { Change in FDI }}
    \end{equation}

    * If ε > 0 and < 1, the sector creates jobs but FDI is also rising.
    * If ε > 1, the sector is highly labor-intensive and creates many jobs relative to FDI.

    https://infonomics-society.org/wp-content/uploads/ijcdse/published-papers/volume-6-2015/Economic-Growth-and-Sectoral-Capacity-for-Employment.pdf
    """)
    return


@app.cell
def _(fdi_cagr_empleo, fdi_cagr_investment, pl):
    elasticidad_empleo_fdi = fdi_cagr_investment.select("CIIU", "cagr_investment").join(
        fdi_cagr_empleo.select("CIIU", "cagr_empleo"), on="CIIU"
    ).with_columns(elasticidad=pl.col("cagr_empleo") / pl.col("cagr_investment"))
    elasticidad_empleo_fdi
    return (elasticidad_empleo_fdi,)


@app.cell
def _(fdi_lac_cagr_empleo, fdi_lac_cagr_investment, pl):
    elasticidad_lac_empleo_fdi = fdi_lac_cagr_investment.select("CIIU", "cagr_investment").join(
        fdi_lac_cagr_empleo.select("CIIU", "cagr_empleo"), on="CIIU"
    ).with_columns(elasticidad=pl.col("cagr_empleo") / pl.col("cagr_investment"))
    elasticidad_lac_empleo_fdi
    return (elasticidad_lac_empleo_fdi,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Crecimiento de la industria en el mundo (produccion, OECD SDBS)
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    Se calcula la tasa de crecimiento de la producción a 2019 vs 2018 de la tabla de datos de la OECD SDBS.
    """)
    return


@app.cell
def _(ANIOS_PRODUCCION, cagr_desde_nivel, df_produccion, pl):
    industry_growth_rate = cagr_desde_nivel(
        pl.from_pandas(df_produccion[["TIME_PERIOD", "ACTIVITY", "PROD"]]),
        grupo="ACTIVITY", anio_col="TIME_PERIOD", valor_col="PROD",
        salida="cagr_production", anios=ANIOS_PRODUCCION,
    )
    industry_growth_rate
    return (industry_growth_rate,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Crecimiento exportador mundial (Atlas)

    Se suman las exportaciones por producto HS12 y año, se ponderan por su peso dentro de cada industria CIIU (concordancia) y se calcula el CAGR.
    """)
    return


@app.cell
def _(ANIOS_EXPORT, atlas_hs12, pl):
    exportaciones_hs = (
        atlas_hs12.group_by("product_hs12_code", "year")
        .agg(pl.col("export_value").sum())
        .filter(pl.col("year").is_in(ANIOS_EXPORT))
    )
    exportaciones_hs
    return (exportaciones_hs,)


@app.cell
def _(ciiu_hs12, exportaciones_hs, pl):
    exportaciones_ciiu = (
        exportaciones_hs.join(ciiu_hs12, left_on="product_hs12_code", right_on="hs12")
        .with_columns((pl.col("export_value") * pl.col("weight")).alias("export_value"))
        .group_by("ciiu", "year")
        .agg(pl.col("export_value").sum())
    )
    exportaciones_ciiu
    return (exportaciones_ciiu,)


@app.cell
def _(mo):
    mo.md(r"""
    Calculamos la tasa de crecimiento compuesta de las exportaciones por actividad CIIU. Como las exportaciones ya vienen expresadas como niveles anuales, usamos la función `cagr_desde_nivel()` para comparar el valor inicial y final dentro de la ventana definida en `ANIOS_EXPORT`.

    El resultado se guarda en `industry_growth_rate_exports` e incluye la variable `cagr_exports`, que aproxima el crecimiento promedio anual de las exportaciones por actividad económica.
    """)
    return


@app.cell
def _(ANIOS_EXPORT, cagr_desde_nivel, exportaciones_ciiu):
    industry_growth_rate_exports = cagr_desde_nivel(
        exportaciones_ciiu, grupo="ciiu", anio_col="year", valor_col="export_value",
        salida="cagr_exports", anios=ANIOS_EXPORT,
    )
    industry_growth_rate_exports
    return (industry_growth_rate_exports,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Posibilidad de sustituir importaciones de EE. UU. desde China
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    Calculamos una medida de intensidad china por actividad CIIU. Para ello cruzamos la concordancia CIIU-HS12 con la participación de China en las importaciones de Estados Unidos por producto HS12.

    Como una actividad CIIU puede estar asociada a varios productos, usamos los ponderadores `weight` para construir un promedio ponderado de `share_imports_china`. El resultado aproxima qué tan expuesta está cada actividad económica "transable" a la presencia de China en el mercado importador estadounidense.
    """)
    return


@app.cell
def _(china_imports, ciiu_hs12, pl):
    ciiu_china_intensiveness = (
        ciiu_hs12.join(china_imports, left_on="hs12", right_on="product_hs12_code")
        .group_by("ciiu")
        .agg(
            share_imports_china=(pl.col("share_imports_china") * pl.col("weight")).sum()
            / pl.col("weight").sum()
        )
    )
    ciiu_china_intensiveness
    return (ciiu_china_intensiveness,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Capacidad de crear empleo (elasticidad empleo-producto)
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    Calculamos la tasa de crecimiento compuesta del empleo por actividad económica. Como el empleo ya viene expresado como un nivel anual, usamos cagr_desde_nivel() para comparar el valor inicial y final dentro de la ventana definida en ANIOS_EMPLEO.
    """)
    return


@app.cell
def _(ANIOS_EMPLEO, cagr_desde_nivel, df_empleo, pl):
    employment_growth_rate = cagr_desde_nivel(
        pl.from_pandas(df_empleo[["TIME_PERIOD", "ACTIVITY", "EMPN"]]),
        grupo="ACTIVITY", anio_col="TIME_PERIOD", valor_col="EMPN",
        salida="cagr_employment", anios=ANIOS_EMPLEO,
    )
    employment_growth_rate
    return (employment_growth_rate,)


@app.cell
def _(mo):
    mo.md(r"""
    Calculamos la elasticidad empleo-producción por actividad económica. Para ello unimos el crecimiento compuesto de la producción, `cagr_production`, con el crecimiento compuesto del empleo, `cagr_employment`, usando `ACTIVITY` como llave común.

    La elasticidad se calcula como la razón entre el crecimiento del empleo y el crecimiento de la producción. Este indicador aproxima qué tan sensible es el empleo ante cambios en la producción de cada actividad.
    """)
    return


@app.cell
def _(employment_growth_rate, industry_growth_rate, pl):
    employment_elasticity = industry_growth_rate.select("ACTIVITY", "cagr_production").join(
        employment_growth_rate.select("ACTIVITY", "cagr_employment"), on="ACTIVITY"
    ).with_columns(elasticity=pl.col("cagr_employment") / pl.col("cagr_production"))
    employment_elasticity
    return (employment_elasticity,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Factores de Viabilidad
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Fortaleza en paises pares (RCA promedio en el grupo)
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    Se calcula el RCA promedio de los países comparables para cada actividad económica. Para ello, filtramos `cdata` usando la lista `PAISES_PEERS` (El Salvador y Ecuador), agrupamos por `ACTIVITY` y estimamos el promedio de `rca`.

    El resultado se guarda en `rca_peers` y sirve como una referencia externa para comparar el desempeño relativo de cada actividad frente a un grupo de países similares. Finalmente, renombramos `ACTIVITY` como `ciiu` para facilitar los cruces posteriores.
    """)
    return


@app.cell
def _(PAISES_PEERS, cdata, pl):
    rca_peers = (
        cdata.filter(pl.col("REF_AREA").is_in(PAISES_PEERS))
        .group_by("ACTIVITY")
        .agg(pl.col("rca").mean().alias("rca_peers"))
        .rename({"ACTIVITY": "ciiu"})
    )
    rca_peers
    return (rca_peers,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Disponibilidad de insumos (AIPNET + RCA de Honduras)

    Para cada producto se mira su cadena de insumos (downstream); un insumo se considera "presente" en Honduras si tiene RCA >= 1 en ese producto. La razon de insumos presentes se agrega a nivel de industria CIIU, ponderada por el peso de cada producto.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    Traducimos la red de producción AIPNET desde productos HS12 hacia actividades CIIU. Para ello cruzamos el producto aguas arriba, que representa el insumo dentro de la cadena, con la concordancia CIIU-HS12.

    Se conserva el ponderador `weight`, ya que un producto puede asociarse con más de una actividad económica. El resultado permite analizar los encadenamientos productivos desde el nivel de actividades CIIU, manteniendo la conexión entre productos aguas arriba y aguas abajo.
    """)
    return


@app.cell
def _(aipnet, ciiu_hs12):
    aipnet_ciiu = (
        aipnet.join(ciiu_hs12, left_on="hs2012_code_upstream", right_on="hs12")
        .select("ciiu", "weight", "hs2012_code_upstream", "hs2012_code_downstream")
        .rename({"hs2012_code_upstream": "hs12"})
    )
    aipnet_ciiu
    return (aipnet_ciiu,)


@app.cell
def _(mo):
    mo.md(r"""
    Filtramos la base del Atlas a nivel HS12 para conservar únicamente los productos exportados por Honduras en el año de análisis definido en `ANIO_ATLAS_HND`.

    El resultado, `atlas_hs12_hnd`, permite trabajar con la canasta exportadora hondureña de ese período y usarla como insumo para cruces posteriores con clasificaciones CIIU, redes productivas u otros indicadores de atractivo y viabilidad.
    """)
    return


@app.cell
def _(ANIO_ATLAS_HND, atlas_hs12, pl):
    atlas_hs12_hnd = atlas_hs12.filter(
        (pl.col("country_iso3_code") == "HND") & (pl.col("year") == ANIO_ATLAS_HND)
    )

    atlas_hs12_hnd
    return (atlas_hs12_hnd,)


@app.cell
def _(mo):
    mo.md(r"""
    Calculamos una medida de disponibilidad de insumos para cada actividad CIIU usando la red AIPNET y la canasta exportadora de Honduras. Primero identificamos si los productos relacionados con cada cadena aparecen con ventaja comparativa revelada en las exportaciones hondureñas.

    Luego estimamos la proporción de insumos presentes respecto al total de insumos asociados a cada actividad. Esta razón se pondera con `weight`, de forma que el indicador refleje tanto la presencia de insumos como la importancia relativa de cada correspondencia entre productos HS12 y actividades CIIU.
    """)
    return


@app.cell
def _(aipnet_ciiu, atlas_hs12_hnd, pl):
    aipnet_ciiu_razon_insumos = (
        aipnet_ciiu.join(
            atlas_hs12_hnd.select("product_hs12_code", "export_rca"),
            left_on="hs2012_code_downstream", right_on="product_hs12_code", how="left",
        )
        .fill_null(0)
        .with_columns(
            M=pl.when(pl.col("export_rca") >= 1).then(pl.lit(1)).otherwise(pl.lit(0))
        )
        .group_by("ciiu", "hs12", "weight")
        .agg(
            pl.col("M").sum().alias("inputs_presentes"),
            pl.col("M").count().alias("inputs_totales"),
        )
        .with_columns(
            razon_insumos_presentes=pl.col("inputs_presentes") / pl.col("inputs_totales")
        )
        .with_columns(
            weight__insumos_presentes=pl.col("weight") * pl.col("razon_insumos_presentes")
        )
    )
    aipnet_ciiu_razon_insumos
    return (aipnet_ciiu_razon_insumos,)


@app.cell
def _(mo):
    mo.md(r"""
    Agregamos la medida de disponibilidad de insumos a nivel de actividad CIIU. Para ello sumamos la razón ponderada de insumos presentes calculada previamente para cada combinación de producto y actividad.

    El resultado, `ciiu_insumos_presentes`, aproxima qué proporción ponderada de los insumos asociados a cada actividad económica ya está presente en la canasta exportadora de Honduras. Esta variable se usa como un indicador de viabilidad productiva.
    """)
    return


@app.cell
def _(aipnet_ciiu_razon_insumos, pl):
    ciiu_insumos_presentes = aipnet_ciiu_razon_insumos.group_by("ciiu").agg(
        pl.col("weight__insumos_presentes").sum().alias("razon_insumos_presentes")
    )
    ciiu_insumos_presentes
    return (ciiu_insumos_presentes,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Dependencia de energia (participacion de energia en los insumos)
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    Se aproxima la participación de la energía dentro de los insumos totales de producción por actividad económica. Para ello filtramos el año definido en `ANIO_SHARE_ENERGY` y dividimos `INEN` entre `INGS`.

    El resultado, `share_energy`, aproxima qué tan intensiva en energía es cada actividad.
    """)
    return


@app.cell
def _(ANIO_SHARE_ENERGY, df_produccion, pl):
    share_energy = (
        pl.from_pandas(df_produccion)
        .filter(pl.col("TIME_PERIOD") == ANIO_SHARE_ENERGY)
        .with_columns(share_energy=pl.col("INEN") / pl.col("INGS"))
        .select("ACTIVITY", "share_energy")
    )
    share_energy
    return (share_energy,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Dependencia de electricidad (intensidad electrica, SAIC Mexico)
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    Cargamos la base de electricidad de SAIC y construimos una medida de intensidad eléctrica por actividad. Para ello calculamos la razón entre el gasto por consumo de energía eléctrica y el gasto total por consumo de bienes y servicios.

    Luego dejamos la base en formato ancho, con una fila por actividad y una columna por año. Esta estructura permite comparar la participación del gasto eléctrico en el tiempo y usarla como indicador de exposición a costos energéticos por actividad económica.
    """)
    return


@app.cell
def _(VA_DIR, pl):
    electricidad = pl.read_delta(VA_DIR / "electricidad_saic_2003-2023").to_pandas()
    electricidad["actividad"] = electricidad["actividad"].apply(lambda x: x.split()[1])

    col_electricidad = "K412A Gasto por consumo de energía eléctrica (millones de pesos)"
    col_total = "K000A Total de gastos por consumo de bienes y servicios (millones de pesos)"
    electricidad["razon_electricidad_gasto_total"] = (
        electricidad[col_electricidad] / electricidad[col_total]
    )
    electricidad = electricidad.drop(columns=[col_electricidad, col_total])
    electricidad = electricidad.pivot(
        index="actividad", columns="anio", values="razon_electricidad_gasto_total"
    ).reset_index()
    electricidad
    return (electricidad,)


@app.cell
def _(mo):
    mo.md(r"""
    Seleccionamos la medida de intensidad eléctrica para el año definido en `ANIO_ELECTRICIDAD`. La variable se renombra como `razon_electricidad_gasto_total`, que mide la participación del gasto en electricidad dentro del gasto total por bienes y servicios.

    También renombramos la actividad como `naics` y ajustamos su tipo de dato para facilitar el cruce posterior con la concordancia CIIU-NAICS.
    """)
    return


@app.cell
def _(ANIO_ELECTRICIDAD, electricidad, pl):
    electricidad_share = pl.from_pandas(
        electricidad[["actividad", ANIO_ELECTRICIDAD]].rename(
            columns={ANIO_ELECTRICIDAD: "razon_electricidad_gasto_total", "actividad": "naics"}
        )
    ).with_columns(pl.col("naics").cast(pl.Int32))
    electricidad_share
    return (electricidad_share,)


@app.cell
def _(mo):
    mo.md(r"""
    Llevamos la medida de intensidad eléctrica desde NAICS hacia CIIU usando la tabla de concordancia entre ambas clasificaciones. Para cada actividad CIIU, calculamos un promedio ponderado de la razón entre gasto eléctrico y gasto total.

    El ponderador `weight` permite reflejar la importancia relativa de cada correspondencia NAICS-CIIU. El resultado aproxima qué tan expuesta está cada actividad económica a costos de electricidad.
    """)
    return


@app.cell
def _(ciiu_naics, electricidad_share, pl):
    ciiu_razon_electricidad_gasto_total = (
        ciiu_naics.join(electricidad_share, on="naics", how="left")
        .group_by("ciiu")
        .agg(
            razon_electricidad_gasto_total=(
                pl.col("razon_electricidad_gasto_total") * pl.col("weight")
            ).sum()
            / pl.col("weight").sum()
        )
    )
    ciiu_razon_electricidad_gasto_total
    return (ciiu_razon_electricidad_gasto_total,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Reunion de factores e imputacion

    Se normaliza el nombre de la industria a `ciiu` (entero) en todas las tablas, se unen todos los factores por industria y se restringe al universo de Honduras. Los valores faltantes se imputan con K vecinos mas cercanos (determinista).
    """)
    return


@app.cell
def _(cdata, pl):
    cdata_hnd = cdata.filter(pl.col("REF_AREA") == "HND")
    cdata_hnd
    return (cdata_hnd,)


@app.cell
def _(
    a_entero_ciiu,
    cdata_hnd,
    ciiu_china_intensiveness,
    ciiu_insumos_presentes,
    ciiu_razon_electricidad_gasto_total,
    elasticidad_empleo_fdi,
    elasticidad_lac_empleo_fdi,
    employment_elasticity,
    fdi_cagr_investment,
    fdi_capital_investment,
    fdi_lac_cagr_investment,
    fdi_lac_capital_investment,
    industry_growth_rate,
    industry_growth_rate_exports,
    pl,
    rca_peers,
    share_energy,
):
    # Normaliza cada factor a una columna `ciiu` entera + su columna de valor
    fdi_capital_investment_final = a_entero_ciiu(
        pl.from_pandas(fdi_capital_investment).select("CIIU", "Capital investment").rename(
            {"CIIU": "ciiu", "Capital investment": "cumulative_investment_world"}
        )
    )
    fdi_lac_capital_investment_final = a_entero_ciiu(
        pl.from_pandas(fdi_lac_capital_investment).select("CIIU", "Capital investment").rename(
            {"CIIU": "ciiu", "Capital investment": "cumulative_investment_lac"}
        )
    )
    fdi_cagr_investment_final = a_entero_ciiu(
        fdi_cagr_investment.select("CIIU", "cagr_investment").rename(
            {"CIIU": "ciiu", "cagr_investment": "cagr_investment_world"}
        )
    )
    fdi_lac_cagr_investment_final = a_entero_ciiu(
        fdi_lac_cagr_investment.select("CIIU", "cagr_investment").rename(
            {"CIIU": "ciiu", "cagr_investment": "cagr_investment_lac"}
        )
    )
    elasticidad_empleo_fdi_final = a_entero_ciiu(
        elasticidad_empleo_fdi.select("CIIU", "elasticidad").rename(
            {"CIIU": "ciiu", "elasticidad": "elasticidad_empleo_fdi_world"}
        )
    )
    elasticidad_lac_empleo_fdi_final = a_entero_ciiu(
        elasticidad_lac_empleo_fdi.select("CIIU", "elasticidad").rename(
            {"CIIU": "ciiu", "elasticidad": "elasticidad_empleo_fdi_lac"}
        )
    )
    industry_growth_rate_final = a_entero_ciiu(
        industry_growth_rate.select("ACTIVITY", "cagr_production").rename({"ACTIVITY": "ciiu"})
    )
    industry_growth_rate_exports_final = a_entero_ciiu(
        industry_growth_rate_exports.select("ciiu", "cagr_exports")
    )
    ciiu_china_intensiveness_final = a_entero_ciiu(ciiu_china_intensiveness)
    employment_elasticity_final = a_entero_ciiu(
        employment_elasticity.select("ACTIVITY", "elasticity").rename(
            {"ACTIVITY": "ciiu", "elasticity": "elasticidad_empleo_producto"}
        )
    )
    rca_peers_final = a_entero_ciiu(rca_peers)
    ciiu_insumos_presentes_final = a_entero_ciiu(ciiu_insumos_presentes)
    share_energy_final = a_entero_ciiu(share_energy.rename({"ACTIVITY": "ciiu"}))
    ciiu_razon_electricidad_gasto_total_final = a_entero_ciiu(ciiu_razon_electricidad_gasto_total)

    ciiu_analiza = a_entero_ciiu(cdata_hnd.select("ACTIVITY").rename({"ACTIVITY": "ciiu"}))

    factores = pl.concat(
        [
            ciiu_analiza,
            fdi_capital_investment_final,
            fdi_lac_capital_investment_final,
            fdi_cagr_investment_final,
            fdi_lac_cagr_investment_final,
            elasticidad_empleo_fdi_final,
            elasticidad_lac_empleo_fdi_final,
            industry_growth_rate_final,
            industry_growth_rate_exports_final,
            ciiu_china_intensiveness_final,
            employment_elasticity_final,
            rca_peers_final,
            ciiu_insumos_presentes_final,
            share_energy_final,
            ciiu_razon_electricidad_gasto_total_final,
        ],
        how="align",
    ).filter(pl.col("ciiu").is_in(cdata_hnd["ACTIVITY"]))
    factores
    return (factores,)


@app.cell
def _(mo):
    mo.md(r"""
    Algunos factores tienen una cobertura baja para el total de actividades usadas para los cálculos de complejidad económica.
    """)
    return


@app.cell
def _(factores, pl):
    faltantes_factores = (
        factores
        .select(
            [
                pl.col(col).is_null().sum().alias(col)
                for col in factores.columns
            ]
        )
        .unpivot(
            variable_name="variable",
            value_name="n_faltantes"
        )
        .with_columns(
            porcentaje_faltantes=(
                pl.col("n_faltantes") / factores.height * 100
            )
        )
        .sort("porcentaje_faltantes", descending=True)
    )

    faltantes_factores
    return


@app.cell
def _(mo):
    mo.md(r"""
    Imputamos los valores faltantes de la tabla de factores usando el método de vecinos más cercanos. Para cada dato faltante, el algoritmo busca las industrias más parecidas según el resto de variables disponibles y reemplaza el valor por el promedio de esas industrias.

    Usamos una imputación determinista con pesos uniformes, por lo que todos los vecinos considerados tienen el mismo peso en el cálculo. El resultado conserva las mismas columnas de la tabla original y deja la base lista para construir indicadores compuestos.
    """)
    return


@app.cell
def _(KNNImputer, KNN_N_NEIGHBORS, factores, pd, pl):
    # Imputacion determinista: cada faltante se reemplaza por el promedio de las
    # K industrias mas parecidas.
    imputer = KNNImputer(n_neighbors=KNN_N_NEIGHBORS, weights="uniform")
    factores_imputados = pl.from_pandas(
        pd.DataFrame(imputer.fit_transform(factores.to_pandas()), columns=factores.columns)
    )
    factores_imputados
    return (factores_imputados,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Agregacion con TOPSIS

    TOPSIS ordena cada industria segun su cercania a una solucion ideal. Con pesos iguales, cada factor contribuye lo mismo; la normalizacion por defecto es min-max. El resultado (`pref`) es un score entre 0 y 1: a mayor score, mas atractiva o mas viable la industria.
    """)
    return


@app.cell
def _(TOPSIS):
    topsis = TOPSIS()
    return (topsis,)


@app.cell
def _(mo):
    mo.md(r"""
    Construimos el ranking de atractivo productivo usando el método TOPSIS. Para ello seleccionamos los factores definidos en `ATRACTIVO_FACTORES` y asignamos el mismo peso a cada uno, de manera que todos los indicadores contribuyan por igual al resultado.

    Luego aplicamos `topsis()` considerando la dirección esperada de cada variable, definida en `ATRACTIVO_TYPES`. El puntaje resultante se convierte en un ranking con `rrankdata()`, lo que permite ordenar las actividades según su atractivo relativo.
    """)
    return


@app.cell
def _(
    ATRACTIVO_FACTORES,
    ATRACTIVO_TYPES,
    factores_imputados,
    np,
    rrankdata,
    topsis,
):
    alts_atractivo = factores_imputados.select(ATRACTIVO_FACTORES).to_numpy()
    weights_atractivo = np.array([1 / len(ATRACTIVO_FACTORES)] * len(ATRACTIVO_FACTORES))
    pref_atractivo = topsis(alts_atractivo, weights_atractivo, ATRACTIVO_TYPES)
    ranking_atractivo = rrankdata(pref_atractivo)
    return pref_atractivo, ranking_atractivo


@app.cell
def _(mo):
    mo.md(r"""
    Construimos el ranking de viabilidad productiva usando el método TOPSIS. Para ello seleccionamos los factores definidos en `VIABILIDAD_FACTORES` y asignamos el mismo peso a cada variable, de modo que todas contribuyan por igual al resultado.

    Luego aplicamos `topsis()` considerando la dirección esperada de cada indicador, definida en `VIABILIDAD_TYPES`. El puntaje resultante se convierte en un ranking con `rrankdata()`, lo que permite ordenar las actividades según su viabilidad relativa.
    """)
    return


@app.cell
def _(
    VIABILIDAD_FACTORES,
    VIABILIDAD_TYPES,
    factores_imputados,
    np,
    rrankdata,
    topsis,
):
    alts_viabilidad = factores_imputados.select(VIABILIDAD_FACTORES).to_numpy()
    weights_viabilidad = np.array([1 / len(VIABILIDAD_FACTORES)] * len(VIABILIDAD_FACTORES))
    pref_viabilidad = topsis(alts_viabilidad, weights_viabilidad, VIABILIDAD_TYPES)
    ranking_viabilidad = rrankdata(pref_viabilidad)
    return pref_viabilidad, ranking_viabilidad


@app.cell
def _(mo):
    mo.md(r"""
    Consolidamos los resultados de atractivo y viabilidad en una sola tabla por actividad CIIU. A cada actividad se le agregan los puntajes TOPSIS de atractivo y viabilidad, junto con sus respectivos rankings.

    Esta tabla permite comparar las actividades según ambos criterios y sirve como base para cruces posteriores con los resultados de complejidad u otras variables del análisis.
    """)
    return


@app.cell
def _(
    factores_imputados,
    pl,
    pref_atractivo,
    pref_viabilidad,
    ranking_atractivo,
    ranking_viabilidad,
):
    scores_viabilidad_atractivo = (
        factores_imputados.select("ciiu")
        .with_columns(
            topsis_atractivo=pref_atractivo,
            topsis_viabilidad=pref_viabilidad,
            ranking_atractivo=ranking_atractivo,
            ranking_viabilidad=ranking_viabilidad,
        )
        .with_columns(pl.col("ciiu").cast(pl.Int64))
    )
    scores_viabilidad_atractivo
    return (scores_viabilidad_atractivo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. Diagramas Viabilidad-Atractivo

    Margen **intensivo** = industrias donde Honduras ya tiene presencia (`mcp == 1`). Margen **extensivo** = industrias potenciales (`mcp == 0`). En ambos casos se exige RCA > 0 y que la industria este en la seleccion final del ejercicio de complejidad. Las lineas rojas marcan el promedio de cada eje (cuadrantes).
    """)
    return


@app.cell
def _(
    alt,
    cdata_hnd,
    ciiu_pedro,
    mapp_ciiu,
    pd,
    pl,
    scores_viabilidad_atractivo,
):
    def arma_dataset_diagrama(mcp_valor, resultados_finales):
        """Une los scores TOPSIS con nombres de actividad y jerarquia CIIU,
        filtrando al margen (intensivo/extensivo) y a la seleccion final."""
        return (
            cdata_hnd.filter(
                (pl.col("REF_AREA") == "HND")
                & (pl.col("rca") > 0)
                & (pl.col("mcp") == mcp_valor)
            )
            .join(mapp_ciiu, left_on="ACTIVITY", right_on="codigo")
            .join(
                ciiu_pedro.select(
                    "clase_codigo", "clase_titulo", "seccion_codigo",
                    "seccion_titulo", "division_titulo",
                ),
                left_on="ACTIVITY", right_on="clase_codigo",
            )
            .join(scores_viabilidad_atractivo, left_on="ACTIVITY", right_on="ciiu")
            .filter(pl.col("ACTIVITY").is_in(resultados_finales["ciiu4_cod"]))
        )

    def grafica_diagrama(datos, subtitulo):
        """Dispersion Viabilidad (x) vs. Atractivo (y) con lineas de referencia."""
        puntos = (
            alt.Chart(datos)
            .mark_circle(
                opacity=0.99, stroke="black", strokeWidth=1.2, strokeOpacity=0.9, size=180
            )
            .encode(
                x=alt.X("topsis_viabilidad").scale(zero=False).title("Viabilidad"),
                y=alt.Y("topsis_atractivo").scale(zero=False).title("Atractivo"),
                color=alt.Color("seccion_titulo").title("Seccion"),
                tooltip=[
                    alt.Tooltip("nombre_actividad", title="Actividad"),
                    alt.Tooltip("division_titulo", title="Division CIIU Rev 4"),
                    alt.Tooltip("OBS_VALUE", title="Empleo"),
                ],
            )
        )
        regla_atractivo = (
            alt.Chart(pd.DataFrame({"y": [datos["topsis_atractivo"].mean()]}))
            .mark_rule(color="red").encode(y="y:Q")
        )
        regla_viabilidad = (
            alt.Chart(pd.DataFrame({"x": [datos["topsis_viabilidad"].mean()]}))
            .mark_rule(color="red").encode(x="x:Q")
        )
        return (puntos + regla_atractivo + regla_viabilidad).properties(
            title=alt.TitleParams(
                "Diagrama Viabilidad-Atractivo", subtitle=subtitulo, subtitleColor="gray"
            )
        )

    return arma_dataset_diagrama, grafica_diagrama


@app.cell
def _(
    OUTPUT_DIR,
    arma_dataset_diagrama,
    grafica_diagrama,
    resultados_finales_intensivo,
):
    cdata_intensivo = arma_dataset_diagrama(1, resultados_finales_intensivo)
    grafico_intensivo = grafica_diagrama(cdata_intensivo, "Margen Intensivo")
    grafico_intensivo.save(str(OUTPUT_DIR / "diagrama_margen_intensivo.html"))
    grafico_intensivo
    return (cdata_intensivo,)


@app.cell
def _(
    OUTPUT_DIR,
    arma_dataset_diagrama,
    grafica_diagrama,
    resultados_finales_extensivo,
):
    cdata_extensivo = arma_dataset_diagrama(0, resultados_finales_extensivo)
    grafico_extensivo = grafica_diagrama(cdata_extensivo, "Margen Extensivo")
    grafico_extensivo.save(str(OUTPUT_DIR / "diagrama_margen_extensivo.html"))
    grafico_extensivo
    return (cdata_extensivo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Exportacion de resultados

    Se guarda un Excel con los factores, los factores imputados, los scores de TOPSIS y los datos de cada margen, ademas de los dos diagramas en HTML (en la carpeta `resultados/`).
    """)
    return


@app.cell
def _(
    OUTPUT_DIR,
    cdata_extensivo,
    cdata_intensivo,
    factores,
    factores_imputados,
    pd,
    scores_viabilidad_atractivo,
):
    salida_excel = OUTPUT_DIR / "viabilidad_atractivo_resultados.xlsx"
    with pd.ExcelWriter(salida_excel, engine="openpyxl") as writer:
        factores.to_pandas().to_excel(writer, sheet_name="factores", index=False)
        factores_imputados.to_pandas().to_excel(
            writer, sheet_name="factores_imputados", index=False
        )
        scores_viabilidad_atractivo.to_pandas().to_excel(
            writer, sheet_name="scores_topsis", index=False
        )
        cdata_intensivo.select(
            "clase_titulo", "topsis_atractivo", "topsis_viabilidad"
        ).to_pandas().to_excel(writer, sheet_name="margen_intensivo", index=False)
        cdata_extensivo.select(
            "clase_titulo", "topsis_atractivo", "topsis_viabilidad"
        ).to_pandas().to_excel(writer, sheet_name="margen_extensivo", index=False)

    print(f"Resultados guardados en: {OUTPUT_DIR.resolve()}")
    return


if __name__ == "__main__":
    app.run()
