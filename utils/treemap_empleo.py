# =============================================================================
#  TREEMAPS DE EMPLEO FORMAL EN HONDURAS (sector, cociente de localización, PCI)
# =============================================================================
#
#  QUÉ HACE
#    Lee el Excel de empleo por actividad (CIIU Rev. 4, 4 dígitos) y dibuja un
#    treemap: el tamaño de cada caja es el share del empleo y el color depende
#    de la versión que elijas:
#       sector -> un color por sector            (Figura 5.1)
#       lq     -> cociente de localización (LQ)  (Figura 5.2)
#       pci    -> complejidad de la actividad    (Figura 5.3)
#    Las cajas quedan en el mismo lugar en las tres versiones.
#
#  QUÉ NECESITAS
#    Python 3 y tres librerías. Se instalan una sola vez desde la terminal:
#       pip install pandas matplotlib openpyxl
#
#  CÓMO CORRERLO
#    1. Guarda este archivo con extensión .py (por ejemplo, treemap.py) en la
#       misma carpeta que el Excel. Si lo recibiste como .txt, solo cámbiale
#       la extensión. Se puede abrir y editar con cualquier editor de texto
#       (Bloc de notas, TextEdit, VS Code, etc.).
#    2. Abre una terminal en esa carpeta y escribe:
#          python treemap.py sector
#          python treemap.py lq
#          python treemap.py pci
#       Si no escribes la versión, genera las tres.
#    3. Los PNG, los SVG y una tabla de nombres quedan en la carpeta "out".
#
#  QUÉ EDITAR
#    Casi todo lo que querrías cambiar está en la sección 1 (CONFIGURACIÓN):
#    archivo de entrada, títulos, textos de las notas, fuente, colores,
#    nombres cortos de las actividades y a qué sector pertenece cada una.
#    Las secciones 2 en adelante hacen el dibujo y normalmente no hay que tocarlas.
# =============================================================================

import os
import sys

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")                      # dibuja sin abrir ventanas
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, to_rgba
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Rectangle


# =============================================================================
# 1. CONFIGURACIÓN
# =============================================================================

# --- Archivo de entrada y carpeta de salida -----------------------------------
CARPETA_SALIDA = "output"
CARPETA_TREEMAPS = "treemaps"

# Nombres de las columnas del Excel.
COL_CODIGO = "ACTIVITY"            # código CIIU a 4 dígitos
COL_NOMBRE = "nombre_actividad"    # nombre largo original
COL_EMPLEO = "Empleo"
COL_SHARE = "Share empleo"
COL_PCI = "pci"
COL_LQ = "rca"                     # en el Excel se llama rca; en el paper es el LQ

# --- Textos de la figura ------------------------------------------------------
ANIO = 2019
ENCABEZADO = "Empleo formal, {anio}: {total}"       # arriba a la izquierda
TITULO = "¿Dónde está el empleo formal en Honduras?"

NOTA = {
    "sector": "Tamaño: participación en el empleo formal (CIIU Rev. 4, 4 dígitos). Porcentajes: share del empleo.",
    "lq":     "Tamaño: share del empleo formal.\nColor: LQ, escala log centrada en 1.",
    "pci":    "Tamaño: participación en el empleo formal. Color: PCI de la actividad (CIIU Rev. 4, 4 dígitos).",
}

# --- Tipografía ---------------------------------------------------------------
# Carlito es una letra libre equivalente a Calibri. Si no la tienes instalada,
# cámbiala por una que sí tengas, por ejemplo "Calibri", "Arial" o "Source Sans 3".
FUENTE = "Carlito"

# --- Escala de color del PCI (naranja = baja, verde = alta) --------------------
# Colores tomados del Atlas de Complejidad Económica. Cada tupla es
# (posición en la escala de 0 a 1, color RGB de 0 a 255).
LIMITE_PCI = 4.0          # la escala se satura en -4 y +4
COLORES_PCI = [
    (0.000, (226, 156,  92)),
    (0.300, (231, 173, 120)),
    (0.499, (247, 229, 211)),
    (0.501, (205, 236, 232)),
    (0.620, ( 90, 184, 176)),
    (0.800, ( 30, 157, 147)),
    (1.000, (  3, 140, 128)),
]

# --- Escala de color del LQ (gris = sin especialización, azul = con ella) -----
# Escala logarítmica centrada en 1; se satura en 0.1 y 10.
COLORES_LQ = [
    (0.000, (160, 160, 160)),
    (0.499, (238, 238, 238)),
    (0.501, (205, 225, 243)),
    (0.750, ( 66, 146, 198)),
    (1.000, (  8,  69, 148)),
]

# --- Colores por sector -------------------------------------------------------
COLORES_SECTOR = {
    "Textil y confección":           "#C85A7C",
    "Alimentos, bebidas y tabaco":   "#D99A2B",
    "Otras manufacturas":            "#7B68B0",
    "Comercio":                      "#3A86C8",
    "Servicios de apoyo a empresas": "#3FA796",
    "Servicios profesionales":       "#1F5F7A",
    "Transporte y logística":        "#8C6D4F",
    "Energía, agua y residuos":      "#E0703A",
    "Turismo y alojamiento":         "#B5AE2C",
    "TIC y medios":                  "#5E9A3C",
    "Construcción":                  "#8A8A8A",
    "Minería":                       "#4A4A4A",
}


