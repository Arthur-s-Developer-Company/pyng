if __name__ == "__main__":
    from Caminhos import Caminho
else:
    from classes.Caminhos import Caminho  
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

        self.hue_titulo = 0.0
        self.hue_opcoes = 0.0
        self.escala_atual = 1.0  # Escala atual (interpolada)
        self.escala_alvo = 1.0   # Escala alvo

        self.rotacao_atual = 0.0
        self.rotacao_alvo = 0.0

        # Estado de clique / animação de clique
        self.clicking = False
        self.click_phase = None        # 'down' ou 'up'
        self.escala_clique_alvo = 1.0
        self.click_speed = 20.0        # controla rapidez da animação de clique
        self.click_threshold = 0.01    # quando considerar que atingiu o alvo
        
        # estado do botão do mouse no frame anterior (para detectar release)
        self.prev_mouse_pressed = False

        self.alpha_opcoes_atual = 255
        self.alpha_opcoes_alvo = 255

        self.cor_hover_atual = pg.Color(255, 255, 255)
        self.cor_hover_alvo = pg.Color(255, 255, 255)
        self.s = 0
        
    def desenhar_tela(self):
        self.screen.fill("black")
    
    def RasterForgeRegular(self, tamanho):
        return pg.font.Font(Caminho().obter_caminho("Fonts/RasterForgeRegular-JpBgm.ttf"), tamanho)


    def mostrar_titulo(self):
        self.hue_titulo = (self.hue_titulo + 0.5) % 360

        cor_atual = pg.Color(0, 0, 0)
        cor_atual.hsva = (self.hue_titulo, 100, 100, 100)

        self.titulo_pyng = self.RasterForgeRegular(250).render("Pyng", True, (cor_atual))
        self.rect_titulo_pyng = self.titulo_pyng.get_rect()
        self.rect_titulo_pyng.topleft = (int(self.screen.get_width() / 2 - self.rect_titulo_pyng.width / 2), int(self.screen.get_height() / 5))
        
        # --- Se está em animação de clique, ela sobrescreve o hover ---
        if self.clicking:
            velocidade = self.click_speed * self.dt
            self.escala_atual = pg.math.lerp(self.escala_atual, self.escala_clique_alvo, velocidade)
            self.alpha_opcoes_alvo = 100

            # quando atingir o alvo, troca de fase (down -> up) ou encerra
                # apenas uma vez por transição: se estávamos na fase 'down', passamos para 'up'
            if self.click_phase == 'down':
                # Verifica se mouse está sobre o texto (hover verdadeiro)
                if self.rect_titulo_pyng.collidepoint(self.pos_mouse):
                    self.alpha_opcoes_alvo = 100
                    # Vai direto para 1.5 com rotação
                    self.click_phase = 'down'
                    self.escala_clique_alvo = 0.5
                    self.rotacao_alvo = 0.0
                else:
                    # Volta apenas para 1.0 sem rotação
                    self.click_phase = 'up'
                    self.escala_clique_alvo = 1.0
                    self.rotacao_alvo = 0.0
            else:
                # animação de clique finalizada, retorna ao comportamento normal (hover reaparece)
                self.clicking = False
                self.click_phase = None
                self.escala_clique_alvo = 1.0
                self.rotacao_alvo = 0.0
            
            # Interpola rotação suavemente durante toda animação de clique
            self.rotacao_atual = pg.math.lerp(self.rotacao_atual, self.rotacao_alvo, velocidade)
        else:
            # Comportamento normal de hover (aplica alvo de hover)
            if self.rect_titulo_pyng.collidepoint(self.pos_mouse):
                self.escala_alvo = 1.5
                self.rotacao_alvo = -10.0
                self.alpha_opcoes_alvo = 100
            else:
                self.escala_alvo = 1.0
                self.rotacao_alvo = 0.0
                self.alpha_opcoes_alvo = 255

            velocidade_lerp_hover = 8 * self.dt  # Velocidade de interpolação para hover
            self.escala_atual = pg.math.lerp(self.escala_atual, self.escala_alvo, max(0, min(1, velocidade_lerp_hover)))
            self.rotacao_atual = pg.math.lerp(self.rotacao_atual, self.rotacao_alvo, velocidade_lerp_hover)

        # Aplicar escala e rotação ao sprite final
        nova_largura = max(1, int(self.rect_titulo_pyng.width * self.escala_atual))
        nova_altura = max(1, int(self.rect_titulo_pyng.height * self.escala_atual))
        self.titulo_pyng = pg.transform.smoothscale(self.titulo_pyng, (nova_largura, nova_altura))
        self.titulo_pyng = pg.transform.rotate(self.titulo_pyng, self.rotacao_atual)
        self.rect_titulo_pyng = self.titulo_pyng.get_rect(center=self.rect_titulo_pyng.center)

        self.screen.blit(self.titulo_pyng, self.rect_titulo_pyng)

    def mostrar_opcoes(self):
        self.hue_opcoes = (self.hue_opcoes + 0.5) % 360
        self.botao_play = self.RasterForgeRegular(50).render("Play", True, "white")
        self.rect_botao_play = self.botao_play.get_rect()
        self.rect_botao_play.topleft = (int(self.screen.get_width() / 2 - self.rect_botao_play.width / 2), int(self.screen.get_height() / 2 ))
        self.alpha_opcoes_atual = pg.math.lerp(self.alpha_opcoes_atual, self.alpha_opcoes_alvo, 10 * self.dt)
        self.botao_play.set_alpha(int(self.alpha_opcoes_atual))
        if self.rect_botao_play.collidepoint(self.pos_mouse):
            if self.s < 70:
                self.s += 200 * self.dt
            else:
                self.s = 70
            self.cor_hover_alvo.hsva = (self.hue_opcoes, self.s, 100, 100)
            self.cor_hover_atual = self.cor_hover_atual.lerp(self.cor_hover_alvo, 10 * self.dt)
            self.botao_play = self.RasterForgeRegular(50).render("Play", True, self.cor_hover_atual)
            self.botao_play.set_alpha(int(self.alpha_opcoes_atual))
            
        else:
            if self.s > 0:
                self.s -= 200 * self.dt
            else:
                self.s = 0
            self.cor_hover_alvo.hsva = (self.hue_opcoes, max(0, min(70, self.s)), 100, 100)
            self.cor_hover_atual = self.cor_hover_atual.lerp(self.cor_hover_alvo, 10 * self.dt)
            self.botao_play = self.RasterForgeRegular(50).render("Play", True, self.cor_hover_atual)
            self.botao_play.set_alpha(int(self.alpha_opcoes_atual))

        self.screen.blit(self.botao_play, self.rect_botao_play)


    def mostrar_menus(self):
        while self.running:
            self.dt = self.clock.tick(1000) / 1000
            # Eventos (tratamos QUIT normalmente)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False

            # Atualiza posição do mouse e estado do botão esquerdo
            self.pos_mouse = pg.mouse.get_pos()
            mouse_pressed = pg.mouse.get_pressed()[0]

            # calcula rect aproximado do título sem precisar renderizar (mesma lógica de posicionamento)
            font_preview = self.RasterForgeRegular(250)
            preview_w, preview_h = font_preview.size("Pyng")
            preview_rect = pg.Rect(int(self.screen.get_width() / 2 - preview_w / 2), int(self.screen.get_height() / 5), preview_w, preview_h)

            # Se o botão esquerdo está pressionado sobre o título, entra na fase down (escala 0.5)
            if mouse_pressed and preview_rect.collidepoint(self.pos_mouse):
                self.clicking = True
                self.click_phase = 'down'
                self.escala_clique_alvo = 0.5
                self.rotacao_alvo = 0.0
            else:
                # Detecta release (pressionado no frame anterior e agora não)
                if self.prev_mouse_pressed and not mouse_pressed:
                    # soltou o botão — decidir para onde transitar
                    if preview_rect.collidepoint(self.pos_mouse):
                        # se o mouse está sobre o texto, volte para hover
                        self.clicking = True
                        self.click_phase = 'up'
                        self.escala_clique_alvo = 1.5
                        self.rotacao_alvo = -10.0
                    else:
                        # senão, volta para normal
                        self.clicking = True
                        self.click_phase = 'up'
                        self.escala_clique_alvo = 1.0
                        self.rotacao_alvo = 0.0

            # atualiza o estado anterior do mouse para detectar release no próximo frame
            self.prev_mouse_pressed = mouse_pressed

            self.desenhar_tela()
            self.mostrar_titulo()
            self.mostrar_opcoes()
        
            pg.display.flip()


if __name__ == "__main__":
    main = Main()
    main.mostrar_menus()
    pg.quit()
