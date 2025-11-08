import pygame as pg
import random

class Game:
    def __init__(self):
        pg.init()
        # Tela
        self.screen = pg.display.set_mode((1920, 1080))  # Tamanho fixo

        # Mouse
        pg.display.set_caption("Pyng")  # Título da janela
        pg.mouse.set_visible(False)  # Torna o cursor invisível
        self.mouse_captured = True
        pg.event.set_grab(True)
        
        # Tempo
        self.clock = pg.time.Clock()
        self.running = True
        self.dt = 0
        
        # Inicialização das variáveis do jogo
        self.setup_game()
        
    def setup_game(self):
        # Cooldowns
        self.collision_par_cooldown = 0.1
        self.collision_raq_cooldown = 0.3
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
        
        self.dir_da_bola = self.dir_da_bola.normalize()
        self.velocidade_base_bola = 450.0
        self.velocidade_bola = self.velocidade_base_bola
        # *** NOVO: Fator de arrasto (air drag) ***
        self.drag_factor = 0.1 
        
        ## Raquetes
        self.tamanho_raquetes = pg.Vector2(20, 80)
        
        
        # Raquete Jogador
        self.pos_raquete_jogador = pg.Vector2(self.screen.get_width() / 100, self.screen.get_height() / 2 - self.tamanho_raquetes.y / 2)
        self.vezes_colidiu = 0
        self.pos_anterior_raquete = self.pos_raquete_jogador.copy()
        self.movimento_raquete = pg.Vector2(0, 0) # Inicializa o movimento

        # Quantidade máxima de vezes que a raquete pode colidir antes de ficar "transparente" e traspassável
        self.max_vezes_pode_colidir = 0

        # Raquete Oponente
        self.pos_raquete_oponente = pg.Vector2(self.screen.get_width() - self.tamanho_raquetes.x - self.screen.get_width() / 100, self.screen.get_height() / 2 - self.tamanho_raquetes.y / 2)
        # *** NOVO: Rastreamento de movimento para o oponente ***
        self.pos_anterior_raquete_oponente = self.pos_raquete_oponente.copy()
        self.movimento_raquete_oponente = pg.Vector2(0, 0)


    def desenhar_jogo(self):
        # Desenha a linha central
        self.screen.fill("black")
        pg.draw.line(self.screen, "grey", (self.screen.get_width() / 2, 0), (self.screen.get_width() / 2, self.screen.get_height()), 1)

    def checar_colisao_raquete_jogador(self, x_ou_y):
        # Calcula o movimento da raquete entre frames
        movimento_raquete = self.movimento_raquete # Usa o movimento já calculado
        
        # Calcula o movimento da bola entre frames
        movimento_bola = self.dir_da_bola * self.velocidade_bola * self.dt
        
        # Posições anteriores
        bola_anterior = self.pos_da_bola - movimento_bola
        
        # Verifica colisão em múltiplos pontos ao longo da trajetória
        steps = 15
        for i in range(steps):
            t = i / steps
            pos_bola_inter = bola_anterior + movimento_bola * t
            pos_raquete_inter = self.pos_anterior_raquete + movimento_raquete * t
            
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
        # *** MODIFICADO: Usa a mesma lógica de interpolação do jogador ***
        
        # Calcula o movimento da raquete entre frames
        movimento_raquete = self.movimento_raquete_oponente
        
        # Calcula o movimento da bola entre frames
        movimento_bola = self.dir_da_bola * self.velocidade_bola * self.dt
        
        # Posições anteriores
        bola_anterior = self.pos_da_bola - movimento_bola
        
        # Verifica colisão em múltiplos pontos ao longo da trajetória
        steps = 15
        for i in range(steps):
            t = i / steps
            pos_bola_inter = bola_anterior + movimento_bola * t
            pos_raquete_inter = self.pos_anterior_raquete_oponente + movimento_raquete * t
            
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


    def atualizar_bola(self):
        # Aplica o tempo de espera inicial
        if self.espera > 0:
            self.espera -= self.dt
        elif self.espera <= 0:
            self.espera = 0
            
        # (Cooldowns)
        if self.cooldown_par.x > 0: self.cooldown_par.x -= self.dt
        if self.cooldown_par.y > 0: self.cooldown_par.y -= self.dt
        if self.cooldown_raq_jogador.x > 0: self.cooldown_raq_jogador.x -= self.dt
        if self.cooldown_raq_jogador.y > 0: self.cooldown_raq_jogador.y -= self.dt
        if self.cooldown_raq_oponente.x > 0: self.cooldown_raq_oponente.x -= self.dt
        if self.cooldown_raq_oponente.y > 0: self.cooldown_raq_oponente.y -= self.dt
        
        # Reseta contador do jogador
        if self.pos_da_bola.x - self.raio_da_bola >= self.screen.get_width() / 2:
            self.vezes_colidiu = 0 


        if self.espera == 0:
            # *** NOVO: Aplica Air Drag (Arrasto) ***
            if self.velocidade_bola > self.velocidade_base_bola:
                self.velocidade_bola -= self.drag_factor * self.velocidade_bola * self.dt
                # Garante que não caia abaixo da base
                if self.velocidade_bola < self.velocidade_base_bola:
                    self.velocidade_bola = self.velocidade_base_bola

            # Zona segura para checar o jogador (metade esquerda + buffer)
            zona_jogador = self.screen.get_width() * (3/5) 
            # Zona segura para checar o oponente (metade direita + buffer)
            zona_oponente = self.screen.get_width() * (2/5)
            # Movimento da bola
            self.pos_da_bola += self.dir_da_bola * self.velocidade_bola * self.dt

            # Colisão com paredes (X)
            if (self.pos_da_bola.x + self.raio_da_bola > self.screen.get_width() or self.pos_da_bola.x - self.raio_da_bola < 0) and self.cooldown_par.x <= 0:
                if self.pos_da_bola.x + self.raio_da_bola > self.screen.get_width(): self.pos_da_bola.x = self.screen.get_width() - self.raio_da_bola
                elif self.pos_da_bola.x - self.raio_da_bola < 0: self.pos_da_bola.x = self.raio_da_bola
                self.dir_da_bola.x *= -1
                self.cooldown_par.x = self.collision_par_cooldown

            # Colisão com paredes (Y)
            if (self.pos_da_bola.y + self.raio_da_bola > self.screen.get_height() or self.pos_da_bola.y - self.raio_da_bola < 0) and self.cooldown_par.y <= 0:
                if self.pos_da_bola.y + self.raio_da_bola > self.screen.get_height(): self.pos_da_bola.y = self.screen.get_height() - self.raio_da_bola
                elif self.pos_da_bola.y - self.raio_da_bola < 0: self.pos_da_bola.y = self.raio_da_bola
                self.dir_da_bola.y *= -1
                self.cooldown_par.y = self.collision_par_cooldown

            if self.pos_da_bola.x < zona_jogador:
                if self.checar_colisao_raquete_jogador("x") and self.vezes_colidiu <= self.max_vezes_pode_colidir and self.cooldown_raq_jogador.x <= 0:  
                    paddle_vel = pg.Vector2(0, 0)
                    if self.dt > 0: paddle_vel = self.movimento_raquete / self.dt
                    
                    self.dir_da_bola.x *= -1
                    
                    y_influence = 0.0005 
                    self.dir_da_bola.y += paddle_vel.y * y_influence
                    
                    x_influence = 0.1 
                    if paddle_vel.x > 0: # Move contra a bola
                        self.velocidade_bola += paddle_vel.x * x_influence
                    
                    self.dir_da_bola = self.dir_da_bola.normalize()
                    
                    max_speed = 1500.0
                    if self.velocidade_bola > max_speed: self.velocidade_bola = max_speed
                    if self.velocidade_bola < self.velocidade_base_bola: self.velocidade_bola = self.velocidade_base_bola
                    
                    self.vezes_colidiu += 1
                    self.cooldown_raq_jogador.x = self.collision_raq_cooldown
                
                elif self.checar_colisao_raquete_jogador("y") and self.vezes_colidiu <= self.max_vezes_pode_colidir and self.cooldown_raq_jogador.y <= 0:
                    paddle_vel = pg.Vector2(0, 0)
                    if self.dt > 0: paddle_vel = self.movimento_raquete / self.dt

                    self.dir_da_bola.y *= -1
                    
                    x_influence = 0.0005 
                    self.dir_da_bola.x += paddle_vel.x * x_influence
                    
                    y_influence = 0.1
                    if (self.dir_da_bola.y > 0 and paddle_vel.y < 0) or \
                       (self.dir_da_bola.y < 0 and paddle_vel.y > 0):
                       self.velocidade_bola += abs(paddle_vel.y) * y_influence

                    self.dir_da_bola = self.dir_da_bola.normalize()
                    
                    max_speed = 1500.0
                    if self.velocidade_bola > max_speed: self.velocidade_bola = max_speed
                    if self.velocidade_bola < self.velocidade_base_bola: self.velocidade_bola = self.velocidade_base_bola
                         
                    self.cooldown_raq_jogador.y = self.collision_raq_cooldown

            # --- Física de colisão do oponente ---
            # Só executa a checagem cara se a bola estiver na zona do oponente
            if self.pos_da_bola.x > zona_oponente:
                if self.checar_colisao_raquete_oponente("x") and self.cooldown_raq_oponente.x <= 0:
                    paddle_vel = pg.Vector2(0, 0)
                    if self.dt > 0: paddle_vel = self.movimento_raquete_oponente / self.dt

                    self.dir_da_bola.x *= -1
                    
                    y_influence = 0.0005
                    self.dir_da_bola.y += paddle_vel.y * y_influence

                    x_influence = 0.1
                    if paddle_vel.x < 0: # Move contra a bola (para a esquerda)
                        self.velocidade_bola += abs(paddle_vel.x) * x_influence

                    self.dir_da_bola = self.dir_da_bola.normalize()

                    max_speed = 1500.0
                    if self.velocidade_bola > max_speed: self.velocidade_bola = max_speed
                    if self.velocidade_bola < self.velocidade_base_bola: self.velocidade_bola = self.velocidade_base_bola

                    self.cooldown_raq_oponente.x = self.collision_raq_cooldown

                elif self.checar_colisao_raquete_oponente("y") and self.cooldown_raq_oponente.y <= 0:
                    paddle_vel = pg.Vector2(0, 0)
                    if self.dt > 0: paddle_vel = self.movimento_raquete_oponente / self.dt

                    self.dir_da_bola.y *= -1

                    x_influence = 0.0005
                    self.dir_da_bola.x += paddle_vel.x * x_influence

                    y_influence = 0.1
                    if (self.dir_da_bola.y > 0 and paddle_vel.y < 0) or \
                       (self.dir_da_bola.y < 0 and paddle_vel.y > 0):
                       self.velocidade_bola += abs(paddle_vel.y) * y_influence

                    self.dir_da_bola = self.dir_da_bola.normalize()
                    
                    max_speed = 1500.0
                    if self.velocidade_bola > max_speed: self.velocidade_bola = max_speed
                    if self.velocidade_bola < self.velocidade_base_bola: self.velocidade_bola = self.velocidade_base_bola

                    self.cooldown_raq_oponente.y = self.collision_raq_cooldown

        pg.draw.circle(self.screen, "white", self.pos_da_bola, self.raio_da_bola)

    def atualizar_raquete_jogador(self):
        # Armazena a posição anterior da raquete
        self.pos_anterior_raquete = self.pos_raquete_jogador.copy()

        # Posição da raquete segue o mouse instantaneamente
        mouse_x, mouse_y = pg.mouse.get_pos()
        self.pos_raquete_jogador = pg.Vector2(mouse_x - self.tamanho_raquetes.x / 2,
                                              mouse_y - self.tamanho_raquetes.y / 2)
        
        # Limites da tela
        if self.pos_raquete_jogador.y <= 0: self.pos_raquete_jogador.y = 0
        if self.pos_raquete_jogador.y + self.tamanho_raquetes.y >= self.screen.get_height(): self.pos_raquete_jogador.y = self.screen.get_height() - self.tamanho_raquetes.y
        if self.pos_raquete_jogador.x <= 0: self.pos_raquete_jogador.x = 0
        if self.pos_raquete_jogador.x + self.tamanho_raquetes.x >= self.screen.get_width() * (2/5): self.pos_raquete_jogador.x = self.screen.get_width() * (2/5) - self.tamanho_raquetes.x
        
        # Calcula o movimento real (deslocamento)
        self.movimento_raquete = self.pos_raquete_jogador - self.pos_anterior_raquete
        
        # Desenha a raquete
        if self.vezes_colidiu >= self.max_vezes_pode_colidir + 1:
            pg.draw.rect(self.screen, "grey", pg.Rect(self.pos_raquete_jogador.x, self.pos_raquete_jogador.y, self.tamanho_raquetes.x, self.tamanho_raquetes.y))
        else:
            pg.draw.rect(self.screen, "white", pg.Rect(self.pos_raquete_jogador.x, self.pos_raquete_jogador.y, self.tamanho_raquetes.x, self.tamanho_raquetes.y))
            
    def atualizar_raquete_oponente(self):
        # *** NOVO: Armazena posição anterior do oponente ***
        self.pos_anterior_raquete_oponente = self.pos_raquete_oponente.copy()
        
        velocidade = 600
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
            self.pos_raquete_oponente += direcao * velocidade * self.dt
        
        
        ## Limites da tela
        if self.pos_raquete_oponente.y + self.tamanho_raquetes.y >= self.screen.get_height(): self.pos_raquete_oponente.y = self.screen.get_height() - self.tamanho_raquetes.y
        if self.pos_raquete_oponente.y <= 0: self.pos_raquete_oponente.y = 0
        if self.pos_raquete_oponente.x + self.tamanho_raquetes.x >= self.screen.get_width(): self.pos_raquete_oponente.x = self.screen.get_width() - self.tamanho_raquetes.x
        if self.pos_raquete_oponente.x <= self.screen.get_width() * (3/5): self.pos_raquete_oponente.x = self.screen.get_width() * (3/5) 

        # *** NOVO: Calcula o movimento do oponente ***
        self.movimento_raquete_oponente = self.pos_raquete_oponente - self.pos_anterior_raquete_oponente

        pg.draw.rect(self.screen, "white", pg.Rect(self.pos_raquete_oponente.x, self.pos_raquete_oponente.y, self.tamanho_raquetes.x, self.tamanho_raquetes.y))
        pass

    def run(self):
        while self.running:
            self.dt = self.clock.tick(60) / 1000
            
            # Eventos
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.mouse_captured = not self.mouse_captured
                        pg.event.set_grab(self.mouse_captured)
                        pg.mouse.set_visible(not self.mouse_captured)


            # Atualização
            self.desenhar_jogo()
            self.atualizar_raquete_jogador()
            self.atualizar_raquete_oponente()
            self.atualizar_bola()
            
            # Renderização
            pg.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()
    pg.quit()