# --- Sector de cada actividad -------------------------------------------------
# Se asigna por rangos del código CIIU. Si quieres mover una actividad a otro
# sector, agrega una línea al diccionario EXCEPCIONES_SECTOR, por ejemplo:
#     EXCEPCIONES_SECTOR = {7911: "Turismo y alojamiento"}
EXCEPCIONES_SECTOR = {}

def sector_de(codigo):
    if codigo in EXCEPCIONES_SECTOR:
        return EXCEPCIONES_SECTOR[codigo]
    if codigo < 1000:                          return "Minería"
    if codigo < 1300:                          return "Alimentos, bebidas y tabaco"
    if codigo < 1600:                          return "Textil y confección"
    if codigo < 3500:                          return "Otras manufacturas"
    if codigo < 4000:                          return "Energía, agua y residuos"
    if codigo < 4500:                          return "Construcción"
    if codigo < 4900:                          return "Comercio"
    if codigo < 5500:                          return "Transporte y logística"
    if codigo < 5600 or 7900 <= codigo < 8000: return "Turismo y alojamiento"
    if codigo < 6800:                          return "TIC y medios"
    if codigo < 7700:                          return "Servicios profesionales"
    return "Servicios de apoyo a empresas"


# --- Nombres cortos -----------------------------------------------------------
# Código CIIU: nombre que aparece en la caja. El comentario a la derecha es el
# nombre original del Excel, como referencia. Para cambiar una etiqueta, edita
# solo el texto entre comillas.
NOMBRES_CORTOS = {
    810: 'Piedra, arena y arcilla',                       # Extracción de piedra de cantera, arena y arcilla
    899: 'Otras minas y canteras',                        # Explotación de otras minas y canteras n.c.p.
    910: 'Apoyo a petróleo y gas',                        # Actividades de apoyo para la extracción de petróleo y gas natural
    990: 'Apoyo a minería',                               # Actividades de apoyo para otras actividades de explotación de minas y canteras
    1010: 'Carne',                                        # Elaboración y conservación de carne
    1020: 'Pescados y mariscos',                          # Elaboración y conservación de pescado, crustáceos y moluscos
    1030: 'Frutas y hortalizas procesadas',               # Elaboración y conservación de frutas, legumbres y hortalizas
    1040: 'Aceites y grasas',                             # Elaboración de aceites y grasas de origen vegetal y animal
    1050: 'Lácteos',                                      # Elaboración de productos lácteos
    1061: 'Molienda',                                     # Elaboración de productos de molienda
    1062: 'Almidones',                                    # Elaboración de almidones y productos derivados del almidón
    1071: 'Panadería',                                    # Elaboración de productos de panadería
    1072: 'Azúcar',                                       # Elaboración de azúcar
    1073: 'Cacao y confitería',                           # Elaboración de cacao y chocolate y de productos de confitería
    1074: 'Pastas',                                       # Elaboración de macarrones, fideos, alcuzcuz y productos farináceos similares
    1075: 'Comidas preparadas',                           # Elaboración de comidas y platos preparados
    1079: 'Otros alimentos',                              # Elaboración de otros productos alimenticios n.c.p.
    1080: 'Alimento para animales',                       # Elaboración de alimentos preparados para animales
    1101: 'Licores destilados',                           # Destilación, rectificación y mezcla de bebidas alcohólicas
    1102: 'Vinos',                                        # Elaboración de vinos
    1103: 'Cerveza',                                      # Elaboración de malta y licores de malta
    1104: 'Bebidas no alcohólicas',                       # Elaboración de bebidas no alcohólicas
    1200: 'Tabaco',                                       # Elaboración de productos de tabaco
    1311: 'Hilatura',                                     # Preparación e hilatura de fibras textiles
    1312: 'Tejedura',                                     # Tejedura de productos textiles
    1313: 'Acabado textil',                               # Acabado de productos textiles
    1391: 'Tejidos de punto',                             # Fabricación de tejidos de punto y ganchillo
    1392: 'Textiles para el hogar',                       # Fabricación de artículos confeccionados de materiales textiles, excepto prendas de vestir
    1393: 'Tapices y alfombras',                          # Fabricación de tapices y alfombras
    1394: 'Cuerdas y redes',                              # Fabricación de cuerdas, cordeles, bramantes y redes
    1399: 'Otros textiles',                               # Fabricación de otros productos textiles n.c.p.
    1410: 'Prendas de vestir',                            # Fabricación de prendas de vestir, excepto prendas de piel
    1511: 'Curtido de cuero',                             # Curtido y adobo de cueros
    1520: 'Calzado',                                      # Fabricación de calzado
    1610: 'Aserrado de madera',                           # Aserrado y acepilladura de madera
    1621: 'Tableros de madera',                           # Fabricación de hojas de madera para enchapado y tableros a base de madera
    1622: 'Carpintería para construcción',                # Fabricación de partes y piezas de carpintería para edificios y construcciones
    1623: 'Recipientes de madera',                        # Fabricación de recipientes de madera
    1629: 'Otros productos de madera',                    # Fabricación de otros productos de madera; fabricación de artículos de corcho, paja y materiales trenzables
    1701: 'Pasta y papel',                                # Fabricación de pasta de madera, papel y cartón
    1702: 'Cartón y envases de papel',                    # Fabricación de papel y cartón ondulado y de envases de papel y cartón
    1709: 'Otros artículos de papel',                     # Fabricación de otros artículos de papel y cartón
    1811: 'Impresión',                                    # Impresión
    1812: 'Servicios de impresión',                       # Actividades de servicios relacionadas con la impresión
    1920: 'Refinación de petróleo',                       # Fabricación de productos de la refinación del petróleo
    2011: 'Químicos básicos',                             # Fabricación de sustancias químicas básicas
    2012: 'Abonos',                                       # Fabricación de abonos y compuestos de nitrógeno
    2013: 'Plásticos primarios',                          # Fabricación de plásticos y caucho sintético en formas primarias
    2021: 'Agroquímicos',                                 # Fabricación de plaguicidas y otros productos químicos de uso agropecuario
    2022: 'Pinturas y tintas',                            # Fabricación de pinturas, barnices y productos de revestimiento similares, tintas de imprenta y masillas
    2023: 'Jabones, detergentes y cosméticos',            # Fabricación de jabones y detergentes, preparados para limpiar y pulir, perfumes y preparados de tocador
    2029: 'Otros químicos',                               # Fabricación de otros productos químicos n.c.p.
    2030: 'Fibras artificiales',                          # Fabricación de fibras artificiales
    2100: 'Farmacéuticos',                                # Fabricación de productos farmacéuticos, sustancias químicas medicinales y productos botánicos de uso farmacéutico
    2211: 'Llantas',                                      # Fabricación de llantas y tubos de hule, reconstrucción y revitalizado de llantas de hule
    2219: 'Otros de caucho',                              # Fabricación de otros productos de caucho
    2220: 'Productos de plástico',                        # Fabricación de productos de plástico
    2310: 'Vidrio',                                       # Fabricación de vidrio y productos de vidrio
    2391: 'Refractarios',                                 # Fabricación de productos refractarios
    2392: 'Ladrillos y tejas',                            # Fabricación de materiales de construcción de arcilla
    2393: 'Cerámica',                                     # Fabricación de otros productos de porcelana y de cerámica
    2394: 'Cemento, cal y yeso',                          # Fabricación de cemento, cal y yeso
    2395: 'Artículos de concreto',                        # Fabricación de artículos de hormigón, cemento y yeso
    2396: 'Piedra tallada',                               # Corte, talla y acabado de la piedra
    2399: 'Otros minerales no metálicos',                 # Fabricación de otros productos minerales no metálicos n.c.p.
    2410: 'Hierro y acero',                               # Industrias básicas de hierro y acero
    2420: 'Metales no ferrosos',                          # Fabricación de metales preciosos básicos y de otros metales no ferrosos
    2431: 'Fundición de hierro',                          # Fundición de hierro y acero
    2432: 'Fundición no ferrosa',                         # Fundición de metales no ferrosos
    2511: 'Estructuras metálicas',                        # Fabricación de productos metálicos para uso estructural
    2512: 'Tanques metálicos',                            # Fabricación de tanques, depósitos y recipientes de metal
    2513: 'Generadores de vapor',                         # Fabricación de generadores de vapor, excepto calderas de agua caliente para calefacción central
    2520: 'Armas',                                        # Fabricación de armas y municiones
    2591: 'Forja y estampado',                            # Forja, prensado, estampado y laminado de metales; pulvimetalurgia
    2592: 'Tratamiento de metales',                       # Tratamiento y revestimiento de metales
    2593: 'Herramientas y ferretería',                    # Fabricación de artículos de cuchillería, herramientas de mano y artículos de ferretería
    2599: 'Otros productos metálicos',                    # Fabricación de otros productos elaborados de metal n.c.p.
    2610: 'Componentes electrónicos',                     # Fabricación de componentes y tableros electrónicos
    2620: 'Computadoras',                                 # Fabricación de ordenadores (computadoras) y equipo periférico
    2630: 'Equipo de comunicaciones',                     # Fabricación de equipo de comunicaciones
    2640: 'Electrónica de consumo',                       # Fabricación de aparatos electrónicos de consumo
    2651: 'Instrumentos de medición',                     # Fabricación de equipo de medición, prueba, navegación y control
    2652: 'Relojes',                                      # Fabricación de relojes
    2660: 'Equipo electromédico',                         # Fabricación de equipo de irradiación y equipo electrónico de uso médico y terapéutico
    2670: 'Óptica y fotografía',                          # Fabricación de instrumentos ópticos y equipo fotográfico
    2710: 'Motores y transformadores',                    # Fabricación de motores, generadores y transformadores eléctricos y aparatos de distribución y control de la energía eléctrica
    2731: 'Cables de fibra óptica',                       # Fabricación de cables de fibra óptica
    2732: 'Otros cables eléctricos',                      # Fabricación de otros hilos y cables eléctricos
    2733: 'Dispositivos de cableado',                     # Fabricación de dispositivos de cableado
    2750: 'Electrodomésticos',                            # Fabricación de aparatos de uso doméstico
    2790: 'Otro equipo eléctrico',                        # Fabricación de otros tipos de equipo eléctrico
    2811: 'Motores y turbinas',                           # Fabricación de motores y turbinas, excepto motores para aeronaves, vehículos automotores y motocicletas
    2812: 'Bombas hidráulicas',                           # Fabricación de equipo de propulsión de fluidos
    2813: 'Bombas, compresores y válvulas',               # Fabricación de otras bombas, compresores, grifos y válvulas
    2814: 'Cojinetes y engranajes',                       # Fabricación de cojinetes, engranajes, trenes de engranajes y piezas de transmisión
    2815: 'Hornos y quemadores',                          # Fabricación de hornos, hogares y quemadores
    2816: 'Equipo de elevación',                          # Fabricación de equipo de elevación y manipulación
    2817: 'Maquinaria de oficina',                        # Fabricación de maquinaria y equipo de oficina [excepto ordenadores (computadoras) y equipo periférico]
    2818: 'Herramientas motorizadas',                     # Fabricación de herramientas de mano motorizadas
    2819: 'Maquinaria de uso general',                    # Fabricación de otros tipos de maquinaria de uso general
    2821: 'Maquinaria agrícola',                          # Fabricación de maquinaria agropecuaria y forestal
    2822: 'Máquinas herramienta',                         # Fabricación de maquinaria para la conformación de metales y de máquinas herramienta
    2823: 'Maquinaria metalúrgica',                       # Fabricación de maquinaria metalúrgica
    2824: 'Maquinaria para minería y construcción',       # Fabricación de maquinaria para la explotación de minas y canteras y para obras de construcción
    2825: 'Maquinaria para alimentos',                    # Fabricación de maquinaria para la elaboración de alimentos, bebidas y tabaco
    2826: 'Maquinaria textil',                            # Fabricación de maquinaria para la elaboración de productos textiles, prendas de vestir y cueros
    2829: 'Otra maquinaria especial',                     # Fabricación de otros tipos de maquinaria de uso especial
    2910: 'Vehículos',                                    # Fabricación de vehículos automotores
    2920: 'Carrocerías',                                  # Fabricación de carrocerías para vehículos automotores
    2930: 'Autopartes',                                   # Fabricación de partes, piezas y accesorios para vehículos automotores
    3011: 'Buques',                                       # Construcción de buques y estructuras flotantes
    3012: 'Embarcaciones de recreo',                      # Construcción de embarcaciones de recreo y de deporte
    3020: 'Locomotoras',                                  # Fabricación de locomotoras y material rodante
    3030: 'Aeronaves',                                    # Fabricación de aeronaves, naves espaciales y maquinaria conexa
    3040: 'Vehículos militares',                          # Fabricación de vehículos militares de combate
    3091: 'Motocicletas',                                 # Fabricación de motocicletas
    3092: 'Bicicletas',                                   # Fabricación de bicicletas y vehículos de transporte para personas con discapacidad física
    3099: 'Otro equipo de transporte',                    # Fabricación de otros tipos de equipo de transporte n.c.p.
    3100: 'Muebles',                                      # Fabricación de muebles
    3211: 'Joyería',                                      # Fabricación de joyas y artículos conexos
    3212: 'Bisutería',                                    # Fabricación de bisutería y artículos conexos
    3220: 'Instrumentos musicales',                       # Fabricación de instrumentos de música
    3230: 'Artículos deportivos',                         # Fabricación de artículos de deporte
    3240: 'Juguetes',                                     # Fabricación de juegos y juguetes
    3250: 'Instrumental médico',                          # Fabricación de instrumentos y materiales médicos y odontológicos
    3290: 'Otras manufacturas',                           # Otras industrias manufactureras n.c.p.
    3510: 'Energía eléctrica',                            # Generación, transmisión y distribución de energía eléctrica
    3530: 'Vapor y aire acondicionado',                   # Suministro de vapor y de aire acondicionado
    3600: 'Agua potable',                                 # Captación, tratamiento y distribución de agua
    3700: 'Aguas residuales',                             # Evacuación de aguas residuales
    3811: 'Recolección de basura',                        # Recolección de desechos no peligrosos
    3812: 'Recolección de desechos peligrosos',           # Recolección de desechos peligrosos
    3821: 'Tratamiento de desechos',                      # Tratamiento y eliminación de desechos no peligrosos
    3822: 'Desechos peligrosos',                          # Tratamiento y eliminación de desechos peligrosos
    3830: 'Reciclaje',                                    # Recuperación de materiales
    4220: 'Obras de servicio público',                    # Construcción de proyectos de servicio público
    4290: 'Obras de ingeniería civil',                    # Construcción de otras obras de ingeniería civil
    4311: 'Demolición',                                   # Demolición
    4312: 'Preparación del terreno',                      # Preparación del terreno
    4390: 'Construcción especializada',                   # Otras actividades especializadas de construcción
    4530: 'Venta de autopartes',                          # Venta de partes, piezas y accesorios para vehículos automotores
    4540: 'Motocicletas: venta y reparación',             # Venta, mantenimiento y reparación de motocicletas y sus partes, piezas y accesorios
    4610: 'Intermediarios mayoristas',                    # Venta al por mayor a cambio de una retribución o por contrato
    4620: 'Mayoreo de materias primas agrícolas',         # Venta al por mayor de materias primas agropecuarias y animales vivos
    4630: 'Mayoreo de alimentos y bebidas',               # Venta al por mayor de alimentos, bebidas y tabaco
    4641: 'Mayoreo de textiles y calzado',                # Venta al por mayor de productos textiles, prendas de vestir y calzado
    4649: 'Mayoreo de enseres domésticos',                # Venta al por mayor de otros enseres domésticos
    4651: 'Mayoreo de computadoras',                      # Venta al por mayor de ordenadores (computadoras), equipo periférico y programas de informática
    4652: 'Mayoreo de electrónica',                       # Venta al por mayor de equipo, partes y piezas electrónicos y de telecomunicaciones
    4653: 'Mayoreo de maquinaria agrícola',               # Venta al por mayor de maquinaria, equipo y materiales agropecuarios
    4659: 'Mayoreo de otra maquinaria',                   # Venta al por mayor de otros tipos de maquinaria y equipo
    4661: 'Mayoreo de combustibles',                      # Venta al por mayor de combustibles sólidos, líquidos y gaseosos y productos conexos
    4662: 'Mayoreo de metales',                           # Venta al por mayor de metales y minerales metalíferos
    4663: 'Mayoreo de materiales construcción',           # Venta al por mayor de materiales de construcción, artículos de ferretería y equipo y materiales de fontanería y calefacción
    4669: 'Mayoreo de chatarra y otros',                  # Venta al por mayor de desperdicios, desechos y chatarra y otros productos n.c.p.
    4911: 'Ferrocarril de pasajeros',                     # Transporte interurbano de pasajeros por ferrocarril
    4922: 'Transporte de pasajeros',                      # Otras actividades de transporte por vía terrestre
    4923: 'Transporte de carga',                          # Transporte de carga por carretera
    4930: 'Transporte por tuberías',                      # Transporte por tuberías
    5011: 'Transporte marítimo de pasajeros',             # Transporte de pasajeros marítimo y de cabotaje
    5012: 'Transporte marítimo de carga',                 # Transporte de carga marítimo y de cabotaje
    5021: 'Transporte fluvial de pasajeros',              # Transporte de pasajeros por vías de navegación interiores
    5022: 'Transporte fluvial de carga',                  # Transporte de carga por vías de navegación interiores
    5110: 'Transporte aéreo de pasajeros',                # Transporte de pasajeros por vía aérea
    5120: 'Transporte aéreo de carga',                    # Transporte de carga por vía aérea
    5210: 'Almacenamiento',                               # Almacenamiento y depósito
    5221: 'Servicios al transporte terrestre',            # Actividades de servicios vinculadas al transporte terrestre
    5222: 'Servicios portuarios',                         # Actividades de servicios vinculadas al transporte acuático
    5223: 'Servicios aeroportuarios',                     # Actividades de servicios vinculadas al transporte aéreo
    5224: 'Manipulación de carga',                        # Manipulación de la carga
    5229: 'Otros servicios logísticos',                   # Otras actividades de apoyo al transporte
    5510: 'Hoteles',                                      # Actividades de alojamiento para estancias cortas
    5520: 'Campamentos',                                  # Actividades de campamentos, parques de vehículos recreativos y parques de caravanas
    5590: 'Otro alojamiento',                             # Otras actividades de alojamiento
    5911: 'Producción audiovisual',                       # Actividades de producción de películas cinematográficas, videos y programas de televisión
    5912: 'Postproducción',                               # Actividades de postproducción de películas cinematográficas, videos y programas de televisión
    5913: 'Distribución audiovisual',                     # Actividades de distribución de películas cinematográficas, videos y programas de televisión
    5914: 'Cines',                                        # Actividades de exhibición de películas cinematográficas y cintas de video
    5920: 'Grabación de sonido',                          # Actividades de grabación de sonido y edición de música
    6190: 'Telecomunicaciones',                           # Otras actividades de telecomunicaciones
    6201: 'Programación',                                 # Programación informática
    6202: 'Consultoría informática',                      # Consultoría de informática y gestión de instalaciones informáticas
    6209: 'Otros servicios de TI',                        # Otras actividades de tecnología de la información y de servicios informáticos
    6311: 'Procesamiento de datos',                       # Procesamiento de datos, hospedaje y actividades conexas
    6810: 'Inmobiliarias',                                # Actividades inmobiliarias realizadas con bienes propios o arrendados
    6910: 'Servicios jurídicos',                          # Actividades jurídicas
    6920: 'Contabilidad y auditoría',                     # Actividades de contabilidad, teneduría de libros y auditoría; consultoría fiscal
    7010: 'Oficinas corporativas',                        # Actividades de oficinas principales
    7020: 'Consultoría de gestión',                       # Actividades de consultoría de gestión
    7110: 'Arquitectura e ingeniería',                    # Actividades de arquitectura e ingeniería y actividades conexas de consultoría técnica
    7210: 'I+D ciencias e ingeniería',                    # Investigaciones y desarrollo experimental en el campo de las ciencias naturales y la ingeniería
    7220: 'I+D ciencias sociales',                        # Investigaciones y desarrollo experimental en el campo de las ciencias sociales y las humanidades
    7310: 'Publicidad',                                   # Publicidad
    7320: 'Estudios de mercado',                          # Estudios de mercado y encuestas de opinión pública
    7410: 'Diseño',                                       # Actividades especializadas de diseño
    7490: 'Otros servicios profesionales',                # Otras actividades profesionales, científicas y técnicas n.c.p.
    7710: 'Alquiler de vehículos',                        # Alquiler y arrendamiento de vehículos automotores
    7721: 'Alquiler de equipo recreativo',                # Alquiler y arrendamiento de equipo recreativo y deportivo
    7730: 'Alquiler de maquinaria',                       # Alquiler y arrendamiento de otros tipos de maquinaria, equipo y bienes tangibles
    7740: 'Licencias de propiedad intelectual',           # Arrendamiento de propiedad intelectual y productos similares, excepto obras protegidas por derechos de autor
    7810: 'Agencias de empleo',                           # Actividades de agencias de empleo
    7830: 'Otros servicios de personal',                  # Otras actividades de dotación de recursos humanos
    7911: 'Agencias de viajes',                           # Actividades de agencias de viajes
    7912: 'Operadores turísticos',                        # Actividades de operadores turísticos
    7990: 'Reservas y servicios turísticos',              # Otros servicios de reservas y actividades conexas
    8110: 'Gestión de instalaciones',                     # Actividades combinadas de apoyo a instalaciones
    8129: 'Limpieza industrial',                          # Otras actividades de limpieza de edificios y de instalaciones industriales
    8219: 'Apoyo de oficina',                             # Fotocopiado, preparación de documentos y otras actividades especializadas de apoyo de oficina
    8220: 'Centros de llamadas',                          # Actividades de centros de llamadas
    8230: 'Convenciones y exposiciones',                  # Organización de convenciones y exposiciones comerciales
    8291: 'Agencias de cobro',                            # Actividades de agencias de cobro y agencias de calificación crediticia
    8292: 'Envasado y empaquetado',                       # Actividades de envasado y empaquetado
    8299: 'Otros servicios a empresas',                   # Otras actividades de servicios de apoyo a las empresas n.c.p.
}


