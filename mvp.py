import streamlit as st
import pandas as pd
import base64
import os
from io import BytesIO
import tempfile
from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time
import requests
import openai 
import logging

import pandas as pd
import base64
import os
import tempfile
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import base64
from PIL import Image
from io import BytesIO
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize session state variables
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'selected_items' not in st.session_state:
    st.session_state.selected_items = set()
if 'doc_io' not in st.session_state:
    st.session_state.doc_io = None
if 'similarity_results' not in st.session_state:
    st.session_state.similarity_results = []


openai.api_key = os.environ['OPENAI_API_KEY']

def similitud_semanticas(texto1, texto2):
    client = OpenAI()
    prompt = f"""Imagina que eres un analista para una marca, necesitas determinar la similitud fonética de acuerdo con el alfabeto fonetico internacional, y también analiza semanticamente las siguientes denominacion:

Denominación_1:{texto1}
Denominación_2:{texto2}

Regresa este formato (Solo regresa lo siguiente):

Descripción de las similutud fonética:[Descripcion]
Score Fonético: [score 0 y 100]
¿Cómo se pronuncia ambos?: [Ambas similitudes en lenguaje fonético]

Descripción de las similutud semántica:[Descripcion]
Score Semántico: [score número entre 0 y 100]
¿Qué signfican ambos?: [Ambas signficados]

tu respuesta debe ser en markdown."""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Eres un asistente de marca que necesita determinar la similitud fonética y semántica de dos denominaciones."},
            {"role": "user", "content": prompt},
        ],
        temperature=0
    )
    return response.choices[0].message.content
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
def prepare_image(image_path):
    # Open the image
    img = Image.open(image_path)
    
    # Check the size and convert if necessary
    if img.format not in ['PNG', 'JPEG', 'GIF', 'WEBP']:
        img = img.convert('RGB')
        new_path = image_path.rsplit('.', 1)[0] + '.jpeg'
        img.save(new_path)
        return new_path
    else:
        return image_path
# Function to call GPT with the image
def analyze_image(image_path_2):
    #print(st.session_state.path)
    #print(image_path_2)
    base64_image_1 = encode_image(prepare_image(st.session_state.path))
    #base64_image_2 = encode_image(prepare_image(image_path_2))
    client = OpenAI()
    response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "system",
            "content":
            """
            You are ImageMaster, an AI assistant powered by GPT-4 with computer vision.
            - ImageMaster is fine-tuned specifically to assist with requests involving image analysis based on the content of an image. Images may include charts, plots, graphics, presentations…
            - Image inputs have been validated to be within the capabilities of GPT-4 to answer about.
            - ImageMaster always analyzes to the best of its abilities, never reporting failure nor denying an attempt at image recognition.
            - ImageMaster skills include image text extraction, data formatting, textual or table presentation, and business analysis and insights.
            Eres un asistente que trabaja en una empresa de transporte que busca que la mercancia llegue a su destino sin que se siniestralice. 
            \n Tu función es interpretar y darle valor a las decisiones de negocio a través de los datos de las gráficas.
            \n Tu interpretación concisa y de no mas de tres puntos.
            """,
            },
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": """IMAGINA QUE ERES UN ANALSTA DE IMAGENES Y TIENES QUE ANALIZAR LAS SIGUIENTES DOS IMAGENES, TU TRABAJO ES IDENTIFICAR SIMILITUDES Y TAMBIEN BRINDAR UNA DESCRIPCIÓN DE AMBAS PARA UN REPORTE.

                        regresa el formato así:

                        Descripción:[Descripcion de las imagenes]
                        Score: [Score de similitud entre imagenes ( esto debe ser un número entre 0 y 100)]
                        Argumento del score:[Brinda un argumento sobre porque le diste ese score]"""
            },
            {
              "type": "image_url",
              "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image_1}"
              }
            },
            {
              "type": "image_url",
              "image_url": {
                "url": f"data:image/jpeg;base64,{image_path_2}"
              }
            }
          ]
        }
    
      ],
      max_tokens= 1500,
    )

    print(response.choices[0].message.content)
    
    return response.choices[0].message.content
prompt = """
Imagina que eres el encargado de clasificar empresas basadas en su descripción y giro de negocio. Dado las siguiente clases Niza, clasifica la empresa.
Clases Niza:

