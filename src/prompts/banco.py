
BANCO_DE_PROMPTS = [
    {
        "nombre": "armar_ficha_shopify",
        "system_instruction": (
            "Eres un especialista en catálogo e-commerce para Shopify. "
            "Tu tarea es recibir información cruda de un producto entrante y estructurar "
            "su título comercial, descripción limpia en formato HTML básico y su categoría principal. "
            "Responde estrictamente bajo el esquema JSON solicitado, sin markdown adicional."
        ),
        "ejemplo_usuario": (
            "Llegó polerón hoodie unisex color grafito, 100% algodón orgánico, "
            "ideal para invierno, cierre metálico, marca Kerna Urban."
        ),
        "claves_esperadas": ["title", "body_html", "product_type", "vendor"],
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "title": {"type": "STRING"},
                "body_html": {"type": "STRING"},
                "product_type": {"type": "STRING"},
                "vendor": {"type": "STRING"}
            },
            "required": ["title", "body_html", "product_type", "vendor"]
        }
    },
    {
        "nombre": "extractor_variantes_inventario",
        "system_instruction": (
            "Eres un auditor de inventario y bodega para Shopify. "
            "Tu tarea es recibir un texto desestructurado con cantidades, tallas o colores y "
            "desglosarlo en una lista estricta de variantes con SKU sugerido, precio unitario y cantidad física. "
            "Todos los números de stock y precio deben ser enteros o decimales válidos."
        ),
        "ejemplo_usuario": (
            "Tenemos 10 unidades en talla S a 29990, 15 en talla M al mismo precio y 5 en L. "
            "Código base sugerido: POL-GRAF."
        ),
        "claves_esperadas": ["variants"],
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "variants": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "option1_value": {"type": "STRING"},
                            "sku": {"type": "STRING"},
                            "price": {"type": "NUMBER"},
                            "inventory_quantity": {"type": "INTEGER"}
                        },
                        "required": ["option1_value", "sku", "price", "inventory_quantity"]
                    }
                }
            },
            "required": ["variants"]
        }
    },
    {
        "nombre": "generador_tags_seo",
        "system_instruction": (
            "Eres un consultor SEO técnico para tiendas Shopify. "
            "Recibes la información de un producto y debes generar una lista de tags separados por coma "
            "para filtrar colecciones, un handle (slug amigable para URL en minúsculas y separado por guiones) "
            "y una meta descripción atractiva de máximo 150 caracteres."
        ),
        "ejemplo_usuario": (
            "Polerón Hoodie Algodón Orgánico Grafito para hombre y mujer, temporada frío."
        ),
        "claves_esperadas": ["tags", "handle", "meta_description"],
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "tags": {
                    "type": "ARRAY",
                    "items": {"type": "STRING"}
                },
                "handle": {"type": "STRING"},
                "meta_description": {"type": "STRING"}
            },
            "required": ["tags", "handle", "meta_description"]
        }
    },
    {
    "nombre": "extraer_fila_csv_shopify",
    "system_instruction": (
        "Eres un procesador de datos para e-commerce. Tu tarea es recibir una fila o texto "
        "desordenado de un producto o inventario de proveedor y estructurarlo exactamente en los campos "
        "requeridos para crear el producto en Shopify. Si falta el SKU, genera uno coherente en mayúsculas."
    ),
    "ejemplo_usuario": (
        "Polerón canguro franela gris talla L, 25 unidades en bodega central, costo unitario 19990. Marca Kerna."
    ),
    "claves_esperadas": ["title", "sku", "price", "quantity", "vendor"],
    "response_schema": {
        "type": "OBJECT",
        "properties": {
            "title": {"type": "STRING"},
            "sku": {"type": "STRING"},
            "price": {"type": "NUMBER"},
            "quantity": {"type": "INTEGER"},
            "vendor": {"type": "STRING"},
        },
        "required": ["title", "sku", "price", "quantity", "vendor"],
    },
}
]