from pyiceberg.catalog import load_catalog
import polars as pl 
import yaml
import glob

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

### Crea Namespaces
catalog.create_namespace("complejidad") if not catalog.namespace_exists("complejidad") else "Ya existe namespace"
catalog.create_namespace("viabilidad_atractivo") if not catalog.namespace_exists("viabilidad_atractivo") else "Ya existe namespace"
catalog.create_namespace("diccionarios") if not catalog.namespace_exists("diccionarios") else "Ya existe namespace"

## Carga metadatos de tablas
tablas_meta = glob.glob("metadatos/*.yml")

## Creamos las tablas
for tabla in tablas_meta:
    # Open the file using a context manager
    with open(tabla, "r") as file:
        try:
            # Load and parse the YAML file content
            data = yaml.safe_load(file)
        except yaml.YAMLError as exc:
            print(f"Error parsing YAML file: {exc}")

    print(f"Exportando {data['name']}")
    
    if not catalog.table_exists(f"{data['namespace']}.{data['name']}"):

        ### Load it into your PyArrow dataframe : Actividades Transables
        df = pl.read_delta(f"datos/{data['name']}").to_arrow()

        ### Create a new Iceberg table:
        table = catalog.create_table(
            f"{data['namespace']}.{data['name']}",
            schema=df.schema,
        )

        # 2. Open a transaction and add metadata properties
        with table.transaction() as transaction:
            transaction.set_properties(
                name=data["name"],
                longname=data["longname"],
                url=data["url"],
                namespace=data["namespace"],
                description=data["assumptions"]
            )
            
        ### Append the dataframe to the table:
        table.append(df)

len(table.scan().to_arrow())

catalog.load_table("datos.taxi_dataset").to_polars().collect()
