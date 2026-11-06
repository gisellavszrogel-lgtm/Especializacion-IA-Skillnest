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


# Clasificador: detecta qué quiere hacer el almacenero con su mensaje de voz o texto
plantilla_clasificacion = PromptTemplate.from_template(
    'Clasifica el siguiente mensaje de voz de un almacenero en una sola palabra: '
    'movimiento, consulta o alerta. Responde solo con esa palabra.\n\n{mensaje}'
)

paso_clasificación = (
    plantilla_clasificacion
    | modelo
    | StrOutputParser()
    | (lambda texto: texto.strip().lower())
)

""" mensaje_prueba = 'llegaron 5 paquetes de fideos'

clasificacion = paso_clasificación.invoke(
    {'mensaje': mensaje_prueba}
)

print(clasificacion) """

# Camino 1: Consultas de inventario (cuánto queda, precios, ubicación)
cadena_consulta = (
    PromptTemplate.from_template(
        'Eres el asistente de un negocio de barrio. Responde claro, breve y amigable a esta consulta de inventario:\n\n{mensaje}'
    )
    | modelo
    | StrOutputParser()
)

# Camino 2: Alertas e incidencias (productos vencidos, quejas de proveedores, faltantes)
cadena_alerta = (
    PromptTemplate.from_template(
        'Eres un asistente de negocio. Registra esta alerta o problema con calma, resumiendo el problema para resolverlo:\n\n{mensaje}'
    )
    | modelo
    | StrOutputParser()
)

# Camino 3: Movimiento de stock (entradas o salidas de mercadería)
cadena_movimiento = (
    PromptTemplate.from_template(
        'Identifica el producto y la cantidad que entra o sale de bodega en este mensaje, confirmando el registro de forma muy sencilla:\n\n{mensaje}'
    )
    | modelo
    | StrOutputParser()
)

""" caminos = RunnableBranch(   #cada condicion debe ser una función, suele ser un lamda
    (condicion_1, rama_1),
    (condicion_2, rama_2),
    (condicion_3, rama 3),
    rama_por_defecto
) """

# Enrutador: si avisa un problema va a alerta, si avisa mercadería va a movimiento, si pregunta va a consulta
bifurcacion = RunnableBranch(
    (lambda x: x['clasificacion'] == 'alerta', cadena_alerta),
    (lambda x: x['clasificacion'] == 'movimiento', cadena_movimiento),
    cadena_consulta
)

cadena_con_enrutamiento = (
    RunnablePassthrough.assign(clasificacion=paso_clasificación)
    | bifurcacion
)

#fallback: cadena de respaldo. Captura las caídas de mi LLm (RateLimitError, 401, APIConenectionError, respuestas vacías
def fallback_con_log(x):
    logger.warning("Cadena principal falló. Activando respuesta genérica, Error: %s", x.get("error"))
    return "Disculpa, no entendí bien el mensaje. Por favor repítemelo o anótalo directamente en la lista."

respuesta_generica = RunnableLambda(
    fallback_con_log
)

cadena_robusta = cadena_con_enrutamiento.with_fallbacks([respuesta_generica], exception_key='error')

def procesar_mensaje_seguro(cadena, mensaje):
    try:
        return cadena.invoke({"mensaje": mensaje})
    except Exception as error:
        logger.error("Error procesando mensaje: %s", error)
        return "Tuvimos un problema técnico momentáneo. Intenta de nuevo en unos segundos."


def construir_cadena_alerta_segura(cadena):
    """Protege la rama de alertas con un salvavidas si falla el modelo."""
    return cadena.with_fallbacks([respuesta_generica])

def construir_cadena_con_enrutamiento(paso_clasificacion=paso_clasificación):
    """Permite armar la cadena inyectando una clasificación normal o de prueba."""
    return (
        RunnablePassthrough.assign(clasificacion=paso_clasificacion)
        | bifurcacion
    )

if __name__ == "__main__": #Solamente ejecuta el siguiente bloque de código si la ejecución es directa del archivo. NO EJECUTES si es import
    mensaje = "Anota que me llegaron 12 tarros de café y se me rompió una bolsa de arroz."
    print(procesar_mensaje_seguro(cadena_robusta, mensaje))