import pygame
from random import randint, choice
from time import time
from pygame.locals import *

pygame.init()

# Cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
AZUL = (0, 100, 255)
ROXO = (128, 0, 128)

# Tela
largura_tela, altura_tela = 600, 800
tela = pygame.display.set_mode((largura_tela, altura_tela))
pygame.display.set_caption("Pega-Comida")

# Fonte
fonte = pygame.font.SysFont(None, 40)

# Variável de controle para o ESC
esc_pressionado_anterior = False

class Jogador:
    def __init__(self):
        self.largura = 40
        self.altura = 80
        self.x = largura_tela / 2 - self.largura / 2
        self.y = altura_tela - 100
        self.velocidade = 9

    def mover(self, dx):
        self.x += dx
        self.x = max(0, min(self.x, largura_tela - self.largura))

    def get_hitboxes(self):
        cima = pygame.Rect(self.x, self.y, self.largura, self.altura / 2)
        baixo = pygame.Rect(self.x, self.y + self.altura / 2, self.largura, self.altura / 2)
        return cima, baixo

    def desenhar(self, tela):
        pygame.draw.rect(tela, AZUL, (self.x, self.y, self.largura, self.altura))

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
        self.vel_comida = 4
        self.spawn_intervalo = 1.0
        self.ultimo_spawn = 0
        self.tempo_inicio = time()
        self.imagem_fundo = pygame.image.load(r"sprites\fundo.jpg")
        self.imagem_fundo = pygame.transform.scale(self.imagem_fundo, (largura_tela, altura_tela))
        posiveis_comidas = [
            r"sprites\Avocado.png",
            r"sprites\Bacon.png",
            r"sprites\Bread.png",
            r"sprites\Brownie.png",
            r"sprites\Cheese.png",
            r"sprites\Cookie.png",
            r"sprites\Beer.png"
        ]
        imagens_comida = []
        for string in posiveis_comidas:
            sprite_comida = pygame.image.load(string)
            sprite_comida = pygame.transform.scale(sprite_comida, (60, 60))
            imagens_comida.append(sprite_comida)
        self.imagens_comida = imagens_comida
    
    def exibir_pausa(self):
        global esc_ja_pressionado
        # Desenhar o estado atual do jogo
        tela.blit(self.imagem_fundo, (0, 0))
        self.jogador.desenhar(tela)
        for comida in self.comidas:
            comida.desenhar(tela)

        # Criar overlay escuro
        overlay = pygame.Surface((largura_tela, altura_tela))
        tela.blit(fonte.render(f"Pontuação: {self.pontos}", True, BRANCO), (20, 20))
        tela.blit(fonte.render(f"Vidas: {self.vidas}", True, BRANCO), (470, 20))
        overlay.set_alpha(150)  # semitransparente
        overlay.fill(PRETO)
        tela.blit(overlay, (0, 0))

        # Texto "Continuar"
        texto = fonte.render("Continuar", True, BRANCO)
        texto_rect = texto.get_rect(center=(largura_tela // 2, altura_tela // 2))
        hitbox_continuar = pygame.Rect(
            texto_rect.left - 10, texto_rect.top - 10,
            texto_rect.width + 20, texto_rect.height + 20
        )

        # Desenhar botão
        pygame.draw.rect(tela, (200, 200, 200), hitbox_continuar, 2)
        tela.blit(texto, texto_rect)
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
                if teclas[K_ESCAPE]:
                    if not esc_ja_pressionado:
                        esperando = False
                else:
                    esc_ja_pressionado = False

    def rodar(self):
        clock = pygame.time.Clock()
        rodando = True
        global esc_ja_pressionado
        esc_ja_pressionado = False
        
        while rodando:
            deley_spawn_antes_pause = None
            tela.blit(self.imagem_fundo, (0, 0))
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    rodando = False
                    pygame.quit()
                    exit()

            teclas = pygame.key.get_pressed()

            # Detecta o primeiro frame do ESC pressionado
            if teclas[K_ESCAPE]:
                if not esc_ja_pressionado:
                    deley_spawn_antes_pause = time() - self.ultimo_spawn
                    tempo_antes_pause = time()
                    esc_ja_pressionado = True
                    self.exibir_pausa()
                    esc_ja_pressionado = False
            else:
                esc_ja_pressionado = False

            dx = 0
            if teclas[K_a]:
                dx = -self.jogador.velocidade
            elif teclas[K_d]:
                dx = self.jogador.velocidade

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
                comida.mover(self.vel_comida)
                if hitbox_cima.colliderect(comida.rect):
                    self.pontos += 1
                elif comida.y < altura_tela:
                    novas_comidas.append(comida)
                else:
                    self.vidas -= 1
                    if self.vidas == 0:
                        return  # fim de jogo

            self.comidas = novas_comidas

            if deley_spawn_antes_pause:
                self.ultimo_spawn = time() - deley_spawn_antes_pause
                self.tempo_inicio += time() - tempo_antes_pause
            elif time() - self.ultimo_spawn > self.spawn_intervalo:
                self.comidas.append(Comida(choice(self.imagens_comida)))
                self.ultimo_spawn = time()
            
            if time() - self.tempo_inicio > 10:
                self.spawn_intervalo = 0.7

            self.jogador.desenhar(tela)
            for comida in self.comidas:
                comida.desenhar(tela)

            tela.blit(fonte.render(f"Pontuação: {self.pontos}", True, BRANCO), (20, 20))
            tela.blit(fonte.render(f"Vidas: {self.vidas}", True, BRANCO), (470, 20))

            pygame.display.flip()
            clock.tick(60)

def exibir_menu():
    texto = fonte.render("Iniciar", True, BRANCO)
    texto_rect = texto.get_rect(center=(largura_tela // 2, altura_tela // 2))
    hitbox_iniciar = pygame.Rect(
        texto_rect.left - 10, texto_rect.top - 10,
        texto_rect.width + 20, texto_rect.height + 20
    )

    esperando = True
    while esperando:
        tela.fill(PRETO)
        pygame.draw.rect(tela, (200, 200, 200), hitbox_iniciar, 2)
        tela.blit(texto, texto_rect)
        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if hitbox_iniciar.collidepoint(evento.pos):
                    esperando = False

while True:
    exibir_menu()
    jogo = Jogo()
    jogo.rodar()