# =============================================================================
# 2. LECTURA DE DATOS
# =============================================================================

def leer_datos(df : pd.DataFrame) -> pd.DataFrame:
    #df = pd.read_excel(ARCHIVO_EXCEL)
    df["corto"] = df[COL_CODIGO].map(NOMBRES_CORTOS)
    df["sector"] = df[COL_CODIGO].map(sector_de)

    faltan = df.loc[df["corto"].isna(), COL_CODIGO].tolist()
    if faltan:
        raise ValueError(f"Faltan nombres cortos para estos códigos: {faltan}")

    os.makedirs(CARPETA_SALIDA, exist_ok=True)
    os.makedirs(os.path.join(CARPETA_SALIDA, CARPETA_TREEMAPS), exist_ok=True)
    #df[[COL_CODIGO, COL_NOMBRE, "corto", "sector", COL_EMPLEO, COL_SHARE, COL_PCI, COL_LQ]].to_excel(os.path.join(CARPETA_SALIDA, "equivalencias_nombres.xlsx"), index=False)

    # Las actividades con empleo cero no ocupan espacio en el treemap.
    return df[df[COL_EMPLEO] > 0].copy()


# =============================================================================
# 3. ACOMODO DE LAS CAJAS (algoritmo "squarified treemap")
# =============================================================================
# Reparte un rectángulo en cajas con áreas proporcionales a los valores,
# procurando que queden lo más cuadradas posible. Los valores deben venir
# ordenados de mayor a menor. Devuelve una lista de (x, y, ancho, alto).