# Clasificaciones de Productos y Servicios

## Clase 1
- Productos químicos para la industria, la ciencia y la fotografía, así como para la agricultura, la horticultura y la silvicultura.
- Resinas artificiales en bruto, materias plásticas en bruto.
- Composiciones para la extinción de incendios y la prevención de incendios.
- Preparaciones para templar y soldar metales.
- Sustancias para curtir cueros y pieles de animales.
- Adhesivos (pegamentos) para la industria.
- Masillas y otras materias de relleno en pasta.
- Compost, abonos, fertilizantes.
- Preparaciones biológicas para la industria y la ciencia.

## Clase 2
- Pinturas, barnices, lacas.
- Productos contra la herrumbre y el deterioro de la madera.
- Colorantes, tintes.
- Tintas de imprenta, tintas de marcado y tintas de grabado.
- Resinas naturales en bruto.
- Metales en hojas y en polvo para la pintura, la decoración, la imprenta y trabajos artísticos.

## Clase 3
- Productos cosméticos y preparaciones de tocador no medicinales.
- Dentífricos no medicinales.
- Productos de perfumería, aceites esenciales.
- Preparaciones para blanquear y otras sustancias para lavar la ropa.
- Preparaciones para limpiar, pulir, desengrasar y raspar.

## Clase 4
- Aceites y grasas para uso industrial, ceras.
- Lubricantes.
- Composiciones para absorber, rociar y asentar el polvo.
- Combustibles y materiales de alumbrado.
- Velas y mechas de iluminación.

## Clase 5
- Productos farmacéuticos, preparaciones para uso médico y veterinario.
- Productos higiénicos y sanitarios para uso médico.
- Alimentos y sustancias dietéticas para uso médico o veterinario, alimentos para bebés.
- Suplementos alimenticios para personas o animales.
- Emplastos, material para apósitos.
- Material para empastes e impresiones dentales.
- Desinfectantes.
- Productos para eliminar animales dañinos.
- Fungicidas, herbicidas.

## Clase 6
- Metales comunes y sus aleaciones, minerales metalíferos.
- Materiales de construcción y edificación metálicos.
- Construcciones transportables metálicas.
- Cables e hilos metálicos no eléctricos.
- Pequeños artículos de ferretería metálicos.
- Recipientes metálicos de almacenamiento y transporte.
- Cajas de caudales.

## Clase 7
- Máquinas, máquinas herramientas y herramientas mecánicas.
- Motores, excepto motores para vehículos terrestres.
- Acoplamientos y elementos de transmisión, excepto para vehículos terrestres.
- Instrumentos agrícolas que no sean herramientas de mano que funcionan manualmente.
- Incubadoras de huevos.
- Distribuidores automáticos.

## Clase 8
- Herramientas e instrumentos de mano que funcionan manualmente.
- Artículos de cuchillería, tenedores y cucharas.
- Armas blancas.
- Maquinillas de afeitar.

## Clase 9
- Aparatos e instrumentos científicos, de investigación, de navegación, geodésicos, fotográficos, cinematográficos, audiovisuales, ópticos, de pesaje, de medición, de señalización, de detección, de pruebas, de inspección, de salvamento y de enseñanza.
- Aparatos e instrumentos de conducción, distribución, transformación, acumulación, regulación o control de la distribución o consumo de electricidad.
- Aparatos e instrumentos de grabación, transmisión, reproducción o tratamiento de sonidos, imágenes o datos.
- Soportes grabados o telecargables, software, soportes de registro y almacenamiento digitales o análogos vírgenes.
- Mecanismos para aparatos que funcionan con monedas.
- Cajas registradoras, dispositivos de cálculo.
- Ordenadores y periféricos de ordenador.
- Trajes de buceo, máscaras de buceo, tapones auditivos para buceo, pinzas nasales para submarinistas y nadadores, guantes de buceo, aparatos de respiración para la natación subacuática.
- Extintores.

