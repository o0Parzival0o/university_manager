# ui/screens/lauree.py
"""
Schermata gestione corsi di laurea
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.list import MDList, TwoLineAvatarIconListItem, IconLeftWidget, IconRightWidget
from kivy.metrics import dp
from kivymd.app import MDApp


class LaureeScreen(Screen):
    """Schermata per gestire i corsi di laurea"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.build_ui()
    
    def build_ui(self):
        """Costruisce l'interfaccia"""
        layout = BoxLayout(orientation='vertical')
        
        # Header
        header = self.create_header()
        layout.add_widget(header)
        
        # Lista lauree (scrollable)
        self.scroll = ScrollView()
        self.lauree_list = MDList()
        self.scroll.add_widget(self.lauree_list)
        layout.add_widget(self.scroll)
        
        # Bottone add
        add_btn = MDRaisedButton(
            text="➕ Aggiungi Corso",
            pos_hint={'center_x': 0.5},
            size_hint=(0.9, None),
            height=dp(50),
            on_release=self.show_add_dialog
        )
        
        btn_container = BoxLayout(
            size_hint_y=None,
            height=dp(70),
            padding=dp(10)
        )
        btn_container.add_widget(add_btn)
        layout.add_widget(btn_container)
        
        self.add_widget(layout)
    
    def create_header(self):
        """Crea l'header della schermata"""
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(60),
            padding=[dp(10), dp(10), dp(10), 0]
        )
        
        # Bottone back
        back_btn = MDIconButton(
            icon="arrow-left",
            on_release=lambda x: self.get_app().go_back()
        )
        header.add_widget(back_btn)
        
        # Titolo
        title = MDLabel(
            text="I Miei Corsi",
            font_style="H5",
            halign="left"
        )
        header.add_widget(title)
        
        return header
    
    def on_enter(self):
        """Aggiorna lista quando si entra nella schermata"""
        self.refresh_list()
    
    def refresh_list(self):
        """Aggiorna la lista delle lauree"""
        self.lauree_list.clear_widgets()
        app = self.get_app()
        app.refresh_lauree()
        
        if not app.lauree:
            # Nessuna laurea
            empty_label = MDLabel(
                text="Nessun corso di laurea.\nAggiungi il tuo primo corso!",
                halign="center",
                theme_text_color="Secondary"
            )
            self.lauree_list.add_widget(empty_label)
        else:
            for laurea in app.lauree:
                item = self.create_laurea_item(laurea)
                self.lauree_list.add_widget(item)
    
    def create_laurea_item(self, laurea):
        """Crea un item per una laurea"""
        # Conta voti
        app = self.get_app()
        voti = app.db.get_voti_by_laurea(laurea.id)
        num_voti = len(voti)
        
        # Calcola crediti
        crediti_acquisiti = sum(v.crediti for v in voti)
        
        item = TwoLineAvatarIconListItem(
            text=laurea.nome,
            secondary_text=f"{laurea.tipo_display} • {num_voti} esami • {crediti_acquisiti}/{laurea.crediti_totali} CFU",
            on_release=lambda x: self.open_voti(laurea)
        )
        
        # Icona
        icon_widget = IconLeftWidget(
            icon="school" if laurea.tipo == "triennale" else "school-outline"
        )
        item.add_widget(icon_widget)
        
        # Bottone elimina
        delete_btn = IconRightWidget(
            icon="delete",
            on_release=lambda x: self.confirm_delete(laurea)
        )
        item.add_widget(delete_btn)
        
        return item
    
    def open_voti(self, laurea):
        """Apre la schermata voti per una laurea"""
        app = self.get_app()
        app.current_laurea = laurea
        app.go_to_screen('voti')
    
    def show_add_dialog(self, instance):
        """Mostra dialog per aggiungere laurea"""
        if self.dialog:
            self.dialog.dismiss()
        
        # Campi input
        self.nome_field = MDTextField(
            hint_text="Nome corso (es. Informatica)",
            required=True
        )
        
        self.crediti_field = MDTextField(
            hint_text="Crediti totali",
            text="180",
            input_filter="int"
        )
        
        # Switch tipo
        switch_box = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=dp(10)
        )
        switch_box.add_widget(MDLabel(text="Magistrale", size_hint_x=0.7))
        self.tipo_switch = MDSwitch()
        switch_box.add_widget(self.tipo_switch)
        
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(180)
        )
        content.add_widget(self.nome_field)
        content.add_widget(self.crediti_field)
        content.add_widget(switch_box)
        
        self.dialog = MDDialog(
            title="Nuovo Corso di Laurea",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="ANNULLA",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="AGGIUNGI",
                    on_release=self.add_laurea
                )
            ]
        )
        self.dialog.open()
    
    def add_laurea(self, instance):
        """Aggiunge una nuova laurea"""
        nome = self.nome_field.text.strip()
        
        if not nome:
            self.get_app().show_snackbar("❌ Inserisci un nome")
            return
        
        try:
            crediti = int(self.crediti_field.text or "180")
            tipo = "magistrale" if self.tipo_switch.active else "triennale"
            
            app = self.get_app()
            app.db.add_laurea(nome, tipo, crediti)
            
            self.dialog.dismiss()
            self.refresh_list()
            app.show_snackbar(f"✅ {nome} aggiunto!")
            
        except ValueError as e:
            app = self.get_app()
            app.show_snackbar(f"❌ {str(e)}")
        except Exception as e:
            app = self.get_app()
            app.show_snackbar(f"❌ Errore: {str(e)}")
    
    def confirm_delete(self, laurea):
        """Conferma eliminazione laurea"""
        if self.dialog:
            self.dialog.dismiss()
        
        self.dialog = MDDialog(
            title="Elimina Corso",
            text=f"Vuoi eliminare '{laurea.nome}'?\nVerranno eliminati anche tutti i voti associati.",
            buttons=[
                MDFlatButton(
                    text="ANNULLA",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="ELIMINA",
                    on_release=lambda x: self.delete_laurea(laurea)
                )
            ]
        )
        self.dialog.open()
    
    def delete_laurea(self, laurea):
        """Elimina una laurea"""
        app = self.get_app()
        app.db.delete_laurea(laurea.id)
        
        if app.current_laurea and app.current_laurea.id == laurea.id:
            app.current_laurea = None
        
        self.dialog.dismiss()
        self.refresh_list()
        app.show_snackbar(f"🗑️ {laurea.nome} eliminato")
    
    def get_app(self):
        """Ottiene l'istanza dell'app"""
        return MDApp.get_running_app()