import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import sys
import os

# ---------------- FUNCIONES DE DESCARGA ----------------

# Descarga de un solo audio/video
def descargar_audio_unico(url, carpeta_destino, modo, calidad, text_output):
    """Descarga un solo audio/video de la URL especificada."""
    
    text_output.insert(tk.END, f"\nDescargando: {url} en modo '{modo.upper()}' con calidad '{calidad}'\n")
    text_output.see(tk.END)
    
    opciones_ytdlp = generar_opciones_ytdlp(carpeta_destino, modo, calidad)

    try:
        comando = [obtener_ruta_binario('yt-dlp'), url] + opciones_ytdlp
        proceso = subprocess.run(
            comando,
            check=True,
            text=True,
            capture_output=True,
            encoding='utf-8', 
            timeout=600
        )
        text_output.insert(tk.END, proceso.stdout + "\n")
        text_output.insert(tk.END, "✅ Descarga completada.\n")
        
    except subprocess.CalledProcessError as e:
        error_limpio = limpiar_salida_error(e.stderr)
        text_output.insert(tk.END, f"❌ Error al descargar {url}: {error_limpio}\n")
    except FileNotFoundError:
        messagebox.showerror("Error", "No se encontró 'yt-dlp'. Asegúrate de tenerlo instalado y en el PATH.")
    except subprocess.TimeoutExpired:
        messagebox.showerror("Error", f"Tiempo de espera agotado al intentar descargar {url}.")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error inesperado: {e}")
        
    text_output.see(tk.END)

# Inicia la descarga de un solo audio/video desde la interfaz
def iniciar_descarga_unico(entry_url, entry_carpeta, text_output, modo_descarga, calidad_descarga):
    url = entry_url.get()
    carpeta = entry_carpeta.get()
    modo = modo_descarga.get()
    calidad = calidad_descarga.get() # OBTENEMOS LA CALIDAD

    if not url.strip():
        messagebox.showerror("Error", "Introduce una URL de audio válida.")
        return
    if not carpeta or not os.path.exists(carpeta):
        messagebox.showerror("Error", "Selecciona una carpeta de destino válida.")
        return

    descargar_audio_unico(url, carpeta, modo, calidad, text_output)

