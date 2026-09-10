from pyiceberg.catalog import load_catalog
from nicegui import ui
import pandas as pd
import polars as pl

### Cargamos catálogo
warehouse_path = "warehouse"

catalog = load_catalog(
    "default",
    **{
        'type': 'sql',
        "uri": f"sqlite:///{warehouse_path}/pyiceberg_catalog.db",
        "warehouse": f"{warehouse_path}",
    },
)

### Obtenemos namespaces
namespaces = [i[0] for i in catalog.list_namespaces()]

### Creamos diccionario con las tablas correspondientes a cada namespace
DATA_MAP = {
    namespace : [i[1] for i in catalog.list_tables(namespace)]
    for namespace in namespaces
}

def handle_category_change(e):
    selected_category = e.value
    
    if selected_category:
        new_options = DATA_MAP[selected_category]
        subcategory_select.set_options(new_options)
        subcategory_select.value = None
    else:
        subcategory_select.set_options([])

def show_selected_values():
    global cat 
    global sub

    # Access the .value property of each UI element
    cat = category_select.value
    sub = subcategory_select.value



    # El diálogo se crea y se abre inmediatamente al ejecutarse la función
    with ui.dialog() as dialog, ui.card().style('width: 1000px; max-width: none; height: 800px;'):
        table = catalog.load_table(f"{cat}.{sub}")
        lazy_df = pl.scan_iceberg(table)

        df = (
            lazy_df
            .head(5)
            .collect()
        ).to_pandas()

        # Convert DataFrame to NiceGUI table format
        columns = [{'name': col, 'label': col, 'field': col} for col in df.columns]
        rows = df.to_dict('records')

        ui.markdown(f'''
        # **Metadatos de la Tabla**
        - **Tabla** : `{table.properties['name']}`
        - **Namespace** : `{table.properties['namespace']}`
        - **Nombre** : {table.properties['longname']} 
        - **Descripción** : {table.properties['description']}
        - **url** : <{table.properties['url']}>
        ''').classes('w-240')

        ui.markdown("## **Data Sample**")
        ui.table(columns=columns, rows=rows)
        ui.button('Cerrar', on_click=dialog.close)
    dialog.open()


        

def set_allow_moving(event):
    print(event.value)

with ui.card().classes('w-[500px] mx-auto mt-20 p-12 gap-20 rounded-2xl shadow-lg border border-gray-100 items-center'):
    ui.label('Catálogo de Datos').classes('text-h6')
    
    with ui.row().classes('w-full items-start no-wrap'):
        
        with ui.column():
            category_select = ui.select(
                options=list(DATA_MAP.keys()), 
                label='Selecciona namespace',
                on_change=handle_category_change
            ).classes('w-58')

            subcategory_select = ui.select(
                options=[], 
                label='Seleccion Tabla'
            ).classes('w-58')

            with ui.dialog() as dialog, ui.card():
                ui.label('Hello world!')
                ui.label(category_select.value)
                ui.button('Close', on_click=dialog.close)
                
            ui.button('Carga Tabla', on_click=show_selected_values)

ui.run()