def squarify(valores, x, y, ancho, alto):
    total = sum(valores)
    areas = [v * ancho * alto / total for v in valores]
    cajas = []

    def peor_proporcion(fila, lado):
        s = sum(fila)
        return max(max(lado**2 * a / s**2, s**2 / (lado**2 * a)) for a in fila)

    def colocar_fila(fila, x, y, ancho, alto):
        s = sum(fila)
        if ancho >= alto:                       # fila vertical a la izquierda
            w = s / alto
            yy = y
            for a in fila:
                cajas.append((x, yy, w, a / w))
                yy += a / w
            return x + w, y, ancho - w, alto
        h = s / ancho                           # fila horizontal arriba
        xx = x
        for a in fila:
            cajas.append((xx, y, a / h, h))
            xx += a / h
        return x, y + h, ancho, alto - h

    fila, i = [], 0
    while i < len(areas):
        lado = min(ancho, alto)
        if not fila or peor_proporcion(fila + [areas[i]], lado) <= peor_proporcion(fila, lado):
            fila.append(areas[i])
            i += 1
        else:
            x, y, ancho, alto = colocar_fila(fila, x, y, ancho, alto)
            fila = []
    if fila:
        colocar_fila(fila, x, y, ancho, alto)
    return cajas


# =============================================================================
# 4. COLORES
# =============================================================================