# Descarga de múltiples audios/videos desde un archivo de texto
def descargar_audios_lote(archivo_urls, carpeta_destino, modo, calidad, text_output):
    """Descarga múltiples audios/videos de un archivo de texto."""

    try:
        with open(archivo_urls, 'r') as file:
            linea = file.read().strip()
            # Asume URLs separadas por punto y coma (;) o nuevas líneas
            # Hacemos una limpieza simple
            urls_raw = linea.replace('\n', ';').split(';')
            urls = [url.strip() for url in urls_raw if url.strip()]
    except FileNotFoundError:
        messagebox.showerror("Error", f"No se encontró el archivo '{archivo_urls}'")
        return

    if not urls:
        messagebox.showwarning("Advertencia", "El archivo de URLs está vacío o no tiene URLs válidas.")
        return

    text_output.insert(tk.END, f"Se encontraron {len(urls)} URLs. Iniciando la descarga en modo '{modo.upper()}'...\n")
    text_output.see(tk.END)

    opciones_ytdlp = generar_opciones_ytdlp(carpeta_destino, modo, calidad)

    for url in urls:
        text_output.insert(tk.END, f"\nDescargando: {url}\n")
        text_output.see(tk.END)

        try:
            comando = [obtener_ruta_binario('yt-dlp.exe'), url] + opciones_ytdlp
            proceso = subprocess.run(
                comando,
                check=True,
                text=True,
                capture_output=True,
                encoding='utf-8',
                timeout=600
            )
            text_output.insert(tk.END, proceso.stdout + "\n")
            text_output.insert(tk.END, "✅ Descarga completada.\n")
            
        except subprocess.CalledProcessError as e:
            error_limpio = limpiar_salida_error(e.stderr)
            text_output.insert(tk.END, f"❌ Error al descargar {url}: {error_limpio}\n")
        except FileNotFoundError:
            messagebox.showerror("Error", "No se encontró 'yt-dlp'. Asegúrate de tenerlo instalado y en el PATH.")
            break
        text_output.see(tk.END)
    """
    Lee un archivo de texto con URLs separadas por punto y coma y
    descarga el audio de cada URL usando yt-dlp.
    """

    try:
        with open(archivo_urls, 'r') as file:
            linea = file.read().strip()
            urls = [url.strip() for url in linea.split(';') if url.strip()]
    except FileNotFoundError:
        messagebox.showerror("Error", f"No se encontró el archivo '{archivo_urls}'")
        return

    if not urls:
        messagebox.showwarning("Advertencia", "El archivo de URLs está vacío o no tiene URLs válidas.")
        return

    text_output.insert(tk.END, f"Se encontraron {len(urls)} URLs. Iniciando la descarga...\n")
    text_output.see(tk.END)

    opciones_ytdlp = [
        # Opcion -x: Extraer solo audio
        '-x',
        # Opcion --audio-format: Convertir a MP3
        '--audio-format', 'mp3',
        # Opcion --audio-quality: Asegura la mejor calidad (V0/casi 250kbps)
        '--audio-quality', '0', 
        # Opcion --embed-thumbnail: Incrustar la miniatura
        '--embed-thumbnail',
        # Opcion --format: SOLUCION AL ERROR. Pide la mejor pista de audio que encuentre.
        # Esto previene el fallo si el video no tiene el formato "por defecto" accesible.
        # Usa 'bestaudio/best' en lugar de confiar en el formato predeterminado.
        '--format', 'bestaudio/best', 
        # Opcion --output: Carpeta de destino
        '--output', os.path.join(carpeta_destino, '%(title)s.%(ext)s')
    ]

    for url in urls:
        text_output.insert(tk.END, f"\nDescargando: {url}\n")
        text_output.see(tk.END)

        try:
            # Comando: ['yt-dlp', URL, OPCCIONES...]
            comando = ['yt-dlp', url] + opciones_ytdlp
            proceso = subprocess.run(
                comando,
                check=True,
                text=True,
                capture_output=True,
                # 2. MEJORA: Aumentar el tiempo de espera (timeout)
                # Las descargas largas o conversiones complejas pueden exceder el tiempo por defecto.
                timeout=600 # 10 minutos
            )
            text_output.insert(tk.END, proceso.stdout + "\n")
            text_output.insert(tk.END, "✅ Descarga completada.\n")
            
        # 3. MEJORA: Captura de errores de proceso (el que contiene el error "Requested format is not available")
        except subprocess.CalledProcessError as e:
            # Es vital limpiar el stderr (salida de error) de la herramienta yt-dlp
            # para no mostrar todos los warnings (nsig extraction failed, etc.)
            error_limpio = limpiar_salida_error(e.stderr)
            text_output.insert(tk.END, f"❌ Error al descargar {url}: {error_limpio}\n")
        except FileNotFoundError:
            messagebox.showerror("Error", "No se encontró 'yt-dlp'. Asegúrate de tenerlo instalado y en el PATH.")
            break
        text_output.see(tk.END)

# --------------- FUNCIONES DE INTERFAZ ----------------
def seleccionar_archivo(entry):
    archivo = filedialog.askopenfilename(
        title="Seleccionar archivo de URLs",
        filetypes=[("Archivos de texto", "*.txt")]
    )
    if archivo:
        entry.delete(0, tk.END)
        entry.insert(0, archivo)

# Seleccionar carpeta de destino
def seleccionar_carpeta(entry):
    carpeta = filedialog.askdirectory(title="Seleccionar carpeta de destino")
    if carpeta:
        entry.delete(0, tk.END)
        entry.insert(0, carpeta)

