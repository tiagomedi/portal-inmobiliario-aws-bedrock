# STELLART HOMES

Portal inmobiliario con integración de IA usando Amazon Bedrock.

## Requisitos

- Docker y Docker Compose
- AWS CLI configurado
- Acceso a Amazon Bedrock

## Configuración

1. Configurar variables de entorno:
```bash
cp env.example .env
# Editar .env con tus credenciales AWS
```

2. Ejecutar con Docker:
```bash
docker-compose up --build
```

3. Acceder a la aplicación:
- Frontend: http://localhost:3000
- Backend API: http://localhost:3001

## Despliegue en AWS

1. Configurar Terraform:
```bash
cd infraestructura
terraform init
terraform plan
terraform apply
```

2. Configurar variables de entorno en producción según los outputs de Terraform.

## Estructura

- `frontend/` - Interfaz web (HTML, CSS, JavaScript)
- `backend/` - API FastAPI con integración Bedrock
- `infraestructura/` - Configuración Terraform para AWS
- `docs/` - Documentación técnica

## Documentación

Ver `docs/` para guías detalladas de desarrollo y despliegue.
