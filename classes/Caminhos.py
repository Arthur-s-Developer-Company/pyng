import os 
import sys

class Caminho():
    def obter_caminho(self, caminho_relativo):
        self.caminho_relativo = caminho_relativo
        """Obtém o caminho absoluto para recursos, compatível com PyInstaller."""
        try:
            # Caminho gerado pelo PyInstaller em tempo de execução
            caminho_base = sys._MEIPASS # type: ignore
        except AttributeError:
            # Caminho padrão (desenvolvimento)
            caminho_base = os.path.abspath(".")
        
        # É importante usar os.path.join para construir o caminho
        return os.path.join(caminho_base, caminho_relativo)