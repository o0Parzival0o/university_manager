# ui/screens/domande.py
"""
Schermata gestione domande d'esame
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.list import MDList, TwoLineAvatarIconListItem, IconLeftWidget, IconRightWidget
from kivymd.uix.menu import MDDropdownMenu
from kivy.metrics import dp
from kivymd.app import MDApp


class DomandeScreen(Screen):
    """Schermata gestione domande d'esame"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.selected_materia = None
        self.selected_anno = None
        self.materia_menu = None
        self.anno_menu = None
        self.difficolta_menu = None
        self.selected_difficolta = None
        self.build_ui()
    
    def build_ui(self):
        """Costruisce l'interfaccia"""
        layout = BoxLayout(orientation='vertical')
        
        # Header
        header = self.create_header()
        layout.add_widget(header)
        
        # Filtri
        filters = self.create_filters()
        layout.add_widget(filters)
        
        # Lista domande
        self.scroll = ScrollView()
        self.domande_list = MDList()
        self.scroll.add_widget(self.domande_list)
        layout.add_widget(self.scroll)
        
        # Bottone add
        add_btn = MDRaisedButton(
            text="➕ Aggiungi Domanda",
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
        """Crea l'header"""
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(60),
            padding=[dp(10), dp(10), dp(10), 0]
        )
        
        back_btn = MDIconButton(
            icon="arrow-left",
            on_release=lambda x: self.get_app().go_back()
        )
        header.add_widget(back_btn)
        
        title = MDLabel(
            text="Domande d'Esame",
            font_style="H5",
            halign="left"
        )
        header.add_widget(title)
        
        return header
    
    def create_filters(self):
        """Crea i filtri"""
        filters = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(60),
            padding=dp(10),
            spacing=dp(10)
        )
        
        # Bottone materia
        self.materia_btn = MDRaisedButton(
            text="Materia: Tutte",
            size_hint_x=0.5,
            on_release=self.show_materia_menu
        )
        filters.add_widget(self.materia_btn)
        
        # Bottone anno
        self.anno_btn = MDRaisedButton(
            text="Anno: Tutti",
            size_hint_x=0.5,
            on_release=self.show_anno_menu
        )
        filters.add_widget(self.anno_btn)
        
        return filters
    
    def show_materia_menu(self, instance):
        """Mostra menu materie"""
        app = self.get_app()
        materie = app.db.get_all_materie()
        
        menu_items = [
            {
                "text": "Tutte",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.select_materia(None)
            }
        ]
        
        for materia in materie:
            menu_items.append({
                "text": materia,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=materia: self.select_materia(x)
            })
        
        self.materia_menu = MDDropdownMenu(
            caller=instance,
            items=menu_items,
            width_mult=4
        )
        self.materia_menu.open()
    
    def select_materia(self, materia):
        """Seleziona una materia"""
        self.selected_materia = materia
        self.materia_btn.text = f"Materia: {materia or 'Tutte'}"
        if self.materia_menu:
            self.materia_menu.dismiss()
        self.refresh_list()
    
    def show_anno_menu(self, instance):
        """Mostra menu anni"""
        app = self.get_app()
        anni = app.db.get_all_anni()
        
        menu_items = [
            {
                "text": "Tutti",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.select_anno(None)
            }
        ]
        
        for anno in anni:
            menu_items.append({
                "text": anno,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=anno: self.select_anno(x)
            })
        
        self.anno_menu = MDDropdownMenu(
            caller=instance,
            items=menu_items,
            width_mult=3
        )
        self.anno_menu.open()
    
    def select_anno(self, anno):
        """Seleziona un anno"""
        self.selected_anno = anno
        self.anno_btn.text = f"Anno: {anno or 'Tutti'}"
        if self.anno_menu:
            self.anno_menu.dismiss()
        self.refresh_list()
    
    def on_enter(self):
        """Aggiorna quando si entra"""
        self.refresh_list()
    
    def refresh_list(self):
        """Aggiorna lista domande"""
        self.domande_list.clear_widgets()
        app = self.get_app()
        
        # Filtra domande
        if self.selected_materia:
            domande = app.db.get_domande_by_materia(
                self.selected_materia,
                self.selected_anno
            )
        else:
            # Prendi tutte le domande
            materie = app.db.get_all_materie()
            domande = []
            for materia in materie:
                domande.extend(app.db.get_domande_by_materia(materia, self.selected_anno))
        
        if not domande:
            empty_label = MDLabel(
                text="Nessuna domanda trovata.\nAggiungi la tua prima domanda!",
                halign="center",
                theme_text_color="Secondary"
            )
            self.domande_list.add_widget(empty_label)
        else:
            for domanda in domande:
                item = self.create_domanda_item(domanda)
                self.domande_list.add_widget(item)
    
    def create_domanda_item(self, domanda):
        """Crea un item per una domanda"""
        item = TwoLineAvatarIconListItem(
            text=f"{domanda.difficolta_emoji} {domanda.testo[:50]}...",
            secondary_text=f"{domanda.materia} • {domanda.anno}",
            on_release=lambda x: self.show_domanda_detail(domanda)
        )
        
        # Icona
        icon_widget = IconLeftWidget(icon="file-document-outline")
        item.add_widget(icon_widget)
        
        # Bottone elimina
        delete_btn = IconRightWidget(
            icon="delete",
            on_release=lambda x: self.confirm_delete_domanda(domanda)
        )
        item.add_widget(delete_btn)
        
        return item
    
    def show_domanda_detail(self, domanda):
        """Mostra dettaglio domanda"""
        if self.dialog:
            self.dialog.dismiss()
        
        content = MDLabel(
            text=domanda.testo,
            size_hint_y=None,
            height=dp(200)
        )
        
        self.dialog = MDDialog(
            title=f"{domanda.materia} ({domanda.anno})",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CHIUDI",
                    on_release=lambda x: self.dialog.dismiss()
                )
            ]
        )
        self.dialog.open()
    
    def show_add_dialog(self, instance):
        """Mostra dialog per aggiungere domanda"""
        if self.dialog:
            self.dialog.dismiss()
        
        self.materia_field = MDTextField(
            hint_text="Materia",
            required=True
        )
        
        self.anno_field = MDTextField(
            hint_text="Anno (es. 2024/25)",
            required=True
        )
        
        self.testo_field = MDTextField(
            hint_text="Testo della domanda",
            multiline=True,
            required=True
        )
        
        # Bottone difficoltà
        self.difficolta_btn = MDRaisedButton(
            text="Difficoltà: Non specificata",
            on_release=self.show_difficolta_menu
        )
        
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(280)
        )
        content.add_widget(self.materia_field)
        content.add_widget(self.anno_field)
        content.add_widget(self.testo_field)
        content.add_widget(self.difficolta_btn)
        
        self.dialog = MDDialog(
            title="Nuova Domanda",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="ANNULLA",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="AGGIUNGI",
                    on_release=self.add_domanda
                )
            ]
        )
        self.dialog.open()
    
    def show_difficolta_menu(self, instance):
        """Mostra menu difficoltà"""
        menu_items = [
            {
                "text": "🟢 Facile",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.select_difficolta("facile")
            },
            {
                "text": "🟡 Media",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.select_difficolta("media")
            },
            {
                "text": "🔴 Difficile",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.select_difficolta("difficile")
            }
        ]
        
        self.difficolta_menu = MDDropdownMenu(
            caller=instance,
            items=menu_items,
            width_mult=3
        )
        self.difficolta_menu.open()
    
    def select_difficolta(self, difficolta):
        """Seleziona difficoltà"""
        self.selected_difficolta = difficolta
        emoji = {"facile": "🟢", "media": "🟡", "difficile": "🔴"}
        self.difficolta_btn.text = f"Difficoltà: {emoji[difficolta]} {difficolta.capitalize()}"
        if self.difficolta_menu:
            self.difficolta_menu.dismiss()
    
    def add_domanda(self, instance):
        """Aggiunge una domanda"""
        materia = self.materia_field.text.strip()
        anno = self.anno_field.text.strip()
        testo = self.testo_field.text.strip()
        
        if not materia or not anno or not testo:
            self.get_app().show_snackbar("❌ Compila tutti i campi obbligatori")
            return
        
        try:
            app = self.get_app()
            app.db.add_domanda(
                materia=materia,
                anno=anno,
                testo=testo,
                difficolta=self.selected_difficolta
            )
            
            self.dialog.dismiss()
            self.refresh_list()
            app.show_snackbar(f"✅ Domanda aggiunta")
            
        except Exception as e:
            self.get_app().show_snackbar(f"❌ Errore: {str(e)}")
    
    def confirm_delete_domanda(self, domanda):
        """Conferma eliminazione domanda"""
        if self.dialog:
            self.dialog.dismiss()
        
        self.dialog = MDDialog(
            title="Elimina Domanda",
            text=f"Vuoi eliminare questa domanda?",
            buttons=[
                MDFlatButton(
                    text="ANNULLA",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="ELIMINA",
                    on_release=lambda x: self.delete_domanda(domanda)
                )
            ]
        )
        self.dialog.open()
    
    def delete_domanda(self, domanda):
        """Elimina una domanda"""
        app = self.get_app()
        app.db.delete_domanda(domanda.id)
        
        self.dialog.dismiss()
        self.refresh_list()
        app.show_snackbar(f"🗑️ Domanda eliminata")
    
    def get_app(self):
        return MDApp.get_running_app()