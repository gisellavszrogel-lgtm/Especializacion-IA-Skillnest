import os
import requests
from dotenv import load_dotenv

load_dotenv()

#variables constantes
MODELO = 'gemini-3.6-flash'
URL_BASE = 'https://generativelanguage.googleapis.com/v1beta/models/'
API_KEY = os.getenv('GEMINI_API_KEY')

#función para crear la solicitud
def armar_peticion(pregunta):
    url = f'{URL_BASE}{MODELO}:generateContent?key={API_KEY}' #url = https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key=MI API KEY'
    body = {
        'contents':
            [{'parts': [{'text': pregunta}]}]
      }
    return url, body

#función envía la petición
def enviar_peticion(url, body):
    respuesta = requests.post(url, json=body)
    return respuesta.json()

#función procesa y extrae dato
def extraer_texto(datos):
    return datos ['candidates'][0]['content']['parts'][0]['text']

def obtener_dato_de_prueba(pregunta): #pregunta= 'Confirma la conexión'
    url, body = armar_peticion(pregunta) #obtiene url y body
    datos = enviar_peticion(url, body)
    return extraer_texto(datos)

print(obtener_dato_de_prueba('Confirma en una frase corta que esta conexión funciona'))