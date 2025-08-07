import pygame
from random import randint, choice
from time import time
from pygame.locals import *
from constantes import *

pygame.init()
dificuldade = ""
# Cores
CINZA = (200, 200, 200)
BRANCO = (255, 255, 255)
VERMELHO = (255, 0, 0)
PRETO = (0, 0, 0)
AZUL = (0, 100, 255)
ROXO = (128, 0, 128)

# Tela
largura_tela, altura_tela = 600, 800
tela = pygame.display.set_mode((largura_tela, altura_tela))
pygame.display.set_caption("Pega-Comida")

# Fonte
fonte = pygame.font.SysFont(None, 40)
fonte2 = pygame.font.SysFont(None, 20)

# Variável de controle para o ESC
esc_pressionado_anterior = False

class Jogador:
    def __init__(self):
        self.largura = 40
        self.altura = 80
        self.x = largura_tela / 2 - self.largura / 2
        self.y = altura_tela - 100
        self.velocidade_inicial_jogador = 9

    def mover(self, dx):
        self.x += dx
        # Sem limites: permite sair parcialmente da tela

        # Wrap total (opcional): se quiser que ele nunca "escape" demais da tela
        if self.x < -self.largura:
            self.x = largura_tela
        elif self.x > largura_tela:
            self.x = 0

    def get_hitboxes(self):
        cima = pygame.Rect(self.x + 10, self.y, self.largura, self.altura / 2 + 10)
        baixo = pygame.Rect(self.x + 10, self.y + self.altura / 2 + 10, self.largura, self.altura / 2 - 10)
        return cima, baixo

    def desenhar(self, tela, string):
        sprite_jogador = pygame.image.load(string)
        sprite_jogador = pygame.transform.scale(sprite_jogador, (self.largura*1.5, self.altura*1.5))

        # Posição normal
        tela.blit(sprite_jogador, (self.x, self.y - 20))

        # Wrap visual: desenha do lado oposto quando estiver saindo da tela
        if self.x < -self.largura:
            tela.blit(sprite_jogador, (-self.x + largura_tela, self.y))
        elif self.x > largura_tela:
            tela.blit(sprite_jogador, (self.x - largura_tela, self.y))

class Comida:
    def __init__(self, imagem):
        self.x = randint(0, largura_tela - 60)
        self.y = 0
        self.imagem = imagem
        self.rect = pygame.Rect(self.x, self.y, 60, 60)

    def mover(self, vel):
        self.y += vel
        self.rect.top = self.y

    def desenhar(self, tela):
        tela.blit(self.imagem, (self.x, self.y))