## Clase 10
- Aparatos e instrumentos quirúrgicos, médicos, odontológicos y veterinarios.
- Miembros, ojos y dientes artificiales.
- Artículos ortopédicos.
- Material de sutura.
- Dispositivos terapéuticos y de asistencia para personas discapacitadas.
- Aparatos de masaje.
- Aparatos, dispositivos y artículos de puericultura.
- Aparatos, dispositivos y artículos para actividades sexuales.

## Clase 11
- Aparatos e instalaciones de alumbrado, calefacción, enfriamiento, producción de vapor, cocción, secado, ventilación y distribución de agua, así como instalaciones sanitarias.

## Clase 12
- Vehículos; aparatos de locomoción terrestre, aérea o acuática.

## Clase 13
- Armas de fuego; municiones y proyectiles; explosivos; fuegos artificiales.

## Clase 14
- Metales preciosos y sus aleaciones; artículos de joyería, piedras preciosas y semipreciosas; artículos de relojería e instrumentos cronométricos.

## Clase 15
- Instrumentos musicales; atriles para partituras y soportes para instrumentos musicales; batutas.

## Clase 16
- Papel y cartón; productos de imprenta; material de encuadernación; fotografías.
- Artículos de papelería y artículos de oficina, excepto muebles.
- Adhesivos (pegamentos) de papelería o para uso doméstico.
- Material de dibujo y material para artistas.
- Pinceles.
- Material de instrucción y material didáctico.
- Hojas, películas y bolsas de materias plásticas para embalar y empaquetar.
- Caracteres de imprenta, clichés de imprenta.

## Clase 17
- Caucho, gutapercha, goma, amianto y mica en bruto o semielaborados, así como sucedáneos de estos materiales.
- Materias plásticas y resinas en forma extrudida utilizadas en procesos de fabricación.
- Materiales para calafatear, estopar y aislar.
- Tubos flexibles no metálicos.

## Clase 18
- Cuero y cuero de imitación; pieles de animales.
- Artículos de equipaje y bolsas de transporte.
- Paraguas y sombrillas; bastones.
- Fustas, arneses y artículos de guarnicionería.
- Collares, correas y ropa para animales.

## Clase 19
- Materiales de construcción no metálicos; tuberías rígidas no metálicas para la construcción.
- Asfalto, pez, alquitrán y betún.
- Construcciones transportables no metálicas; monumentos no metálicos.


## Clase 20
- Muebles, espejos, marcos; contenedores no metálicos de almacenamiento o transporte.
- Hueso, cuerno, ballena o nácar, en bruto o semielaborados; conchas.
- Espuma de mar; ámbar amarillo.

## Clase 21
- Utensilios y recipientes para uso doméstico y culinario; utensilios de cocina y vajilla, excepto tenedores, cuchillos y cucharas.
- Peines y esponjas; cepillos.
- Materiales para fabricar cepillos; material de limpieza.
- Vidrio en bruto o semielaborado, excepto vidrio de construcción.
- Artículos de cristalería, porcelana y loza.

## Clase 22
- Cuerdas y cordeles; redes.
- Tiendas de campaña y lonas; toldos de materias textiles o sintéticas.
- Velas de navegación.
- Sacos para el transporte y almacenamiento de mercancías a granel.
- Materiales de acolchado y relleno, excepto papel, cartón, caucho o materias plásticas.
- Materias textiles fibrosas en bruto y sus sucedáneos.

## Clase 23
- Hilos e hilados para uso textil.

