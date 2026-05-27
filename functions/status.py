import os
import logging
from datetime import datetime
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
    """Get CPU usage percentage from /proc/stat"""
    try:
        with open('/proc/stat', 'r') as f:
            line = f.readline()
        
        if not line.startswith('cpu '):
            return "Error"
        
        # Parse CPU stats: user nice system idle iowait irq softirq steal guest guest_nice
        tokens = line.split()
        user = int(tokens[1])
        nice = int(tokens[2])
        system = int(tokens[3])
        idle = int(tokens[4])
        
        total = user + nice + system + idle
        used = total - idle
        
        if total == 0:
            return "0%"
        
        cpu_percent = (used / total) * 100
        return f"{cpu_percent:.1f}%"
    
    except Exception as e:
        logging.error(f"Error getting CPU usage: {e}")
        return "Error"

def get_ram_usage() -> tuple:
    """Get RAM usage from /proc/meminfo"""
    try:
        meminfo = {}
        with open('/proc/meminfo', 'r') as f:
            for line in f:
                if ':' in line:
                    key, value = line.split(':', 1)
                    meminfo[key.strip()] = int(value.split()[0])
        
        total_kb = meminfo.get('MemTotal', 0)
        available_kb = meminfo.get('MemAvailable', 0)
        used_kb = total_kb - available_kb
        
        if total_kb == 0:
            return "0%", "0GB", "0GB"
        
        percent = (used_kb / total_kb) * 100
        used_gb = used_kb / (1024 * 1024)
        total_gb = total_kb / (1024 * 1024)
        
        return f"{percent:.1f}%", f"{used_gb:.2f}GB", f"{total_gb:.2f}GB"
    
    except Exception as e:
        logging.error(f"Error getting RAM usage: {e}")
        return "Error", "Error", "Error"

def get_disk_usage() -> tuple:
    """Get disk usage using df command"""
    try:
        result = subprocess.run(
            ['df', '-B1', '/'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) >= 2:
                # Parse df output
                parts = lines[1].split()
                total = int(parts[1])
                used = int(parts[2])
                
                if total == 0:
                    return "0%", "0GB", "0GB"
                
                percent = (used / total) * 100
                used_gb = used / (1024 ** 3)
                total_gb = total / (1024 ** 3)
                
                return f"{percent:.1f}%", f"{used_gb:.2f}GB", f"{total_gb:.2f}GB"
    
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
    
    return "N/A"

def get_network_stats() -> dict:
    """Get network interface statistics from /proc/net/dev"""
    try:
        net_stats = {
            'bytes_sent': 0,
            'bytes_recv': 0,
            'packets_sent': 0,
            'packets_recv': 0,
            'errors': 0,
            'dropped': 0
        }
        
        with open('/proc/net/dev', 'r') as f:
            lines = f.readlines()[2:]  # Skip header lines
            
            for line in lines:
                if ':' in line:
                    parts = line.split(':')[1].split()
                    if len(parts) >= 10:
                        # Format: recv_bytes recv_packets recv_errors recv_dropped ... send_bytes send_packets ...
                        net_stats['bytes_recv'] += int(parts[0])
                        net_stats['packets_recv'] += int(parts[1])
                        net_stats['errors'] += int(parts[2])
                        net_stats['dropped'] += int(parts[3])
                        net_stats['bytes_sent'] += int(parts[8])
                        net_stats['packets_sent'] += int(parts[9])
        
        bytes_sent_mb = net_stats['bytes_sent'] / (1024 ** 2)
        bytes_recv_mb = net_stats['bytes_recv'] / (1024 ** 2)
        
        return {
            'sent_mb': f"{bytes_sent_mb:.2f}MB",
            'recv_mb': f"{bytes_recv_mb:.2f}MB",
            'packets_sent': net_stats['packets_sent'],
            'packets_recv': net_stats['packets_recv'],
            'errors': net_stats['errors'],
            'dropped': net_stats['dropped']
        }
    
    except Exception as e:
        logging.error(f"Error getting network stats: {e}")
        return None

def get_process_count() -> dict:
    """Get process count from /proc"""
    try:
        # Count directories in /proc that are numeric (process IDs)
        proc_dir = '/proc'
        total_processes = 0
        
        if os.path.isdir(proc_dir):
            for item in os.listdir(proc_dir):
                if item.isdigit():
                    total_processes += 1
        
        # Approximate running count by checking /proc/stat
        running = 0
        try:
            with open('/proc/stat', 'r') as f:
                for line in f:
                    if line.startswith('procs_running'):
                        running = int(line.split()[1])
                        break
        except:
            pass
        
        return {
            'total': total_processes,
            'running': running if running > 0 else "?"
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