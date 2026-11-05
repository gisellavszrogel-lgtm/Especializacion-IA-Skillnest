from dotenv import load_dotenv #Carga variables de entorno ocultas desde archivo .env
from langchain_google_genai import ChatGoogleGenerativeAI #Conector LangChain para modelos de gemini
from langchain_core.prompts import PromptTemplate #Permite crear textos dinámicos entre llaves {mensaje}
from langchain_core.output_parsers import StrOutputParser #extrae texto plano de la respuesta
from langchain_core.runnables import (RunnableBranch, RunnablePassthrough, RunnableLambda) #bifurcaciones/branches/ramificaciones -> clase de lang.chain

import logging #generar un archivo log con los errores que se presenten

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s', #2026-11-04 16:40 [WARNING] main: no se pudo ejecutar x
    datefmt="%Y-%m-%d %H:%M:%S",
    filename='error.log',
    filemode='a', #agrega al final del archivo la nueva línea sin eliminar los anteriores registrados
    encoding='utf-8',
    force=True
)
logger = logging.getLogger(__name__)

load_dotenv()

modelo = ChatGoogleGenerativeAI(model='gemini-3.1-flash-lite')


plantilla_clasificacion = PromptTemplate.from_template(
    'Clasifica el siguiente mensaje de soporte en una sola palabra:'
    'pregunta, queja o sugerencia. Responde solo con esa palabra. \n\n {mensaje}'
)

paso_clasificación = (
    plantilla_clasificacion
    | modelo
    | StrOutputParser()
    | (lambda texto: texto.strip().lower())
)

""" mensaje_prueba = 'mi telefono no está funcionando'

clasificacion = paso_clasificación.invoke(
    {'mensaje': mensaje_prueba}
)

print(clasificacion) """

cadena_pregunta = (
    PromptTemplate.from_template('Responde esta pregunta técnica con precisión: \n\n {mensaje}')
    | modelo
    | StrOutputParser()
)

cadena_queja = (
    PromptTemplate.from_template('Responde esta queja con empatía reconociendo el problema antes de ofrecer una solución: \n\n {mensaje}')
    | modelo
    | StrOutputParser()
)

cadena_sugerencia = (
    PromptTemplate.from_template('Agradece esta sugerencia y explica como se evaluará dentro del producto: \n\n {mensaje}')
    | modelo
    | StrOutputParser()
)

""" caminos = RunnableBranch(   #cada condicion debe ser una función, suele ser un lamda
    (condicion_1, rama_1),
    (condicion_2, rama_2),
    (condicion_3, rama 3),
    rama_por_defecto
) """


#x= {'clasificacion': 'queja', 'mensaje': 'Mi teléfono no funciona'}
bifurcacion = RunnableBranch(
    (lambda x: x['clasificacion'] == 'queja', cadena_queja),
    (lambda x: x['clasificacion'] == 'sugerencia', cadena_sugerencia),
    cadena_pregunta
)

cadena_con_enrutamiento = (
    RunnablePassthrough.assign(clasificacion=paso_clasificación)
    | bifurcacion
)

#fallback: cadena de respaldo. Caputa las caídas de mi LLm (RateLimitError, 401, APIConenectionError, respuestas vacías
def fallback_con_log(x):
    logger.warning("Cadena principal falló. Activando respuesta genérica, Error: %s", x.get("error"))
    return "Gracias por tu mensaje. Un miembro de nuestro equipo te va a responder pronto."
 
respuesta_generica = RunnableLambda(
    fallback_con_log
)

cadena_robusta = cadena_con_enrutamiento.with_fallbacks([respuesta_generica], exception_key='error')

def procesar_mensaje_seguro(cadena, mensaje):
    try:
        return cadena.invoke({"mensaje": mensaje})
    except Exception as error:
        logger.error("Error procesando mensaje: %s", error)
        return "No pudimos procesar tu mensaje en este momento. Intenta de nuevo más tarde"

if __name__ == "__main__": #Solamente ejecuta el siguiente bloque de código si la ejecución es directa del archivo. NO EJECUTES si es import
    mensaje = "Llevo varios días sin poder entrar a mi cuenta."
    print(procesar_mensaje_seguro(cadena_robusta, mensaje))