## Clase 24
- Tejidos y sus sucedáneos; ropa de hogar; cortinas de materias textiles o de materias plásticas.

## Clase 25
- Prendas de vestir, calzado, artículos de sombrerería.

## Clase 26
- Encajes, cordones y bordados, así como cintas y lazos de mercería.
- Botones, ganchos y ojetes, alfileres y agujas.
- Flores artificiales; adornos para el cabello; cabello postizo.

## Clase 27
- Alfombras, felpudos, esteras, linóleo y otros revestimientos de suelos; tapices murales que no sean de materias textiles.

## Clase 28
- Juegos y juguetes; aparatos de videojuegos.
- Artículos de gimnasia y deporte; adornos para árboles de Navidad.

## Clase 29
- Carne, pescado, carne de ave y carne de caza; extractos de carne.
- Frutas y verduras, hortalizas y legumbres en conserva, congeladas, secas y cocidas.
- Jaleas, confituras, compotas; huevos.
- Leche, quesos, mantequilla, yogur y otros productos lácteos.
- Aceites y grasas para uso alimenticio.

## Clase 30
- Café, té, cacao y sucedáneos del café; arroz, pastas alimenticias y fideos.
- Tapioca y sagú; harinas y preparaciones a base de cereales.
- Pan, productos de pastelería y confitería; chocolate.
- Helados cremosos, sorbetes y otros helados; azúcar, miel, jarabe de melaza.
- Levadura, polvos de hornear; sal, productos para sazonar, especias, hierbas en conserva; vinagre, salsas y otros condimentos; hielo.

## Clase 31
- Productos agrícolas, acuícolas, hortícolas y forestales en bruto y sin procesar; granos y semillas en bruto o sin procesar.
- Frutas y verduras, hortalizas y legumbres frescas, hierbas aromáticas frescas.
- Plantas y flores naturales; bulbos, plantones y semillas para plantar.
- Animales vivos; productos alimenticios y bebidas para animales; malta.

## Clase 32
- Cervezas; bebidas sin alcohol; aguas minerales y aguas gaseosas.
- Bebidas a base de frutas y zumos de frutas; siropes y otras preparaciones para hacer bebidas.

## Clase 33
- Bebidas alcohólicas excepto cervezas; preparaciones alcohólicas para elaborar bebidas.

## Clase 34
- Tabaco y sucedáneos del tabaco; cigarrillos y puros.
- Cigarrillos electrónicos y vaporizadores bucales para fumadores; artículos para fumadores.
- Cerillas.

## Clase 35
- Publicidad; gestión de negocios comerciales; administración comercial; trabajos de oficina.

## Clase 36
- Servicios de seguros; operaciones financieras; operaciones monetarias; negocios inmobiliarios.

## Clase 37
- Servicios de construcción; servicios de instalación y reparación.
- Extracción minera, perforación de gas y de petróleo.

## Clase 38
- Servicios de telecomunicaciones.

## Clase 39
- Transporte; embalaje y almacenamiento de mercancías; organización de viajes.

## Clase 40
- Tratamiento de materiales; reciclaje de residuos y desechos.
- Purificación del aire y tratamiento del agua; servicios de impresión.
- Conservación de alimentos y bebidas.

## Clase 41
- Educación; formación; servicios de entretenimiento; actividades deportivas y culturales.

## Clase 42
- Servicios científicos y tecnológicos, así como servicios de investigación y diseño conexos.
- Servicios de análisis industrial, investigación industrial y diseño industrial; control de calidad y servicios de autenticación.
- Diseño y desarrollo de equipos informáticos y software.

## Clase 43
- Servicios de restauración (alimentación); hospedaje temporal.

## Clase 44
- Servicios médicos; servicios veterinarios; tratamientos de higiene y de belleza para personas o animales.
- Servicios de agricultura, acuicultura, horticultura y silvicultura.