# Inicia la descarga por lotes desde la interfaz
def iniciar_descarga(entry_archivo, entry_carpeta, text_output, modo_descarga, calidad_descarga):
    archivo = entry_archivo.get()
    carpeta = entry_carpeta.get()
    modo = modo_descarga.get()
    calidad = calidad_descarga.get()

    if not archivo or not os.path.exists(archivo):
        messagebox.showerror("Error", "Selecciona un archivo de URLs válido.")
        return
    if not carpeta or not os.path.exists(carpeta):
        messagebox.showerror("Error", "Selecciona una carpeta de destino válida.")
        return

    descargar_audios_lote(archivo, carpeta, modo, calidad, text_output)

# --------------- FUNCIONES AUXILIARES ----------------
def limpiar_salida_error(stderr_output):
    """Filtra los warnings de yt-dlp y solo muestra la línea de error final."""
    lineas = stderr_output.split('\n')
    lineas_limpias = [
        linea.strip() for linea in lineas 
        if linea.strip() and not linea.strip().startswith('WARNING')
    ]
    errores = [l for l in lineas_limpias if l.startswith('ERROR')]
    if errores:
        return errores[-1]
    return "\n".join(lineas_limpias)

# Genera opciones de yt-dlp según el modo
def generar_opciones_ytdlp(carpeta_destino, modo, calidad_video):
    """Genera la lista de opciones de yt-dlp basadas en el modo y la calidad."""
    
    # Opción de salida común para ambos modos
    output_path = os.path.join(carpeta_destino, '%(title)s.%(ext)s')
    
    if modo == 'audio':
        # Modo Solo Audio (MP3)
        return [
            '-x', 
            '--audio-format', 'mp3',
            '--audio-quality', '0', 
            '--embed-thumbnail', 
            '--format', 'bestaudio/best', 
            '--output', output_path
        ]
        
    elif modo == 'video':
        # MODO VIDEO (Añadimos el filtro de calidad)
        
        # 1. Definimos el filtro de formato de yt-dlp
        if calidad_video == 'Mejor Disponible':
            # Usa el mejor video que encuentre sin límite de resolución
            formato_str = 'bestvideo+bestaudio/best'
        else:
            # Filtra por la altura (ej: 720p, 480p)
            altura = calidad_video.replace('p', '')
            formato_str = f'bestvideo[height<={altura}]+bestaudio/best'
            
        # 2. Construimos las opciones
        return [
            '--format', formato_str, 
            '--recode-video', 'mp4', # Mantenemos el recode que el usuario quiere
            '--embed-thumbnail',
            '--output', output_path
        ]
    return []

def obtener_ruta_binario(nombre_binario):
    """Devuelve la ruta absoluta al ejecutable, esté dentro del paquete de PyInstaller o en el PATH."""
    
    # Si la aplicación se ejecuta dentro del paquete PyInstaller
    if getattr(sys, 'frozen', False):
        # La ruta temporal en el sistema del usuario (creada por PyInstaller)
        bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
        return os.path.join(bundle_dir, nombre_binario)
    
    # Si se ejecuta como un script normal de Python
    return nombre_binario # Esperamos que esté en el PATH

# ---------------- INTERFAZ ----------------
ventana = tk.Tk()
ventana.title("🎵 Descargador Multimedia (Audio/Video)")
ventana.geometry("700x650")

# Variable para controlar el modo de descarga
modo_descarga = tk.StringVar(ventana, value='audio')

# Variable para la calidad del video (NUEVA)
calidad_descarga = tk.StringVar(ventana, value='Mejor Disponible')
opciones_calidad = ['Mejor Disponible', '1080p', '720p', '480p']

# --- 1. SECCIÓN DE CONFIGURACIÓN GLOBAL (MODIFICADA) ---
frame_global = tk.LabelFrame(ventana, text="⚙️ Configuración Global", padx=10, pady=10)
frame_global.pack(pady=10, padx=10, fill="x")

# --- 1. SECCIÓN DE CONFIGURACIÓN GLOBAL ---
frame_global = tk.LabelFrame(ventana, text="⚙️ Configuración Global", padx=10, pady=10)
frame_global.pack(pady=10, padx=10, fill="x")

