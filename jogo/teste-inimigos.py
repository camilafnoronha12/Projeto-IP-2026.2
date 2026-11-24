import pygame
import os
import random
pygame.init()
LARGURA, ALTURA = 1366, 720
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Agente CIncreto")
relogio = pygame.time.Clock()
fonte = pygame.font.SysFont(None, 36)
CAMINHO = os.path.dirname(os.path.abspath(__file__))
PASTA_ASSETS = os.path.join(CAMINHO, "assets")
SPAWN = (653, 640)  # embaixo, no meio (como o início do Crossy Road)


def carregar(nome, tamanho, cor):
    """Carrega assets/nome; se o arquivo não existir, usa um retângulo colorido."""
    caminho = os.path.join(PASTA_ASSETS, nome)
    if os.path.exists(caminho):
        return pygame.transform.scale(
            pygame.image.load(caminho).convert_alpha(), tamanho)
    img = pygame.Surface(tamanho)
    img.fill(cor)
    return img


# ------------------------------------------------------------------ INIMIGOS
class Inimigo:
    def __init__(self, y, direcao, velocidade, imagem):
        # vira a imagem para o lado em que ele anda
        self.imagem = imagem if direcao > 0 else pygame.transform.flip(
            imagem, True, False)
        self.rect = self.imagem.get_rect(centery=y)
        # nasce logo FORA da tela, do lado oposto ao destino
        self.rect.x = -self.rect.w if direcao > 0 else LARGURA
        self.direcao = direcao
        self.velocidade = velocidade

    def mover(self):
        self.rect.x += self.direcao * self.velocidade

    def saiu(self):
        return self.rect.right < 0 or self.rect.left > LARGURA

    def desenhar(self, superficie):
        superficie.blit(self.imagem, self.rect)


class Faixa:
    """Uma 'pista': gera inimigos num y fixo, sempre na mesma direção."""

    def __init__(self, y, direcao, velocidade, intervalo, imagem):
        self.y, self.direcao, self.velocidade = y, direcao, velocidade
        self.intervalo = intervalo      # tempo médio entre inimigos (ms)
        self.imagem = imagem
        self.proximo = 0                # quando nasce o próximo

    def gerar(self, agora, inimigos):
        if agora >= self.proximo:
            inimigos.append(Inimigo(self.y, self.direcao,
                            self.velocidade, self.imagem))
            # sorteia o próximo para não ficar uma fila perfeitamente regular
            self.proximo = agora + random.randint(
                int(self.intervalo * 0.7), int(self.intervalo * 1.5))


IMG_INIMIGO = carregar("inimigo.png", (90, 50), (200, 40, 40))
FAIXAS = [  # y, direcao (1 = direita, -1 = esquerda), velocidade, intervalo
    Faixa(100, 1, 4, 1600, IMG_INIMIGO),
    Faixa(200, -1, 6, 1200, IMG_INIMIGO),
    Faixa(300, 1, 5, 1400, IMG_INIMIGO),
    Faixa(400, -1, 3, 2000, IMG_INIMIGO),
    Faixa(500, 1, 7, 1000, IMG_INIMIGO),
]


# ------------------------------------------------------------------ JOGADOR
class Jogador:
    def __init__(self, x, y):
        self.imagem = carregar("perna_cabeluda.png", (60, 60), (60, 120, 255))
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
        # sem diagonal: se moveu nos dois eixos, desfaz o novo
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

    def desenhar(self, superficie):
        superficie.blit(self.imagem, self.rect)


# ------------------------------------------------------------------ JOGO
jogador = Jogador(*SPAWN)
inimigos = []
vidas = 3
rodando = True
while rodando:
    # Eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
    # Lógica
    teclas = pygame.key.get_pressed()
    jogador.mover(teclas)

    agora = pygame.time.get_ticks()
    for f in FAIXAS:
        f.gerar(agora, inimigos)                           # nascem
    for i in inimigos:
        i.mover()                                          # andam
    # somem ao sair da tela
    inimigos = [i for i in inimigos if not i.saiu()]

    for i in inimigos:                                     # atingiram o jogador?
        # hitboxes levemente menores que as imagens: colisão mais justa
        if jogador.rect.inflate(-20, -20).colliderect(i.rect.inflate(-10, -10)):
            vidas -= 1
            jogador.rect.topleft = SPAWN
            if vidas == 0:
                vidas = 3                                  # game over: recomeça
            break
    # Desenho
    tela.fill((0, 0, 0))  # fundo preto
    for i in inimigos:
        i.desenhar(tela)
    jogador.desenhar(tela)
    tela.blit(fonte.render(f"Vidas: {vidas}",
              True, (255, 255, 255), (0, 0, 0)), (10, 10))
    pygame.display.flip()
    relogio.tick(60)
pygame.quit()
