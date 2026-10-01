# Transcribe

Transcribe es una aplicación local para **descargar y transcribir contenido al que el usuario ya tiene acceso** desde Zoom y YouTube.

- **Zoom:** grabaciones públicas o institucionales, reutilizando sesiones locales autorizadas cuando la grabación requiere autenticación.
- **YouTube:** videos públicos y, cuando sea necesario, acceso mediante una sesión local autorizada.
- **Transcripción local:** genera archivos TXT, SRT y VTT con `faster-whisper`.
- **Reanudación:** conserva el estado de los trabajos para evitar repetir descargas o continuar procesos interrumpidos.

## Flujo de trabajo

Ambos proveedores utilizan el mismo pipeline:

```text
URL
 ↓
video
 ↓
MP3 permanente
 ↓
FLAC temporal 16 kHz mono
 ↓
faster-whisper
 ↓
TXT + SRT + VTT
```

## Menú

```text
========================================
               TRANSCRIBE
========================================
1) Zoom
2) YouTube
3) Salir
```

Después de seleccionar una fuente, el programa solicita la URL y un nombre para la transcripción.

## Zoom

Pega una URL de grabación:

```text
https://institucion.zoom.us/rec/play/...
```

El programa:

1. valida la URL;
2. comprueba si puede acceder a la grabación;
3. si requiere acceso institucional, busca una sesión válida en los navegadores configurados;
4. prepara una copia local de las cookies necesarias;
5. descarga el video;
6. genera un MP3;
7. crea un FLAC temporal para Whisper;
8. transcribe y guarda los resultados.

Transcribe **no inicia sesión por el usuario ni evade controles de acceso**. Solo reutiliza sesiones locales que ya tengan permiso para acceder al contenido.

Las cookies exportadas se almacenan únicamente en:

```text
private/zoom.cookies.txt
```

`private/` está excluido de Git.

## YouTube

Acepta URLs de YouTube y YouTube Music.

Para videos públicos se intenta trabajar sin cookies. Si el recurso requiere una sesión y el usuario ya dispone de acceso en un navegador compatible, se utiliza el mismo mecanismo local de sesión.

La descarga limita el video a una altura máxima configurable, por defecto **720p**, porque la prioridad del proyecto es obtener el audio y la transcripción de forma eficiente.

## Instalación

### Requisitos

- Windows 10/11
- Python 3.10+
- `ffmpeg`
- `ffprobe`
- dependencias Python de `requirements.txt`
- opcionalmente, una GPU NVIDIA compatible

Clona el repositorio:

```bat
git clone https://github.com/JaimeArriagadaRosas/Transcribe.git
cd Transcribe
```

Se recomienda utilizar un entorno virtual:

```bat
python -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

`ffmpeg` y `ffprobe` deben estar disponibles en `PATH`.

Las versiones de `faster-whisper` y PyAV están fijadas en `requirements.txt` para mantener una combinación compatible con la decodificación de audio en Python 3.12.

## Ejecución

Desde la raíz del proyecto:

```bat
python -m app.main
```

Si estás utilizando el entorno virtual:

```bat
.venv\Scripts\python.exe -m app.main
```

También existe un lanzador PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File tools\run.ps1
```

El menú pertenece a la aplicación Python; no existe un `run.bat`.

## Estructura principal

```text
app/
├── main.py
├── core/
│   ├── audio.py
│   ├── browser.py
│   ├── jobs.py
│   ├── pipeline.py
│   └── transcribe.py
└── providers/
    ├── base.py
    ├── ytdlp.py
    ├── zoom.py
    └── youtube.py

tools/
└── run.ps1

output/
data/
temp/
logs/
private/
```

Los directorios generados en tiempo de ejecución se crean automáticamente y no se versionan.

## Trabajos y resultados

Cada nueva URL obtiene un número consecutivo:

```text
output/
├── 001_zoom_clase-de-redes/
├── 002_youtube_python-networking/
└── 003_zoom_reunion-proyecto/
```

Cada trabajo puede contener:

```text
video.mp4
audio.mp3
<NOMBRE>.txt
<NOMBRE>.srt
<NOMBRE>.vtt
metadata.json
```

El nombre solicitado al iniciar el trabajo se utiliza como base para los archivos de transcripción. Los caracteres no válidos para nombres de archivo se reemplazan automáticamente.

El archivo global:

```text
data/jobs.json
```

mantiene la numeración, permite detectar URLs ya procesadas y reanudar trabajos incompletos.

Si una URL ya fue completada, Transcribe no vuelve a descargarla automáticamente. Si quedó interrumpida o fallida, la siguiente ejecución reutiliza el mismo trabajo.

## Transcripción

Configuración predeterminada:

- modelo: `medium`;
- idioma: detección automática;
- GPU: preferida;
- CUDA: `int8_float16`;
- batch inicial: 4;
- fallback: CPU `int8`.

El programa conserva el MP3 y utiliza FLAC mono a 16 kHz únicamente como entrada temporal de Whisper.

## Configuración

`config.json`:

```json
{
  "whisper_model": "medium",
  "language": "auto",
  "browser": "chrome",
  "browser_priority": ["chrome", "edge", "opera", "firefox"],
  "prefer_gpu": true,
  "delete_temporary_audio": true,
  "max_video_height": 720,
  "batch_size": 4
}
```

Para forzar español:

```json
"language": "es"
```

## Privacidad

Transcribe no almacena contraseñas.

Los datos sensibles de sesión quedan bajo `private/`, que está ignorado por Git. Los videos, MP3, transcripciones, logs y metadata de trabajos también quedan fuera del repositorio.
