import os
from kivy.logger import Logger
from kivy.app import App
from kivy.config import Config
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
import firebase_admin
from firebase_admin import credentials, firestore

# Configuração do Kivy
Config.set('graphics', 'backend', 'auto')

Logger.info("App: Inicializando o aplicativo de receitas para diabéticos")

# Verificar se o arquivo de credenciais Firebase existe
if not os.path.exists('projetofaculdade-c05bb-firebase-adminsdk-zm28v-16554f2ec7.json'):
    Logger.error("App: Arquivo de credenciais Firebase não encontrado")
else:
    try:
        Logger.info("App: Tentando inicializar Firebase")
        cred = credentials.Certificate('projetofaculdade-c05bb-firebase-adminsdk-zm28v-16554f2ec7.json')
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        Logger.info("App: Firebase inicializado com sucesso")
    except Exception as e:
        Logger.error(f"App: Erro ao inicializar Firebase - {e}")

# Inicialize o Firestore novamente de maneira explícita
try:
    db = firestore.client()
    Logger.info("App: Firestore cliente inicializado com sucesso")
except Exception as e:
    Logger.error(f"App: Erro ao inicializar Firestore - {e}")

class NavigationManager:
    def __init__(self, app):
        self.app = app
        self.stack = []  # Pilha de telas
        Logger.info("App: Gerenciador de navegação inicializado")

    def change_screen(self, new_screen):
        Logger.info(f"App: Tentando mudar para a nova tela {new_screen}")
        try:
            if self.app.main_layout.children:
                current_screen = self.app.main_layout.children[0]
                self.stack.append(current_screen)  # Empilha a tela atual antes de mudar
                self.app.main_layout.clear_widgets()

            self.app.main_layout.add_widget(new_screen)
            Logger.info(f"App: Tela {new_screen} carregada com sucesso")
        except Exception as e:
            Logger.error(f"App: Erro ao trocar a tela - {e}")

    def go_back(self):
        Logger.info("App: Voltando para a tela anterior")
        try:
            if self.stack:
                previous_screen = self.stack.pop()  # Desempilha a tela anterior
                self.app.main_layout.clear_widgets()
                self.app.main_layout.add_widget(previous_screen)
                Logger.info("App: Tela anterior carregada com sucesso")
            else:
                self.app.show_main_menu()  # Mostra o menu principal se não houver telas na pilha
                Logger.info("App: Mostrando o menu principal")
        except Exception as e:
            Logger.error(f"App: Erro ao voltar para a tela anterior - {e}")

class ReceitaApp(App):
    def build(self):
        Logger.info("ReceitaApp: Iniciando o aplicativo")
        self.main_layout = BoxLayout(orientation='vertical')
        self.navigation_manager = NavigationManager(self)
        self.show_main_menu()
        Logger.info("ReceitaApp: Menu principal exibido")
        return self.main_layout

    def show_main_menu(self):
        Logger.info("App: Mostrando o menu principal")
        self.main_layout.clear_widgets()
        self.btn_adicionar_receita = Button(text='Adicionar Receita', size_hint=(1, 0.1))
        self.btn_adicionar_receita.bind(on_press=self.abrir_formulario_receita)
        self.btn_ver_receitas = Button(text='Ver Receitas', size_hint=(1, 0.1))
        self.btn_ver_receitas.bind(on_press=self.abrir_lista_receitas)
        self.main_layout.add_widget(self.btn_adicionar_receita)
        self.main_layout.add_widget(self.btn_ver_receitas)

    def abrir_formulario_receita(self, instance):
        Logger.info("App: Abrindo formulário de receita")
        self.navigation_manager.change_screen(FormularioReceita(self))

    def abrir_lista_receitas(self, instance):
        Logger.info("App: Abrindo lista de receitas")
        self.navigation_manager.change_screen(ListaReceitas(self))