def crear_escala(nombre, puntos):
    return LinearSegmentedColormap.from_list(
        nombre, [(pos, tuple(c / 255 for c in rgb)) for pos, rgb in puntos])

ESCALA_PCI = crear_escala("pci", COLORES_PCI)
ESCALA_LQ = crear_escala("lq", COLORES_LQ)

def posicion_pci(pci):
    """PCI -> posición entre 0 y 1 en la escala."""
    return float(np.clip((pci + LIMITE_PCI) / (2 * LIMITE_PCI), 0, 1))

def posicion_lq(lq):
    """LQ -> posición entre 0 y 1 (escala log: 0.1 -> 0, 1 -> 0.5, 10 -> 1)."""
    return float(np.clip((np.log10(max(lq, 1e-6)) + 1) / 2, 0, 1))

def luminosidad(color):
    return 0.2126 * color[0] + 0.7152 * color[1] + 0.0722 * color[2]

def color_de_caja(fila, version):
    """Devuelve (color de fondo, color del texto) de una caja."""
    if version == "pci":
        fondo = ESCALA_PCI(posicion_pci(fila[COL_PCI]))
        if luminosidad(fondo) < 0.80:
            texto = "white"
        else:                                  # cajas muy claras: texto oscuro
            texto = "#2f6f69" if fila[COL_PCI] > 0 else "#6b5641"
    elif version == "lq":
        fondo = ESCALA_LQ(posicion_lq(fila[COL_LQ]))
        texto = "white" if luminosidad(fondo) < 0.55 else "#333333"
    else:
        fondo = to_rgba(COLORES_SECTOR[fila["sector"]])
        texto = "white"
    return fondo, texto

