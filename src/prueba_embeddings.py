from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

# Usamos el nombre oficial corregido
embedding = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

vector = []
vector2 = []

try:
  vector = embedding.embed_query("Hola, cómo estás?")
  vector2 = embedding.embed_query("Qué tal, como va todo?")

  print("Dimensión:", len(vector))
  print("Primeros valores:", vector[:5])
  print("*****")
  print("Dimensión:", len(vector2))
  print("Primeros valores:", vector2[:5])

except Exception as error:
  mensaje = str(error)
  if "429" in mensaje or "RESOURCE_EXHAUSTED" in mensaje:
    print("Límite de peticiones alcanzado.")
  else:
    print("No se pudo generar el embedding:", mensaje)

#inicializando el vector store
vector_store = Chroma(
  collection_name='ejemplo_rag',
  embedding_function=embedding,
  persist_directory='./chroma_db'
)

#agrega un fragmento de texto o chunk a mi vector_store
vector_store.add_texts(['El cliente realiza hasta tres reintentos en caso de error de red.'])

datos = vector_store.get() #obtengo mi colección completa
print('IDs almacenados: ', datos['ids'])
print('Textos guardados: ', datos['documents'])