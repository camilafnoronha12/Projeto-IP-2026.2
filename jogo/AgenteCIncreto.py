import pygame
import os
import random
pygame.init()
LARGURA, ALTURA = 1366, 720
ALTURA_MAPA = 2160  # Exemplo: 3x a altura da tela (ajuste conforme a imagem do cenário)
MAPA_RECT = pygame.Rect(0, 0, LARGURA, ALTURA_MAPA)

tela = pygame.display.set_mode((1366, 720))
pygame.display.set_caption("Agente CIncreto")
relogio = pygame.time.Clock()
CAMINHO = os.path.dirname(os.path.abspath(__file__))
PASTA_ASSETS = os.path.join(CAMINHO, "assets")

spawn = (653, ALTURA_MAPA - 80)  # Nasce na parte de baixo do mapa


reinicio = 1

# # cenário de fundo  - Reativar quando tiver cenario
# cenario = pygame.image.load(os.path.join(
#     PASTA_ASSETS, "capa_agente_cincretov1.png")).convert()
# cenario = pygame.transform.scale(cenario, tela.get_size())

# # Cada obstáculo - pygame.Rect(x, y, largura, altura), em pixels da imagem.  - Reativar quando houver cenario
# HITBOXES = [
#     # pygame.Rect(605, 223, 299, 483),
# ]


class Inimigo:
    def __init__(self, y, direcao, velocidade, imagem):
        # vira a imagem para o lado em que ele anda
        self.imagem = imagem if direcao > 0 else pygame.transform.flip(
            imagem, True, False)
        self.rect = self.imagem.get_rect(centery=y)
        # nasce num extremo da tela, para ir até o outro lado.
        self.rect.x = -self.rect.w if direcao > 0 else LARGURA
        self.direcao = direcao
        self.velocidade = velocidade

    def mover(self):
        self.rect.x += self.direcao * self.velocidade

    def saiu(self):
        return self.rect.right < 0 or self.rect.left > LARGURA

    def desenhar(self, superficie, camera_y):
        superficie.blit(self.imagem, self.rect.move(0, -camera_y))


class Faixa:
    def __init__(self, y, direcao, velocidade, intervalo, imagem):
        self.y, self.direcao, self.velocidade = y, direcao, velocidade
        self.intervalo = intervalo      # intervalo entre os inimigos surgindo
        self.imagem = imagem
        self.proximo = 0                # quando nasce o próximo

    def gerar(self, agora, inimigos):
        if agora >= self.proximo:
            inimigos.append(Inimigo(self.y, self.direcao,
                            self.velocidade, self.imagem))
            # randomiza para os inimigos surgirem de forma irregular
            self.proximo = agora + random.randint(
                int(self.intervalo * 0.7), int(self.intervalo * 1.5))


IMG_INIMIGO = pygame.image.load(os.path.join(
    PASTA_ASSETS, "bicicleta_1.png")).convert_alpha()
IMG_INIMIGO = pygame.transform.scale(IMG_INIMIGO, (90, 70))

FAIXAS = [  # y, direcao (1 = direita, -1 = esquerda), velocidade, intervalo, imagem
    # Parte de cima do mapa (perto da chegada)
    Faixa(150, 1, 7, 1000, IMG_INIMIGO),
    Faixa(300, -1, 6, 1200, IMG_INIMIGO),
    Faixa(450, 1, 5, 1400, IMG_INIMIGO),
    Faixa(600, -1, 6, 1100, IMG_INIMIGO),

    # Meio do mapa
    Faixa(800, 1, 4, 1600, IMG_INIMIGO),
    Faixa(950, -1, 5, 1300, IMG_INIMIGO),
    Faixa(1100, 1, 6, 1200, IMG_INIMIGO),
    Faixa(1250, -1, 3, 1800, IMG_INIMIGO),

    # Parte de baixo do mapa (perto do spawn em y = 2080)
    Faixa(1450, 1, 5, 1400, IMG_INIMIGO),
    Faixa(1600, -1, 4, 1500, IMG_INIMIGO),
    Faixa(1750, 1, 6, 1200, IMG_INIMIGO),
    Faixa(1900, -1, 3, 1700, IMG_INIMIGO),
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
        # Troquei o limite da tela pelo limite do mapa:
        self.rect.clamp_ip(MAPA_RECT)
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
        # if self.rect.collidelist(HITBOXES) != -1:  #Reativar quando tiver hitboxes definidas nos cenarios
        #     self.rect.topleft = (x0, y0)

    def desenhar(self, superficie, camera_y):
        superficie.blit(self.imagem, self.rect.move(0, -camera_y))


jogador = Jogador(*spawn)
inimigos = []

# Configuração da câmera estilo Crossy Road
VELOCIDADE_CAMERA = 0.5  # Ajuste aqui se quiser que a tela suba mais rápido ou devagar
camera_y = float(ALTURA_MAPA - ALTURA)  # Começa mostrando o fundo do
camera_ativa = False

rodando = True
while rodando:
    # Eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
    # Lógica
    teclas = pygame.key.get_pressed()
    pos_antes = jogador.rect.topleft
    jogador.mover(teclas)
    if jogador.rect.topleft != pos_antes:
        camera_ativa = True

    # Nascimento dos inimigos
    agora = pygame.time.get_ticks()
    for f in FAIXAS:
        f.gerar(agora, inimigos)
    for i in inimigos:
        i.mover()
    inimigos = [i for i in inimigos if not i.saiu()]

    # Câmera (só começa a subir após o primeiro passo do jogador)
    if camera_ativa:
        camera_y -= VELOCIDADE_CAMERA
        alvo_camera = jogador.rect.centery - ALTURA // 2
        if alvo_camera < camera_y:
            camera_y = alvo_camera
        camera_y = max(0, camera_y)

    # Câmera engoliu o jogador
    if jogador.rect.top > camera_y + ALTURA:
        reinicio -= 1
        jogador.rect.topleft = spawn
        camera_y = float(ALTURA_MAPA - ALTURA)
        camera_ativa = False

    # Colisão faz voltar do começo
    for i in inimigos:
        if jogador.rect.inflate(-20, -20).colliderect(i.rect.inflate(-10, -10)):
            reinicio -= 1
            jogador.rect.topleft = spawn
            camera_y = float(ALTURA_MAPA - ALTURA)
            camera_ativa = False
            break

    # Desenho
    tela.fill((0, 255, 0))
    # cenário por cima do fill, antes do resto
    # tela.blit(cenario, (0, -camera_y))  # <--- Quando reativarem o cenário, use -camera_y

    # Desenho temporário das ruas para visualizar a câmera subindo/descendo
    for f in FAIXAS:
        rua_rect = pygame.Rect(0, f.y - 40 - camera_y, LARGURA, 80)
        pygame.draw.rect(tela, (60, 60, 60), rua_rect)

    # desenhar inimigo
    for i in inimigos:
        i.desenhar(tela, camera_y)
    jogador.desenhar(tela, camera_y)

    pygame.display.flip()
    relogio.tick(60)

pygame.quit()
