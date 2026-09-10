from pyiceberg.catalog import load_catalog
from nicegui import ui

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

# 2. Define the selection logic
def handle_namespace_change(e):
    namespace = e.value
    # Get the sub-options corresponding to the chosen namespace
    new_options = TABLAS.get(namespace, [])
    
    # Update the country dropdown's choices and clear its current value
    tabla_select.set_options(new_options)
    tabla_select.set_value(None)


# 3. Define the update logic when the parent selection changes
def handle_category_change(e):
    # e.value contains the selected item from the parent
    selected_category = e.value
    
    if selected_category:
        # Update the nested dropdown with corresponding subcategories
        new_options = DATA_MAP[selected_category]
        subcategory_select.set_options(new_options)
        # Clear the old subcategory value to avoid mismatch
        subcategory_select.value = None
    else:
        subcategory_select.set_options([])

def show_selected_values():
    global cat 
    global sub

    # Access the .value property of each UI element
    cat = category_select.value
    sub = subcategory_select.value

    
    ui.markdown(f'''
    ## Example
    This line is not .
    This is normal text again.

    {cat}
    {sub}
    ''').classes('w-48')
        

def set_allow_moving(event):
    print(event.value)

with ui.card().classes('w-[500px] mx-auto mt-20 p-12 gap-20 rounded-2xl shadow-lg border border-gray-100 items-center'):
    ui.label('Catálogo de Datos').classes('text-h6')
    
    # Create a horizontal row container spanning the full width
    with ui.row().classes('w-full items-start no-wrap'):
        
        with ui.column():
            # 1. Create the parent selection
            category_select = ui.select(
                options=list(DATA_MAP.keys()), 
                label='Selecciona namespace',
                on_change=handle_category_change
            ).classes('w-58')

            # 2. Create the nested selection (initially empty)
            subcategory_select = ui.select(
                options=[], 
                label='Seleccion Tabla'
            ).classes('w-58')

            ui.button('Carga Tabla', on_click=show_selected_values)

          
            
            # Button to trigger value retrieval

ui.run()