# ui/screens/tasse.py
"""
Schermata gestione tasse universitarie
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.list import MDList, ThreeLineAvatarIconListItem, IconLeftWidget, IconRightWidget
from kivymd.uix.pickers import MDDatePicker
from kivy.metrics import dp
from kivymd.app import MDApp
from datetime import datetime


class TasseScreen(Screen):
    """Schermata gestione tasse"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.date_picker = None
        self.selected_date = datetime.now()
        self.build_ui()
    
    def build_ui(self):
        """Costruisce l'interfaccia"""
        layout = BoxLayout(orientation='vertical')
        
        # Header
        header = self.create_header()
        layout.add_widget(header)
        
        # Card riepilogo
        self.summary_card = self.create_summary_card()
        layout.add_widget(self.summary_card)
        
        # Lista tasse
        self.scroll = ScrollView()
        self.tasse_list = MDList()
        self.scroll.add_widget(self.tasse_list)
        layout.add_widget(self.scroll)
        
        # Bottone add
        add_btn = MDRaisedButton(
            text="➕ Aggiungi Tassa",
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
            text="Tasse Universitarie",
            font_style="H5",
            halign="left"
        )
        header.add_widget(title)
        
        return header
    
    def create_summary_card(self):
        """Crea card riepilogo"""
        card = MDCard(
            orientation='vertical',
            padding=dp(15),
            spacing=dp(10),
            size_hint=(0.95, None),
            height=dp(120),
            pos_hint={'center_x': 0.5},
            elevation=3,
            radius=[15]
        )
        
        title = MDLabel(
            text="💰 Riepilogo Tasse",
            font_style="H6",
            size_hint_y=None,
            height=dp(30)
        )
        card.add_widget(title)
        
        # Labels per totali
        self.totale_label = MDLabel(
            text="Totale: € 0.00",
            font_style="Body1",
            size_hint_y=None,
            height=dp(25)
        )
        card.add_widget(self.totale_label)
        
        self.da_pagare_label = MDLabel(
            text="Da pagare: € 0.00",
            font_style="Body1",
            theme_text_color="Error",
            size_hint_y=None,
            height=dp(25)
        )
        card.add_widget(self.da_pagare_label)
        
        return card
    
    def update_summary(self):
        """Aggiorna il riepilogo"""
        app = self.get_app()
        tasse = app.db.get_all_tasse()
        
        totale = sum(t.importo for t in tasse)
        da_pagare = sum(t.importo for t in tasse if not t.pagata)
        
        self.totale_label.text = f"Totale: € {totale:.2f}"
        self.da_pagare_label.text = f"Da pagare: € {da_pagare:.2f}"
    
    def on_enter(self):
        """Aggiorna quando si entra"""
        self.refresh_list()
        self.update_summary()
    
    def refresh_list(self):
        """Aggiorna lista tasse"""
        self.tasse_list.clear_widgets()
        app = self.get_app()
        tasse = app.db.get_all_tasse()
        
        if not tasse:
            empty_label = MDLabel(
                text="Nessuna tassa registrata.\nAggiungi la tua prima tassa!",
                halign="center",
                theme_text_color="Secondary"
            )
            self.tasse_list.add_widget(empty_label)
        else:
            for tassa in tasse:
                item = self.create_tassa_item(tassa)
                self.tasse_list.add_widget(item)
    
    def create_tassa_item(self, tassa):
        """Crea un item per una tassa"""
        # Determina colore basato su stato
        if tassa.pagata:
            icon = "check-circle"
            icon_color = [0, 1, 0, 1]  # Verde
        elif tassa.giorni_alla_scadenza < 0:
            icon = "alert-circle"
            icon_color = [1, 0, 0, 1]  # Rosso
        elif tassa.giorni_alla_scadenza <= 7:
            icon = "clock-alert"
            icon_color = [1, 0.6, 0, 1]  # Arancione
        else:
            icon = "clock-outline"
            icon_color = [0.5, 0.5, 0.5, 1]  # Grigio
        
        item = ThreeLineAvatarIconListItem(
            text=tassa.descrizione,
            secondary_text=f"Scadenza: {tassa.scadenza_formattata}",
            tertiary_text=f"{tassa.importo_formattato} • {tassa.stato}",
            on_release=lambda x: self.toggle_pagamento(tassa)
        )
        
        # Icona stato
        icon_widget = IconLeftWidget(icon=icon)
        item.add_widget(icon_widget)
        
        # Bottone elimina
        delete_btn = IconRightWidget(
            icon="delete",
            on_release=lambda x: self.confirm_delete_tassa(tassa)
        )
        item.add_widget(delete_btn)
        
        return item
    
    def toggle_pagamento(self, tassa):
        """Cambia stato pagamento"""
        app = self.get_app()
        app.db.toggle_pagamento_tassa(tassa.id)
        
        stato = "pagata" if not tassa.pagata else "da pagare"
        app.show_snackbar(f"✅ Tassa segnata come {stato}")
        
        self.refresh_list()
        self.update_summary()
    
    def show_add_dialog(self, instance):
        """Mostra dialog per aggiungere tassa"""
        if self.dialog:
            self.dialog.dismiss()
        
        self.descrizione_field = MDTextField(
            hint_text="Descrizione (es. Prima rata)",
            required=True
        )
        
        self.importo_field = MDTextField(
            hint_text="Importo (€)",
            input_filter="float"
        )
        
        # Data picker button
        self.date_btn = MDRaisedButton(
            text=f"Scadenza: {self.selected_date.strftime('%d/%m/%Y')}",
            on_release=self.show_date_picker
        )
        
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(180)
        )
        content.add_widget(self.descrizione_field)
        content.add_widget(self.importo_field)
        content.add_widget(self.date_btn)
        
        self.dialog = MDDialog(
            title="Nuova Tassa",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="ANNULLA",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="AGGIUNGI",
                    on_release=self.add_tassa
                )
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
        self.date_btn.text = f"Scadenza: {value.strftime('%d/%m/%Y')}"
        instance.dismiss()
    
    def add_tassa(self, instance):
        """Aggiunge una tassa"""
        descrizione = self.descrizione_field.text.strip()
        
        if not descrizione:
            self.get_app().show_snackbar("❌ Inserisci una descrizione")
            return
        
        try:
            importo = float(self.importo_field.text.replace(',', '.'))
            
            if importo <= 0:
                self.get_app().show_snackbar("❌ Importo deve essere positivo")
                return
            
            app = self.get_app()
            app.db.add_tassa(
                descrizione=descrizione,
                importo=importo,
                scadenza=self.selected_date
            )
            
            self.dialog.dismiss()
            self.refresh_list()
            self.update_summary()
            app.show_snackbar(f"✅ Tassa aggiunta: {descrizione}")
            
        except ValueError:
            self.get_app().show_snackbar("❌ Importo non valido")
        except Exception as e:
            self.get_app().show_snackbar(f"❌ Errore: {str(e)}")
    
    def confirm_delete_tassa(self, tassa):
        """Conferma eliminazione tassa"""
        if self.dialog:
            self.dialog.dismiss()
        
        self.dialog = MDDialog(
            title="Elimina Tassa",
            text=f"Vuoi eliminare '{tassa.descrizione}'?",
            buttons=[
                MDFlatButton(
                    text="ANNULLA",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="ELIMINA",
                    on_release=lambda x: self.delete_tassa(tassa)
                )
            ]
        )
        self.dialog.open()
    
    def delete_tassa(self, tassa):
        """Elimina una tassa"""
        app = self.get_app()
        app.db.delete_tassa(tassa.id)
        
        self.dialog.dismiss()
        self.refresh_list()
        self.update_summary()
        app.show_snackbar(f"🗑️ Tassa eliminata")
    
    def get_app(self):
        return MDApp.get_running_app()