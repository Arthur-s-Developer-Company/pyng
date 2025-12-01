if __name__ == "__main__":
    from Caminhos import Caminho
else:
    from classes.Caminhos import Caminho  
import pygame as pg
import random

class Game:
    def __init__(self):
        pg.init()
        # Tela
        self.screen = pg.display.set_mode((1920, 1080), pg.FULLSCREEN)  # Tamanho fixo
        
        # Mixer
        pg.mixer.init()

        # Mouse
        pg.display.set_caption("Pyng")  # Título da janela
        # pg.mouse.set_visible(False)  # Torna o cursor invisível
        pg.event.set_grab(True)
        self.mouse_captured = True
        
        # Tempo
        self.clock = pg.time.Clock()
        self.running = True
        self.dt = 0
        
        # Inicialização das variáveis do jogo
        self.setup_game()
        
    def setup_game(self):
        self.caminho = Caminho()
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
        self.pos_da_bola = pg.Vector2(self.screen.get_width() / 2, self.screen.get_height() / 2)
        self.dir_da_bola = pg.Vector2(-1 if random.randint(1,2) == 1 else 1,
                                      -1 if random.randint(1,2) == 1 else 1)
        self.velocidade_base_bola = 450
        self.velocidade_bola = self.velocidade_base_bola
        self.air_drag = 0.3        
        self.movimento_bola = pg.Vector2(self.dir_da_bola.x * self.velocidade_bola * self.dt,
                                         self.dir_da_bola.y * self.velocidade_bola * self.dt)
        ## Raquetes
        self.tamanho_raquetes = pg.Vector2(20, 80)

        # Zona segura para checar o jogador (metade esquerda + buffer)
        self.zona_jogador = self.screen.get_width() * (3/5) 
        # Zona segura para checar o oponente (metade direita + buffer)
        self.zona_oponente = self.screen.get_width() * (2/5)
        
        
        # Raquete Jogador
        self.pos_raquete_jogador = pg.Vector2(self.screen.get_width() / 100, self.screen.get_height() / 2 - self.tamanho_raquetes.y / 2)
        self.vezes_colidiu = 0
        self.pos_anterior_raquete_jogador = self.pos_raquete_jogador.copy()

        # Quantidade máxima de vezes que a raquete pode colidir antes de ficar "transparente" e traspassável
        self.max_vezes_pode_colidir = 0

        # Raquete Oponente
        self.pos_raquete_oponente = pg.Vector2(self.screen.get_width() - self.tamanho_raquetes.x - self.screen.get_width() / 100, self.screen.get_height() / 2 - self.tamanho_raquetes.y / 2)

        # Placar
        self.pontuacao_jogador = 0
        self.pontuacao_oponente = 0
        self.ponto_jog_placar = self.pontuacao_jogador
        self.ponto_opon_placar = self.pontuacao_oponente
        self.fonte_placar = pg.font.Font(self.caminho.obter_caminho("Fonts/FiraCode-Bold.ttf"), 50)
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
        self.som_colisao_raquete = pg.mixer.Sound(self.caminho.obter_caminho("Sons/hit_paddle.wav"))


    def desenhar_jogo(self):
        # Desenha a linha central
        self.screen.fill("black")
        pg.draw.line(self.screen, "grey", (self.screen.get_width() / 2, 0), (self.screen.get_width() / 2, self.screen.get_height()), 1)

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
        
        
        
        bola_rect = pg.Rect(self.pos_da_bola.x - self.raio_da_bola, self.pos_da_bola.y - self.raio_da_bola,
                            self.raio_da_bola * 2, self.raio_da_bola * 2)
        
        # ---------------------------------

        # Placar Jogador
        self.placar_jogador = self.fonte_placar.render(f"{self.pontuacao_jogador}", True, (255, 255, 255))
        self.rect_placar_jogador = self.placar_jogador.get_rect()
        self.rect_placar_jogador.topleft = (int(self.screen.get_width() / 2) - 70 - self.rect_placar_jogador.width, 20)
        
        if bola_rect.colliderect(self.rect_placar_jogador):
            self.alpha_alvo_jog = 100
            self.delay_jog = self.delay_padrao  # Começa o delay de 1s
        
        velo_lerp = min(1.0, 15.0 * self.dt)
        self.alpha_atual_jog = pg.math.lerp(self.alpha_atual_jog, self.alpha_alvo_jog, velo_lerp)
        self.placar_jogador.set_alpha(int(self.alpha_atual_jog))

        if self.ponto_jog_placar != self.pontuacao_jogador:
            self.azul_alvo_jog = 100
            self.ponto_jog_placar = self.pontuacao_jogador

        self.azul_jog = pg.math.lerp(self.azul_jog, self.azul_alvo_jog, min(1.0, 8.0 * self.dt))
        
        if self.azul_jog <= 100 + 1:
            self.azul_alvo_jog = 255

        self.placar_jogador = self.fonte_placar.render(f"{self.pontuacao_jogador}", True, (255, 255, int(self.azul_jog)))

        self.screen.blit(self.placar_jogador, self.rect_placar_jogador)
        
        # ---------------------------------

        # Placar Oponente
        self.placar_oponente = self.fonte_placar.render(f"{self.pontuacao_oponente}", True, (255, 255, 255))
        self.rect_placar_oponente = self.placar_oponente.get_rect()
        self.rect_placar_oponente.topleft = (int(self.screen.get_width() / 2) + 70, 20)
        
        if bola_rect.colliderect(self.rect_placar_oponente):
            self.alpha_alvo_opon = 100
            self.delay_opon = self.delay_padrao  # Começa o delay de 1s
        
        self.alpha_atual_opon = pg.math.lerp(self.alpha_atual_opon, self.alpha_alvo_opon, velo_lerp)
        self.placar_oponente.set_alpha(int(self.alpha_atual_opon))

        if self.ponto_opon_placar != self.pontuacao_oponente:
            self.azul_alvo_opon = 100
            self.ponto_opon_placar = self.pontuacao_oponente

        self.azul_opon = pg.math.lerp(self.azul_opon, self.azul_alvo_opon, min(1.0, 8.0 * self.dt))
        
        if self.azul_opon <= 100 + 1:
            self.azul_alvo_opon = 255

        self.placar_oponente = self.fonte_placar.render(f"{self.pontuacao_oponente}", True, (255, 255, int(self.azul_opon)))

        self.screen.blit(self.placar_oponente, self.rect_placar_oponente)


    def reiniciar_bola(self):
        self.pos_da_bola = pg.Vector2(self.screen.get_width() / 2, self.screen.get_height() / 2)
        self.dir_da_bola = pg.Vector2(-1 if random.randint(1,2) == 1 else 1,
                                      -1 if random.randint(1,2) == 1 else 1)
        self.velocidade_bola = self.velocidade_base_bola
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
            pos_raquete_inter = self.pos_anterior_raquete_jogador + movimento_raquete * t
            
            # Verifica colisão na posição interpolada
            if x_ou_y == 'x':
                if (pos_raquete_inter.y <= pos_bola_inter.y <= pos_raquete_inter.y + self.tamanho_raquetes.y and
                    pos_bola_inter.x - self.raio_da_bola <= pos_raquete_inter.x + self.tamanho_raquetes.x and 
                    pos_bola_inter.x + self.raio_da_bola >= pos_raquete_inter.x):
                    return True
            elif x_ou_y == 'y':
                if (pos_raquete_inter.x <= pos_bola_inter.x <= pos_raquete_inter.x + self.tamanho_raquetes.x and 
                    pos_bola_inter.y + self.raio_da_bola >= pos_raquete_inter.y and 
                    pos_bola_inter.y - self.raio_da_bola <= pos_raquete_inter.y + self.tamanho_raquetes.y):
                    return True
        
        return False

    def checar_colisao_raquete_oponente(self, x_ou_y):
        if x_ou_y == 'x':
            return (
                # Colisão no eixo X
                self.pos_raquete_oponente.y <= self.pos_da_bola.y <= self.pos_raquete_oponente.y + self.tamanho_raquetes.y and
                self.pos_da_bola.x - self.raio_da_bola <= self.pos_raquete_oponente.x + self.tamanho_raquetes.x and 
                self.pos_da_bola.x + self.raio_da_bola >= self.pos_raquete_oponente.x
                )
        elif x_ou_y == 'y':
            return (
                # Colisão no eixo Y
                self.pos_raquete_oponente.x <= self.pos_da_bola.x <= self.pos_raquete_oponente.x + self.tamanho_raquetes.x and 
                self.pos_da_bola.y + self.raio_da_bola >= self.pos_raquete_oponente.y and 
                self.pos_da_bola.y - self.raio_da_bola <= self.pos_raquete_oponente.y + self.tamanho_raquetes.y
                )
        else:
            return (
                # Colisão no eixo X
                self.pos_raquete_oponente.y <= self.pos_da_bola.y <= self.pos_raquete_oponente.y + self.tamanho_raquetes.y and
                self.pos_da_bola.x - self.raio_da_bola <= self.pos_raquete_oponente.x + self.tamanho_raquetes.x and 
                self.pos_da_bola.x + self.raio_da_bola >= self.pos_raquete_oponente.x and
                # Colisão no eixo Y
                self.pos_raquete_oponente.x <= self.pos_da_bola.x <= self.pos_raquete_oponente.x + self.tamanho_raquetes.x and 
                self.pos_da_bola.y + self.raio_da_bola >= self.pos_raquete_oponente.y and 
                self.pos_da_bola.y - self.raio_da_bola <= self.pos_raquete_oponente.y + self.tamanho_raquetes.y
                )

    def atualizar_bola(self):     

        # Aplica o tempo de espera inicial
        if self.espera > 0:
            self.espera -= self.dt

        elif self.espera <= 0:
            self.espera = 0


        # Diminui o cooldown de colisão com paredes
        if self.cooldown_par.x > 0:
            self.cooldown_par.x -= self.dt

            if self.cooldown_par.x < 0:
                self.cooldown_par.x = 0

        if self.cooldown_par.y > 0:
            self.cooldown_par.y -= self.dt

            if self.cooldown_par.y < 0:
                self.cooldown_par.y = 0


        # Diminui o cooldown da raquete do jogador
        if self.cooldown_raq_jogador.x > 0:
            self.cooldown_raq_jogador.x -= self.dt

            if self.cooldown_raq_jogador.x < 0:
                self.cooldown_raq_jogador.x = 0

        if self.cooldown_raq_jogador.y > 0:
            self.cooldown_raq_jogador.y -= self.dt

            if self.cooldown_raq_jogador.y < 0:
                self.cooldown_raq_jogador.y = 0


        # Diminui o cooldown da raquete do oponente
        if self.cooldown_raq_oponente.x > 0:
            self.cooldown_raq_oponente.x -= self.dt

            if self.cooldown_raq_oponente.x < 0:
                self.cooldown_raq_oponente.x = 0

        if self.cooldown_raq_oponente.y > 0:
            self.cooldown_raq_oponente.y -= self.dt

            if self.cooldown_raq_oponente.y < 0:
                self.cooldown_raq_oponente.y = 0

        
        if self.pos_da_bola.x - self.raio_da_bola >= self.screen.get_width() / 2:
            self.vezes_colidiu = 0 


        if self.espera == 0:
            # Normaliza a direção da bola e aplica pequenas correções para evitar ângulos muito retos
            if abs(self.dir_da_bola.x) < 0.25:
                self.dir_da_bola.y *= 0.995
            self.dir_da_bola = self.dir_da_bola.normalize()
            
            # Movimento da bola com air drag
            self.velocidade_bola -= self.air_drag

            if self.velocidade_bola <= self.velocidade_base_bola:
                self.velocidade_bola = self.velocidade_base_bola

            self.pos_da_bola += self.dir_da_bola.normalize() * self.velocidade_bola * self.dt
            
            # colisão no eixo X (verifica e reinicia a bola)
            if self.pos_da_bola.x + self.raio_da_bola >= self.screen.get_width() -2:
                self.pontuacao_jogador += 1
                self.reiniciar_bola()

            elif self.pos_da_bola.x - self.raio_da_bola <= 2:
                self.pontuacao_oponente += 1
                self.reiniciar_bola()
                
            # colisão no eixo Y (verifica e aplica cooldown)
            if (self.pos_da_bola.y + self.raio_da_bola > self.screen.get_height() or self.pos_da_bola.y - self.raio_da_bola < 0) and self.cooldown_par.y <= 0:
                self.dir_da_bola.y *= -1

                self.cooldown_par.y = self.collision_par_cooldown
            
            # Colisão com as raquetes
            if self.pos_da_bola.x < self.zona_jogador:

                # colisão com a raquete do jogador (verifica e aplica cooldown)
                if self.checar_colisao_raquete_jogador("x") and self.cooldown_raq_jogador.x <= 0:  
                    
                    self.cooldown_par = pg.Vector2(0.0, 0.0)
                    self.cooldown_raq_jogador.x = self.collision_raq_cooldown.x
                    self.cooldown_raq_jogador.y = self.collision_raq_cooldown.y

                    self.som_colisao_raquete.play()

                    # Trecho que calcula a velocidade da raquete no momento da colisão
                    velo_raquete = pg.Vector2(0, 0)
                    fator_influencia_x = 0.05
                    fator_influencia_y = 0.05

                    if self.dt > 0:
                        velo_raquete = self.movimento_raquete_jogador / self.dt
                        # print(velo_raquete)

                    dir_raquete = self.movimento_raquete_jogador.normalize() if self.movimento_raquete_jogador.length() > 0 else pg.Vector2(0, 0)

                    if self.dir_da_bola.x > 0:
                        self.dir_da_bola.x += dir_raquete.x
                    else:
                        self.dir_da_bola.x *= -1

                    # Aumenta a velocidade da bola com base na velocidade da raquete
                    if velo_raquete.x != 0:
                        self.velocidade_bola += velo_raquete.x * fator_influencia_x
                        if dir_raquete.x > 0:
                            self.dir_da_bola.x += dir_raquete.x

                    if velo_raquete.y != 0:
                        self.velocidade_bola += abs(velo_raquete.y) * fator_influencia_y
                        if dir_raquete.y != 0:
                            self.dir_da_bola.y = dir_raquete.y

                    self.dir_da_bola.y += dir_raquete.y

                    self.dir_da_bola = self.dir_da_bola.normalize()

                    if velo_raquete.x / 2 > abs(velo_raquete.y):
                        if abs(self.dir_da_bola.y) * 1.5 >= abs(self.dir_da_bola.x):
                            self.dir_da_bola.y /= 100

                    elif abs(velo_raquete.x) < 10 and abs(velo_raquete.y) < 10:
                        self.velocidade_bola /= 2

                    self.dir_da_bola = self.dir_da_bola.normalize()

                    velocidade_max = 1000

                    if self.velocidade_bola > velocidade_max: 
                        self.velocidade_bola = velocidade_max
                    if self.velocidade_bola < self.velocidade_base_bola:
                        self.velocidade_bola = self.velocidade_base_bola

                    self.vezes_colidiu += 1

                elif self.checar_colisao_raquete_jogador("y") and self.cooldown_raq_jogador.y <= 0:
                    self.cooldown_par = pg.Vector2(0.0, 0.0)

                    self.cooldown_raq_jogador.y = self.collision_raq_cooldown.y

                    velo_raquete = pg.Vector2(0, 0)

                    fator_influencia_y = 0.0005 # Ajuste esse valor para controlar a influência da raquete na bola

                    if self.dt > 0:
                        velo_raquete = self.movimento_raquete_jogador / self.dt

                    if self.pos_da_bola.y < self.pos_raquete_jogador.y and self.dir_da_bola.y < 0:
                        if velo_raquete.y != 0:
                            self.dir_da_bola.y += velo_raquete.y * fator_influencia_y

                    elif self.pos_da_bola.y > self.pos_raquete_jogador.y + self.tamanho_raquetes.y and self.dir_da_bola.y > 0:
                        if velo_raquete.y != 0:
                            self.dir_da_bola.y += velo_raquete.y * fator_influencia_y

                    self.dir_da_bola.y *= -1

            if self.pos_da_bola.x > self.zona_oponente:

                # Colisão com a raquete do oponente (verifica e aplica cooldown)
                if self.checar_colisao_raquete_oponente("x") and self.cooldown_raq_oponente.x <= 0:

                    self.cooldown_par = pg.Vector2(0.0, 0.0)

                    self.cooldown_raq_oponente.x = self.collision_raq_cooldown.x
                    self.cooldown_raq_oponente.y = self.collision_raq_cooldown.y

                    # Trecho que calcula a velocidade da raquete no momento da colisão
                    velo_raquete = pg.Vector2(0, 0)
                    fator_influencia_x = 0.005
                    fator_influencia_y = 0.00005

                    self.dir_raq_oponente = self.dir_raq_oponente.normalize() if self.dir_raq_oponente.length() > 0 else pg.Vector2(0, 0)

                    if self.dt > 0:
                        velo_raquete = self.dir_raq_oponente * self.velo_raq_oponente / self.dt
                        # print(velo_raquete)

                    self.dir_da_bola.x *= -1

                    if self.dir_raq_oponente.x < 0:
                        self.velocidade_bola += abs(velo_raquete.x) * fator_influencia_x
                        self.dir_da_bola.x += self.dir_da_bola.x / 2
                    if self.dir_raq_oponente.y != 0:
                        self.velocidade_bola += abs(velo_raquete.y) * fator_influencia_y
                        self.dir_da_bola.y += self.dir_raq_oponente.y / 2

                    self.dir_da_bola = self.dir_da_bola.normalize()

                    velocidade_max = 1000

                    if self.velocidade_bola > velocidade_max: 
                        self.velocidade_bola = velocidade_max
                    if self.velocidade_bola < self.velocidade_base_bola:
                        self.velocidade_bola = self.velocidade_base_bola

                    self.vezes_colidiu += 1

                elif self.checar_colisao_raquete_oponente("y") and self.cooldown_raq_oponente.y <= 0:
                    print(self.cooldown_raq_oponente.y)
                    self.cooldown_par = pg.Vector2(0.0, 0.0)

                    self.cooldown_raq_oponente.y = self.collision_raq_cooldown.y

                    velo_raquete = pg.Vector2(0, 0)

                    fator_influencia_y = 0.00005 # Ajuste esse valor para controlar a influência da raquete na bola

                    if self.dt > 0:
                        velo_raquete = self.dir_raq_oponente * self.velo_raq_oponente / self.dt

                    if self.pos_da_bola.y < self.pos_raquete_oponente.y and self.dir_da_bola.y < 0:
                        if velo_raquete.y != 0:
                            self.dir_da_bola.y += velo_raquete.y * fator_influencia_y

                    elif self.pos_da_bola.y > self.pos_raquete_oponente.y + self.tamanho_raquetes.y and self.dir_da_bola.y > 0:
                        if velo_raquete.y != 0:
                            self.dir_da_bola.y += velo_raquete.y * fator_influencia_y

                    self.dir_da_bola.y *= -1

        pg.draw.circle(self.screen, "white", self.pos_da_bola, self.raio_da_bola)

    def atualizar_raquete_jogador(self):
        # Armazena a posição anterior da raquete
        self.pos_anterior_raquete_jogador = self.pos_raquete_jogador.copy()

        # posição desejada baseada no mouse (centraliza a raquete)
        mouse_x, mouse_y = pg.mouse.get_pos()
        desejada = pg.Vector2(mouse_x - self.tamanho_raquetes.x / 2,
                            mouse_y - self.tamanho_raquetes.y / 2)

        # deslocamento bruto (pixels por frame)
        desloc = desejada - self.pos_anterior_raquete_jogador
        
        """velocidade = 450
        direcao = pg.Vector2(0, 0)
        key = pg.key.get_pressed()
        if key[pg.K_w]:
            direcao.y -= 1
        if key[pg.K_r]:
            direcao.y += 1
        if key[pg.K_a]:
            direcao.x -= 1
        if key[pg.K_s]:
            direcao.x += 1
        if direcao.length() > 0:
            direcao = direcao.normalize()
        if direcao.y > 0:
            print(direcao.y)
            self.pos_raquete += direcao * velocidade * self.dt"""
        
        self.pos_raquete_jogador = pg.Vector2(pg.mouse.get_pos()[0] - self.tamanho_raquetes.x / 2,
                                              pg.mouse.get_pos()[1] - self.tamanho_raquetes.y / 2)

        self.movimento_raquete_jogador = pg.Vector2(self.pos_raquete_jogador.x - self.pos_anterior_raquete_jogador.x,
                              self.pos_raquete_jogador.y - self.pos_anterior_raquete_jogador.y)
        # print(self.movimento_raquete)
        
        

        # Limites da tela
        if self.pos_raquete_jogador.y <= 0:
            self.pos_raquete_jogador.y = 0
        if self.pos_raquete_jogador.y + self.tamanho_raquetes.y >= self.screen.get_height():
            self.pos_raquete_jogador.y = self.screen.get_height() - self.tamanho_raquetes.y
        if self.pos_raquete_jogador.x <= 0:
            self.pos_raquete_jogador.x = 0
        if self.pos_raquete_jogador.x + self.tamanho_raquetes.x >= self.screen.get_width() * (2/5):
            self.pos_raquete_jogador.x = self.screen.get_width() * (2/5) - self.tamanho_raquetes.x
        
        pos_raquete_imaginaria = self.pos_raquete_jogador.copy()     
        pos_mouse_desejada = pg.Vector2(pg.mouse.get_pos()[0], pg.mouse.get_pos()[1])    

        # Quando em cooldown, limitamos apenas a posição visual; NÃO sobrescrever self.pos_raquete_jogador
        if self.cooldown_raq_jogador.x > 0 and self.cooldown_raq_jogador.y > 0 and self.dir_da_bola.x > 0:
            pos_raquete_imaginaria.x = min(pos_raquete_imaginaria.x, self.pos_da_bola.x - 5 - self.raio_da_bola - self.tamanho_raquetes.x / 2 )
            # <-- removida a atribuição self.pos_raquete_jogador = pos_raquete_imaginaria

            if self.pos_da_bola.x >= self.screen.get_width() * 2/5:
                # só ajusta a posição visual (não a usada para colisão)
                pos_raquete_imaginaria.x = pos_raquete_imaginaria.x

        if pos_raquete_imaginaria.x + self.tamanho_raquetes.x >= self.screen.get_width() * (2/5):
            pos_raquete_imaginaria.x = self.screen.get_width() * (2/5) - self.tamanho_raquetes.x

        # Desenho: use pos_raquete_imaginaria apenas para visual quando cooldown ativo,
        # mas mantenha self.pos_raquete_jogador para colisões em atualizar_bola()
        if self.cooldown_raq_jogador.x > 0:
            pg.draw.rect(self.screen, "grey", pg.Rect(pos_raquete_imaginaria.x, pos_raquete_imaginaria.y, self.tamanho_raquetes.x, self.tamanho_raquetes.y))
        else:
            pg.draw.rect(self.screen, "white", pg.Rect(self.pos_raquete_jogador.x, self.pos_raquete_jogador.y, self.tamanho_raquetes.x, self.tamanho_raquetes.y))
            
    def atualizar_raquete_oponente(self):
        self.pos_anterior_raquete_oponente = self.pos_raquete_oponente.copy()
        
        self.velo_raq_oponente = 800
        self.dir_raq_oponente = pg.Vector2(0, 0)
        key = pg.key.get_pressed()
        if key[pg.K_w]:
            self.dir_raq_oponente.y -= 1
        if key[pg.K_r]:
            self.dir_raq_oponente.y += 1
        if key[pg.K_a]:
            self.dir_raq_oponente.x -= 1
        if key[pg.K_s]:
            self.dir_raq_oponente.x += 1
        if self.dir_raq_oponente.length() > 0:
            self.dir_raq_oponente = self.dir_raq_oponente.normalize()
            self.pos_raquete_oponente += self.dir_raq_oponente * self.velo_raq_oponente * self.dt
        
        self.movimento_raquete_oponente = pg.Vector2(self.pos_raquete_oponente.x - self.pos_anterior_raquete_oponente.x,
                              self.pos_raquete_oponente.y - self.pos_anterior_raquete_oponente.y)
        
        ## Limites da tela
        # Limita o chão
        if self.pos_raquete_oponente.y + self.tamanho_raquetes.y >= self.screen.get_height():
            self.pos_raquete_oponente.y = self.screen.get_height() - self.tamanho_raquetes.y
        # Limita o teto
        if self.pos_raquete_oponente.y <= 0:
            self.pos_raquete_oponente.y = 0
        # Limita canto direito
        if self.pos_raquete_oponente.x + self.tamanho_raquetes.x >= self.screen.get_width():
            self.pos_raquete_oponente.x = self.screen.get_width() - self.tamanho_raquetes.x
        # Limita o meio
        if self.pos_raquete_oponente.x <= self.screen.get_width() * (3/5):
            self.pos_raquete_oponente.x = self.screen.get_width() * (3/5) 

        if self.cooldown_raq_oponente.x > 0:
            pg.draw.rect(self.screen, "grey", pg.Rect(self.pos_raquete_oponente.x, self.pos_raquete_oponente.y, self.tamanho_raquetes.x, self.tamanho_raquetes.y))
        else:
            pg.draw.rect(self.screen, "white", pg.Rect(self.pos_raquete_oponente.x, self.pos_raquete_oponente.y, self.tamanho_raquetes.x, self.tamanho_raquetes.y))

    def run(self):
        while self.running:
            self.dt = self.clock.tick(1000) / 1000
            
            # Eventos
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.mouse_captured = not self.mouse_captured
                        pg.event.set_grab(self.mouse_captured)

            # Atualização
            self.desenhar_jogo()
            self.atualizar_raquete_jogador()
            self.atualizar_raquete_oponente()
            self.atualizar_bola()
            self.atualizar_placar()
            print(self.cooldown_raq_jogador)
            
            # Renderização
            pg.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()
    pg.quit()