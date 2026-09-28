import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de AWS
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")

# Configuración de Bedrock
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")
KNOWLEDGE_BASE_ID = os.getenv("KNOWLEDGE_BASE_ID", "")
USE_DIRECT_RAG = os.getenv("USE_DIRECT_RAG", "true").lower() == "true"

# Configuración de la aplicación
PORT = int(os.getenv("PORT", 3001))
NODE_ENV = os.getenv("NODE_ENV", "development")

# Validar configuración requerida
if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
    print("⚠️  Advertencia: AWS_ACCESS_KEY_ID y AWS_SECRET_ACCESS_KEY no están configurados")
    print("   El backend funcionará pero no podrá conectarse a Bedrock")