class Jogo:
    def __init__(self):
        self.jogador = Jogador()
        self.comidas = []
        self.pontos = 0
        self.vidas = 5
        self.vel_comida_inicial = 4
        self.spawn_intervalo = 1.0
        self.ultimo_spawn = 0
        self.tempo_inicio = time()
        self.imagem_fundo = pygame.image.load(r"sprites\fundo_deck_praia.png")
        self.imagem_fundo = pygame.transform.scale(self.imagem_fundo, (largura_tela, altura_tela))
        self.posiveis_comidas = [
            r"sprites\Avocado.png",
            r"sprites\Bacon.png",
            r"sprites\Bread.png",
            r"sprites\Brownie.png",
            r"sprites\Cheese.png",
            r"sprites\Cookie.png",
            r"sprites\Beer.png"
        ]

        self.posicoes_personagem = [
            r"sprites\correndo_esquerda.png",
            r"sprites\parado.png",
            r"sprites\correndo_direita.png"
        ]

        imagens_comida = []
        for string in self.posiveis_comidas:
            sprite_comida = pygame.image.load(string)
            sprite_comida = pygame.transform.scale(sprite_comida, (60, 60))
            imagens_comida.append(sprite_comida)
        self.imagens_comida = imagens_comida

        self.qtd_comidas = {}
        for n in range(len(self.imagens_comida)):
            self.qtd_comidas[f"qtd_comida{n + 1}"] = 0
    
    def exibir_game_over(self, string_jogador):
        global esc_ja_pressionado
        global voltou_no_menu
        # Desenhar o estado atual do jogo
        tela.blit(self.imagem_fundo, (0, 0))
        self.jogador.desenhar(tela, string_jogador)
        for comida in self.comidas:
            comida.desenhar(tela)

        # Criar overlay escuro
        overlay = pygame.Surface((largura_tela, altura_tela))
        tela.blit(fonte.render(f"Pontuação: {self.pontos}", True, BRANCO), (20, 20))
        tela.blit(fonte.render(f"Vidas: {self.vidas}", True, BRANCO), (470, 20))
        overlay.set_alpha(150)  # semitransparente
        overlay.fill(PRETO)
        tela.blit(overlay, (0, 0))

        # Texto "Sair"
        texto1 = fonte.render("Sair", True, VERMELHO)
        texto_rect1 = texto1.get_rect(center=(largura_tela // 2, altura_tela // 2 + 25))
        hitbox_Sair = pygame.Rect(
            texto_rect1.left - 10, texto_rect1.top - 10,
            texto_rect1.width + 20, texto_rect1.height + 20
        )

        texto2 = fonte.render("Recomeçar", True, BRANCO)
        texto_rect2 = texto2.get_rect(center=(largura_tela // 2, altura_tela // 2 - 25))
        hitbox_continuar = pygame.Rect(
            texto_rect2.left - 10, texto_rect2.top - 10,
            texto_rect2.width + 20, texto_rect2.height + 20
        )

        # Desenhar botão
        pygame.draw.rect(tela, CINZA, hitbox_continuar, 2)
        pygame.draw.rect(tela, CINZA, hitbox_Sair, 2)
        tela.blit(texto1, texto_rect1)
        tela.blit(texto2, texto_rect2)
        pygame.display.flip()

        # Esperar clique para continuar
        esperando = True
        while esperando:
            teclas = pygame.key.get_pressed()
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    if evento.button == 1 and hitbox_continuar.collidepoint(evento.pos):
                        esperando = False
                    if evento.button == 1 and hitbox_Sair.collidepoint(evento.pos):
                        esperando = False
                        voltou_no_menu = True
                if teclas[K_ESCAPE]:
                    if not esc_ja_pressionado:
                        esperando = False
                else:
                    esc_ja_pressionado = False
    
    def exibir_pausa(self, string_jogador):
        global voltou_no_menu
        global esc_ja_pressionado
        # Desenhar o estado atual do jogo
        tela.blit(self.imagem_fundo, (0, 0))
        self.jogador.desenhar(tela, string_jogador)
        for comida in self.comidas:
            comida.desenhar(tela)

        # Criar overlay escuro
        overlay = pygame.Surface((largura_tela, altura_tela))
        tela.blit(fonte.render(f"Pontuação: {self.pontos}", True, BRANCO), (20, 20))
        tela.blit(fonte.render(f"Vidas: {self.vidas}", True, BRANCO), (470, 20))
        overlay.set_alpha(150)  # semitransparente
        overlay.fill(PRETO)
        tela.blit(overlay, (0, 0))

        # Texto "Sair"
        texto1 = fonte.render("Sair", True, VERMELHO)
        texto_rect1 = texto1.get_rect(center=(largura_tela // 2, altura_tela // 2 + 25))
        hitbox_Sair = pygame.Rect(
            texto_rect1.left - 10, texto_rect1.top - 10,
            texto_rect1.width + 20, texto_rect1.height + 20
        )

        texto2 = fonte.render("Continuar", True, BRANCO)
        texto_rect2 = texto2.get_rect(center=(largura_tela // 2, altura_tela // 2 - 25))
        hitbox_continuar = pygame.Rect(
            texto_rect2.left - 10, texto_rect2.top - 10,
            texto_rect2.width + 20, texto_rect2.height + 20
        )

        # Desenhar botão
        pygame.draw.rect(tela, CINZA, hitbox_continuar, 2)
        pygame.draw.rect(tela, CINZA, hitbox_Sair, 2)
        tela.blit(texto1, texto_rect1)
        tela.blit(texto2, texto_rect2)
        pygame.display.flip()

        # Esperar clique para continuar
        esperando = True
        while esperando:
            teclas = pygame.key.get_pressed()
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                
                if teclas[K_ESCAPE]:
                    if not esc_ja_pressionado:
                        esperando = False
                else:
                    esc_ja_pressionado = False
                    
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    if evento.button == 1 and hitbox_continuar.collidepoint(evento.pos):
                        esperando = False
                    elif evento.button == 1 and hitbox_Sair.collidepoint(evento.pos):
                        esperando = False
                        voltou_no_menu = True
                
    def rodar(self):
        velocidade_jogador = self.jogador.velocidade_inicial_jogador
        clock = pygame.time.Clock()
        rodando = True
        morreu = False
        global esc_ja_pressionado
        global dificuldade
        esc_ja_pressionado = False
        vel_comida = self.vel_comida_inicial

        if dificuldade == "facil":
            multiplicador_spawn = 0.95
            multiplicador_velocidade_objetos = 1.04
            multiplicador_velocidade_jogador = 1
            chance_bomba = 8 # porcentagem
        elif dificuldade == "medio":
            multiplicador_spawn = 0.93
            multiplicador_velocidade_objetos = 1.07
            multiplicador_velocidade_jogador = 1.01
            chance_bomba = 13 # porcentagem
        elif dificuldade == "dificil":
            multiplicador_spawn = 0.9
            multiplicador_velocidade_objetos = 1.09
            multiplicador_velocidade_jogador = 1.02
            chance_bomba = 18 # porcentagem

        while rodando:
            deley_spawn_antes_pause = None
            tela.blit(self.imagem_fundo, (0, 0))
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    rodando = False
                    pygame.quit()
                    exit()

            teclas = pygame.key.get_pressed()

            dx = 0
            if teclas[K_a]:
                dx = -velocidade_jogador
            elif teclas[K_d]:
                dx = velocidade_jogador
            
            if dx < 0:
                n = 0
            elif dx == 0:
                n = 1
            else:
                n = 2
            string_jogador = self.posicoes_personagem[n]

            # Detecta o primeiro frame do ESC pressionado
            if teclas[K_ESCAPE] and not esc_ja_pressionado:
                deley_spawn_antes_pause = time() - self.ultimo_spawn
                tempo_antes_pause = time()
                esc_ja_pressionado = True
                self.exibir_pausa(string_jogador)
                if voltou_no_menu:
                    rodando = False
                esc_ja_pressionado = False
            else:
                esc_ja_pressionado = False

            hitbox_cima, hitbox_baixo = self.jogador.get_hitboxes()

            comida_empurrada = None
            for comida in self.comidas:
                nova_comida = comida.rect.move(-dx, 0)
                if hitbox_baixo.colliderect(nova_comida):
                    comida_empurrada = comida
                    break

            if comida_empurrada:
                comida_empurrada.rect.move_ip(dx, 0)
                comida_empurrada.x = comida_empurrada.rect.left
                self.jogador.mover(dx)
            else:
                self.jogador.mover(dx)

            novas_comidas = []
            for comida in self.comidas:
                comida.mover(vel_comida)
                if hitbox_cima.colliderect(comida.rect):
                    self.pontos += 1
                    # for n in range(len(self.posiveis_comidas)):
                    #     if comida.imagem == self.posiveis_comidas[n]:
                    #         self.qtd_comidas[f"qtd_comida{n + 1}"] += 1
                    #         break
                    

                elif comida.y < altura_tela:
                    novas_comidas.append(comida)
                else:
                    self.vidas -= 1
                    if self.vidas == 0:
                        morreu = True

            self.comidas = novas_comidas

            if deley_spawn_antes_pause:
                self.ultimo_spawn = time() - deley_spawn_antes_pause
                self.tempo_inicio += time() - tempo_antes_pause
            if time() - self.ultimo_spawn > self.spawn_intervalo:
                randomico_0_100 = randint(1, 100)
                if randomico_0_100 < chance_bomba:
                    imagem_bomba = pygame.image.load(r"sprites\bomba.png")
                    imagem_bomba = pygame.transform.scale(imagem_bomba, (60, 60))
                    self.comidas.append(Comida(imagem_bomba))
                else:
                    self.comidas.append(Comida(choice(self.imagens_comida)))
                self.ultimo_spawn = time()
            
            blocos_tempo = (time() - self.tempo_inicio)//5 - 2
            if 0 < blocos_tempo <= 8:
                self.spawn_intervalo = int(1000 * multiplicador_spawn ** blocos_tempo) / 1000
                vel_comida = self.vel_comida_inicial * multiplicador_velocidade_objetos ** blocos_tempo
                velocidade_jogador = self.jogador.velocidade_inicial_jogador * multiplicador_velocidade_jogador ** blocos_tempo

            self.jogador.desenhar(tela, string_jogador)
            for comida in self.comidas:
                comida.desenhar(tela)

            tela.blit(fonte.render(f"Pontuação: {self.pontos}", True, BRANCO), (20, 20))
            tela.blit(fonte.render(f"Vidas: {self.vidas}", True, BRANCO), (470, 20))
            # for n in range(len(self.imagens_comida)):
            #     qtd_comida = self.qtd_comidas[f"qtd_comida{n + 1}"]
            #     tela.blit(fonte2.render(f"Vidas: {qtd_comida}", True, BRANCO), (470, 25*(n + 5)))

            pygame.display.flip()

            if morreu:
                pygame.time.delay(200)
                self.exibir_game_over(string_jogador)
                return # fim de jogo

            clock.tick(60)

def exibir_escolha_dificuldades():
    global dificuldade
    texto1 = fonte.render("Fácil", True, PRETO)
    texto2 = fonte.render("médio", True, PRETO)
    texto3 = fonte.render("difícil", True, PRETO)

    facil_rect = texto1.get_rect(center=(largura_tela // 2, altura_tela // 2 - 50))
    hitbox_facil = pygame.Rect(
        facil_rect.left - 10, facil_rect.top - 10,
        facil_rect.width + 20, facil_rect.height + 20
    )

    medio_rect = texto2.get_rect(center=(largura_tela // 2, altura_tela // 2))
    hitbox_medio = pygame.Rect(
        medio_rect.left - 10, medio_rect.top - 10,
        medio_rect.width + 20, medio_rect.height + 20
    )

    dificil_rect = texto3.get_rect(center=(largura_tela // 2, altura_tela // 2 + 50))
    hitbox_dificil = pygame.Rect(
        dificil_rect.left - 10, dificil_rect.top - 10,
        dificil_rect.width + 20, dificil_rect.height + 20
    )

    esperando = True
    while esperando:
        fundo_menu = pygame.image.load(r"sprites\menu_fundo_novo.png")
        fundo_menu = pygame.transform.scale(fundo_menu, (largura_tela, altura_tela))
        tela.blit(fundo_menu, (0, 0))
        pygame.draw.rect(tela, CINZA, hitbox_facil, 2)
        tela.blit(texto1, facil_rect)
        pygame.draw.rect(tela, CINZA, hitbox_medio, 2)
        tela.blit(texto2, medio_rect)
        pygame.draw.rect(tela, CINZA, hitbox_dificil, 2)
        tela.blit(texto3, dificil_rect)
        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if hitbox_facil.collidepoint(evento.pos):
                    esperando = False
                    dificuldade = "facil"
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if hitbox_medio.collidepoint(evento.pos):
                    esperando = False
                    dificuldade = "medio"
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if hitbox_dificil.collidepoint(evento.pos):
                    esperando = False
                    dificuldade = "dificil"

def exibir_menu():
    texto = fonte.render("Iniciar", True, PRETO)
    texto_rect = texto.get_rect(center=(largura_tela // 2, altura_tela // 2))
    hitbox_iniciar = pygame.Rect(
        texto_rect.left - 10, texto_rect.top - 10,
        texto_rect.width + 20, texto_rect.height + 20
    )

    esperando = True
    while esperando:
        fundo_menu = pygame.image.load(r"sprites\menu_fundo_novo.png")
        fundo_menu = pygame.transform.scale(fundo_menu, (largura_tela, altura_tela))
        tela.blit(fundo_menu, (0, 0))
        pygame.draw.rect(tela, CINZA, hitbox_iniciar, 2)
        tela.blit(texto, texto_rect)
        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if hitbox_iniciar.collidepoint(evento.pos):
                    esperando = False
voltou_no_menu = None
while True:
    if voltou_no_menu == None:
        voltou_no_menu = False
        exibir_menu()
        exibir_escolha_dificuldades()
    if voltou_no_menu:
        voltou_no_menu = not voltou_no_menu
        exibir_menu()
        exibir_escolha_dificuldades()
    jogo = Jogo()
    jogo.rodar()