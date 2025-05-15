#!/bin/bash

echo "=== Iniciando despliegue del sistema de recomendación ==="

# Verificar si Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "Docker no está instalado. Por favor, instala Docker primero."
    exit 1
fi

# Verificar si Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose no está instalado. Por favor, instala Docker Compose primero."
    exit 1
fi

echo "=== Construyendo y levantando contenedores ==="
docker-compose build
docker-compose up -d

echo "=== Verificando el estado de los servicios ==="
docker-compose ps

echo "=== Despliegue completado ==="
echo "Backend API: http://localhost:8000"
echo "Blog Frontend: http://localhost:4173"
echo "Admin Dashboard: http://localhost:4174"
echo "API para Power BI: http://localhost:8000/api/users/analytics/power-bi?api_key=pfe2025_test"
