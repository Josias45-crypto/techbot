#!/bin/bash
# ============================================================
# TechBot — Script de configuración de base de datos
# Uso: bash scripts/setup_db.sh
# ============================================================

DB_NAME="techbot_db"
DB_USER="postgres"

echo "🚀 Iniciando configuración de base de datos TechBot..."

echo "📦 Creando base de datos..."
psql -U $DB_USER -c "CREATE DATABASE $DB_NAME;" 2>/dev/null || echo "Base de datos ya existe, continuando..."

echo "📋 Ejecutando módulos SQL..."
for file in database/schemas/*.sql; do
    echo "  → Ejecutando $file..."
    psql -U $DB_USER -d $DB_NAME -f "$file"
done

echo "✅ Base de datos configurada correctamente."
echo "📊 Tablas creadas:"
psql -U $DB_USER -d $DB_NAME -c "SELECT COUNT(*) as total_tablas FROM pg_tables WHERE schemaname = 'public';"
