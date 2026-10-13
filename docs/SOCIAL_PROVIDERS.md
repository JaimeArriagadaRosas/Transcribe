# TikTok e Instagram

Los dos proveedores utilizan el mismo entorno virtual y motor `faster-whisper` del proyecto. No requieren descargar aplicaciones de TikTok ni Instagram. Para actualizar el extractor:

```bat
.venv\Scripts\python.exe -m pip install -U "yt-dlp[default]"
```

Ejecuta `transcribe.cmd`, selecciona **3) TikTok** o **4) Instagram**, pega un enlace y escribe un nombre.

## TikTok

Acepta URLs `www.tiktok.com/@usuario/video/ID` y enlaces compartidos `vm.tiktok.com`, `vt.tiktok.com` o `www.tiktok.com/t/...`. Se intenta acceso público antes de una sesión local autorizada. Los enlaces de fotografías y directos no están incluidos.

## Instagram

Acepta `/reel/ID/`, `/p/ID/`, `/tv/ID/` y `/stories/usuario/ID/`. Puede procesar múltiples archivos de video de una misma publicación. Para un carrusel los archivos de transcripción llevan sufijos `_01`, `_02`, etc. Las imágenes estáticas no se transcriben. Las historias pueden requerir sesión y pueden no estar disponibles después de expirar.

## Sesiones y privacidad

Solo intenta usar la sesión autorizada del navegador si la comprobación pública indica un problema de acceso. Nunca introduzcas credenciales de TikTok o Instagram en la consola. El mecanismo compartido exporta cookies desde el navegador a `private/<plataforma>.cookies.txt`, un directorio excluido de Git; esas exportaciones **pueden contener cookies de otros sitios web**, por lo que deben tratarse como secretos locales y nunca compartirse. Se recomienda eliminar archivos de cookies cuando ya no se necesiten.

Los errores de límites de solicitudes y extractor no se resuelven automáticamente con cookies. Usa únicamente publicaciones a las que tengas autorización de acceso.

## Pruebas sin descargas reales

```bat
.venv\Scripts\python.exe -m unittest tests.test_social_providers tests.test_providers
```

El soporte depende de cambios externos a yt-dlp, TikTok e Instagram. No se garantiza acceso a contenido privado ni a videos que las plataformas no permitan obtener.
