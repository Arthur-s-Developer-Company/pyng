from classes.Caminhos import Caminho
from classes.States import States
import pygame as pg



class Opcoes:
    def __init__(self):
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((1920, 1080), pg.FULLSCREEN)
        pg.display.set_caption("Pyng - Opções")
        pg.mouse.set_visible(True)

        self.clock = pg.time.Clock()
        self.running = True
        self.dt = 0
        self.hue_titulo = 0.0

        self.caminho = Caminho()
        self.states = States()

        # UI state
        self.layouts = ["qwerty", "colemak"]
        self.layout_selecionado = "qwerty"
        try:
            arquivo_config = self.states.carregar_config()
        except Exception:
            self.states.salvar_config(self.layout_selecionado)
            arquivo_config = self.states.carregar_config()
        # Load existing config if present
        if arquivo_config and isinstance(arquivo_config, dict): 
            # Filtra o valor da chave e verifica se está na lista de layouts permitidos
            layout = arquivo_config.get("keyboard_layout")
            if layout in self.layouts:
                self.layout_selecionado = layout
        self.quit_rect = None

        # fonts
        self.title_font = lambda size: pg.font.Font(self.caminho.obter_caminho("Fonts/RasterForgeRegular-JpBgm.ttf"), size)
        self.small_font = lambda size: pg.font.Font(self.caminho.obter_caminho("Fonts/RasterForgeRegular-JpBgm.ttf"), size)

    # --- Drawing helpers ---
    def desenhar_tela(self):
        self.screen.fill((0, 0, 0))

    def mostrar_titulo(self):
        if not hasattr(self, 'hue_titulo'):
            self.hue_titulo = 0.0
        self.hue_titulo = (self.hue_titulo + 0.5) % 360
        cor_atual = pg.Color(0, 0, 0)
        cor_atual.hsva = (self.hue_titulo, 70, 100, 100)
        titulo = self.title_font(120).render("Opções", True, (cor_atual))
        rect = titulo.get_rect(center=(self.screen.get_width() // 2, int(self.screen.get_height() * 0.12)))
        self.screen.blit(titulo, rect)

    def mostrar_layout_selector(self):
        # Label
        label = self.small_font(48).render("Layout do teclado:", True, (200, 200, 200))
        label_rect = label.get_rect(center=(self.screen.get_width() // 2, int(self.screen.get_height() * 0.35)))
        self.screen.blit(label, label_rect)

        # Buttons for each layout
        gap = 60
        btn_w, btn_h = 300, 80
        total_w = len(self.layouts) * btn_w + (len(self.layouts) - 1) * gap
        start_x = self.screen.get_width() // 2 - total_w // 2
        y = int(self.screen.get_height() * 0.45)

        self.option_rects = []

        for i, name in enumerate(self.layouts):
            x = start_x + i * (btn_w + gap)
            rect = pg.Rect(x, y, btn_w, btn_h)
            self.option_rects.append((rect, name))
            color = (50, 50, 50)
            if name == self.layout_selecionado:
                color = (30, 144, 255)
            pg.draw.rect(self.screen, color, rect, border_radius=10)
            txt = self.small_font(48).render(name.capitalize(), True, (255, 255, 255))
            txt_rect = txt.get_rect(center=rect.center)
            self.screen.blit(txt, txt_rect)

        # Hint / status
        status = self.small_font(32).render(f"Selecionado: {self.layout_selecionado}", True, (180, 180, 180))
        status_rect = status.get_rect(center=(self.screen.get_width() // 2, y + btn_h + 60))
        self.screen.blit(status, status_rect)

        # Save button
        save_btn = pg.Rect(self.screen.get_width() // 2 - 120, status_rect.bottom + 40, 240, 64)
        pg.draw.rect(self.screen, (34, 139, 34), save_btn, border_radius=8)
        save_txt = self.small_font(36).render("Salvar", True, (255, 255, 255))
        save_rect = save_txt.get_rect(center=save_btn.center)
        self.screen.blit(save_txt, save_rect)
        self.save_rect = save_btn
    
    def mostrar_botao_quit(self):
        cor_do_x = (255, 0, 0)
        tamanho_do_x = 40
        pos_x = self.screen.get_width() - tamanho_do_x - 20
        pos_y = 20
        self.quit_rect = pg.Rect(pos_x, pos_y, tamanho_do_x, tamanho_do_x)
        pg.draw.rect(self.screen, cor_do_x, self.quit_rect)
        fonte_x = self.small_font(36)
        texto_x = fonte_x.render("X", True, (255, 255, 255))
        texto_x_rect = texto_x.get_rect(center=self.quit_rect.center, left=pos_x + 8)
        self.screen.blit(texto_x, texto_x_rect)

    def mostrar_menus(self):
        while self.running:
            self.dt = self.clock.tick(60) / 1000
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.running = False
                elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    pos = pg.mouse.get_pos()
                    # check option_rects
                    for rect, name in getattr(self, 'option_rects', []):
                        if rect.collidepoint(pos):
                            self.layout_selecionado = name
                    if getattr(self, 'save_rect', None) and self.save_rect.collidepoint(pos):
                        self.states.salvar_config(self.layout_selecionado)
            self.pos_mouse = pg.mouse.get_pos()
            mouse_pressed = pg.mouse.get_pressed()[0]
            if mouse_pressed and self.quit_rect.collidepoint(self.pos_mouse):
                self.running = False

            self.desenhar_tela()
            self.mostrar_titulo()
            self.mostrar_layout_selector()
            self.mostrar_botao_quit()

            pg.display.flip()


if __name__ == '__main__':
    op = Opcoes()
    op.mostrar_menus()
    pg.quit()

