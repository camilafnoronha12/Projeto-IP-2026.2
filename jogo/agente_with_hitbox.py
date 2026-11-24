import pygame
import os
pygame.init()
tela = pygame.display.set_mode((1366, 720))
pygame.display.set_caption("Agente CIncreto")
relogio = pygame.time.Clock()
CAMINHO = os.path.dirname(os.path.abspath(__file__))
PASTA_ASSETS = os.path.join(CAMINHO, "assets")


# cenário de fundo
cenario = pygame.image.load(os.path.join(
    PASTA_ASSETS, "capa_agente_cincretov1.png")).convert()
cenario = pygame.transform.scale(cenario, tela.get_size())

# Cada obstáculo - pygame.Rect(x, y, largura, altura), em pixels da imagem.
HITBOXES = [
    pygame.Rect(605, 223, 299, 483),
]


class Jogador:
    def __init__(self, x, y):
        self.imagem = pygame.image.load(os.path.join(
            PASTA_ASSETS, "perna_cabeluda.png")).convert_alpha()
        self.imagem = pygame.transform.scale(self.imagem, (60, 60))
        self.rect = self.imagem.get_rect(topleft=(x, y))
        self.velocidade = 5
        self.eixo = "x"  # último eixo em que ele andou

    def mover(self, teclas):
        x0, y0 = self.rect.topleft  # posição antes de mover
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            self.rect.x -= self.velocidade
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            self.rect.x += self.velocidade
        if teclas[pygame.K_UP] or teclas[pygame.K_w]:
            self.rect.y -= self.velocidade
        if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
            self.rect.y += self.velocidade
        # Mantém dentro da tela
        self.rect.clamp_ip(tela.get_rect())
        # sem diagonal
        dx, dy = self.rect.x - x0, self.rect.y - y0
        if dx and dy:
            if self.eixo == "x":
                self.rect.y = y0
            else:
                self.rect.x = x0
        elif dx:
            self.eixo = "x"
        elif dy:
            self.eixo = "y"
        if self.rect.collidelist(HITBOXES) != -1:
            self.rect.topleft = (x0, y0)

    def desenhar(self, superficie):
        superficie.blit(self.imagem, self.rect)


jogador = Jogador(370, 270)
rodando = True
while rodando:
    # Eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
    # Lógica
    teclas = pygame.key.get_pressed()
    jogador.mover(teclas)
    # Desenho
    tela.fill((30, 30, 40))
    # cenário por cima do fill, antes do resto
    tela.blit(cenario, (0, 0))
    jogador.desenhar(tela)
    pygame.display.flip()
    relogio.tick(60)
pygame.quit()
