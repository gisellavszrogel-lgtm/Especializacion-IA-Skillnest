# Límites de la métrica de evaluación

## Qué mide
La métrica calcula la precisión, cobertura y valor F1 a partir del solapamiento exacto de tokens (palabras individuales) entre la respuesta de referencia y la respuesta generada por el asistente de inventario, utilizando una bolsa de palabras (`Counter`).

## Modos de falla conocidos
- **Alucinación de datos numéricos con F1 alto (Falso Positivo):** La métrica premia oraciones que copian la estructura sintáctica de la referencia aunque el dato central sea falso. En la consulta *"¿Cuál es el monto mínimo de compra que exige el proveedor de cecinas?"*, la métrica arrojó un F1 alto de 0.58 a pesar de que el modelo respondió cincuenta mil pesos en lugar de los veinticinco mil reales.
- **Invención de fechas en respuestas estructuradas (Falso Positivo):** En consultas de calendario como *"¿Para qué fecha está programada la entrega de las bebidas?"*, el modelo obtuvo un F1 de 0.58 calcando la frase inicial pero inventando una fecha ('quince de noviembre' en vez de 'este viernes temprano').
- **Penalización por lenguaje formal o sinónimos (Falso Negativo):** Cuando el modelo responde correctamente pero utiliza términos más técnicos, el F1 se desploma. En *"¿Qué hago con el papel de la guía de despacho que me firmó el chofer?"*, la respuesta fue correcta pero obtuvo apenas F1=0.21 por usar términos como 'recepción conforme' y 'gestionar la facturación'.
- **Evasivas del modelo por falta de contexto RAG (Falsos Negativos):** Al no estar conectado aún a una base de datos local en vivo, el modelo responde como asistente genérico deslindando responsabilidad (ej. *"carezco de acceso a tu despensa"* o *"depende de la ruta de su distribuidor"*), obteniendo F1 mínimos de 0.15.

## Muestra revisada
Se revisó a mano una muestra de 10 casos extraídos del lote de 20 registros guardados en `resultados_metricas.json`:
- **5 casos con F1 más bajo (0.15 a 0.21):** Consultas sobre días de visita de CCU, stock de azúcar, pedido de huevos, reposición de harina y archivo de guías de despacho.
- **5 casos con F1 más alto (0.48 a 0.58):** Consultas sobre contacto de panadería, fecha de compra de galletas, momento de registro en estanterías, mínimo de compra de cecinas y fecha de entrega de bebidas.

## Recomendación de uso
- **Cuándo confiar en el número solo:** Únicamente como prueba de humo (*smoke test*) automatizada en despliegues para asegurar que el pipeline procesa texto, no arroja respuestas vacías y mantiene un vocabulario general cercano al dominio de almacén.
- **Cuándo revisar a mano:** Es obligatorio revisar manualmente siempre que se evalúen datos críticos para el almacenero (montos de compra, días de reparto de proveedores, cantidades de stock mínimo y fechas). Un F1 superior a 0.55 no garantiza que el número entregado al usuario sea verídico, y un F1 inferior a 0.25 no implica necesariamente una mala respuesta si el asistente utilizó un sinónimo más claro o pausado para una persona mayor.