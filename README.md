# University Manager 📚

Applicazione multi-platform per la gestione della carriera universitaria.

## ✨ Funzionalità

- **Gestione Voti**: Registra e monitora i tuoi voti
  - Calcolo automatico della media ponderata
  - Proiezione voto di laurea
  - Statistiche dettagliate
  
- **Tasse Universitarie**: Tieni traccia delle scadenze
  - Promemoria scadenze
  - Stato pagamenti
  - Riepilogo importi

- **Domande d'Esame**: Organizza il materiale di studio
  - Cataloga domande per materia e anno
  - Sistema di difficoltà
  - Ricerca e filtri

## 🚀 Installazione

### Desktop (Windows/Mac/Linux)
```bash
# Clona il repository
git clone https://github.com/tuousername/university-manager.git
cd university-manager

# Installa dipendenze
pip install -r requirements.txt

# Avvia l'app
python main.py
```

### Android
```bash
# Installa Buildozer
pip install buildozer

# Build APK
buildozer android debug

# Output in: bin/universitymanager-1.0-debug.apk
```

## 📁 Struttura Progetto
````
university_manager/
├── main.py                 # Entry point
├── requirements.txt        # Dipendenze
├── buildozer.spec         # Config Android
├── core/                  # Logica business
│   ├── models.py          # Modelli dati
│   ├── database.py        # Database SQLite
│   └── calculator.py      # Calcoli statistiche
├── ui/                    # Interfaccia utente
│   ├── app.py             # App Kivy principale
│   └── screens/           # Schermate
│       ├── home.py
│       ├── lauree.py
│       ├── voti.py
│       ├── tasse.py
│       └── domande.py
└── utils/                 # Utilities
    ├── validators.py
    └── exporters.py

## 💾 Database

L'applicazione utilizza **SQLite** per memorizzare i dati in locale.  
Il file del database viene creato automaticamente in:

- **Desktop:** `~/UniversityManager/university_manager.db`  
- **Android:** `/data/data/com.unimanager.universitymanager/`

---

## 🛠️ Tecnologie

- **Kivy** – Framework UI multi-platform  
- **KivyMD** – Componenti Material Design  
- **SQLite** – Database locale  
- **NumPy** – Calcoli statistici  
- **Pandas** – Esportazione dati  

---

## 📱 Compatibilità

- ✅ **Windows 10/11**  
- ✅ **macOS 10.14+**  
- ✅ **Linux** (Ubuntu, Debian, Fedora)  
- ✅ **Android 5.0+ (API 21+)**

---

## 📄 Licenza

MIT License – vedi il file `LICENSE`.

---

## 👨‍💻 Autore

Creato con ❤️ per studenti universitari.

---

## 🤝 Contributi

I contributi sono benvenuti!  
Apri una **issue** o una **pull request**.