## Clase 45
- Servicios jurídicos; servicios de seguridad para la protección física de bienes materiales y personas.
- Servicios personales y sociales prestados por terceros para satisfacer necesidades individuales.
Descripción:{descripción}

Clasifica la descripción basado en las clases, si ninguna aplica regresa la que más tenga similitud. Siempre deben perteneces a una clase.

Clase: [Regresa la clase o clases aquí]

\n Descripción: [Regresa una breve descripción que argumente tu decisión.]

\n Argumento de la decisión: [Brinda un argumento sobre porque le diste esa clase o clases]

"""
# Initialize WebDriver in headless mode
def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument('--window-size=1920x10080')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    options.add_argument('--incognito')
    options.add_argument('--disable-extensions')
    driver = webdriver.Chrome(options=options)
    return driver

# Save image from base64 string to file
def save_image_from_base64(base64_str, index):
    # Decode the base64 string
    image_data = base64.b64decode(base64_str)
    # Use BytesIO to convert the binary data to a file-like object
    image_file = io.BytesIO(image_data)
    # Try to open the image to verify it's valid
    try:
        with Image.open(image_file) as img:
            # If successful, rewind the file-like object
            image_file.seek(0)
            # Define the directory and path for saving the image
            image_folder = os.path.join(tempfile.gettempdir(), "trademark_images")
            if not os.path.exists(image_folder):
                os.makedirs(image_folder)
            image_path = os.path.join(image_folder, f"image{index + 1}.png")

            # Save the image
            img.save(image_path)
            return image_path
    except Exception as e:
        print(f"Error loading image: {e}")
        return None
def classify_brand(description):
    client = OpenAI()
    # Realizar la llamada a la API de GPT-4 para clasificar la descripción de la marca
    response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Eres un experto en clasificación de marcas."},
                {"role": "user", "content": prompt.format(descripción=description)},
            ]
        )
    # Asumiendo que la respuesta de la API incluye una clasificación en el texto de respuesta
    return response.choices[0].message.content
# Perform search and process images
def search_marks(name, clase):
    driver = init_driver()
    driver.get('https://acervomarcas.impi.gob.mx:8181/marcanet/vistas/common/datos/bsqFoneticaCompleta.pgi')
    time.sleep(5)

    clase_input = driver.find_element(By.ID, "frmBsqFonetica:clases")
    clase_input.clear()
    clase_input.send_keys(clase)

    denominacion_input = driver.find_element(By.ID, "frmBsqFonetica:denominacion")
    denominacion_input.clear()
    denominacion_input.send_keys(name)

    buscar_button = driver.find_element(By.ID, "frmBsqFonetica:busquedaId2")
    buscar_button.click()

    time.sleep(5)  # Better to use WebDriverWait
    rows = driver.find_elements(By.XPATH, "//tbody[@id='frmBsqFonetica:resultadoExpediente_data']/tr")

    data = []
    table_data = []
    headers = driver.find_elements(By.XPATH, "//thead/tr/th")  # Adjust the XPath as needed
    expediente_column_index = None
    for i, header in enumerate(headers):
        if header.text == 'Expediente':
            expediente_column_index = i
            break

    if expediente_column_index is None:
        raise Exception("Expediente column not found")

    for index, row in enumerate(rows[:5]):
        print(index)
        cols = row.find_elements(By.TAG_NAME, "td")
        row_data = {}  # Exclude the image column initially
        try:
            image_element = cols[-1].find_element(By.TAG_NAME, "img")
            image_src = image_element.get_attribute("src")
            if image_src.startswith('data:image'):
                _, encoded_data = image_src.split(',', 1)
                encoded_data = encoded_data.replace("%0A", "")
                image_data = base64.b64decode(encoded_data)
                row_data['base_64']=encoded_data

                # Use BytesIO to convert the binary data to a file-like object
                image = Image.open(BytesIO(image_data))

                # Specify the path and filename where you want to save the image
                image_path = f"./image_{index+1}.png"

                # Save the image to the specified path
                image.save(image_path)
                row_data['Path']=image_path  # Append the file path instead of base64
            else:
                row_data['Path']=None
        except Exception as e:
            row_data['Path']=None

        original_window_handle = driver.current_window_handle

        # Click the "Expediente" link which opens a new window/tab
        expediente_link = cols[expediente_column_index].find_element(By.TAG_NAME, "a")
        logging.info(f"Clicking on expediente link for row {index + 1}")
        expediente_link.click()

        # Wait for the new window/tab to open
        WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))

        # Switch to the new window
        new_window_handle = [handle for handle in driver.window_handles if handle != original_window_handle][0]
        driver.switch_to.window(new_window_handle)

        # Wait for the necessary elements to load in the new window
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "span[id^='j_idt']")))
        time.sleep(5)  # Additional wait time to ensure all elements are loaded

        # Extract "Número de expediente", "Número de registro", and "Denominación"
        try:
            numero_de_expediente = driver.find_element(By.ID, "j_idt148:0:dataNumExpId").text
        except NoSuchElementException:
            numero_de_expediente = "Not found"
        
        # Assuming "Número de registro" can be similarly found if it had a consistent and identifiable element  # Adjust the ID based on actual ID used in the page
        try:
            clase = driver.find_element(By.CSS_SELECTOR, "span[id*='claseProdId']").text
        except NoSuchElementException:
            clase = "Not found"
          # Placeholder since it's not available/visible in the provided HTML snippet
        
        try:
            denominacion = driver.find_element(By.ID, "j_idt183:0:dataDenId").text
        except NoSuchElementException:
            denominacion = "Not found"
        try:
            # Locate the "Número de registro" span by its ID and extract its text
            numero_de_registro = driver.find_element(By.ID, "j_idt153:0:dataNumRegId").text
        except NoSuchElementException:
            numero_de_registro = "Not found"
        try:
            fecha_vigencia = driver.find_element(By.ID, "j_idt173:0:dataFechaVigId").text
            row_data['Fecha de vigencia'] = fecha_vigencia
            row_data['Estado'] = "Vigente" if fecha_vigencia else "No vigente"
        except NoSuchElementException:
            row_data['Fecha de vigencia'] = "No disponible"
            row_data['Estado'] = "No disponible"
        
        try:
            descripcion = driver.find_element(By.ID, "dtGrdProductosId:0:dtTblProdServId:0:descProId").text
            row_data['Descripción'] = descripcion

        except NoSuchElementException:
            descripcion = "No disponible"
            row_data['Descripción'] = descripcion
        try:
            # Locate the "Número de registro" span by its ID and extract its text
            titular = driver.find_element(By.ID, "j_idt252:0:dataTitNomId").text
        except NoSuchElementException:
            titular = "Not found"

        except TimeoutException:
            titular = "Loading timeout"
        
        row_data['Número de expediente'] = numero_de_expediente
        row_data['Denominación'] = denominacion
        row_data['Clase'] = clase
        
        # Assuming you've adjusted the ID to match the actual "Número de registro"
        row_data['Número de registro'] = numero_de_registro 
        row_data["Titular"]=titular # Adjust the ID based on your needs
        
        # Append these details to your row data or handle them as needed
        table_data.append(row_data)

        # Close the new window and switch back to the original window
        driver.close()
        driver.switch_to.window(original_window_handle)
    driver.quit()

    return table_data

# Add custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stTitle {
        color: #2c3e50;
        font-size: 3rem !important;
        padding-bottom: 2rem;
        text-align: center;
    }
    .stButton button {
        background-color: #2c3e50;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 2rem;
        width: 100%;
    }
    .stButton button:hover {
        background-color: #34495e;
    }
    .stExpander {
        border: 1px solid #eee;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    .stTextInput input {
        border-radius: 5px;
    }
    .stFileUploader {
        border: 2px dashed #ccc;
        border-radius: 5px;
        padding: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# App header with logo/icon
st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1 style='color: #2c3e50;'>🔍 D4ne</h1>
        <p style='color: #7f8c8d; font-size: 1.2rem;'>Herramienta de IA para similitud de marcas</p>
    </div>
""", unsafe_allow_html=True)

