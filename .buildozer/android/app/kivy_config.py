from kivy.config import Config
from kivy.logger import Logger

def configure_kivy():
    Logger.info("Configuração do Kivy: Inicializando as configurações gráficas")

    # Definir resolução do aplicativo
    Config.set('graphics', 'width', '360')
    Config.set('graphics', 'height', '640')

    # Configuração do backend gráfico
    Config.set('graphics', 'backend', 'sdl2')

    # Configura o teclado no Android
    Config.set('kivy', 'keyboard_mode', 'dock')

