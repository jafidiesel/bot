# Bot de Telegram con Manejo de Errores Mejorado

Este bot de Telegram proporciona información financiera (dólar, Bitso, conversiones) con un sistema robusto de manejo de errores.

## 🚀 Características Nuevas

### ✅ Manejo de Errores Robusto
- **Decorador `@handle_errors`**: Captura automáticamente errores y los envía al usuario
- **Logging detallado**: Todos los errores se registran en `bot.log`
- **Modo debug**: Información técnica detallada para administradores
- **Fallbacks**: Respuestas alternativas cuando fallan los sistemas principales

### ✅ Llamadas Seguras a APIs
- **Timeouts**: Evita que el bot se cuelgue esperando APIs lentas
- **Manejo de errores de conexión**: Informa problemas de red
- **Códigos de estado HTTP**: Reporta errores específicos de las APIs
- **Validación de datos**: Verifica que las respuestas sean válidas

### ✅ Comandos Mejorados
- `/start` - Menú principal mejorado
- `/dolar` - Información del dólar con manejo de errores
- `/bitso` - Datos de Bitso con validación robusta
- `/debug` - Activar/desactivar modo debug (solo administradores)
- `/myid` - Obtener tu ID de usuario de Telegram

## 📋 Configuración

### 1. Variables de Entorno (.env)
```env
TELEGRAM_TOKEN=tu_token_de_botfather_aqui
DOLLAR_API_URL=https://api.ejemplo.com/dolar
DOLLAR_BITSO_URL=https://api.bitso.com/v3/ticker
```

### 2. Configurar Usuario Autorizado
En `bot.py`, línea del comando debug, cambiar:
```python
authorized_users = [123456789]  # ⚠️ CAMBIAR POR TU USER ID REAL
```

Para obtener tu User ID:
1. Ejecuta el bot
2. Envía `/myid` al bot
3. Reemplaza `123456789` con tu ID real
4. Reinicia el bot

## 🛠️ Instalación

### Opción 1: Instalación Automática (Recomendada)
```bash
cd /home/pi/git/bot/bot/
chmod +x install_service.sh
./install_service.sh
```

### Opción 2: Prueba Local Primero
```bash
cd /home/pi/git/bot/bot/
chmod +x test_bot.sh
./test_bot.sh
```

## 🎮 Uso del Servicio

```bash
# Controlar el servicio
sudo systemctl start telegram-bot     # Iniciar
sudo systemctl stop telegram-bot      # Detener
sudo systemctl restart telegram-bot   # Reiniciar
sudo systemctl status telegram-bot    # Ver estado

# Ver logs
sudo journalctl -u telegram-bot -f    # En tiempo real
sudo journalctl -u telegram-bot       # Histórico
cat bot.log                           # Log del bot
```

## 📊 Logs y Monitoreo

### Archivos de Log
- `bot.log` - Log detallado del bot
- `journalctl -u telegram-bot` - Log del servicio systemd

### Información en los Logs
- ✅ Comandos ejecutados correctamente
- ❌ Errores capturados y enviados al usuario
- 🌐 Problemas de conectividad con APIs
- 🐛 Información de debug (cuando está activado)

## 🔧 Resolución de Problemas

### Error: "TELEGRAM_TOKEN no configurado"
- Verificar que el archivo `.env` existe
- Verificar que `TELEGRAM_TOKEN=tu_token_real` está en `.env`

### Error: "API URL no configurada"
- Verificar que `DOLLAR_API_URL` y `DOLLAR_BITSO_URL` están en `.env`
- Verificar que las URLs son válidas

### Error: "No autorizado para usar comando debug"
- Usar `/myid` para obtener tu User ID
- Actualizar `authorized_users = [TU_ID_AQUI]` en `bot.py`
- Reiniciar el bot

### Bot no responde
```bash
# Verificar estado del servicio
sudo systemctl status telegram-bot

# Ver logs recientes
sudo journalctl -u telegram-bot --since "10 minutes ago"

# Reiniciar servicio
sudo systemctl restart telegram-bot
```

## 📁 Estructura del Proyecto

```
bot/
├── bot.py                    # Archivo principal con manejo de errores
├── .env                      # Variables de entorno
├── requirements.txt          # Dependencias Python
├── bot.log                   # Log del bot (se crea automáticamente)
├── telegram-bot.service      # Archivo de servicio systemd
├── install_service.sh        # Script de instalación
├── test_bot.sh              # Script de prueba local
├── build_run_silent.sh      # Script de construcción y ejecución
└── functions/               # Funciones individuales mejoradas
    ├── start.py             # Comando start mejorado
    ├── dolar.py             # Comando dólar con manejo de errores
    ├── bitso.py             # Comando bitso con validación
    ├── temp.py              # Comando temperatura
    ├── usdars.py            # Conversión USD a ARS
    ├── arsusd.py            # Conversión ARS a USD
    └── test.py              # Comando de prueba
```

## 🔒 Seguridad

- ✅ Token almacenado en `.env` (no en el código)
- ✅ Comando debug restringido a usuarios autorizados
- ✅ Validación de entrada en todas las funciones
- ✅ Timeouts para evitar ataques de denegación de servicio
- ✅ Logging detallado para auditoria

## 📈 Mejoras Implementadas

1. **Antes**: Errores causaban que el bot se colgara
   **Ahora**: Errores se capturan y reportan al usuario

2. **Antes**: APIs lentas bloqueaban el bot indefinidamente
   **Ahora**: Timeout de 10 segundos con mensaje explicativo

3. **Antes**: Errores solo se mostraban en la consola
   **Ahora**: Errores se envían al usuario y se registran en logs

4. **Antes**: Difícil diagnosticar problemas
   **Ahora**: Modo debug y logging detallado

5. **Antes**: Mensajes de error genéricos
   **Ahora**: Mensajes específicos según el tipo de error

## 🚀 Próximas Mejoras

- [ ] Comando `/status` para verificar salud de las APIs
- [ ] Rate limiting para evitar spam
- [ ] Base de datos para histórico de precios
- [ ] Notificaciones automáticas de cambios significativos
- [ ] Dashboard web de administración
