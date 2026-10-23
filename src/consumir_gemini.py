import os
import requests
from dotenv import load_dotenv
import time

import json
import re

load_dotenv()

#variables constantes
MODELO = 'gemini-3.6-flash'
URL_BASE = 'https://generativelanguage.googleapis.com/v1beta/models/'
API_KEY = os.getenv('GEMINI_API_KEY')


#función para crear la solicitud
def armar_peticion(modelo, pregunta, system_instruction, response_schema=None):
    if not pregunta:
        raise ValueError('La pregunta no puede estar vacía')
    url = f'{URL_BASE}{modelo}:generateContent?key={API_KEY}' #url = https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key=MI API KEY'
    body = {
        'systemInstruction':{
            'parts': [ 
                {'text': system_instruction}
            ]
        },
        'contents':
            [{'parts': [{'text': pregunta}]}]
        }
    if response_schema is not None:
            body['generationConfig'] = {
                'responseMimeType': 'application/json',  # Con 'm' y con la coma al final
                'responseSchema': response_schema
            }
    return url, body

#función envía la petición
def enviar_peticion(url, body):
    try:
        respuesta = requests.post(url, json=body, timeout=60)
    except requests.exceptions.ConnectionError:
        raise RuntimeError('No se pudo conectar con el servicio. Intenta de nuevos en unos minutos')
    except requests.exceptions.Timeout:
        raise RuntimeError('Se agotó el tiempo, intenta de nuevo en unos momentos.')
    
    if respuesta.status_code != 200:
        raise RuntimeError(f'Error en la petición. Status Code: {respuesta.status_code}')
    
    try:
        return respuesta.json()
    except requests.exceptions.JSONDecodeError:
        raise RuntimeError('La respuesta del servicio no llegó en el formato esperado')

#función procesa y extrae dato
def extraer_texto(datos): #gemini
    try:
        return datos ['candidates'][0]['content']['parts'][0]['text']
    except(KeyError, IndexError): #error de llave o clave, se da cuando un diccionario no tiene un dato específico
        raise RuntimeError('La respuesta no recibe un texto generado en el lugar definido')
    
def obtener_dato_de_prueba(pregunta): #pregunta= 'Confirma la conexión'

    response_schema = {
        'type': 'OBJECT',
        'properties': {
            "title": {"type": "STRING"},
            "sku": {"type": "STRING"},
            "price": {"type": "NUMBER"},
            "quantity": {"type": "INTEGER"},
            "vendor": {"type": "STRING"},
        },
        "required": ["title", "sku", "price", "quantity", "vendor"],
    }

    system_instruction = 'Eres un procesador de catálogo de e-commerce. Extrae la información'
    "de la entrada respetando estrictamente el esquema JSON."
    url, body = armar_peticion(MODELO, pregunta, system_instruction, response_schema) #obtiene url y body
    
    inicio = time.perf_counter() #empezar el contador
    datos = enviar_peticion(url, body) 
    fin = time.perf_counter() #termina el contador

    latencia = fin - inicio
    print(f'Latencia: {latencia:.2f} segundos')

    costo = calcular_costo(datos, 0.00000075, 0.00000375)
    print(f'Costo de la petición: ${costo:.6f} USD')

    texto_crudo = extraer_texto(datos)
    claves_a_revisar = ["title", "sku", "price", "quantity", "vendor"]
    datos_limpios = parsear_respuesta_json(texto_crudo, claves_a_revisar)

    return datos_limpios

def calcular_costo(datos, precio_entrada, precio_salida): #def calcular_costos(datos: dict, precio_entrada: float, precio_salida: float) -> float:
    #datos = {dict... 'usageMetada'}
    uso = datos['usageMetadata']
    tokens_entrada = uso['promptTokenCount']
    tokens_salida = uso['candidatesTokenCount']
    tokens_razonamiento = uso.get('thoughtsTokenCount', 0) #revisar si existe o no, si no existe ingresar '0'
    costo = (tokens_entrada * precio_entrada) + ((tokens_salida + tokens_razonamiento) * precio_salida)
    return costo 

def parsear_respuesta_json(texto, claves_requeridas=None):
    texto_limpio = texto.strip()
    texto_limpio = re.sub(r"^```(?:json)?\s*", "", texto_limpio)
    texto_limpio = re.sub(r"\s*```$", "", texto_limpio)

    try:
        datos = json.loads(texto_limpio)
    except json.JSONDecodeError:
        raise ValueError("La respuesta del modelo no es JSON válido")
    
    if claves_requeridas:
        faltantes = [clave for clave in claves_requeridas if clave not in datos]
        if faltantes:
            raise ValueError("La respuesta no tiene la estructura esperada.")
    return datos

if __name__ == "__main__": 
    try:
        print(
            obtener_dato_de_prueba(
                "Hola Eva, necesito que me ayudes a registrar una factura"
            )
        )
    except (ValueError, RuntimeError) as error:
        print("No se pudo completar la operación: ", error)