import random  # noqa: N999

import pygame as pg

from classes.Caminhos import Caminho
from classes.States import States


class Game:
    def __init__(self):
        pg.init()

        # Tela
        self.screen = pg.display.set_mode((1920, 1080), pg.FULLSCREEN)  # Tamanho fixo

        # Mixer
        pg.mixer.init()

        # Mouse
        pg.display.set_caption("Pyng")  # Título da janela
        pg.mouse.set_visible(False)  # Torna o cursor invisível
        pg.event.set_grab(True)
        self.mouse_captured = True
        self.mouse_visible = False

        # Tempo
        self.clock = pg.time.Clock()
        self.running = True
        self.paused = False
        self.dt = 0

        # For mouse offset when pausing to prevent teleportation
        self.saved_mouse_offset = pg.Vector2(0, 0)

        # Inicialização das variáveis do jogo
        self.setup_game()

    def setup_game(self):
        self.caminho = Caminho()
        self.state = States()

        self.layouts = ["qwerty", "colemak"]
        self.layout_selecionado = "qwerty"

        arquivo_config = self.state.carregar_config()
        # Load existing config if present
        if arquivo_config and isinstance(arquivo_config, dict):
            # Filtra o valor da chave e verifica se está na lista de layouts permitidos
            layout = arquivo_config.get("keyboard_layout")
            if layout in self.layouts:
                self.layout_selecionado = layout
        print(f"Layout do teclado selecionado: {self.layout_selecionado}")
        # Cooldowns
        self.collision_par_cooldown = 0.3
        self.collision_raq_cooldown = pg.Vector2(2.0, 2.0)
        self.cooldown_par = pg.Vector2(0.0, 0.0)
        self.cooldown_raq_jogador = pg.Vector2(0.0, 0.0)
        self.cooldown_raq_oponente = pg.Vector2(0.0, 0.0)

        # Espera inicial
        self.espera = 1.0

        # Bola
        self.raio_da_bola = 10
        self.pos_da_bola = pg.Vector2(
            self.screen.get_width() / 2, self.screen.get_height() / 2
        )
        self.dir_da_bola = pg.Vector2(
            -1 if random.randint(1, 2) == 1 else 1,
            -1 if random.randint(1, 2) == 1 else 1,
        )
        self.velocidade_base_bola = 450
        self.velocidade_bola = self.velocidade_base_bola
        self.air_drag = 0.3
        self.movimento_bola = pg.Vector2(
            self.dir_da_bola.x * self.velocidade_bola * self.dt,
            self.dir_da_bola.y * self.velocidade_bola * self.dt,
        )
        self.ball_velocity = pg.Vector2(-450, -450)
        self.ball_spin = 0.2
        self.magnus_factor = 0.00100
        self.ball_restitution = 0.7
        self.ball_friction = 0.2
        self.slowdown = 0
        self.velocidade_max = 1100
        self.velocidade_max_anterior = self.velocidade_max
        self.colidiu = False

        ## Raquetes
        self.tamanho_raquetes = pg.Vector2(20, 80)
        self.alvo_pos = pg.Vector2(pg.mouse.get_pos())

        # Zona segura para checar o jogador (metade esquerda + buffer)
        self.zona_jogador = (
            self.screen.get_width() * (3 / 5) - (self.screen.get_width() / 5) / 2
        )
        # Zona segura para checar o oponente (metade direita + buffer)
        self.zona_oponente = self.screen.get_width() / 2

        # Raquete Jogador
        self.pos_raquete_jogador = pg.Vector2(
            self.screen.get_width() / 100,
            self.screen.get_height() / 2 - self.tamanho_raquetes.y / 2,
        )
        self.vezes_colidiu = 0
        self.pos_anterior_raquete_jogador = self.pos_raquete_jogador.copy()
        self.segurando = 0
        self.ignore_first_frame = 0
        self.velocidade_maxima = 15.0

        # Charge da raquete
        self.charge_level = 0.0  # De 0.0 a 1.0
        self.charge_speed = 1.5  # Quanto tempo leva para carregar (1.5 = ~0.6s)
        self.pronto = 0
        self.b_amarelo_atual = 50.0
        self.b_amarelo_alvo = 200.0
        self.cooldown_charge_jog = 0.0

        # Quantidade máxima de vezes que a raquete pode colidir antes de ficar "transparente" e traspassável
        self.max_vezes_pode_colidir = 0

        # Raquete Oponente
        self.pos_raquete_oponente = pg.Vector2(
            self.screen.get_width()
            - self.tamanho_raquetes.x
            - self.screen.get_width() / 100,
            self.screen.get_height() / 2 - self.tamanho_raquetes.y / 2,
        )

        # Placar
        self.pontuacao_jogador = 0
        self.pontuacao_oponente = 0
        self.ponto_jog_placar = self.pontuacao_jogador
        self.ponto_opon_placar = self.pontuacao_oponente
        self.fonte_placar = pg.font.Font(
            self.caminho.obter_caminho("Fonts/FiraCode-Bold.ttf"), 50
        )
        self.fonte_retro = lambda tamanho: pg.font.Font(
            self.caminho.obter_caminho("Fonts/RasterForgeRegular-JpBgm.ttf"), tamanho
        )
        self.alpha_atual_jog = 255
        self.alpha_alvo_jog = 255
        self.alpha_atual_opon = 255
        self.alpha_alvo_opon = 255
        self.delay_jog = 0.0
        self.delay_opon = 0.0
        self.delay_padrao = 0.3
        self.azul_jog = 255
        self.azul_alvo_jog = 255
        self.azul_opon = 255
        self.azul_alvo_opon = 255

        # Sons
        self.som_colisao_raquete = pg.mixer.Sound(
            self.caminho.obter_caminho("Sons/hit_paddle.wav")
        )
        self.som_colisao_raquete.set_volume(0.3)
        self.som_ponto = pg.mixer.Sound(
            self.caminho.obter_caminho("Sons/score_point.wav")
        )
        self.som_ponto.set_volume(0.7)

    def desenhar_jogo(self):
        # Desenha a linha central
        self.screen.fill("black")
        pg.draw.line(
            self.screen,
            "grey",
            (self.screen.get_width() / 2, 0),
            (self.screen.get_width() / 2, self.screen.get_height()),
            1,
        )

    def atualizar_placar(self):
        # Diminui os delays a cada frame
        if self.delay_jog > 0:
            self.delay_jog -= self.dt
        if self.delay_opon > 0:
            self.delay_opon -= self.dt

        # Define os alvos de alpha baseado nos delays
        if self.delay_jog <= 0:
            self.alpha_alvo_jog = 255
        if self.delay_opon <= 0:
            self.alpha_alvo_opon = 255

        bola_rect = pg.Rect(
            self.pos_da_bola.x - self.raio_da_bola,
            self.pos_da_bola.y - self.raio_da_bola,
            self.raio_da_bola * 2,
            self.raio_da_bola * 2,
        )

        # ---------------------------------

        # Placar Jogador
        self.placar_jogador = self.fonte_placar.render(
            f"{self.pontuacao_jogador}", True, (255, 255, 255)
        )
        self.rect_placar_jogador = self.placar_jogador.get_rect()
        self.rect_placar_jogador.topleft = (
            int(self.screen.get_width() / 2) - 70 - self.rect_placar_jogador.width,
            20,
        )

        if bola_rect.colliderect(self.rect_placar_jogador):
            self.alpha_alvo_jog = 100
            self.delay_jog = self.delay_padrao  # Começa o delay de 1s

        velo_lerp = min(1.0, 15.0 * self.dt)
        self.alpha_atual_jog = pg.math.lerp(
            self.alpha_atual_jog, self.alpha_alvo_jog, velo_lerp
        )

        if self.ponto_jog_placar != self.pontuacao_jogador:
            self.azul_alvo_jog = 100
            self.ponto_jog_placar = self.pontuacao_jogador

        self.azul_jog = pg.math.lerp(
            self.azul_jog, self.azul_alvo_jog, min(1.0, 8.0 * self.dt)
        )

        if self.azul_jog <= 100 + 1:
            self.azul_alvo_jog = 255

        self.placar_jogador = self.fonte_placar.render(
            f"{self.pontuacao_jogador}", True, (255, 255, int(self.azul_jog))
        )
        self.placar_jogador.set_alpha(int(self.alpha_atual_jog))
        self.screen.blit(self.placar_jogador, self.rect_placar_jogador)

        # ---------------------------------

        # Placar Oponente
        self.placar_oponente = self.fonte_placar.render(
            f"{self.pontuacao_oponente}", True, (255, 255, 255)
        )
        self.rect_placar_oponente = self.placar_oponente.get_rect()
        self.rect_placar_oponente.topleft = (int(self.screen.get_width() / 2) + 70, 20)

        if bola_rect.colliderect(self.rect_placar_oponente):
            self.alpha_alvo_opon = 100
            self.delay_opon = self.delay_padrao  # Começa o delay de 1s

        self.alpha_atual_opon = pg.math.lerp(
            self.alpha_atual_opon, self.alpha_alvo_opon, velo_lerp
        )

        if self.ponto_opon_placar != self.pontuacao_oponente:
            self.azul_alvo_opon = 100
            self.ponto_opon_placar = self.pontuacao_oponente

        self.azul_opon = pg.math.lerp(
            self.azul_opon, self.azul_alvo_opon, min(1.0, 8.0 * self.dt)
        )

        if self.azul_opon <= 100 + 1:
            self.azul_alvo_opon = 255

        self.placar_oponente = self.fonte_placar.render(
            f"{self.pontuacao_oponente}", True, (255, 255, int(self.azul_opon))
        )
        self.placar_oponente.set_alpha(int(self.alpha_atual_opon))
        self.screen.blit(self.placar_oponente, self.rect_placar_oponente)

    def reiniciar_bola(self):
        self.pos_da_bola = pg.Vector2(
            self.screen.get_width() / 2, self.screen.get_height() / 2
        )

        self.ball_spin = random.uniform(0, 2)
        # self.ball_spin = 5.0
        self.ball_velocity = pg.Vector2(
            -450 if random.randint(1, 10) <= 5 else 450,
            -450 if random.randint(1, 10) <= 5 else 450,
        )
        self.espera = 1.0
        self.vezes_colidiu = 0

    def checar_colisao_raquete_jogador(self, x_ou_y):
        # Calcula o movimento da raquete entre frames
        movimento_raquete = self.pos_raquete_jogador - self.pos_anterior_raquete_jogador

        # Posições anteriores
        bola_anterior = self.pos_da_bola - self.movimento_bola

        # Verifica colisão em múltiplos pontos ao longo da trajetória
        steps = 8  # Número de pontos intermediários a verificar
        for i in range(steps):
            # Posição interpolada da bola
            t = i / steps
            pos_bola_inter = bola_anterior + self.movimento_bola * t

            # Posição interpolada da raquete
            pos_raquete_inter = (
                self.pos_anterior_raquete_jogador + movimento_raquete * t
            )

            # Verifica colisão na posição interpolada
            if (
                x_ou_y == "x"
                and (
                    pos_raquete_inter.y
                    <= pos_bola_inter.y
                    <= pos_raquete_inter.y + self.tamanho_raquetes.y
                    and pos_bola_inter.x - self.raio_da_bola
                    <= pos_raquete_inter.x + self.tamanho_raquetes.x
                    and pos_bola_inter.x + self.raio_da_bola >= pos_raquete_inter.x
                )
                or x_ou_y == "y"
                and (
                    pos_raquete_inter.x
                    <= pos_bola_inter.x
                    <= pos_raquete_inter.x + self.tamanho_raquetes.x
                    and pos_bola_inter.y + self.raio_da_bola >= pos_raquete_inter.y
                    and pos_bola_inter.y - self.raio_da_bola
                    <= pos_raquete_inter.y + self.tamanho_raquetes.y
                )
            ):
                return True

        return False

    def checar_colisao_raquete_oponente(self, x_ou_y):
        if x_ou_y == "x":
            return (
                # Colisão no eixo X
                self.pos_raquete_oponente.y
                <= self.pos_da_bola.y
                <= self.pos_raquete_oponente.y + self.tamanho_raquetes.y
                and self.pos_da_bola.x - self.raio_da_bola
                <= self.pos_raquete_oponente.x + self.tamanho_raquetes.x
                and self.pos_da_bola.x + self.raio_da_bola
                >= self.pos_raquete_oponente.x
            )
        elif x_ou_y == "y":
            return (
                # Colisão no eixo Y
                self.pos_raquete_oponente.x
                <= self.pos_da_bola.x
                <= self.pos_raquete_oponente.x + self.tamanho_raquetes.x
                and self.pos_da_bola.y + self.raio_da_bola
                >= self.pos_raquete_oponente.y
                and self.pos_da_bola.y - self.raio_da_bola
                <= self.pos_raquete_oponente.y + self.tamanho_raquetes.y
            )
        else:
            return (
                # Colisão no eixo X
                self.pos_raquete_oponente.y
                <= self.pos_da_bola.y
                <= self.pos_raquete_oponente.y + self.tamanho_raquetes.y
                and self.pos_da_bola.x - self.raio_da_bola
                <= self.pos_raquete_oponente.x + self.tamanho_raquetes.x
                and self.pos_da_bola.x + self.raio_da_bola
                >= self.pos_raquete_oponente.x
                and
                # Colisão no eixo Y
                self.pos_raquete_oponente.x
                <= self.pos_da_bola.x
                <= self.pos_raquete_oponente.x + self.tamanho_raquetes.x
                and self.pos_da_bola.y + self.raio_da_bola
                >= self.pos_raquete_oponente.y
                and self.pos_da_bola.y - self.raio_da_bola
                <= self.pos_raquete_oponente.y + self.tamanho_raquetes.y
            )

    def desenhar_raquete_gradiente(self, rect, charge):
        # ANCHOR Raquete Jogador
        x, y, w, h = rect

        # Cores base
        if self.cooldown_raq_jogador.x <= 0:
            COR_VAZIO = pg.Vector3(255, 255, 255)
            COR_CARREGANDO = pg.Vector3(0, 255, 0)
        else:
            COR_VAZIO = pg.Vector3(100, 100, 100)
            COR_CARREGANDO = pg.Vector3(20, 180, 20)

        # 1. ESTADO: PRONTO (Carga máxima)
        if charge >= 1.0:
            # Definimos o alvo como o Amarelo Claro (B = 200 ou 250)
            # O lerp vai levar a cor até lá e parar.
            alvo_final_azul = 200.0

            # Suaviza a transição de Amarelo Forte para Claro
            self.b_amarelo_atual = pg.math.lerp(
                self.b_amarelo_atual, alvo_final_azul, min(1.0, 5.0 * self.dt)
            )

            color = (255, 255, int(self.b_amarelo_atual))

            if self.cooldown_raq_jogador.x > 0:
                color = (110, 110, 80)

            # if self.cooldown_raq_jogador.x > 0:
            #    self.charge_level = 0.0

            # Desenha o retângulo sólido
            pg.draw.rect(self.screen, color, rect)

        # 2. ESTADO: CARREGANDO (Gradiente linha por linha)
        else:
            # Resetamos a variável do azul para o próximo especial começar "forte" de novo
            self.b_amarelo_atual = 50.0

            for i in range(int(h)):
                pos_relativa = (h - i) / h

                if pos_relativa <= charge:
                    t = pos_relativa / charge if charge > 0 else 0
                    r = pg.math.lerp(COR_VAZIO.x, COR_CARREGANDO.x, t)
                    g = pg.math.lerp(COR_VAZIO.y, COR_CARREGANDO.y, t)
                    b = pg.math.lerp(COR_VAZIO.z, COR_CARREGANDO.z, t)
                    color = (int(r), int(g), int(b))
                else:
                    if self.cooldown_raq_jogador.x > 0:
                        color = (100, 100, 100)
                    else:
                        color = (255, 255, 255)

                # --- CORREÇÃO DO 1 PX ---
                # Desenhamos até x + w - 1 para bater com o tamanho do Rect
                pg.draw.line(
                    self.screen,
                    color,
                    (int(x), int(y + i)),
                    (int(x + w - 1), int(y + i)),
                )

        if self.cooldown_raq_jogador.x > 0 and self.segurando == 0:
            color = (100, 100, 100)
            pg.draw.rect(self.screen, color, rect)

    def reduzir_por_dt(self, variavel, valor_minimo):
        if variavel > 0:
            variavel -= self.dt
            variavel = max(variavel, valor_minimo)
        return variavel

    def atualizar_bola(self):
        #  ANCHOR Cooldowns
        self.espera = self.reduzir_por_dt(self.espera, 0)
        self.cooldown_charge_jog = self.reduzir_por_dt(self.cooldown_charge_jog, 0)
        self.cooldown_par.x = self.reduzir_por_dt(self.cooldown_par.x, 0)
        self.cooldown_par.y = self.reduzir_por_dt(self.cooldown_par.y, 0)
        self.cooldown_raq_jogador.x = self.reduzir_por_dt(
            self.cooldown_raq_jogador.x, 0
        )
        self.cooldown_raq_jogador.y = self.reduzir_por_dt(
            self.cooldown_raq_jogador.y, 0
        )
        self.cooldown_raq_oponente.x = self.reduzir_por_dt(
            self.cooldown_raq_oponente.x, 0
        )
        self.cooldown_raq_oponente.y = self.reduzir_por_dt(
            self.cooldown_raq_oponente.y, 0
        )
        # Reset colidiu when both cooldowns have expired
        if self.cooldown_raq_jogador.x <= 0 and self.cooldown_raq_jogador.y <= 0:
            self.colidiu = False

        if self.pos_da_bola.x - self.raio_da_bola >= self.screen.get_width() / 2:
            self.vezes_colidiu = 0

        # SECTION Bola
        if self.espera == 0:
            ball_acceleration = (
                pg.Vector2(-self.ball_velocity.y, self.ball_velocity.x)
                * self.ball_spin
                * self.magnus_factor
            )

            self.ball_velocity += ball_acceleration
            self.ball_velocity.x = min(self.ball_velocity.x, self.velocidade_max)
            self.ball_velocity.y = min(self.ball_velocity.y, self.velocidade_max)
            self.pos_da_bola += self.ball_velocity * self.dt

            # Diminui o spin gradualmente (atrito com o ar)
            self.ball_spin *= 0.998  # Perde 0.02% de rotação por frame

            # Atrito do ar na velocidade (opcional, mas ajuda muito no realismo)
            self.ball_velocity *= 0.9999995

            if (
                self.pos_da_bola.y + self.raio_da_bola >= self.screen.get_height()
                or self.pos_da_bola.y - self.raio_da_bola <= 0
            ):
                self.ball_velocity.y *= -self.ball_restitution
                self.ball_velocity.x += self.ball_spin * 5 * self.ball_friction
                bouce_effect = self.ball_spin * 15
                self.ball_velocity.x += bouce_effect
                self.ball_spin *= 0.6
                self.ball_spin *= -1
                self.pos_da_bola.y = (
                    self.screen.get_height() - self.raio_da_bola
                    if self.pos_da_bola.y + self.raio_da_bola
                    >= self.screen.get_height()
                    else self.pos_da_bola.y + self.raio_da_bola
                )

            # colisão no eixo X (verifica e reinicia a bola)
            if self.pos_da_bola.x + self.raio_da_bola >= self.screen.get_width() - 2:
                self.pontuacao_jogador += 1
                self.som_ponto.play()
                self.reiniciar_bola()
                self.colidiu = False
                self.cooldown_raq_jogador = pg.Vector2(0.0, 0.0)
                self.cooldown_raq_oponente = pg.Vector2(0.0, 0.0)
            elif self.pos_da_bola.x - self.raio_da_bola <= 2:
                self.pontuacao_oponente += 1
                self.som_ponto.play()
                self.reiniciar_bola()
                self.colidiu = False
                self.cooldown_raq_jogador = pg.Vector2(0.0, 0.0)
                self.cooldown_raq_oponente = pg.Vector2(0.0, 0.0)

            # if (
            #     self.pos_da_bola.x - self.raio_da_bola
            #     < self.pos_raquete_jogador.x + self.tamanho_raquetes.x
            #     and self.colidiu
            # ):
            #     self.pos_da_bola.x = (
            #         self.pos_raquete_jogador.x
            #         + self.tamanho_raquetes.x
            #         + self.raio_da_bola
            #     )

            # # Colisão com as raquetes
            # SECTION Colisão raquete jogador
            # ANCHOR Eixo X
            if self.pos_da_bola.x < self.zona_jogador:
                self.cooldown_raq_oponente = pg.Vector2(0.0, 0.0)
                # colisão com a raquete do jogador (verifica e aplica cooldown)
                if (
                    self.cooldown_raq_jogador.x <= 0
                    and self.checar_colisao_raquete_jogador("x")
                ):
                    self.cooldown_par = pg.Vector2(0.0, 0.0)
                    self.cooldown_raq_jogador.x = self.collision_raq_cooldown.x
                    self.cooldown_raq_jogador.y = self.collision_raq_cooldown.y
                    self.colidiu = True
                    self.som_colisao_raquete.play()

                    # Trecho que calcula a velocidade da raquete no momento da colisão
                    velo_raquete = pg.Vector2(0, 0)
                    raw_velo_raquete = pg.Vector2(0, 0)
                    if self.dt > 0:
                        raw_velo_raquete = self.movimento_raquete_jogador / self.dt
                        # print(velo_raquete)

                    velo_raquete.y = max(-2000, min(2000, raw_velo_raquete.y))
                    velo_raquete.x = max(-2000, min(2000, raw_velo_raquete.x))

                    if velo_raquete.x > 1000 and velo_raquete.x < 100:
                        self.ball_velocity.x += velo_raquete.x * 0.3

                    if self.charge_level < 1.0:
                        spin_factor = 0.005
                        fator_potencia_x = 0.5
                        efeito_borracha = 0.2
                        impulso_mouse = abs(raw_velo_raquete.x) * fator_potencia_x
                    else:
                        spin_factor = 0.05
                        fator_potencia_x = 0.9
                        efeito_borracha = 0.6
                        impulso_mouse = (
                            1000 * abs(raw_velo_raquete.x) * fator_potencia_x
                        )
                    if abs(velo_raquete.y) >= 10:
                        self.ball_spin = (-velo_raquete.y / 4) * spin_factor
                    elif self.charge_level < 1.0:
                        self.ball_spin *= 1 / 2
                    else:
                        self.ball_spin *= 5

                    if self.charge_level < 1.0:
                        self.ball_velocity.x = (
                            abs(self.ball_velocity.x) + impulso_mouse
                        ) * 1.1  # +10% de bônus
                        self.ball_velocity.y += self.ball_spin * abs(
                            self.ball_velocity.x
                        ) * efeito_borracha + (velo_raquete.y / 2)
                    else:
                        self.ball_velocity.x = (
                            abs(self.ball_velocity.x) + impulso_mouse
                        ) * 10  # +1000% de bônus
                        self.ball_velocity.y += (
                            self.ball_spin * abs(self.ball_velocity.x) * efeito_borracha
                            + (velo_raquete.y / 2) * 5
                        )

                    if self.pos_anterior_raquete_jogador.x > self.pos_da_bola.x:
                        self.ball_velocity.x *= -1

                    self.charge_level = 0.0

                    # ANCHOR Eixo Y
                    if (
                        self.cooldown_raq_jogador.y <= 0
                        and self.checar_colisao_raquete_jogador("y")
                    ):
                        self.cooldown_par = pg.Vector2(0.0, 0.0)
                        self.cooldown_raq_jogador.x = self.collision_raq_cooldown.x
                        self.cooldown_raq_jogador.y = self.collision_raq_cooldown.y
                        self.charge_level = 0.0

                        velo_raquete = pg.Vector2(0, 0)
                        raw_velo_raquete = pg.Vector2(0, 0)
                        if self.dt > 0:
                            raw_velo_raquete = self.movimento_raquete_jogador / self.dt
                            # print(velo_raquete)

                        velo_raquete.y = max(
                            -2000, min(2000, raw_velo_raquete.y)
                        )  # Limite de 2000 pixels/seg

                        fator_influencia_y = 0.5
                        self.ball_velocity.y *= -self.ball_restitution
                        self.ball_velocity.y += velo_raquete.y * fator_influencia_y
                        self.ball_velocity.x += self.ball_spin * 5 * self.ball_friction
                        bouce_effect = self.ball_spin * 15
                        self.ball_velocity.x += bouce_effect
                        self.ball_spin *= 0.8
                        self.ball_velocity.y *= -1

            if self.pos_da_bola.x > self.zona_oponente:
                self.cooldown_raq_jogador = pg.Vector2(0.0, 0.0)
                self.colidiu = False
                # Colisão com a raquete do oponente (verifica e aplica cooldown)
                if self.cooldown_raq_oponente.x <= 0:
                    if self.checar_colisao_raquete_oponente("x"):
                        self.cooldown_par = pg.Vector2(0.0, 0.0)

                        self.cooldown_raq_oponente.x = self.collision_raq_cooldown.x
                        self.cooldown_raq_oponente.y = self.collision_raq_cooldown.y

                        self.som_colisao_raquete.play()

                        # Trecho que calcula a velocidade da raquete no momento da colisão
                        velocity_raquete = pg.Vector2(0, 0)

                        if self.dt > 0:
                            velocity_raquete = (
                                self.dir_raq_oponente * self.velo_raq_oponente * self.dt
                            )

                        spin_factor = 0.05
                        if abs(velocity_raquete.y) >= 10:
                            self.ball_spin = (-velocity_raquete.y / 4) * spin_factor
                        else:
                            self.ball_spin *= 1 / 2

                        fator_potencia_x = 200.0
                        efeito_borracha = 1.0
                        impulso_raq_oponente = (
                            abs(velocity_raquete.x) * fator_potencia_x
                        )
                        self.ball_velocity.x = (
                            abs(self.ball_velocity.x) + impulso_raq_oponente
                        ) * 1.1  # +10% de bônus
                        self.ball_velocity.y += self.ball_spin * abs(
                            self.ball_velocity.x
                        ) * efeito_borracha + (velocity_raquete.y / 2)
                        if self.pos_anterior_raquete_oponente.x > self.pos_da_bola.x:
                            self.ball_velocity.x *= -1

                    if (
                        self.cooldown_raq_oponente.y <= 0
                        and self.checar_colisao_raquete_oponente("y")
                    ):
                        self.cooldown_par = pg.Vector2(0.0, 0.0)

                        self.cooldown_raq_oponente.y = self.collision_raq_cooldown.y

                        velo_raquete = pg.Vector2(0, 0)

                        fator_influencia_y = 3.5  # Ajuste esse valor para controlar a influência da raquete na bola

                        if self.dt > 0:
                            velocity_raquete = (
                                self.dir_raq_oponente * self.velo_raq_oponente * self.dt
                            )
                            fator_influencia_y = 0.5
                            self.ball_velocity.y *= -self.ball_restitution
                            self.ball_velocity.y += (
                                velocity_raquete.y * fator_influencia_y
                            )
                            self.ball_velocity.x += (
                                self.ball_spin * 5 * self.ball_friction
                            )
                            bouce_effect = self.ball_spin * 15
                            self.ball_velocity.x += bouce_effect
                            self.ball_spin *= 0.8
                            self.ball_velocity.y *= -1

        pg.draw.circle(self.screen, "white", self.pos_da_bola, self.raio_da_bola)

    def atualizar_raquete_jogador(self):
        pg.event.get()
        mousekey = pg.mouse.get_pressed()
        # Armazena a posição anterior da raquete
        self.pos_anterior_raquete_jogador = self.pos_raquete_jogador.copy()

        if not self.colidiu and self.segurando == 0:
            if (
                self.pos_da_bola.x >= self.zona_jogador
                and self.velocidade_maxima < 15.0
            ):
                self.velocidade_maxima += 0.2
                self.velocidade_maxima = min(self.velocidade_maxima, 15.0)
        elif self.colidiu:
            self.velocidade_maxima = self.velocidade_bola * 0.05
            self.velocidade_maxima = 2.0  # pixels por frame

        # 2. Pegamos a posição alvo (centralizada no mouse)
        posicao_alvo = pg.Vector2(
            pg.mouse.get_pos()[0] - self.tamanho_raquetes.x / 2,
            pg.mouse.get_pos()[1] - self.tamanho_raquetes.y / 2,
        )

        # Cálculo do movimento da raquete
        deslocamento = posicao_alvo - self.pos_raquete_jogador
        distancia = deslocamento.length()

        if distancia > 0:
            # Se a distância até o mouse for maior que a velocidade máxima permitida:
            if distancia > self.velocidade_maxima:
                # Normalizamos o vetor (tamanho 1) e multiplicamos pela velocidade máxima
                direcao = deslocamento.normalize()
                self.pos_raquete_jogador += direcao * self.velocidade_maxima
            else:
                # Se for menor, a raquete simplesmente chega ao mouse suavemente
                self.pos_raquete_jogador = posicao_alvo

        # Mecânica de charge da raquete do jogador
        if not mousekey[0]:
            self.charge_level = max(
                0.0, self.charge_level - self.charge_speed * 2 * self.dt
            )
            self.segurando = 0
        else:
            # Incrementa a carga enquanto segura o botão
            self.charge_level = min(
                1.0, self.charge_level + self.charge_speed * self.dt
            )
            self.segurando = 1

        self.movimento_raquete_jogador = pg.Vector2(
            self.pos_raquete_jogador.x - self.pos_anterior_raquete_jogador.x,
            self.pos_raquete_jogador.y - self.pos_anterior_raquete_jogador.y,
        )

        self.pos_mouse_desejada = pg.Vector2(
            pg.mouse.get_pos()[0], pg.mouse.get_pos()[1]
        )
        # Limites da tela
        self.pos_raquete_jogador.y = max(0, self.pos_raquete_jogador.y)
        if (
            self.pos_raquete_jogador.y + self.tamanho_raquetes.y
            >= self.screen.get_height()
        ):
            self.pos_raquete_jogador.y = (
                self.screen.get_height() - self.tamanho_raquetes.y
            )
        self.pos_raquete_jogador.x = max(0, self.pos_raquete_jogador.x)
        if (
            self.pos_raquete_jogador.x + self.tamanho_raquetes.x
            >= self.screen.get_width() * (2 / 5)
        ):
            self.pos_raquete_jogador.x = (
                self.screen.get_width() * (2 / 5) - self.tamanho_raquetes.x
            )

        raquete_rect = (
            self.pos_raquete_jogador.x,
            self.pos_raquete_jogador.y,
            self.tamanho_raquetes.x,
            self.tamanho_raquetes.y,
        )
        self.desenhar_raquete_gradiente(raquete_rect, self.charge_level)

    def atualizar_raquete_oponente(self):
        self.pos_anterior_raquete_oponente = self.pos_raquete_oponente.copy()

        self.velo_raq_oponente = 900
        self.dir_raq_oponente = pg.Vector2(0, 0)
        key = pg.key.get_pressed()
        if key[pg.K_LSHIFT]:
            self.velo_raq_oponente = 1600
        if self.layout_selecionado == "colemak":
            if key[pg.K_w]:
                self.dir_raq_oponente.y -= 1
            if key[pg.K_r]:
                self.dir_raq_oponente.y += 1
            if key[pg.K_a]:
                self.dir_raq_oponente.x -= 1
            if key[pg.K_s]:
                self.dir_raq_oponente.x += 1
        else:  # qwerty
            if key[pg.K_w]:
                self.dir_raq_oponente.y -= 1
            if key[pg.K_s]:
                self.dir_raq_oponente.y += 1
            if key[pg.K_a]:
                self.dir_raq_oponente.x -= 1
            if key[pg.K_d]:
                self.dir_raq_oponente.x += 1
        if self.dir_raq_oponente.length() > 0:
            self.dir_raq_oponente = self.dir_raq_oponente.normalize()
            self.pos_raquete_oponente += (
                self.dir_raq_oponente * self.velo_raq_oponente * self.dt
            )

        self.movimento_raquete_oponente = pg.Vector2(
            self.pos_raquete_oponente.x - self.pos_anterior_raquete_oponente.x,
            self.pos_raquete_oponente.y - self.pos_anterior_raquete_oponente.y,
        )

        diferenca_y = self.pos_da_bola.y - (
            self.pos_raquete_oponente.y + self.tamanho_raquetes.y / 2
        )
        diferenca_x = self.pos_da_bola.x - (
            self.pos_raquete_oponente.x + self.tamanho_raquetes.x / 2
        )

        if (
            abs(diferenca_x) < 10
            and self.pos_da_bola.y > self.pos_raquete_oponente.y - 10
        ):
            self.pos_raquete_oponente.y += abs(diferenca_y) * 0.1 * self.dt * 60
        if (
            abs(diferenca_x) < 10
            and self.pos_da_bola.y
            < self.pos_raquete_oponente.y + self.tamanho_raquetes.y + 10
        ):
            self.pos_raquete_oponente.y -= abs(diferenca_y) * 0.1 * self.dt * 60

        ## Limites da tela
        # Limita o chão
        if (
            self.pos_raquete_oponente.y + self.tamanho_raquetes.y
            >= self.screen.get_height()
        ):
            self.pos_raquete_oponente.y = (
                self.screen.get_height() - self.tamanho_raquetes.y
            )
        # Limita o teto
        self.pos_raquete_oponente.y = max(0, self.pos_raquete_oponente.y)
        # Limita canto direito
        if (
            self.pos_raquete_oponente.x + self.tamanho_raquetes.x
            >= self.screen.get_width()
        ):
            self.pos_raquete_oponente.x = (
                self.screen.get_width() - self.tamanho_raquetes.x
            )
        # Limita o meio
        self.pos_raquete_oponente.x = max(
            self.screen.get_width() * (3 / 5), self.pos_raquete_oponente.x
        )
        if self.pos_da_bola.x <= self.zona_oponente:
            self.cooldown_raq_oponente = pg.Vector2(0.0, 0.0)

        if self.cooldown_raq_oponente.x > 0:
            pg.draw.rect(
                self.screen,
                "grey",
                pg.Rect(
                    self.pos_raquete_oponente.x,
                    self.pos_raquete_oponente.y,
                    self.tamanho_raquetes.x,
                    self.tamanho_raquetes.y,
                ),
            )
        else:
            pg.draw.rect(
                self.screen,
                "white",
                pg.Rect(
                    self.pos_raquete_oponente.x,
                    self.pos_raquete_oponente.y,
                    self.tamanho_raquetes.x,
                    self.tamanho_raquetes.y,
                ),
            )

    def run(self):
        while self.running:
            # Limit FPS to 60 when paused to save CPU, otherwise unlimited (or 1000)
            if self.paused:
                self.dt = self.clock.tick(60) / 1000
            else:
                self.dt = self.clock.tick(1000) / 1000

            # Eventos
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                elif event.type == pg.KEYDOWN:  # noqa: SIM102
                    if event.key == pg.K_ESCAPE:
                        if self.paused:
                            # Currently paused, so we are about to unpause
                            racket_center = (
                                self.pos_raquete_jogador + self.tamanho_raquetes / 2
                            )
                            desired_mouse_pos = racket_center + self.saved_mouse_offset
                            pg.mouse.set_pos((desired_mouse_pos.x, desired_mouse_pos.y))
                            # discard any accumulated mouse movement
                            pg.mouse.get_rel()
                        else:
                            # Currently not paused, so we are about to pause
                            mouse_pos = pg.Vector2(pg.mouse.get_pos())
                            racket_center = (
                                self.pos_raquete_jogador + self.tamanho_raquetes / 2
                            )
                            self.saved_mouse_offset = mouse_pos - racket_center

                        # Toggle pause state and update mouse grab/visibility
                        self.paused = not self.paused
                        self.mouse_captured = not self.mouse_captured
                        self.mouse_visible = not self.mouse_visible
                        pg.event.set_grab(self.mouse_captured)
                        pg.mouse.set_visible(self.mouse_visible)

            # Desenho do fundo e linha central (sempre)
            self.desenhar_jogo()

            # Atualização e desenho dos objetos do jogo (apenas se não estiver pausado)
            if not self.paused:
                self.atualizar_raquete_jogador()
                self.atualizar_raquete_oponente()
                self.atualizar_bola()
                self.atualizar_placar()

            # Overlay de pausa
            if self.paused:
                overlay = pg.Surface(self.screen.get_size(), pg.SRCALPHA)
                overlay.fill((0, 0, 0, 180))  # semi-transparent black
                self.screen.blit(overlay, (0, 0))
                text = self.fonte_retro(100).render("PAUSED", True, (255, 255, 255))
                help_text = self.fonte_retro(60).render(
                    "Press ESC to unpause", True, (255, 255, 255)
                )
                rect = text.get_rect(
                    center=(
                        self.screen.get_width() // 2,
                        self.screen.get_height() // 2 - 100,
                    )
                )
                help_rect = help_text.get_rect(
                    center=(
                        self.screen.get_width() // 2,
                        self.screen.get_height() // 2,
                    )
                )
                self.screen.blit(text, rect)
                self.screen.blit(help_text, help_rect)

            # Renderização
            pg.display.flip()


if __name__ == "__main__":
    game = Game()
    game.run()
    pg.quit()

# %%
