#!/bin/bash

# STELLART HOMES - Setup Script
# Script para configurar y ejecutar el Portal Inmobiliario

set -e  # Salir si cualquier comando falla

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Verificar dependencias
check_dependencies() {
    print_step "Verificando dependencias..."
    
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI no está instalado. Instálalo con: brew install awscli"
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker no está instalado. Instálalo con: brew install docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose no está instalado. Instálalo con: brew install docker-compose"
        exit 1
    fi
    
    print_info "Todas las dependencias están instaladas"
}

# Obtener credenciales AWS
get_aws_credentials() {
    print_step "Configurando credenciales AWS..."
    
    echo -n "Ingresa tu AWS Access Key ID: "
    read -r AWS_ACCESS_KEY_ID
    
    echo -n "Ingresa tu AWS Secret Access Key: "
    read -s AWS_SECRET_ACCESS_KEY
    echo
    
    if [[ -z "$AWS_ACCESS_KEY_ID" || -z "$AWS_SECRET_ACCESS_KEY" ]]; then
        print_error "Las credenciales no pueden estar vacías"
        exit 1
    fi
    
    print_info "Credenciales AWS capturadas"
}

# Crear archivo .env
create_env_file() {
    print_step "Creando archivo .env..."
    
    # Crear directorio backend si no existe
    mkdir -p backend
    
    # Crear archivo .env directamente
    cat > backend/.env << EOF
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY

# Bedrock Configuration
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
KNOWLEDGE_BASE_ID=your_knowledge_base_id_here
USE_DIRECT_RAG=false

# Application Configuration
PORT=3001
NODE_ENV=development
EOF
    
    print_info "Archivo .env creado exitosamente"
}

# Crear bucket S3 y subir documentos
setup_s3() {
    print_step "Configurando bucket S3..."
    
    # Generar nombre único para el bucket con 8 caracteres aleatorios
    RANDOM_CHARS=$(openssl rand -hex 4)
    BUCKET_NAME="stellart-bedrock-${RANDOM_CHARS}"
    
    print_info "Creando bucket S3: $BUCKET_NAME"
    
    # Crear bucket S3
    if aws s3 mb "s3://$BUCKET_NAME" --region us-east-1; then
        print_info "Bucket S3 creado exitosamente"
    else
        print_error "Error al crear el bucket S3. Verifica tus credenciales y permisos."
        exit 1
    fi
    
    # Subir documentos si existen
    if [[ -d "backend/documents" && "$(ls -A backend/documents)" ]]; then
        print_info "Subiendo documentos al bucket S3..."
        if aws s3 sync backend/documents/ "s3://$BUCKET_NAME/"; then
            print_info "Documentos subidos exitosamente"
        else
            print_warning "Error al subir documentos, continuando..."
        fi
    else
        print_warning "No se encontraron documentos para subir"
    fi
}

# Configurar Knowledge Base ID
setup_knowledge_base() {
    print_step "Configurando Knowledge Base ID..."
    
    echo
    print_warning "IMPORTANTE: Antes de continuar, necesitas crear una Knowledge Base en AWS Bedrock"
    echo
    print_info "Pasos a seguir:"
    print_info "1. Ve a la consola de AWS: https://console.aws.amazon.com/bedrock/"
    print_info "2. Navega a 'Knowledge bases' en el menú lateral"
    print_info "3. Crea una nueva Knowledge Base"
    print_info "4. Sube los documentos que están en tu bucket S3: $BUCKET_NAME"
    print_info "5. Una vez creada, copia el Knowledge Base ID"
    echo
    
    echo -n "Ingresa el Knowledge Base ID: "
    read -r KNOWLEDGE_BASE_ID
    
    if [[ -z "$KNOWLEDGE_BASE_ID" ]]; then
        print_error "El Knowledge Base ID no puede estar vacío"
        exit 1
    fi
    
    # Actualizar el archivo .env con el Knowledge Base ID
    # Leer el archivo .env actual y reemplazar la línea del KNOWLEDGE_BASE_ID
    if [[ -f "backend/.env" ]]; then
        # Crear un archivo temporal con el Knowledge Base ID actualizado
        sed "s/your_knowledge_base_id_here/$KNOWLEDGE_BASE_ID/g" backend/.env > backend/.env.tmp
        mv backend/.env.tmp backend/.env
    else
        print_error "No se encontró el archivo backend/.env"
        exit 1
    fi
    
    print_info "Knowledge Base ID actualizado en el archivo .env"
}

# Ejecutar Docker Compose
run_docker() {
    print_step "Ejecutando Docker Compose..."
    
    print_info "Iniciando contenedores..."
    docker-compose up --build
}

# Función principal
main() {
    clear
    echo "=========================================="
    echo "              STELLART HOMES              "
    echo "=========================================="
    echo
    
    check_dependencies
    get_aws_credentials
    create_env_file
    setup_s3
    setup_knowledge_base
    run_docker
    
    echo
    print_info "¡Setup completado exitosamente!"
    print_info "STELLART HOMES debería estar ejecutándose en:"
    print_info "  Frontend: http://localhost:3000"
    print_info "  Backend: http://localhost:3001"
    print_info "  Bedrock debe crearse en la consola de AWS"
}

# Ejecutar función principal
main "$@"
