from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import boto3
import json
import os
from typing import List, Optional
import logging
from config import AWS_REGION, BEDROCK_MODEL_ID, KNOWLEDGE_BASE_ID, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar cliente de Bedrock
bedrock_agent_runtime = boto3.client(
    'bedrock-agent-runtime',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

# Inicializar FastAPI
app = FastAPI(
    title="STELLART HOMES API",
    description="API para el portal inmobiliario con integración a Amazon Bedrock",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    sources: Optional[List[dict]] = None

class Property(BaseModel):
    id: int
    title: str
    price: int
    location: str
    type: str
    bedrooms: int
    bathrooms: int
    area: int
    description: str
    features: List[str]
    images: List[str]
    status: str
    # Campos adicionales sincronizados con documentos
    price_per_sqm: Optional[int] = None
    year_built: Optional[int] = None
    energy_rating: Optional[str] = None
    amenities: Optional[List[str]] = None
    rental_yield: Optional[str] = None
    price_trend: Optional[str] = None
    community_fees: Optional[int] = None
    property_tax: Optional[int] = None
    terrace_area: Optional[int] = None
    renovation_year: Optional[int] = None

class PropertyResponse(BaseModel):
    properties: List[Property]

# Datos de ejemplo para propiedades - Sincronizados con documentos detallados
SAMPLE_PROPERTIES = [
    {
        "id": 1,
        "title": "Casa Moderna en Chamberí",
        "price": 650000,
        "location": "Chamberí, Madrid",
        "type": "Casa",
        "bedrooms": 4,
        "bathrooms": 3,
        "area": 120,
        "price_per_sqm": 5417,
        "year_built": 2018,
        "energy_rating": "B",
        "description": "Casa moderna de 4 dormitorios en el prestigioso barrio de Chamberí. Completamente reformada en 2018, cuenta con diseño contemporáneo y acabados de alta calidad.",
        "features": [
            "Jardín privado de 50m²",
            "Terraza de 20m²", 
            "Cochera para 2 vehículos",
            "Suelo de parquet de roble",
            "Cocina equipada con electrodomésticos Bosch",
            "Sistema de calefacción por suelo radiante",
            "Aire acondicionado en todas las habitaciones",
            "Alarmas de seguridad",
            "Ascensor privado"
        ],
        "amenities": [
            "Cerca del metro (Líneas 1, 2, 6, 7)",
            "Colegios privados en 500m",
            "Hospitales en 1km",
            "Zona comercial completa",
            "Parques cercanos (Retiro a 15 min caminando)"
        ],
        "rental_yield": "4.2%",
        "price_trend": "+8.5% anual",
        "community_fees": 120,
        "property_tax": 1800,
        "images": ["/images/casa1.jpg"],
        "status": "disponible",
        "createdAt": datetime(2024, 1, 15),
        "updatedAt": datetime(2024, 1, 15),
    },
    {
        "id": 2,
        "title": "Ático con Terraza en Eixample",
        "price": 750000,
        "location": "Eixample, Barcelona",
        "type": "Ático",
        "bedrooms": 3,
        "bathrooms": 2,
        "area": 100,
        "terrace_area": 80,
        "price_per_sqm": 7500,
        "year_built": 2020,
        "energy_rating": "A",
        "description": "Ático de lujo en el corazón del Eixample barcelonés. Obra nueva con terraza privada de 80m² y vistas panorámicas de la ciudad.",
        "features": [
            "Terraza privada de 80m²",
            "Piscina en la azotea comunitaria",
            "Gimnasio privado",
            "Suelo de mármol",
            "Cocina de diseño con isla central",
            "Domótica completa",
            "Parking subterráneo",
            "Portero 24h",
            "Zona de lavandería"
        ],
        "amenities": [
            "Metro Passeig de Gràcia (2 min)",
            "Paseo de Gracia (5 min)",
            "Sagrada Familia (10 min)",
            "Hospitales privados cercanos",
            "Restaurantes Michelin en la zona"
        ],
        "rental_yield": "3.5%",
        "price_trend": "+12% anual",
        "community_fees": 280,
        "property_tax": 2200,
        "images": ["/images/casa2.jpg"],
        "status": "disponible",
        "createdAt": datetime(2024, 1, 10),
        "updatedAt": datetime(2024, 1, 10),
    },
    {
        "id": 3,
        "title": "Casa de Playa en Malvarrosa",
        "price": 420000,
        "location": "Malvarrosa, Valencia",
        "type": "Casa",
        "bedrooms": 3,
        "bathrooms": 2,
        "area": 120,
        "price_per_sqm": 3500,
        "year_built": 2015,
        "energy_rating": "C",
        "description": "Casa de playa a 200 metros del mar en la famosa playa de Malvarrosa. Ideal para residencia permanente o segunda vivienda.",
        "features": [
            "Terraza con vistas al mar",
            "Jardín de 60m²",
            "Cochera cubierta",
            "Suelo de gres porcelánico",
            "Cocina abierta al salón",
            "Aire acondicionado",
            "Calefacción individual",
            "Persianas automáticas"
        ],
        "amenities": [
            "Playa de Malvarrosa (200m)",
            "Paseo marítimo (100m)",
            "Restaurantes de paella",
            "Transporte público",
            "Centro de Valencia (15 min en metro)"
        ],
        "rental_yield": "5.8%",
        "price_trend": "+7% anual",
        "community_fees": 85,
        "property_tax": 1200,
        "images": ["/images/casa3.jpg"],
        "status": "disponible",
        "createdAt": datetime(2024, 1, 5),
        "updatedAt": datetime(2024, 1, 5),
    },
    {
        "id": 4,
        "title": "Casa Histórica en Triana",
        "price": 380000,
        "location": "Triana, Sevilla",
        "type": "Casa",
        "bedrooms": 3,
        "bathrooms": 2,
        "area": 120,
        "price_per_sqm": 3167,
        "year_built": 1890,
        "renovation_year": 2020,
        "energy_rating": "D",
        "description": "Casa histórica del siglo XIX completamente restaurada en el barrio flamenco de Triana. Mantiene la arquitectura original con comodidades modernas.",
        "features": [
            "Patio andaluz de 40m²",
            "Azulejos originales restaurados",
            "Vigas de madera vistas",
            "Suelo de barro cocido",
            "Cocina moderna integrada",
            "Climatización eficiente",
            "Ascensor privado",
            "Almacén en sótano"
        ],
        "amenities": [
            "Centro histórico (5 min caminando)",
            "Mercado de Triana (2 min)",
            "Metro (5 min)",
            "Zona de tapas tradicionales",
            "Catedral y Giralda (10 min)"
        ],
        "rental_yield": "4.8%",
        "price_trend": "+9% anual",
        "community_fees": 95,
        "property_tax": 1100,
        "images": ["/images/casa4.jpg"],
        "status": "disponible",
        "createdAt": datetime(2024, 1, 20),
        "updatedAt": datetime(2024, 1, 20),
    },
    {
        "id": 5,
        "title": "Villa de Lujo en El Limonar",
        "price": 850000,
        "location": "El Limonar, Málaga",
        "type": "Villa",
        "bedrooms": 5,
        "bathrooms": 4,
        "area": 200,
        "price_per_sqm": 4250,
        "year_built": 2021,
        "energy_rating": "A+",
        "description": "Villa de lujo de obra nueva en la exclusiva zona de El Limonar. Diseño contemporáneo con vistas al mar y montaña.",
        "features": [
            "Piscina privada de 8x4m",
            "Jardín de 300m²",
            "Terraza de 50m²",
            "Gimnasio privado",
            "Bodega climatizada",
            "Cocina de chef con isla",
            "Sistema domótico completo",
            "Parking para 4 vehículos",
            "Seguridad perimetral"
        ],
        "amenities": [
            "Playa de La Malagueta (10 min)",
            "Centro histórico (15 min)",
            "Aeropuerto (20 min)",
            "Golf (5 min)",
            "Colegios internacionales"
        ],
        "rental_yield": "4.0%",
        "price_trend": "+18% anual",
        "community_fees": 0,
        "property_tax": 2800,
        "images": ["/images/casa5.jpg"],
        "status": "disponible",
        "createdAt": datetime(2024, 1, 18),
        "updatedAt": datetime(2024, 1, 18),
    },
    {
        "id": 6,
        "title": "Departamento en Torre Premium",
        "price": 420000,
        "location": "Bilbao, España",
        "type": "Departamento",
        "bedrooms": 3,
        "bathrooms": 2,
        "area": 110,
        "price_per_sqm": 3818,
        "year_built": 2019,
        "energy_rating": "B",
        "description": "Departamento en torre premium con vista al mar, amenities de lujo y diseño contemporáneo.",
        "features": [
            "Vista al mar",
            "Terraza privada",
            "Amenities de lujo",
            "Gimnasio",
            "Concierge",
            "Parking subterráneo",
            "Ascensor privado",
            "Suelo de mármol"
        ],
        "amenities": [
            "Metro (3 min)",
            "Centro de Bilbao (10 min)",
            "Guggenheim (15 min)",
            "Hospitales cercanos",
            "Zona comercial"
        ],
        "rental_yield": "4.5%",
        "price_trend": "+10% anual",
        "community_fees": 180,
        "property_tax": 1500,
        "images": ["/images/depto3.jpg"],
        "status": "disponible",
        "createdAt": datetime(2024, 1, 16),
        "updatedAt": datetime(2024, 1, 16),
    },
    {
        "id": 7,
        "title": "Terreno para Construir",
        "price": 180000,
        "location": "Alicante, España",
        "type": "Terreno",
        "bedrooms": 0,
        "bathrooms": 0,
        "area": 800,
        "price_per_sqm": 225,
        "description": "Terreno en zona residencial, ideal para construir casa familiar. Servicios básicos conectados.",
        "features": [
            "Servicios básicos",
            "Zona residencial",
            "Acceso pavimentado",
            "Cerca del mar",
            "Orientación sur",
            "Posibilidad de piscina"
        ],
        "amenities": [
            "Playa (5 min en coche)",
            "Centro de Alicante (15 min)",
            "Aeropuerto (20 min)",
            "Colegios cercanos",
            "Zona comercial"
        ],
        "rental_yield": "N/A",
        "price_trend": "+5% anual",
        "community_fees": 0,
        "property_tax": 400,
        "images": ["/images/terreno1.jpg"],
        "status": "disponible",
        "createdAt": datetime(2024, 1, 14),
        "updatedAt": datetime(2024, 1, 14),
    },
    {
        "id": 8,
        "title": "Casa Histórica Restaurada",
        "price": 480000,
        "location": "Granada, España",
        "type": "Casa",
        "bedrooms": 3,
        "bathrooms": 2,
        "area": 140,
        "price_per_sqm": 3429,
        "year_built": 1850,
        "renovation_year": 2021,
        "energy_rating": "C",
        "description": "Casa histórica completamente restaurada, manteniendo su arquitectura original con comodidades modernas.",
        "features": [
            "Patio andaluz",
            "Azulejos originales",
            "Vigas de madera vistas",
            "Suelo de barro cocido",
            "Cocina moderna",
            "Climatización",
            "Ascensor",
            "Almacén"
        ],
        "amenities": [
            "Alhambra (10 min)",
            "Centro histórico (5 min)",
            "Universidad (15 min)",
            "Metro (3 min)",
            "Zona comercial"
        ],
        "rental_yield": "4.2%",
        "price_trend": "+8% anual",
        "community_fees": 75,
        "property_tax": 1000,
        "images": ["/images/casa4.jpg"],
        "status": "disponible",
        "createdAt": datetime(2024, 1, 12),
        "updatedAt": datetime(2024, 1, 12),
    },
    {
        "id": 9,
        "title": "Departamento en Zona Universitaria",
        "price": 220000,
        "location": "Zaragoza, España",
        "type": "Departamento",
        "bedrooms": 2,
        "bathrooms": 1,
        "area": 75,
        "price_per_sqm": 2933,
        "year_built": 2017,
        "energy_rating": "B",
        "description": "Departamento cerca de universidades, ideal para estudiantes o profesionales jóvenes.",
        "features": [
            "Balcón",
            "Ascensor",
            "Suelo laminado",
            "Cocina equipada",
            "Aire acondicionado",
            "Calefacción individual",
            "Parking opcional"
        ],
        "amenities": [
            "Universidad (5 min caminando)",
            "Metro (2 min)",
            "Centro (10 min)",
            "Hospitales cercanos",
            "Zona comercial"
        ],
        "rental_yield": "5.5%",
        "price_trend": "+6% anual",
        "community_fees": 60,
        "property_tax": 600,
        "images": ["/images/depto4.jpg"],
        "status": "disponible",
        "createdAt": datetime(2024, 1, 10),
        "updatedAt": datetime(2024, 1, 10),
    },
    {
        "id": 10,
        "title": "Casa de Playa con Vista al Mar",
        "price": 380000,
        "location": "Palma de Mallorca, España",
        "type": "Casa",
        "bedrooms": 3,
        "bathrooms": 2,
        "area": 120,
        "price_per_sqm": 3167,
        "year_built": 2016,
        "energy_rating": "B",
        "description": "Casa de playa con vista al mar, ideal para vacaciones o residencia permanente.",
        "features": [
            "Vista al mar",
            "Terraza de 30m²",
            "Jardín de 80m²",
            "Barbacoa",
            "Garage",
            "Aire acondicionado",
            "Suelo de mármol",
            "Cocina equipada"
        ],
        "amenities": [
            "Playa (100m)",
            "Centro de Palma (20 min)",
            "Aeropuerto (15 min)",
            "Golf (5 min)",
            "Restaurantes de mariscos"
        ],
        "rental_yield": "5.2%",
        "price_trend": "+12% anual",
        "community_fees": 0,
        "property_tax": 1200,
        "images": ["/images/casa5.jpg"],
        "status": "disponible",
        "createdAt": datetime(2024, 1, 8),
        "updatedAt": datetime(2024, 1, 8),
    },
]

def get_mock_response(question: str) -> dict:
    """
    Genera una respuesta mock cuando las credenciales AWS no están configuradas
    """
    # Respuestas predefinidas basadas en palabras clave
    question_lower = question.lower()
    
    if any(word in question_lower for word in ['precio', 'costo', 'valor', 'cuanto']):
        return {
            "answer": "Nuestras propiedades van desde €180,000 hasta €850,000. Por ejemplo: Casa en Chamberí (Madrid) €650,000, Ático en Eixample (Barcelona) €750,000, Casa de playa en Malvarrosa (Valencia) €420,000. ¿Te interesa algún rango de precio específico?",
            "sources": ["Catálogo detallado de propiedades - Precios actualizados"],
            "confidence": 0.9
        }
    elif any(word in question_lower for word in ['departamento', 'depto', 'apartamento']):
        return {
            "answer": "Tenemos departamentos premium disponibles: Ático en Eixample (Barcelona) €750,000 con terraza de 80m², Departamento en Bilbao €420,000 con vista al mar, y Departamento en Zaragoza €220,000 cerca de universidades. ¿Te interesa alguna ubicación específica?",
            "sources": ["Catálogo detallado de propiedades - Departamentos"],
            "confidence": 0.9
        }
    elif any(word in question_lower for word in ['casa', 'vivienda']):
        return {
            "answer": "Tenemos casas espectaculares: Casa moderna en Chamberí (Madrid) €650,000 con jardín privado, Casa de playa en Malvarrosa (Valencia) €420,000 a 200m del mar, Villa de lujo en El Limonar (Málaga) €850,000 con piscina privada. ¿Qué tipo de casa buscas?",
            "sources": ["Catálogo detallado de propiedades - Casas"],
            "confidence": 0.9
        }
    elif any(word in question_lower for word in ['ubicacion', 'zona', 'donde', 'lugar']):
        return {
            "answer": "Tenemos propiedades en las mejores zonas de España: Chamberí y Eixample en Madrid/Barcelona (€6,000-8,500/m²), Malvarrosa en Valencia (€3,500/m²), Triana en Sevilla (€3,167/m²), El Limonar en Málaga (€4,250/m²). ¿Qué ciudad te interesa más?",
            "sources": ["Guía de barrios y zonas - Análisis detallado"],
            "confidence": 0.9
        }
    elif any(word in question_lower for word in ['rendimiento', 'rentabilidad', 'inversion']):
        return {
            "answer": "Nuestras propiedades ofrecen excelentes rendimientos: Casa en Malvarrosa (Valencia) 5.8%, Departamento en Zaragoza 5.5%, Casa en Triana (Sevilla) 4.8%, Villa en El Limonar (Málaga) 4.0%. ¿Te interesa conocer más sobre inversión inmobiliaria?",
            "sources": ["Guía de inversión inmobiliaria - Análisis de rendimientos"],
            "confidence": 0.9
        }
    elif any(word in question_lower for word in ['amenidades', 'servicios', 'caracteristicas']):
        return {
            "answer": "Nuestras propiedades incluyen amenidades de lujo: piscinas privadas, gimnasios, terrazas, jardines, domótica, portería 24h, parking subterráneo. Por ejemplo, la Villa en El Limonar tiene piscina privada de 8x4m, gimnasio privado y sistema domótico completo. ¿Qué amenidades te interesan?",
            "sources": ["Guía de amenidades y servicios - Catálogo completo"],
            "confidence": 0.9
        }
    else:
        return {
            "answer": "Hola! Soy tu asistente inmobiliario especializado en el mercado español. Puedo ayudarte con información detallada sobre nuestras propiedades premium en Madrid, Barcelona, Valencia, Sevilla y Málaga. ¿Qué te interesa saber? ¿Precios, ubicaciones, rendimientos o características específicas?",
            "sources": ["Asistente inmobiliario - Información actualizada"],
            "confidence": 0.8
        }

def query_knowledge_base(question: str) -> dict:
    """
    Consulta el Knowledge Base de Bedrock con una pregunta
    """
    try:
        # Verificar si las credenciales están configuradas
        if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY or AWS_ACCESS_KEY_ID == "tu_access_key_aqui":
            logger.warning("Credenciales de AWS no configuradas, usando modo de prueba")
            return get_mock_response(question)
        
        response = bedrock_agent_runtime.retrieve_and_generate(
            input={
                'text': question
            },
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': KNOWLEDGE_BASE_ID,
                    'modelArn': f'arn:aws:bedrock:{AWS_REGION}::foundation-model/{BEDROCK_MODEL_ID}',
                    'retrievalConfiguration': {
                        'vectorSearchConfiguration': {
                            'numberOfResults': 5
                        }
                    }
                }
            }
        )
        
        return response
    except Exception as e:
        logger.error(f"Error consultando Knowledge Base: {str(e)}")
        # Si hay error de credenciales, usar modo de prueba
        if "credentials" in str(e).lower():
            logger.warning("Error de credenciales, usando modo de prueba")
        raise HTTPException(
            status_code=500,
            detail=f"Error consultando la base de conocimiento: {str(e)}"
        )


