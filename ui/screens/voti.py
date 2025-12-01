# ui/screens/voti.py
"""
Schermata gestione voti
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.list import MDList, ThreeLineAvatarIconListItem, IconLeftWidget, IconRightWidget
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.menu import MDDropdownMenu
from kivy.metrics import dp
from kivymd.app import MDApp
from datetime import datetime


class VotiScreen(Screen):
    """Schermata gestione voti"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.date_picker = None
        self.selected_date = datetime.now()
        self.voto_menu = None
        self.selected_voto = 18
        self.build_ui()
    
    def build_ui(self):
        """Costruisce l'interfaccia"""
        self.main_layout = BoxLayout(orientation='vertical')
        
        # Header
        header = self.create_header()
        self.main_layout.add_widget(header)
        
        # Card statistiche
        self.stats_card = self.create_stats_card()
        self.main_layout.add_widget(self.stats_card)
        
        # Lista voti
        self.scroll = ScrollView()
        self.voti_list = MDList()
        self.scroll.add_widget(self.voti_list)
        self.main_layout.add_widget(self.scroll)
        
        # Bottone add
        add_btn = MDRaisedButton(
            text="➕ Aggiungi Voto",
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
        self.main_layout.add_widget(btn_container)
        
        self.add_widget(self.main_layout)
    
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
        
        self.title_label = MDLabel(
            text="Voti",
            font_style="H5",
            halign="left"
        )
        header.add_widget(self.title_label)
        
        # Menu azioni
        menu_btn = MDIconButton(
            icon="dots-vertical",
            on_release=self.show_menu
        )
        header.add_widget(menu_btn)
        
        return header
    
    def create_stats_card(self):
        """Crea la card con le statistiche"""
        card = MDCard(
            orientation='vertical',
            padding=dp(15),
            spacing=dp(10),
            size_hint=(0.95, None),
            height=dp(140),
            pos_hint={'center_x': 0.5},
            elevation=3,
            radius=[15]
        )
        
        # Titolo
        title = MDLabel(
            text="📊 Statistiche",
            font_style="H6",
            size_hint_y=None,
            height=dp(30)
        )
        card.add_widget(title)
        
        # Grid statistiche
        self.stats_grid = GridLayout(
            cols=3,
            spacing=dp(10),
            size_hint_y=None,
            height=dp(80)
        )
        card.add_widget(self.stats_grid)
        
        return card
    
    def update_stats(self):
        """Aggiorna le statistiche"""
        self.stats_grid.clear_widgets()
        
        app = self.get_app()
        if not app.current_laurea:
            return
        
        voti = app.db.get_voti_by_laurea(app.current_laurea.id)
        
        if voti:
            stats = app.calculator.calcola_statistiche(voti, app.current_laurea)
            
            self.add_stat_box(self.stats_grid, "Media", f"{stats.media:.2f}", "🎯")
            self.add_stat_box(self.stats_grid, "Voto Laurea", f"{stats.voto_laurea}/110", "🎓")
            self.add_stat_box(self.stats_grid, "Crediti", f"{stats.crediti_acquisiti}/{stats.crediti_totali}", "📚")
        else:
            self.add_stat_box(self.stats_grid, "Media", "---", "🎯")
            self.add_stat_box(self.stats_grid, "Voto Laurea", "---", "🎓")
            self.add_stat_box(self.stats_grid, "Crediti", "0/180", "📚")
    
    def add_stat_box(self, parent, label, value, emoji):
        """Aggiunge un box statistica"""
        box = BoxLayout(orientation='vertical', spacing=dp(5))
        
        emoji_label = MDLabel(text=emoji, halign="center", font_style="H6")
        box.add_widget(emoji_label)
        
        value_label = MDLabel(text=value, halign="center", font_style="Body1", theme_text_color="Primary")
        box.add_widget(value_label)
        
        label_label = MDLabel(text=label, halign="center", font_style="Caption", theme_text_color="Secondary")
        box.add_widget(label_label)
        
        parent.add_widget(box)
    
    def on_enter(self):
        """Aggiorna quando si entra nella schermata"""
        app = self.get_app()
        
        if not app.current_laurea:
            app.show_snackbar("⚠️ Seleziona prima un corso di laurea")
            app.go_back()
            return
        
        self.title_label.text = app.current_laurea.nome
        self.refresh_list()
        self.update_stats()
    
    def refresh_list(self):
        """Aggiorna lista voti"""
        self.voti_list.clear_widgets()
        app = self.get_app()
        
        if not app.current_laurea:
            return
        
        voti = app.db.get_voti_by_laurea(app.current_laurea.id)
        
        if not voti:
            empty_label = MDLabel(
                text="Nessun voto registrato.\nAggiungi il tuo primo voto!",
                halign="center",
                theme_text_color="Secondary"
            )
            self.voti_list.add_widget(empty_label)
        else:
            for voto in reversed(voti):  # Più recenti prima
                item = self.create_voto_item(voto)
                self.voti_list.add_widget(item)
    
    def create_voto_item(self, voto):
        """Crea un item per un voto"""
        item = ThreeLineAvatarIconListItem(
            text=voto.materia,
            secondary_text=f"{voto.data_formattata} • {voto.crediti} CFU",
            tertiary_text=f"Voto: {voto.voto_display}"
        )
        
        # Icona voto
        icon_widget = IconLeftWidget(icon="trophy" if voto.voto >= 28 else "check")
        item.add_widget(icon_widget)
        
        # Bottone elimina
        delete_btn = IconRightWidget(
            icon="delete",
            on_release=lambda x: self.confirm_delete_voto(voto)
        )
        item.add_widget(delete_btn)
        
        return item
    
    def show_add_dialog(self, instance):
        """Mostra dialog per aggiungere voto"""
        if self.dialog:
            self.dialog.dismiss()
        
        # Campi
        self.materia_field = MDTextField(hint_text="Materia", required=True)
        
        self.crediti_field = MDTextField(
            hint_text="Crediti (CFU)",
            text="6",
            input_filter="int"
        )
        
        # Data picker button
        date_btn = MDRaisedButton(
            text=f"Data: {self.selected_date.strftime('%d/%m/%Y')}",
            on_release=self.show_date_picker
        )
        
        # Voto picker button
        self.voto_btn = MDRaisedButton(
            text=f"Voto: {self.selected_voto}",
            on_release=self.show_voto_menu
        )
        
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(240)
        )
        content.add_widget(self.materia_field)
        content.add_widget(self.crediti_field)
        content.add_widget(date_btn)
        content.add_widget(self.voto_btn)
        
        self.dialog = MDDialog(
            title="Nuovo Voto",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="ANNULLA", on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="AGGIUNGI", on_release=self.add_voto)
            ]
        )
        self.dialog.open()
    
    def show_date_picker(self, instance):
        """Mostra date picker"""
        if not self.date_picker:
            self.date_picker = MDDatePicker()
            self.date_picker.bind(on_save=self.on_date_selected)
        
        self.date_picker.open()
    
    def on_date_selected(self, instance, value, date_range):
        """Callback selezione data"""
        self.selected_date = value
        instance.dismiss()
    
    def show_voto_menu(self, instance):
        """Mostra menu selezione voto"""
        voti = [str(v) for v in range(18, 31)] + ["30L"]
        
        menu_items = [
            {
                "text": voto,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=voto: self.select_voto(x)
            } for voto in voti
        ]
        
        self.voto_menu = MDDropdownMenu(
            caller=instance,
            items=menu_items,
            width_mult=2
        )
        self.voto_menu.open()
    
    def select_voto(self, voto_str):
        """Seleziona un voto"""
        self.selected_voto = 31 if voto_str == "30L" else int(voto_str)
        self.voto_btn.text = f"Voto: {voto_str}"
        self.voto_menu.dismiss()
    
    def add_voto(self, instance):
        """Aggiunge un voto"""
        materia = self.materia_field.text.strip()
        
        if not materia:
            self.get_app().show_snackbar("❌ Inserisci una materia")
            return
        
        try:
            crediti = int(self.crediti_field.text or "6")
            app = self.get_app()
            
            app.db.add_voto(
                materia=materia,
                data=self.selected_date,
                crediti=crediti,
                voto=self.selected_voto,
                laurea_id=app.current_laurea.id
            )
            
            self.dialog.dismiss()
            self.refresh_list()
            self.update_stats()
            app.show_snackbar(f"✅ Voto aggiunto: {materia}")
            
        except Exception as e:
            self.get_app().show_snackbar(f"❌ Errore: {str(e)}")
    
    def confirm_delete_voto(self, voto):
        """Conferma eliminazione voto"""
        if self.dialog:
            self.dialog.dismiss()
        
        self.dialog = MDDialog(
            title="Elimina Voto",
            text=f"Vuoi eliminare il voto di '{voto.materia}'?",
            buttons=[
                MDFlatButton(text="ANNULLA", on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="ELIMINA", on_release=lambda x: self.delete_voto(voto))
            ]
        )
        self.dialog.open()
    
    def delete_voto(self, voto):
        """Elimina un voto"""
        app = self.get_app()
        app.db.delete_voto(voto.id)
        
        self.dialog.dismiss()
        self.refresh_list()
        self.update_stats()
        app.show_snackbar(f"🗑️ Voto eliminato")
    
    def show_menu(self, instance):
        """Mostra menu azioni"""
        menu_items = [
            {"text": "📊 Proiezione voti", "on_release": lambda x: self.show_proiezione()},
            {"text": "📈 Grafico andamento", "on_release": lambda x: self.show_grafico()},
            {"text": "📄 Esporta PDF", "on_release": lambda x: self.esporta_pdf()},
        ]
        
        menu = MDDropdownMenu(caller=instance, items=menu_items, width_mult=4)
        menu.open()
    
    def show_proiezione(self):
        """Mostra proiezione voti"""
        self.get_app().show_snackbar("📊 Proiezione voti - Coming soon!")
    
    def show_grafico(self):
        """Mostra grafico"""
        self.get_app().show_snackbar("📈 Grafico - Coming soon!")
    
    def esporta_pdf(self):
        """Esporta in PDF"""
        self.get_app().show_snackbar("📄 Esportazione - Coming soon!")
    
    def get_app(self):
        return MDApp.get_running_app()