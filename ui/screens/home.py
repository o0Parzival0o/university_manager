# ui/screens/home.py
"""
Schermata home dell'applicazione
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle


class HomeScreen(Screen):
    """Schermata principale con menu"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        """Costruisce l'interfaccia"""
        # Layout principale
        layout = BoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(15)
        )
        
        # Header con titolo
        self.add_header(layout)
        
        # Card con statistiche veloci
        self.add_stats_card(layout)
        
        # Grid con bottoni menu
        self.add_menu_buttons(layout)
        
        # Footer con info
        self.add_footer(layout)
        
        self.add_widget(layout)
    
    def add_header(self, parent):
        """Aggiunge l'header con titolo"""
        header = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(120),
            spacing=dp(5)
        )
        
        # Titolo principale
        title = MDLabel(
            text="University Manager",
            halign="center",
            font_style="H4",
            theme_text_color="Primary"
        )
        header.add_widget(title)
        
        # Sottotitolo
        subtitle = MDLabel(
            text="Il tuo assistente universitario",
            halign="center",
            font_style="Caption",
            theme_text_color="Secondary"
        )
        header.add_widget(subtitle)
        
        parent.add_widget(header)
    
    def add_stats_card(self, parent):
        """Aggiunge una card con statistiche rapide"""
        card = MDCard(
            orientation='vertical',
            padding=dp(15),
            spacing=dp(10),
            size_hint_y=None,
            height=dp(150),
            elevation=3,
            radius=[15]
        )
        
        # Titolo card
        card_title = MDLabel(
            text="📊 Panoramica",
            font_style="H6",
            size_hint_y=None,
            height=dp(30)
        )
        card.add_widget(card_title)
        
        # Stats grid
        stats_grid = GridLayout(
            cols=3,
            spacing=dp(10),
            size_hint_y=None,
            height=dp(80)
        )
        
        # Prendi statistiche dall'app
        app = self.get_app()
        
        # Conta lauree
        num_lauree = len(app.lauree) if hasattr(app, 'lauree') else 0
        
        # Media attuale (se c'è una laurea selezionata)
        media_text = "---"
        if app.current_laurea:
            voti = app.db.get_voti_by_laurea(app.current_laurea.id)
            if voti:
                media = app.calculator.calcola_media(voti)
                media_text = f"{media:.2f}"
        
        # Tasse non pagate
        tasse_non_pagate = len(app.db.get_tasse_non_pagate())
        
        # Aggiungi stat boxes
        self.add_stat_box(stats_grid, "Corsi", str(num_lauree), "📚")
        self.add_stat_box(stats_grid, "Media", media_text, "🎯")
        self.add_stat_box(stats_grid, "Tasse", str(tasse_non_pagate), "💰")
        
        card.add_widget(stats_grid)
        parent.add_widget(card)
    
    def add_stat_box(self, parent, label, value, emoji):
        """Aggiunge un box con una statistica"""
        box = BoxLayout(orientation='vertical', spacing=dp(5))
        
        emoji_label = MDLabel(
            text=emoji,
            halign="center",
            font_style="H5"
        )
        box.add_widget(emoji_label)
        
        value_label = MDLabel(
            text=value,
            halign="center",
            font_style="H6",
            theme_text_color="Primary"
        )
        box.add_widget(value_label)
        
        label_label = MDLabel(
            text=label,
            halign="center",
            font_style="Caption",
            theme_text_color="Secondary"
        )
        box.add_widget(label_label)
        
        parent.add_widget(box)
    
    def add_menu_buttons(self, parent):
        """Aggiunge i bottoni del menu principale"""
        # Grid per bottoni
        grid = GridLayout(
            cols=1,
            spacing=dp(10),
            size_hint_y=None
        )
        grid.bind(minimum_height=grid.setter('height'))
        
        # Definizione bottoni menu
        menu_items = [
            {
                'text': '📚 Gestione Voti',
                'description': 'Visualizza e gestisci i tuoi voti',
                'screen': 'lauree',
                'color': [0.13, 0.59, 0.95, 1]  # Blue
            },
            {
                'text': '💰 Tasse Universitarie',
                'description': 'Monitora scadenze e pagamenti',
                'screen': 'tasse',
                'color': [1, 0.6, 0, 1]  # Orange
            },
            {
                'text': '📝 Domande Esame',
                'description': 'Organizza domande e materiale di studio',
                'screen': 'domande',
                'color': [0.61, 0.15, 0.69, 1]  # Purple
            }
        ]
        
        for item in menu_items:
            btn = self.create_menu_button(
                item['text'],
                item['description'],
                item['screen'],
                item['color']
            )
            grid.add_widget(btn)
        
        parent.add_widget(grid)
    
    def create_menu_button(self, text, description, screen, color):
        """Crea un bottone menu con stile card"""
        # Card container
        card = MDCard(
            orientation='vertical',
            padding=dp(15),
            size_hint_y=None,
            height=dp(90),
            elevation=2,
            radius=[10],
            ripple_behavior=True
        )
        
        # Colora il background
        with card.canvas.before:
            Color(*color)
            self.rect = RoundedRectangle(
                size=card.size,
                pos=card.pos,
                radius=[dp(10)]
            )
        
        card.bind(size=self._update_rect, pos=self._update_rect)
        
        # Layout interno
        inner_layout = BoxLayout(orientation='vertical', spacing=dp(5))
        
        # Titolo
        title = MDLabel(
            text=text,
            font_style="H6",
            theme_text_color="Custom",
            text_color=[1, 1, 1, 1],
            size_hint_y=None,
            height=dp(30)
        )
        inner_layout.add_widget(title)
        
        # Descrizione
        desc = MDLabel(
            text=description,
            font_style="Caption",
            theme_text_color="Custom",
            text_color=[1, 1, 1, 0.8],
            size_hint_y=None,
            height=dp(20)
        )
        inner_layout.add_widget(desc)
        
        card.add_widget(inner_layout)
        
        # Bind touch per navigazione
        card.bind(on_release=lambda x: self.navigate_to(screen))
        
        return card
    
    def _update_rect(self, instance, value):
        """Aggiorna il rettangolo colorato quando la card cambia dimensioni"""
        if hasattr(self, 'rect'):
            self.rect.pos = instance.pos
            self.rect.size = instance.size
    
    def add_footer(self, parent):
        """Aggiunge il footer con info e settings"""
        footer = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(60),
            spacing=dp(10),
            padding=[0, dp(10), 0, 0]
        )
        
        # Bottone settings
        settings_btn = MDIconButton(
            icon="cog",
            on_release=self.open_settings
        )
        footer.add_widget(settings_btn)
        
        # Spacer
        footer.add_widget(BoxLayout())
        
        # Bottone info
        info_btn = MDIconButton(
            icon="information",
            on_release=self.show_info
        )
        footer.add_widget(info_btn)
        
        # Bottone backup
        backup_btn = MDIconButton(
            icon="cloud-upload",
            on_release=self.create_backup
        )
        footer.add_widget(backup_btn)
        
        parent.add_widget(footer)
    
    def navigate_to(self, screen_name):
        """Naviga a una schermata specifica"""
        app = self.get_app()
        app.go_to_screen(screen_name)
    
    def open_settings(self, instance):
        """Apre le impostazioni"""
        app = self.get_app()
        app.show_snackbar("⚙️ Impostazioni in arrivo!")
    
    def show_info(self, instance):
        """Mostra informazioni sull'app"""
        app = self.get_app()
        app.show_snackbar("ℹ️ University Manager v1.0 - Made with ❤️")
    
    def create_backup(self, instance):
        """Crea un backup dei dati"""
        app = self.get_app()
        app.create_backup()
    
    def get_app(self):
        """Ottiene l'istanza dell'app"""
        from kivymd.app import MDApp
        return MDApp.get_running_app()
    
    def on_enter(self):
        """Chiamato quando si entra nella schermata"""
        # Aggiorna le statistiche
        app = self.get_app()
        app.refresh_lauree()