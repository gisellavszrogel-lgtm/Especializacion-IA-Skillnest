from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import (RunnableBranch, RunnablePassthrough) #bifurcaciones/branches/ramificaciones -> clase de lang.chain

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
    (lambda x: x ['clasificacion'] == 'queja', cadena_queja),
    (lambda x: x['clasificacion'] == 'sugerencia', cadena_sugerencia),
    cadena_pregunta
)


#ejecutar paso_clasificacion, obtener la respuesta como clasificacion y también conservar el mensaje original
cadena_con_enrutamiento = (
    RunnablePassthrough.assign(clasificacion=paso_clasificación) #
    | bifurcacion
)

resultado = cadena_con_enrutamiento.invoke(
    {'mensaje': 'Deberían tener más agentes disponibles'}
)

print(resultado)