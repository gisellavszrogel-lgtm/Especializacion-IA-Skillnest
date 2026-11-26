# Decision de personalizacion

## 1. El problema
En el registro de inventario por voz para un negocio de barrio, el modelo no siempre entrega en un formato consistente la acción, el producto, la cantidad y la unidad a partir de frases habladas. De 20 respuestas revisadas, 3 (15 %) fallaron el formato esperado cuando la frase incluía más de un producto, devolviendo una lista o dos objetos JSON en lugar de un único objeto JSON.

## 2. Resultado del metodo de decision
- PEFT: 3 puntos
- RAG: 2 puntos
- Fine-tuning completo: 1 puntos

La técnica mejor puntuada es **PEFT**.

## 3. Tecnica elegida y por que
Elijo **PEFT** como referencia de personalización porque el fallo es de consistencia en el formato de salida (no de consultar documentos que cambien cada mes), descarto **Fine-tuning completo** por su alto costo de cómputo y tiempo, y mantengo el objetivo inicial del MVP con gasto $0 usando la API gratuita de Gemini y sin base vectorial ni Supabase por ahora, dejando abierta la posibilidad de incorporar una base de datos (como Supabase) más adelante para persistir el inventario, ya que aún no hemos visto una clase específica sobre ese almacenamiento.

## 4. Que necesitarias para ejecutarla
Hoy tengo 0 ejemplos etiquetados de este caso y me faltan 200 ejemplos para llegar al umbral de 200 ejemplos (y luego revisar 20 al azar para verificar 0 etiquetas contradictorias). Etiquetar y revisar 200 ejemplos a 5 minutos por ejemplo tomaría aproximadamente 16,7 horas (1.000 minutos), además de definir más adelante cómo persistir el inventario si se incorpora una base de datos como Supabase.