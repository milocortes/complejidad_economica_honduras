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

    table = catalog.load_table(f"{data['namespace']}.{data['name']}")
    
    # 2. Open a transaction and add metadata properties
    with table.transaction() as transaction:
        transaction.set_properties(
            name=data["name"],
            longname=data["longname"],
            url=data["url"],
            namespace=data["namespace"],
            description=data["assumptions"]
        )
        