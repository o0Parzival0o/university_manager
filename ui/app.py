# ui/app.py
"""
Applicazione principale KivyMD
"""

from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.snackbar import Snackbar
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from datetime import datetime

from core.database import Database
from core.calculator import CalcolatoreVoti
from ui.screens.home import HomeScreen
from ui.screens.lauree import LaureeScreen
from ui.screens.voti import VotiScreen
from ui.screens.tasse import TasseScreen
from ui.screens.domande import DomandeScreen


class UniversityManagerApp(MDApp):
    """Applicazione principale"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "University Manager"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.primary_hue = "700"
        self.theme_cls.theme_style = "Light"
        self.theme_cls.material_style = "M3"
        
        # Database
        self.db = Database()
        
        # Calculator
        self.calculator = CalcolatoreVoti()
        
        # Stato applicazione
        self.current_laurea = None
        self.lauree = []
        
        # Screen manager
        self.sm = None
    
    def build(self):
        """Costruisce l'interfaccia"""
        # Configura finestra (per desktop)
        Window.size = (400, 700)
        Window.minimum_width = 350
        Window.minimum_height = 600
        
        # Crea screen manager
        self.sm = ScreenManager(transition=SlideTransition())
        
        # Aggiungi schermate
        self.sm.add_widget(HomeScreen(name='home'))
        self.sm.add_widget(LaureeScreen(name='lauree'))
        self.sm.add_widget(VotiScreen(name='voti'))
        self.sm.add_widget(TasseScreen(name='tasse'))
        self.sm.add_widget(DomandeScreen(name='domande'))
        
        # Carica dati iniziali
        self.refresh_lauree()
        
        return self.sm
    
    def go_to_screen(self, screen_name, direction='left'):
        """Naviga a una schermata"""
        self.sm.transition.direction = direction
        self.sm.current = screen_name
    
    def go_back(self):
        """Torna alla schermata precedente"""
        self.go_to_screen('home', direction='right')
    
    def refresh_lauree(self):
        """Ricarica la lista delle lauree"""
        self.lauree = self.db.get_all_lauree()
        
        # Se c'è una sola laurea, selezionala automaticamente
        if len(self.lauree) == 1 and self.current_laurea is None:
            self.current_laurea = self.lauree[0]
    
    def show_snackbar(self, text, duration=2):
        """Mostra un messaggio snackbar"""
        Snackbar(
            text=text,
            snackbar_x="10dp",
            snackbar_y="10dp",
            duration=duration
        ).open()
    
    def create_backup(self):
        """Crea un backup del database"""
        try:
            backup_path = self.db.backup_database()
            self.show_snackbar(f"✅ Backup creato: {backup_path}")
        except Exception as e:
            self.show_snackbar(f"❌ Errore backup: {str(e)}")
    
    def on_stop(self):
        """Chiude il database quando l'app si chiude"""
        self.db.close()