@app.get("/")
async def root():
    return {"message": "STELLART HOMES API", "version": "1.0.0"}

@app.get("/api/test")
async def test_connection():
    """Endpoint para probar la conexión con el backend"""
    return {
        "status": "ok",
        "message": "Backend conectado correctamente",
        "aws_region": AWS_REGION,
        "knowledge_base_id": KNOWLEDGE_BASE_ID
    }

@app.get("/api/properties", response_model=PropertyResponse)
async def get_properties(
    search: Optional[str] = None,
    type: Optional[str] = None,
    minPrice: Optional[int] = None,
    maxPrice: Optional[int] = None,
    bedrooms: Optional[int] = None
):
    """Obtener lista de propiedades con filtros opcionales"""
    try:
        properties = SAMPLE_PROPERTIES.copy()
        
        # Aplicar filtros
        if search:
            search_lower = search.lower()
            properties = [
                p for p in properties 
                if search_lower in p["title"].lower() or 
                   search_lower in p["description"].lower() or
                   search_lower in p["location"].lower()
            ]
        
        if type:
            properties = [p for p in properties if p["type"].lower() == type.lower()]
        
        if minPrice:
            properties = [p for p in properties if p["price"] >= minPrice]
        
        if maxPrice:
            properties = [p for p in properties if p["price"] <= maxPrice]
        
        if bedrooms:
            properties = [p for p in properties if p["bedrooms"] >= bedrooms]
        
        return PropertyResponse(properties=properties)
    
    except Exception as e:
        logger.error(f"Error obteniendo propiedades: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_ai(message_data: ChatMessage):
    """Chat con IA usando el Knowledge Base de Bedrock"""
    try:
        question = message_data.message
        
        if not question.strip():
            raise HTTPException(status_code=400, detail="El mensaje no puede estar vacío")
        
        # Consultar Knowledge Base
        response = query_knowledge_base(question)
        
        # Extraer respuesta y fuentes
        if 'output' in response:
            # Formato de Bedrock Knowledge Base
            generated_text = response.get('output', {}).get('text', 'No se pudo generar una respuesta.')
            citations = response.get('citations', [])
            
            # Formatear fuentes si existen
            sources = []
            if citations:
                for citation in citations:
                    if 'retrievedReferences' in citation:
                        for ref in citation['retrievedReferences']:
                            sources.append({
                                'content': ref.get('content', {}).get('text', ''),
                                'location': ref.get('location', {}).get('s3Location', {}).get('uri', ''),
                                'score': ref.get('score', 0)
                            })
        else:
            # Formato de respuesta mock
            generated_text = response.get('answer', 'No se pudo generar una respuesta.')
            sources = []
            if 'sources' in response:
                for source in response['sources']:
                    sources.append({
                        'content': source,
                        'location': '',
                        'score': response.get('confidence', 0.7)
                    })
        
        return ChatResponse(
            response=generated_text,
            sources=sources
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en chat: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error procesando la consulta. Inténtalo de nuevo."
        )

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "aws_region": AWS_REGION,
        "knowledge_base_id": KNOWLEDGE_BASE_ID
    }

@app.get("/api/test-bedrock")
async def test_bedrock_connection():
    """Endpoint para probar la conexión con Bedrock"""
    try:
        # Probar una consulta simple
        test_question = "¿Qué tipos de propiedades hay disponibles?"
        response = query_knowledge_base(test_question)
        
        return {
            "status": "success",
            "message": "Conexión con Bedrock exitosa",
            "test_response": response.get('output', {}).get('text', 'No response')[:200] + "..."
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error conectando con Bedrock: {str(e)}",
            "fallback_mode": "Usando respuestas simuladas"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001)
