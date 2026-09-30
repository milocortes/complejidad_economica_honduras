import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    from pyiceberg.catalog import load_catalog
    import polars as pl
    from utils.treemap_empleo import leer_datos, dibujar
    import matplotlib.pyplot as plt

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
    return catalog, dibujar, leer_datos, pl


@app.cell
def _(catalog, pl):
    ## Cargamos cdata como LazyDataFrame
    lazy_cdata = (
        catalog.load_table("complejidad.cdata")
        .to_polars()
        .filter(REF_AREA = "HND")
        .select("ACTIVITY", "OBS_VALUE", "eci", "pci", "rca")
    )

    ## Cargamos catálogo de nombre de actividades como LazyDataFrame
    lazy_nombres_actividades = (
        catalog.load_table("diccionarios.catalogo_ciiu_rev4")
        .to_polars()
        .select("clase_codigo", "clase_titulo")
    )

    ## Reunimos LazyDataFrames, cambiamos nombres de columnas y creamos nueva columna
    empleo = lazy_cdata.join(
                lazy_nombres_actividades, 
                left_on="ACTIVITY", 
                right_on="clase_codigo"
            ).rename(
                {
                    "OBS_VALUE" : "Empleo", 
                    "clase_titulo" : "nombre_actividad"
                }
            ).with_columns(
                (
                    pl.col("Empleo")/pl.col("Empleo").sum()
                ).alias("Share empleo")
            ).collect()
    empleo
    return (empleo,)


@app.cell
def _():
    return


@app.cell
def _(empleo, leer_datos):
    ## Ajustamos datos
    datos = leer_datos(empleo.to_pandas())
    datos
    return (datos,)


@app.cell
def _(datos, dibujar):
    ## Creamos Treemap plots

    ### Sector
    dibujar(datos, "sector")
    ### LQ
    dibujar(datos, "lq")
    ### PCI
    dibujar(datos, "pci")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Cargamos Treemaps
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.image(
        src="output/treemaps/treemap_empleo_sector_HND.svg",
        alt="Marimo logo",
        width=1000,
        height=500,
        rounded=True,
        caption="¿Dónde está el empleo formal en Honduras? Sectores",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.image(
        src="output/treemaps/treemap_empleo_lq_HND.svg",
        alt="Marimo logo",
        width=1000,
        height=500,
        rounded=True,
        caption="¿Dónde está el empleo formal en Honduras? LQ",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.image(
        src="output/treemaps/treemap_empleo_pci_HND.svg",
        alt="Marimo logo",
        width=1000,
        height=500,
        rounded=True,
        caption="¿Dónde está el empleo formal en Honduras? PCI",
    )
    return


if __name__ == "__main__":
    app.run()
