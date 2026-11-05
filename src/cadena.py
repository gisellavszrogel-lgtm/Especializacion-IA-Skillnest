from dotenv import load_dotenv #lectura de variables de entorno
import os
from langchain_google_genai import ChatGoogleGenerativeAI #crea el modelo al que me quiero conectar
from langchain_core.prompts import PromptTemplate #importa la clase para crear una plantilla -> prompt dinámico
from langchain_core.output_parsers import StrOutputParser #parsea la respuesta y la transforma en un solo texto, sin datos innecesarios
from langchain_core.prompts import ChatPromptTemplate #plantilla que incluye el rol del sistema e instrucción

load_dotenv() #carga las variables de entorno

modelo = ChatGoogleGenerativeAI(model='gemini-3.5-flash-lite')
#respuesta = modelo.invoke('Qué es un token?')
#print(respuesta.content)

plantilla = PromptTemplate.from_template(
    'Explica el concepto de {tema} en un párrafo, para alguien que recién comienza en {area}.'
)

#prompt = plantilla.invoke(
#    {'tema': 'tokenización', 'area': 'procesamiento de texto'}
#)

#print(prompt.text)

cadena_simple = plantilla | modelo | StrOutputParser()
respuesta = cadena_simple.invoke(
    {'tema': 'embeddings', 'area': 'búsqueda semántica'}
)

print(respuesta)

plantilla_conrol = ChatPromptTemplate.from_messages([
    ('system', 'Eres un experto en el área correspondiente, vas a responder siempre con texto simple para el usuario.')
    ('human', 'Explica el concepto de {tema} en un párrado, para alguien que recién comienza en el {área}')
])