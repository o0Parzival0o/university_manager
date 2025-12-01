# main.py
"""
University Manager - Entry Point
Avvia l'applicazione multi-platform (Desktop e Android)
"""

import os
import sys
from pathlib import Path

# Aggiungi la directory root al path
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

from ui.app import UniversityManagerApp


def main():
    """Entry point dell'applicazione"""
    app = UniversityManagerApp()
    app.run()


if __name__ == '__main__':
    main()