def segunda_linea(fila, version):
    """Valor que aparece debajo del nombre en cada caja."""
    if version == "pci":
        return f"{fila[COL_PCI]:.3f}".replace("-", "−")      # signo menos tipográfico
    if version == "lq":
        lq = fila[COL_LQ]
        return f"LQ {lq:.1f}" if lq >= 10 else f"LQ {lq:.2f}"
    return f"{fila[COL_SHARE] * 100:.1f}%"


# =============================================================================
# 5. DIBUJO
# =============================================================================

# Tamaño del lienzo en píxeles (a 200 dpi equivale a 17 x 7.5 pulgadas).
ANCHO, ALTO, DPI = 3400, 1500, 200
# Área que ocupa el treemap dentro del lienzo: x, y, ancho, alto (origen arriba a la izquierda).
TX, TY, TW, TH = 90, 200, 3220, 1080

REGULAR = FontProperties(family=FUENTE)
NEGRITA = FontProperties(family=FUENTE, weight="bold")


def dibujar(d, version):
    fig = plt.figure(figsize=(ANCHO / DPI, ALTO / DPI), dpi=DPI)
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, ANCHO)
    ax.set_ylim(ALTO, 0)                       # y crece hacia abajo, como en pantalla
    ax.axis("off")

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()

    def ancho_texto(texto, tam, fuente=REGULAR):
        """Ancho en píxeles que ocupa un texto a cierto tamaño de letra."""
        p = fuente.copy()
        p.set_size(tam)
        w, _, _ = renderer.get_text_width_height_descent(texto, p, ismath=False)
        return w

    # --- Cajas: primero se reparte el espacio entre sectores y después, dentro
    #     de cada sector, entre sus actividades.
    por_sector = d.groupby("sector")[COL_EMPLEO].sum().sort_values(ascending=False)
    cajas_sector = squarify(list(por_sector.values), TX, TY, TW, TH)

    for sector, (sx, sy, sw, sh) in zip(por_sector.index, cajas_sector):
        acts = d[d["sector"] == sector].sort_values(COL_EMPLEO, ascending=False)
        cajas = squarify(list(acts[COL_EMPLEO].values), sx, sy, sw, sh)
        for (_, fila), (x, y, w, h) in zip(acts.iterrows(), cajas):
            fondo, color_texto = color_de_caja(fila, version)
            ax.add_patch(Rectangle((x, y), w, h, facecolor=fondo, edgecolor="white", linewidth=0.6))
            poner_etiqueta(ax, ancho_texto, fila["corto"], segunda_linea(fila, version),
                           x, y, w, h, color_texto)
        # borde blanco más grueso alrededor de cada sector
        ax.add_patch(Rectangle((sx, sy), sw, sh, facecolor="none", edgecolor="white", linewidth=2.5))

    # --- Encabezado y título
    encabezado = ENCABEZADO.format(anio=ANIO, total=f"{d[COL_EMPLEO].sum():,.0f}")
    ax.text(TX, 120, encabezado, fontproperties=NEGRITA, fontsize=15, color="#222", va="center")
    ax.plot([TX, TX + ancho_texto(encabezado, 15, NEGRITA)], [150, 150],
            ls=(0, (1, 1.5)), color="#444", lw=1)
    ax.text(ANCHO / 2 + 60, 120, TITULO, fontproperties=NEGRITA, fontsize=18,
            color="#222", va="center", ha="center")

    # --- Leyenda
    if version == "sector":
        leyenda_sectores(ax, ancho_texto, d, por_sector)
    elif version == "lq":
        leyenda_gradiente(ax, ESCALA_LQ, "COCIENTE DE\nLOCALIZACIÓN (LQ)",
                          "Sin especialización relativa", "Con especialización relativa",
                          [(posicion_lq(v), t) for v, t in
                           [(0.1, "≤ 0.1"), (0.3, "0.3"), (1, "1"), (3, "3"), (10, "≥ 10")]])
        ax.text(TX, ALTO - 40, NOTA["lq"], fontproperties=REGULAR, fontsize=9, color="#777", va="bottom")
    else:
        leyenda_gradiente(ax, ESCALA_PCI, "COMPLEJIDAD DEL\nPRODUCTO (PCI)",
                          "Baja complejidad", "Alta complejidad",
                          [(posicion_pci(v), t) for v, t in
                           [(-4, "≤ −4"), (-2, "−2"), (0, "0"), (2, "+2"), (4, "≥ +4")]])
        ax.text(TX, ALTO - 40, NOTA["pci"], fontproperties=REGULAR, fontsize=9, color="#777", va="bottom")

    # --- Guardar
    base = os.path.join(CARPETA_SALIDA, CARPETA_TREEMAPS, f"treemap_empleo_{version}_HND")
    fig.savefig(base + ".png", dpi=DPI, facecolor="white")
    fig.savefig(base + ".svg", facecolor="white")
    plt.close(fig)
    print(f"Listo: {base}.png y .svg")


