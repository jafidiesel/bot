#!/bin/bash

# Script de verificación de configuración del bot

echo "=== Verificando Configuración del Bot de Telegram ==="
echo ""

# Verificar directorio actual
if [[ ! -f "bot.py" ]]; then
    echo "❌ Error: No se encuentra bot.py"
    echo "   Ejecuta este script desde el directorio del bot (/home/pi/git/bot/bot/)"
    exit 1
fi
echo "✅ Archivo bot.py encontrado"

# Verificar archivo .env
if [[ ! -f ".env" ]]; then
    echo "❌ Error: No se encuentra el archivo .env"
    echo "   Ejecuta: cp .env.example .env (si existe) o créalo manualmente"
    exit 1
fi
echo "✅ Archivo .env encontrado"

# Verificar configuración del token
if ! grep -q "TELEGRAM_TOKEN=" .env; then
    echo "❌ Error: TELEGRAM_TOKEN no encontrado en .env"
    exit 1
fi

if grep -q "TU_TOKEN_AQUI" .env; then
    echo "⚠️  Advertencia: TELEGRAM_TOKEN aún no configurado"
    echo "   Edita .env y reemplaza TU_TOKEN_AQUI con tu token real"
else
    echo "✅ TELEGRAM_TOKEN configurado"
fi

# Verificar URLs de APIs
if ! grep -q "DOLLAR_API_URL=" .env; then
    echo "❌ Error: DOLLAR_API_URL no encontrado en .env"
    exit 1
fi

if grep -q "TU_URL_API_DOLAR_AQUI" .env; then
    echo "⚠️  Advertencia: DOLLAR_API_URL aún no configurado"
else
    echo "✅ DOLLAR_API_URL configurado"
fi

if ! grep -q "DOLLAR_BITSO_URL=" .env; then
    echo "❌ Error: DOLLAR_BITSO_URL no encontrado en .env"
    exit 1
fi

if grep -q "TU_URL_API_BITSO_AQUI" .env; then
    echo "⚠️  Advertencia: DOLLAR_BITSO_URL aún no configurado"
else
    echo "✅ DOLLAR_BITSO_URL configurado"
fi

# Verificar requirements.txt
if [[ ! -f "requirements.txt" ]]; then
    echo "❌ Error: No se encuentra requirements.txt"
    exit 1
fi
echo "✅ Archivo requirements.txt encontrado"

# Verificar directorio functions
if [[ ! -d "functions" ]]; then
    echo "❌ Error: No se encuentra el directorio functions/"
    exit 1
fi
echo "✅ Directorio functions/ encontrado"

# Verificar archivos de funciones
required_functions=("start.py" "dolar.py" "bitso.py" "temp.py" "usdars.py" "arsusd.py" "test.py")
for func in "${required_functions[@]}"; do
    if [[ ! -f "functions/$func" ]]; then
        echo "❌ Error: No se encuentra functions/$func"
        exit 1
    fi
done
echo "✅ Todas las funciones encontradas"

# Verificar permisos de scripts
scripts=("build_run_silent.sh" "install_service.sh" "test_bot.sh")
for script in "${scripts[@]}"; do
    if [[ -f "$script" ]]; then
        if [[ ! -x "$script" ]]; then
            echo "⚠️  Advertencia: $script no tiene permisos de ejecución"
            echo "   Ejecuta: chmod +x $script"
        else
            echo "✅ $script tiene permisos correctos"
        fi
    else
        echo "⚠️  Advertencia: $script no encontrado"
    fi
done

# Verificar Python y dependencias
echo ""
echo "=== Verificando Entorno Python ==="

if command -v python3 &> /dev/null; then
    echo "✅ Python3 disponible: $(python3 --version)"
else
    echo "❌ Error: Python3 no encontrado"
    exit 1
fi

if command -v pip3 &> /dev/null; then
    echo "✅ pip3 disponible"
else
    echo "❌ Error: pip3 no encontrado"
    exit 1
fi

echo ""
echo "=== Resumen de Configuración ==="

# Contador de problemas
warnings=0
errors=0

if grep -q "TU_TOKEN_AQUI\|TU_URL_.*_AQUI" .env; then
    echo "⚠️  Configuración incompleta en .env"
    ((warnings++))
fi

if [[ $warnings -eq 0 && $errors -eq 0 ]]; then
    echo "🎉 ¡Configuración completa!"
    echo ""
    echo "Próximos pasos:"
    echo "1. Ejecutar: ./test_bot.sh (para probar localmente)"
    echo "2. Ejecutar: ./install_service.sh (para instalar como servicio)"
elif [[ $errors -eq 0 ]]; then
    echo "⚠️  Configuración casi lista ($warnings advertencias)"
    echo ""
    echo "Para completar la configuración:"
    echo "1. Edita el archivo .env y configura los valores pendientes"
    echo "2. Ejecuta este script nuevamente para verificar"
else
    echo "❌ Configuración incompleta ($errors errores, $warnings advertencias)"
    echo "Corrige los errores mostrados arriba"
    exit 1
fi