# Create tabs for better organization
tab1, tab2 = st.tabs(["Búsqueda de Marcas", "Clasificación Niza"])

with tab1:
    st.markdown("""
        <div style='background-color: #f8f9fa; padding: 1rem; border-radius: 5px; margin-bottom: 2rem;'>
            <h3 style='color: #2c3e50;'>Búsqueda de Marcas</h3>
            <p>Ingrese los detalles de la marca que desea buscar.</p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("search_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input('Denominación de marca:', placeholder='Ingrese el nombre de la marca')
        with col2:
            clase = st.text_input('Clase Niza:', placeholder='Ej: 42')
        
        st.markdown("<br>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("📤 Subir imagen de la marca", type=['png', 'jpeg', 'jpg'])
        
        if uploaded_file is not None:
            img_bytes = uploaded_file.getvalue()
            img = Image.open(BytesIO(img_bytes))
            extension = uploaded_file.name.split('.')[-1]
            file_path = os.path.join(f"./original.{extension}")
            img.save(file_path)
            st.session_state.path = file_path
            
        st.markdown("<br>", unsafe_allow_html=True)
        submitted_search = st.form_submit_button("🔍 Buscar")
        
        if submitted_search:
            if name and clase:
                with st.spinner('Buscando marcas...'):
                    try:
                        results = search_marks(name, clase)
                        st.session_state.search_results = results
                        if results:
                            st.success(f"Se encontraron {len(results)} resultados!")
                        else:
                            st.info("No se encontraron resultados.")
                    except Exception as e:
                        st.error(f"Error durante la búsqueda: {str(e)}")
            else:
                st.warning("Por favor ingrese tanto el nombre como la clase de la marca.")

with tab2:
    st.markdown("""
        <div style='background-color: #f8f9fa; padding: 1rem; border-radius: 5px; margin-bottom: 2rem;'>
            <h3 style='color: #2c3e50;'>Clasificación Niza</h3>
            <p>Describe las actividades de tu empresa para encontrar la clase Niza adecuada.</p>
        </div>
    """, unsafe_allow_html=True)
    
    descripcion = st.text_area('Descripción de la marca:', 
                             placeholder='Ejemplo: Daat es una empresa que brinda servicios de Inteligencia Artificial.',
                             height=150)
    if st.button('🏷️ Clasificar'):
        with st.spinner('Analizando descripción...'):
            texto_clase = classify_brand(descripcion)
            st.success("Clasificación completada!")
            st.info(f"Clase sugerida basada en la descripción:\n\n{texto_clase}")

# Results section
if st.session_state.search_results:
    st.markdown("""
        <div style='background-color: #f8f9fa; padding: 1rem; border-radius: 5px; margin: 2rem 0;'>
            <h3 style='color: #2c3e50;'>Resultados de la búsqueda</h3>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("selection_form"):
        selected_items = []
        for index, result in enumerate(st.session_state.search_results):
            with st.expander(f"📋 {result['Denominación']}", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Número de Expediente:** {result['Número de expediente']}")
                    st.markdown(f"**Clase:** {result['Clase']}")
                    st.markdown(f"**Número de registro:** {result['Número de registro']}")
                with col2:
                    st.markdown(f"**Titular:** {result['Titular']}")
                    st.markdown(f"**Fecha de vigencia:** {result['Fecha de vigencia']}")
                    st.markdown(f"**Descripción:** {result['Descripción']}")
                
                if result["Path"]:
                    st.image(result["Path"], width=300, caption="Imagen de la marca")
                
                key = f"{result['Denominación']}_{index}"
                is_selected = st.checkbox("Seleccionar para análisis", key=key, 
                                       value=key in st.session_state.selected_items)
                if is_selected:
                    selected_items.append(result)

        col1, col2 = st.columns(2)
        with col1:
            submitted_similarity = st.form_submit_button("🔄 Generar Similitud")
        with col2:
            submitted_report = st.form_submit_button("📄 Generar Reporte")

        if submitted_similarity and len(selected_items) > 0 and 'path' in st.session_state:
            st.session_state.similarity_results = []
            with st.spinner('Analizando similitudes...'):
                # Compare each selected item with the user input
                for selected_item in selected_items:
                    # Semantic similarity analysis with user input name
                    semantic_result = similitud_semanticas(
                        name,  # User input name
                        selected_item['Denominación']
                    )
                    
                    # Image similarity analysis with user uploaded image
                    image_result = "No disponible"
                    if selected_item["Path"] and st.session_state.path:
                        try:
                            image_result = analyze_image(
                                encode_image(selected_item["Path"])
                            )
                        except Exception as e:
                            st.error(f"Error in image analysis: {str(e)}")
                            image_result = f"Error en análisis de imagen: {str(e)}"
                    
                    st.session_state.similarity_results.append({
                        'Marca 1': name,  # Changed from 'Marca Original'
                        'Marca 2': selected_item['Denominación'],  # Changed from 'Marca Comparada'
                        'Análisis Semántico': semantic_result,
                        'Análisis Visual': image_result
                    })

    # Move the results display outside the form
    if st.session_state.similarity_results:
        st.markdown("""
            <div style='background-color: #f8f9fa; padding: 1rem; border-radius: 5px; margin: 2rem 0;'>
                <h3 style='color: #2c3e50;'>Resultados del Análisis de Similitud</h3>
            </div>
        """, unsafe_allow_html=True)

        for result in st.session_state.similarity_results:
            # Header container
            st.markdown(f"""
                <div style='background-color: #f0f2f6; padding: 1.5rem; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 1rem;'>
                    <h4 style='color: #000000; margin-bottom: 1rem; font-weight: bold;'>Comparación: {result['Marca 1']} vs {result['Marca 2']}</h4>
                </div>
            """, unsafe_allow_html=True)
            
            # Semantic Analysis container with proper markdown formatting
            with st.container():
                st.markdown("### Análisis Semántico")
                semantic_text = result['Análisis Semántico']
                # Replace double asterisks with markdown headers
                semantic_text = semantic_text.replace("**Descripción de las similitud fonética:**", "#### Descripción de las similitud fonética")
                semantic_text = semantic_text.replace("**Score Fonético:**", "#### Score Fonético")
                semantic_text = semantic_text.replace("**¿Cómo se pronuncia ambos?:**", "#### ¿Cómo se pronuncia ambos?")
                semantic_text = semantic_text.replace("**Descripción de las similitud semántica:**", "#### Descripción de las similitud semántica")
                semantic_text = semantic_text.replace("**Score Semántico:**", "#### Score Semántico")
                semantic_text = semantic_text.replace("**¿Qué significan ambos?:**", "#### ¿Qué significan ambos?")
                st.markdown(semantic_text)
            
            # Visual Analysis container
            st.markdown(f"""
                <div style='background-color: #f0f2f6; padding: 1.5rem; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 1rem;'>
                    <h5 style='color: #000000; font-weight: bold;'>Análisis Visual</h5>
                    <pre style='background-color: #ffffff; padding: 1rem; border-radius: 5px; white-space: pre-wrap; color: #000000; border: 1px solid #e1e4e8;'>{result['Análisis Visual']}</pre>
                </div>
            """, unsafe_allow_html=True)

# Download button styling
if 'doc_io' in st.session_state and st.session_state.doc_io:
    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button(
        label="⬇️ Descargar Análisis",
        data=st.session_state.doc_io,
        file_name='Análisis_de_Marcas.docx',
        mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )
