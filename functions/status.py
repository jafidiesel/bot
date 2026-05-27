import psutil
import os
import logging
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
import subprocess

# Global variable to track bot start time
BOT_START_TIME = None

def set_bot_start_time():
    """Set the bot start time on initialization"""
    global BOT_START_TIME
    BOT_START_TIME = datetime.now()
    logging.info(f"Bot start time set to {BOT_START_TIME}")

def get_bot_uptime() -> str:
    """Get bot uptime as a formatted string"""
    if BOT_START_TIME is None:
        return "Calculando..."
    
    uptime = datetime.now() - BOT_START_TIME
    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days = uptime.days
    
    return f"{days}d {hours}h {minutes}m {seconds}s"

def get_cpu_usage() -> str:
    """Get CPU usage percentage"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        return f"{cpu_percent}%"
    except Exception as e:
        logging.error(f"Error getting CPU usage: {e}")
        return "Error"

def get_ram_usage() -> tuple:
    """Get RAM usage as (used_percent, used_gb, total_gb)"""
    try:
        ram = psutil.virtual_memory()
        used_gb = ram.used / (1024 ** 3)
        total_gb = ram.total / (1024 ** 3)
        return f"{ram.percent}%", f"{used_gb:.2f}GB", f"{total_gb:.2f}GB"
    except Exception as e:
        logging.error(f"Error getting RAM usage: {e}")
        return "Error", "Error", "Error"

def get_disk_usage() -> tuple:
    """Get disk usage for root partition as (used_percent, used_gb, total_gb)"""
    try:
        disk = psutil.disk_usage('/')
        used_gb = disk.used / (1024 ** 3)
        total_gb = disk.total / (1024 ** 3)
        return f"{disk.percent}%", f"{used_gb:.2f}GB", f"{total_gb:.2f}GB"
    except Exception as e:
        logging.error(f"Error getting disk usage: {e}")
        return "Error", "Error", "Error"

def get_raspberry_pi_temp() -> str:
    """
    Get Raspberry Pi CPU temperature.
    Tries vcgencmd first (preferred on RPi), falls back to thermal zone reading.
    """
    try:
        # Try vcgencmd (preferred method on Raspberry Pi)
        result = subprocess.run(
            ['vcgencmd', 'measure_temp'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            # Output format: "temp=52.3'C"
            temp_str = result.stdout.strip()
            if 'temp=' in temp_str:
                return temp_str.replace("temp=", "").replace("'C", "°C")
    
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    except Exception as e:
        logging.debug(f"vcgencmd error: {e}")
    
    # Fallback: read from thermal zone
    try:
        thermal_file = '/sys/class/thermal/thermal_zone0/temp'
        if os.path.exists(thermal_file):
            with open(thermal_file, 'r') as f:
                temp_millidegrees = int(f.read().strip())
                temp_celsius = temp_millidegrees / 1000
                return f"{temp_celsius:.1f}°C"
    except Exception as e:
        logging.error(f"Error reading thermal zone: {e}")
    
    # Fallback: try psutil (less accurate on RPi)
    try:
        temps = psutil.sensors_temperatures()
        if 'cpu_thermal' in temps:
            return f"{temps['cpu_thermal'][0].current:.1f}°C"
        elif len(temps) > 0:
            first_sensor = list(temps.values())[0]
            if first_sensor:
                return f"{first_sensor[0].current:.1f}°C"
    except Exception as e:
        logging.error(f"Error getting temperature from psutil: {e}")
    
    return "N/A"

def get_network_stats() -> dict:
    """Get network interface statistics"""
    try:
        net_io = psutil.net_io_counters()
        bytes_sent = net_io.bytes_sent / (1024 ** 2)  # Convert to MB
        bytes_recv = net_io.bytes_recv / (1024 ** 2)  # Convert to MB
        
        return {
            'sent_mb': f"{bytes_sent:.2f}MB",
            'recv_mb': f"{bytes_recv:.2f}MB",
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv,
            'errors': net_io.errin + net_io.errout,
            'dropped': net_io.dropin + net_io.dropout
        }
    except Exception as e:
        logging.error(f"Error getting network stats: {e}")
        return None

def get_process_count() -> dict:
    """Get process count information"""
    try:
        return {
            'total': len(psutil.pids()),
            'running': len([p for p in psutil.pids() if psutil.Process(p).status() == psutil.STATUS_RUNNING])
        }
    except Exception as e:
        logging.error(f"Error getting process count: {e}")
        return None

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Display comprehensive bot and system status information.
    """
    try:
        # Gather all metrics
        uptime = get_bot_uptime()
        cpu = get_cpu_usage()
        ram_percent, ram_used, ram_total = get_ram_usage()
        disk_percent, disk_used, disk_total = get_disk_usage()
        temp = get_raspberry_pi_temp()
        net_stats = get_network_stats()
        proc_count = get_process_count()
        
        # Build status message
        status_text = (
            "📊 *Estado del Bot y Sistema*\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🤖 *Bot*\n"
            f"⏱️ Uptime: `{uptime}`\n"
            f"📍 Proceso: `Activo`\n\n"
            "💻 *CPU & Temperatura*\n"
            f"🔴 CPU: `{cpu}`\n"
            f"🌡️ Temperatura: `{temp}`\n\n"
            "🧠 *Memoria RAM*\n"
            f"📈 Uso: `{ram_percent}` (`{ram_used}` / `{ram_total}`)\n\n"
            "💾 *Almacenamiento*\n"
            f"📈 Uso: `{disk_percent}` (`{disk_used}` / `{disk_total}`)\n\n"
        )
        
        # Add network stats if available
        if net_stats:
            status_text += (
                "🌐 *Red*\n"
                f"📤 Enviado: `{net_stats['sent_mb']}`\n"
                f"📥 Recibido: `{net_stats['recv_mb']}`\n"
                f"❌ Errores: `{net_stats['errors']}`\n\n"
            )
        
        # Add process info if available
        if proc_count:
            status_text += (
                "⚙️ *Procesos*\n"
                f"Total: `{proc_count['total']}`\n"
                f"Ejecutándose: `{proc_count['running']}`\n\n"
            )
        
        status_text += f"🕐 Actualizado: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`"
        
        await update.message.reply_text(status_text, parse_mode='Markdown')
        logging.info(f"Status command executed by user {update.effective_user.id}")
    
    except Exception as e:
        error_msg = f"❌ Error al obtener estado:\n{str(e)}"
        await update.message.reply_text(error_msg)
        logging.error(f"Status command error: {e}", exc_info=True)
