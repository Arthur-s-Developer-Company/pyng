from Caminhos import Caminho
import pygame as pg


class Main:
    def __init__(self):
        pg.init()
        # Tela
        self.screen = pg.display.set_mode((1920, 1080), pg.FULLSCREEN)  # Tamanho fixo

        # Mixer
        pg.mixer.init()

        # Mouse
        pg.display.set_caption("Pyng")  # Título da janela
        pg.mouse.set_visible(True)  # Torna o cursor invisível

        # Tempo
        self.clock = pg.time.Clock()
        self.running = True
        self.dt = 0

        self.setup_menu()

        self.pos_mouse = pg.mouse.get_pos()
    
    def setup_menu(self):
        self.caminho = Caminho()

        self.hue = 0
        self.escala_atual = 1.0  # Escala atual (interpolada)
        self.escala_alvo = 1.0   # Escala alvo

        self.rotacao_atual = 0.0
        self.rotacao_alvo = 0.0

        # Estado de clique / animação de clique
        self.clicking = False
        self.click_phase = None        # 'down' ou 'up'
        self.click_target = 1.0
        self.click_speed = 20.0        # controla rapidez da animação de clique
        self.click_threshold = 0.01    # quando considerar que atingiu o alvo

        self.fonte_menu = pg.font.Font(self.caminho.obter_caminho("Fonts/RasterForgeRegular-JpBgm.ttf"), 100)
        
    def desenhar_tela(self):
        self.screen.fill("black")
        
    def mostrar_titulo(self):
        self.hue = (self.hue + 0.5) % 360

        cor_atual = pg.Color(0, 0, 0)
        cor_atual.hsva = (self.hue, 100, 100, 100)

        self.titulo_pyng = self.fonte_menu.render("Pyng", True, (cor_atual))
        self.rect_titulo_pyng = self.titulo_pyng.get_rect()
        self.rect_titulo_pyng.topleft = (int(self.screen.get_width() / 2 - self.rect_titulo_pyng.width / 2), int(self.screen.get_height() / 5 - self.rect_titulo_pyng.height / 2))
        
        # --- Se está em animação de clique, ela sobrescreve o hover ---
        if self.clicking:
            velocidade = self.click_speed * self.dt
            self.escala_atual = pg.math.lerp(self.escala_atual, self.click_target, velocidade)

            # quando atingir o alvo, troca de fase (down -> up) ou encerra
            if abs(self.escala_atual - self.click_target) < self.click_threshold:
                while self.click_phase == 'down':
                    # Verifica se mouse está sobre o texto (hover verdadeiro)
                    if self.rect_titulo_pyng.collidepoint(self.pos_mouse):
                        # Vai direto para 1.5 com rotação
                        self.click_phase = 'up'
                        self.click_target = 1.5
                        self.rotacao_alvo = -10.0
                    else:
                        # Volta apenas para 1.0 sem rotação
                        self.click_phase = 'up'
                        self.click_target = 1.0
                        self.rotacao_alvo = 0.0
                else:
                    # animação de clique finalizada, retorna ao comportamento normal (hover reaparece)
                    self.clicking = False
                    self.click_phase = None
                    self.click_target = 1.0
                    self.rotacao_alvo = 0.0
            
            # Interpola rotação suavemente durante toda animação de clique
            self.rotacao_atual = pg.math.lerp(self.rotacao_atual, self.rotacao_alvo, velocidade)
        else:
            # Comportamento normal de hover (aplica alvo de hover)
            if self.rect_titulo_pyng.collidepoint(self.pos_mouse):
                self.escala_alvo = 1.5
                self.rotacao_alvo = -10.0
            else:
                self.escala_alvo = 1.0
                self.rotacao_alvo = 0.0

            velocidade_lerp_hover = 8 * self.dt  # Velocidade de interpolação para hover
            self.escala_atual = pg.math.lerp(self.escala_atual, self.escala_alvo, velocidade_lerp_hover)
            self.rotacao_atual = pg.math.lerp(self.rotacao_atual, self.rotacao_alvo, velocidade_lerp_hover)

        # Aplicar escala e rotação ao sprite final
        nova_largura = max(1, int(self.rect_titulo_pyng.width * self.escala_atual))
        nova_altura = max(1, int(self.rect_titulo_pyng.height * self.escala_atual))
        self.titulo_pyng = pg.transform.smoothscale(self.titulo_pyng, (nova_largura, nova_altura))
        self.titulo_pyng = pg.transform.rotate(self.titulo_pyng, self.rotacao_atual)
        self.rect_titulo_pyng = self.titulo_pyng.get_rect(center=self.rect_titulo_pyng.center)

        self.screen.blit(self.titulo_pyng, self.rect_titulo_pyng)

    def atualizar_mouse(self):
        self.pos_mouse = pg.mouse.get_pos()

    def mostrar_menus(self):
        while self.running:
            self.dt = self.clock.tick(1000) / 1000
            # Eventos
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                if event.type == pg.MOUSEBUTTONDOWN:
                    if self.rect_titulo_pyng.collidepoint(self.pos_mouse):
                        # inicia animação de clique (sobrescreve hover enquanto estiver ativa)
                        self.clicking = True
                        self.click_phase = 'down'
                        self.click_target = 0.5
                        # opcional: reduzir rotação durante clique
                        self.rotacao_alvo = 0.0

            self.desenhar_tela()
            self.mostrar_titulo()
            self.atualizar_mouse()
        
            pg.display.flip()


if __name__ == "__main__":
    main = Main()
    main.mostrar_menus()
    pg.quit()
