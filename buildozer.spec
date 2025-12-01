# buildozer.spec
# Configurazione per build Android

[app]

# Nome dell'app
title = University Manager

# Nome del package (identifica l'app univocamente)
package.name = universitymanager
package.domain = com.unimanager

# Directory sorgente
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,db,ttf

# Versione app
version = 1.0

# Requisiti Python
requirements = python3,kivy==2.3.0,kivymd==1.2.0,sqlite3,numpy,pandas

# Orientamento schermo
orientation = portrait

# Permessi Android
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,INTERNET

# API levels
android.api = 33
android.minapi = 21
android.ndk = 25b

# Icona e splash screen
#icon.filename = %(source.dir)s/assets/icon.png
#presplash.filename = %(source.dir)s/assets/splash.png

# Architetture supportate
android.archs = arm64-v8a,armeabi-v7a

# Accept SDK license
android.accept_sdk_license = True

# Bootstrap
p4a.bootstrap = sdl2

# Colori tema
android.presplash_color = #1976D2

[buildozer]

# Log level (2 = info)
log_level = 2

# Avviso se eseguito come root
warn_on_root = 1