def poner_etiqueta(ax, ancho_texto, nombre, valor, x, y, w, h, color_texto):
    """Escribe nombre y valor en la esquina superior izquierda de una caja.

    El tamaño de letra depende del tamaño de la caja. Si el nombre no cabe,
    primero se parte en dos renglones, luego se reduce un poco la letra y, como
    último recurso, se corta con "…". En cajas muy chicas no se escribe nada.
    """
    TAM_MIN = 5.5
    tam = min(np.sqrt(w * h) / 21, 34, (h - 10) * 72 / (DPI * 1.35))
    margen = max(6, min(18, w * 0.04))
    if tam < TAM_MIN or w < 40:
        return
    disponible = w - 2 * margen

    def partir(texto, t, max_renglones):
        renglones = [""]
        for palabra in texto.split():
            prueba = (renglones[-1] + " " + palabra).strip()
            if ancho_texto(prueba, t) <= disponible or not renglones[-1]:
                renglones[-1] = prueba
            else:
                renglones.append(palabra)
        if len(renglones) > max_renglones:
            renglones = renglones[:max_renglones - 1] + [" ".join(renglones[max_renglones - 1:])]
        return renglones

    def renglones_permitidos(t):
        alto_renglon = t * DPI / 72
        return 1 if h < margen + alto_renglon * 2.5 else 2

    elegido = None
    for t in np.linspace(tam, tam * 0.72, 8):          # probar letras un poco más chicas
        if t < TAM_MIN:
            break
        renglones = partir(nombre, t, renglones_permitidos(t))
        if all(ancho_texto(r, t) <= disponible for r in renglones):
            elegido = (t, renglones)
            break

    if elegido is None:                                # cortar con "…"
        t = tam
        renglones = partir(nombre, t, renglones_permitidos(t))
        ultimo = renglones[-1]
        while ancho_texto(ultimo, t) > disponible and len(ultimo) > 3:
            ultimo = ultimo[:-2].rstrip(" ,:") + "…"
        if ancho_texto(ultimo, t) > disponible or len(ultimo) <= 4:
            return
        renglones[-1] = ultimo
        elegido = (t, renglones)

    t, renglones = elegido
    alto_renglon = t * DPI / 72
    y0 = y + margen * 0.7
    for i, r in enumerate(renglones):
        ax.text(x + margen, y0 + i * alto_renglon * 1.08, r, fontproperties=REGULAR,
                fontsize=t, color=color_texto, va="top", ha="left")
    y_valor = y0 + len(renglones) * alto_renglon * 1.08 + alto_renglon * 0.06
    if y_valor + alto_renglon * 1.15 < y + h:           # solo si cabe
        ax.text(x + margen, y_valor, valor, fontproperties=REGULAR,
                fontsize=t, color=color_texto, va="top", ha="left")