class FormularioReceita(BoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        Logger.info("App: Formulário de Receita inicializado")
        self.app = app
        self.orientation = 'vertical'

        self.entries = {}
        labels = ["Nome da Receita:", "Ingredientes:", "Modo de Preparo:", "Informações Nutricionais:"]

        for label in labels:
            lbl = Label(text=label, size_hint_y=None, height=30)
            self.add_widget(lbl)
            
            entry = TextInput(size_hint_y=None, height=60, multiline=True)
            self.add_widget(entry)
            self.entries[label] = entry

        # Botões
        self.btn_voltar = Button(text="Voltar", size_hint_y=None, height=50)
        self.btn_voltar.bind(on_press=self.voltar_para_inicio)

        self.btn_salvar = Button(text="Salvar", size_hint_y=None, height=50)
        self.btn_salvar.bind(on_press=self.salvar)

        self.add_widget(self.btn_voltar)
        self.add_widget(self.btn_salvar)

    def voltar_para_inicio(self, instance):
        Logger.info("App: Voltando para o menu principal a partir do formulário")
        self.app.show_main_menu()

    def salvar(self, instance):
        Logger.info("App: Salvando informações da receita")
        data = {label: entry.text.strip() for label, entry in list(self.entries.items())}
        if not all(data.values()):
            popup = Popup(title='Aviso', content=Label(text='Todos os campos devem ser preenchidos.'), size_hint=(0.8, 0.3))
            popup.open()
            return

        try:
            db.collection('receitas').add(data)
            Logger.info("App: Informações de receita salvas com sucesso")
            popup = Popup(title='Sucesso', content=Label(text='Informações salvas com sucesso.'), size_hint=(0.8, 0.3))
            popup.open()
            self.voltar_para_inicio(instance)
        except Exception as e:
            Logger.error(f"App: Erro ao salvar informações de receita - {e}")
            popup = Popup(title='Erro', content=Label(text=f'Ocorreu um erro ao salvar as informações: {e}'), size_hint=(0.8, 0.3))
            popup.open()

class ListaReceitas(ScrollView):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app

        self.layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))

        self.load_buttons()
        self.add_widget(self.layout)

    def load_buttons(self):
        try:
            docs = db.collection('receitas').stream()
            for doc in docs:
                data = doc.to_dict()
                nome = data.get('Nome da Receita:', 'N/A')
                ingredientes = data.get('Ingredientes:', 'N/A')

                info_texto = f"{nome} - Ingredientes: {ingredientes}"

                button = Button(
                    text=info_texto,
                    size_hint=(1, None),
                    text_size=(None, None),
                    halign='center',
                    valign='middle',
                    padding=(10, 10)
                )
                button.bind(
                    size=self.adjust_button_text_size
                )
                button.bind(
                    on_press=lambda instance, data=data: self.app.navigation_manager.change_screen(DetalhesReceita(self.app, data))
                )
                self.layout.add_widget(button)

            self.btn_voltar = Button(text="Voltar", size_hint_y=None, height=50)
            self.btn_voltar.bind(on_press=self.voltar_para_inicio)
            self.layout.add_widget(self.btn_voltar)

        except Exception as e:
            Logger.error(f"App: Erro ao carregar as receitas - {e}")
            popup = Popup(title='Erro', content=Label(text=f'Ocorreu um erro ao carregar as receitas: {e}'), size_hint=(0.8, 0.3))
            popup.open()

    def voltar_para_inicio(self, instance):
        self.app.show_main_menu()

    def adjust_button_text_size(self, instance, size):
        instance.text_size = (instance.width - 20, None)
        instance.height = max(50, instance.texture_size[1] + 20)

class DetalhesReceita(BoxLayout):
    def __init__(self, app, data, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.orientation = 'vertical'

        for key, value in list(data.items()):
            self.add_widget(Label(text=f"{key}: {value}", size_hint_y=None, height=30))

        self.btn_voltar = Button(text="Voltar", size_hint_y=None, height=50)
        self.btn_voltar.bind(on_press=self.voltar)
        self.add_widget(self.btn_voltar)

    def voltar(self, instance):
        self.app.navigation_manager.go_back()

if __name__ == "__main__":
    ReceitaApp().run()