# Carpeta destino
tk.Label(frame_global, text="Carpeta de Destino:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
entry_carpeta = tk.Entry(frame_global, width=45) 
entry_carpeta.grid(row=0, column=1, padx=5, sticky="ew") 
tk.Button(frame_global, text="Buscar Carpeta", command=lambda: seleccionar_carpeta(entry_carpeta)).grid(row=0, column=2, padx=5)

# Modo de Descarga (NUEVO CONTROL)
tk.Label(frame_global, text="Modo de Descarga:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
tk.Radiobutton(frame_global, text="Solo Audio (MP3)", variable=modo_descarga, value="audio").grid(row=1, column=1, sticky="w", padx=10)
tk.Radiobutton(frame_global, text="Video + Audio (MP4)", variable=modo_descarga, value="video").grid(row=1, column=2, sticky="w", padx=10)

frame_global.grid_columnconfigure(1, weight=1)

# Selección de Calidad (NUEVO CONTROL)
tk.Label(frame_global, text="Calidad de Video:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
combo_calidad = tk.OptionMenu(frame_global, calidad_descarga, *opciones_calidad)
combo_calidad.grid(row=2, column=1, sticky="ew", padx=10, pady=5, columnspan=2)

frame_global.grid_columnconfigure(1, weight=1)

# --- 2. SECCIÓN DE DESCARGA ÚNICA ---
frame_unico = tk.LabelFrame(ventana, text="🔗 Descarga de URL Individual", padx=10, pady=10)
frame_unico.pack(pady=10, padx=10, fill="x")

# Campo URL Única
tk.Label(frame_unico, text="URL del Audio/Video:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
entry_url_unico = tk.Entry(frame_unico, width=60)
entry_url_unico.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

# Botón de descarga Única (MODIFICADO para pasar calidad_descarga)
btn_descargar_unico = tk.Button(
    frame_unico, 
    text="▶️ Iniciar Descarga Única", 
    bg="#007bff", fg="white", 
    # PASAMOS AHORA LA VARIABLE DE CALIDAD
    command=lambda: iniciar_descarga_unico(entry_url_unico, entry_carpeta, text_output, modo_descarga, calidad_descarga)
)
btn_descargar_unico.grid(row=1, column=0, columnspan=2, pady=10, sticky="ew")

frame_unico.grid_columnconfigure(1, weight=1)

# --- 3. SECCIÓN DE DESCARGA POR LOTES ---
frame_batch = tk.LabelFrame(ventana, text="📋 Descarga por Lotes (Archivo TXT)", padx=10, pady=10)
frame_batch.pack(pady=10, padx=10, fill="x")

# Selección archivo
tk.Label(frame_batch, text="Archivo de URLs (.txt):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
entry_archivo = tk.Entry(frame_batch, width=50)
entry_archivo.grid(row=0, column=1, padx=5, sticky="ew")
tk.Button(frame_batch, text="Buscar Archivo", command=lambda: seleccionar_archivo(entry_archivo)).grid(row=0, column=2, padx=5)

# Botón de descarga Lote (MODIFICADO para pasar calidad_descarga)
btn_descargar_lote = tk.Button(
    frame_batch, 
    text="▶️ Iniciar Descarga de Lote",
    bg="#28a745", fg="white", 
    # PASAMOS AHORA LA VARIABLE DE CALIDAD
    command=lambda: iniciar_descarga(entry_archivo, entry_carpeta, text_output, modo_descarga, calidad_descarga)
)
btn_descargar_lote.grid(row=1, column=0, columnspan=3, pady=10, sticky="ew")

frame_batch.grid_columnconfigure(1, weight=1)

# --- 4. ÁREA DE LOGS (Registro de la Actividad) ---
tk.Label(ventana, text="📝 Registro de Actividad:").pack(padx=10, pady=(5, 0), anchor="w")
text_output = scrolledtext.ScrolledText(ventana, wrap=tk.WORD, height=15)
text_output.pack(fill="both", expand=True, padx=10, pady=(0, 10))

ventana.mainloop()