def leyenda_gradiente(ax, escala, titulo, texto_izq, texto_der, marcas):
    """Barra de color con su título a la izquierda y marcas numéricas abajo."""
    LX, LY, LW, LH = 1360, 1405, 1060, 22
    ax.imshow(np.linspace(0, 1, 512)[None, :], cmap=escala,
              extent=(LX, LX + LW, LY + LH, LY), aspect="auto", zorder=3)
    ax.set_xlim(0, ANCHO)                      # imshow cambia los límites; se restauran
    ax.set_ylim(ALTO, 0)
    ax.text(LX, LY - 18, texto_izq, fontproperties=NEGRITA, fontsize=11, color="#333", va="bottom")
    ax.text(LX + LW, LY - 18, texto_der, fontproperties=NEGRITA, fontsize=11, color="#333",
            va="bottom", ha="right")
    for pos, etiqueta in marcas:
        ax.text(LX + pos * LW, LY + LH + 10, etiqueta, fontproperties=REGULAR, fontsize=9.5,
                color="#555", va="top", ha="center")
    ax.plot([LX - 40, LX - 40], [LY - 50, LY + 70], color="#333", lw=1)
    ax.text(LX - 60, LY - 40, titulo, fontproperties=NEGRITA, fontsize=11.5, color="#333",
            va="top", ha="right", linespacing=1.15)


def leyenda_sectores(ax, ancho_texto, d, por_sector):
    """Cuadritos de color con el nombre del sector y su share, en 4 columnas."""
    total = d[COL_EMPLEO].sum()
    columnas = 4
    ancho_col = TW / columnas
    for i, (sector, empleo) in enumerate(por_sector.items()):
        cx = TX + (i % columnas) * ancho_col
        cy = 1318 + (i // columnas) * 42
        ax.add_patch(Rectangle((cx, cy), 26, 26, facecolor=COLORES_SECTOR[sector], edgecolor="none"))
        ax.text(cx + 40, cy + 13, f"{sector}  ", fontproperties=REGULAR, fontsize=11, color="#333", va="center")
        ax.text(cx + 40 + ancho_texto(sector + "  ", 11), cy + 13, f"{empleo / total * 100:.1f}%",
                fontproperties=NEGRITA, fontsize=11, color="#333", va="center")
    ax.text(ANCHO - 90, ALTO - 14, NOTA["sector"], fontproperties=REGULAR, fontsize=9,
            color="#777", ha="right", va="bottom")


