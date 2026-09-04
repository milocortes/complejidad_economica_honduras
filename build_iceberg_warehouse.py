from pyiceberg.catalog import load_catalog
import polars as pl 

warehouse_path = "warehouse"

catalog = load_catalog(
    "default",
    **{
        'type': 'sql',
        "uri": f"sqlite:///{warehouse_path}/pyiceberg_catalog.db",
        "warehouse": f"{warehouse_path}",
    },
)

### Create a new Iceberg table:
catalog.create_namespace("datos")

### Load it into your PyArrow dataframe : Actividades Transables
df = pl.read_delta("datos/actividades_transables").to_arrow()

### Create a new Iceberg table:
table = catalog.create_table(
    "datos.taxi_dataset",
    schema=df.schema,
)

### Append the dataframe to the table:
table.append(df)
len(table.scan().to_arrow())

catalog.load_table("datos.taxi_dataset").to_polars().collect()