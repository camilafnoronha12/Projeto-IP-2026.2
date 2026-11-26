import pygame
import os
import random
import mapa
 
pygame.init()
LARGURA, ALTURA = 1366, 720
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Agente CIncreto")
relogio = pygame.time.Clock()
CAMINHO = os.path.dirname(os.path.abspath(__file__))
PASTA_ASSETS = os.path.join(CAMINHO, "assets")
reinicio = 1
 
# ---------- FASE ----------
# Uma letra por faixa de 72 px, de cima (chegada) para baixo (começo).
# G = grama, C = calçada, R = rua, B = ciclovia, F = chegada.
LAYOUT = [
    "F", "C", "R", "R", "C", "B", "G", "B", "C", "G",
    "R", "R", "C", "B", "G", "B", "R", "C", "B", "G",
    "C", "R", "R", "C", "B", "B", "G", "C", "R", "G",
]
VELOCIDADES = {
    "rua": (6, 1300),       # (velocidade, intervalo entre carros em ms)
    "ciclovia": (4, 1600),  # (velocidade, intervalo entre bicicletas em ms)
}
ALTURA_MAPA = len(LAYOUT) * mapa.ALTURA_FAIXA
MAPA_RECT = pygame.Rect(0, 0, LARGURA, ALTURA_MAPA)

#Lucas Araujo: mexi na velocidade da camera que Flavio tinha colocado pois estava muito rapido, acho que assim ficou melhor
 #VELOCIDADE_CAMERA caiu de 0.5 para 0.3.
 #Criei SUAVIZACAO_CAMERA = 0.08, e agora a câmera se aproxima do jogador aos poucos em vez de pular para a posição dele.

VELOCIDADE_CAMERA = 0.3   # quanto a câmera sobe sozinha por frame depois do 1º passo
SUAVIZACAO_CAMERA = 0.08  # de 0 a 1: quanto menor, mais devagar a câmera acompanha o jogador
CAMERA_INICIAL = float(ALTURA_MAPA - ALTURA)  # começa mostrando o fundo
 
# ---------- MENU ----------
capa = pygame.image.load(os.path.join(
    PASTA_ASSETS, "capa", "capa_agente_cincretov1.png")).convert()
# ajusta à altura da janela mantendo a proporção
largura_capa = int(capa.get_width() * ALTURA / capa.get_height())
capa = pygame.transform.scale(capa, (largura_capa, ALTURA))
capa_rect = capa.get_rect(center=(LARGURA // 2, ALTURA // 2))
fonte_menu = pygame.font.SysFont(None, 48)
fonte_titulo = pygame.font.SysFont(None, 96)
 
 
def texto_com_sombra(texto, fonte, centro):
    sombra = fonte.render(texto, True, (0, 0, 0))
    frente = fonte.render(texto, True, (255, 255, 255))
    pos = frente.get_rect(center=centro)
    tela.blit(sombra, pos.move(3, 3))
    tela.blit(frente, pos)
 
 
def desenhar_menu():
    tela.fill((18, 14, 32))  # cor das faixas laterais
    tela.blit(capa, capa_rect)
    # texto piscando: visível 600 ms, escondido 400 ms
    if pygame.time.get_ticks() % 1000 < 600:
        texto_com_sombra("Pressione qualquer tecla para iniciar",
                         fonte_menu, (LARGURA // 2, ALTURA - 60))
 
 
class Inimigo:
    def __init__(self, y, direcao, velocidade, imagem):
        # vira a imagem para o lado em que ele anda
        self.imagem = imagem if direcao > 0 else pygame.transform.flip(
            imagem, True, False)
        self.rect = self.imagem.get_rect(centery=y)
        # nasce num extremo da tela, para ir até o outro lado
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
        self.intervalo = intervalo  # intervalo entre os inimigos surgindo
        self.imagem = imagem
        self.proximo = 0            # quando nasce o próximo
 
    def gerar(self, agora, inimigos):
        if agora >= self.proximo:
            inimigos.append(Inimigo(self.y, self.direcao,
                            self.velocidade, self.imagem))
            # randomiza para os inimigos surgirem de forma irregular
            self.proximo = agora + random.randint(
                int(self.intervalo * 0.7), int(self.intervalo * 1.5))
 
def carregar_bicicleta():
    img = pygame.image.load(os.path.join(
        PASTA_ASSETS, "bicicleta_1.png")).convert_alpha()
    return pygame.transform.scale(img, (90, 70))
 
def carregar_carro():
    caminho = os.path.join(PASTA_ASSETS, "carro_1.png")
    if os.path.exists(caminho):
        img = pygame.image.load(caminho).convert_alpha()
        return pygame.transform.scale(img, (130, 58))
    # carro provisório, desenhado por código, até existir o carro_1.png
    img = pygame.Surface((130, 58), pygame.SRCALPHA)
    pygame.draw.rect(img, (200, 50, 50), (0, 16, 130, 34), border_radius=8)
    pygame.draw.rect(img, (170, 40, 40), (28, 2, 66, 26), border_radius=8)
    pygame.draw.rect(img, (160, 210, 240), (36, 7, 24, 16))
    pygame.draw.rect(img, (160, 210, 240), (64, 7, 24, 16))
    pygame.draw.circle(img, (20, 20, 20), (26, 50), 8)
    pygame.draw.circle(img, (20, 20, 20), (104, 50), 8)
    return img
 
IMAGENS_INIMIGO = {
    "bicicleta": carregar_bicicleta(),
    "carro": carregar_carro(),
}
 
def criar_faixas(fase):
    """Cria as Faixas de inimigos nos lugares que o mapa indica."""
    return [Faixa(y, direcao, velocidade, intervalo, IMAGENS_INIMIGO[tipo])
            for y, direcao, velocidade, intervalo, tipo in fase.faixas_inimigos()]
 
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
        # TODO: voltar para (x0, y0) ao bater nas HITBOXES do cenário
 
    def desenhar(self, superficie, camera_y):
        superficie.blit(self.imagem, self.rect.move(0, -camera_y))
 
def nova_partida():
    """Monta a fase do zero: mapa, jogador no começo, faixas e inimigos vazios."""
    fase = mapa.Mapa("UFPE", LAYOUT, VELOCIDADES)
    return fase, Jogador(*fase.posicao_inicial()), criar_faixas(fase), []
 
fase, jogador, FAIXAS, inimigos = nova_partida()
# o mapa inteiro é desenhado uma vez só; a câmera mostra um pedaço dele
mundo = pygame.Surface((LARGURA, ALTURA_MAPA))
fase.desenhar(mundo)
camera_y = CAMERA_INICIAL
camera_ativa = False
estado = "menu"  # "menu", "jogo" ou "vitoria"
 
def desenhar_jogo():
    cam = int(camera_y)
    tela.blit(mundo, (0, -cam))
    for i in inimigos:
        i.desenhar(tela, cam)
    jogador.desenhar(tela, cam)
 
rodando = True
while rodando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
        if evento.type == pygame.KEYDOWN:
            if estado == "menu":
                fase, jogador, FAIXAS, inimigos = nova_partida()
                camera_y, camera_ativa = CAMERA_INICIAL, False
                estado = "jogo"
            elif estado == "vitoria":
                estado = "menu"
 
    if estado == "menu":
        desenhar_menu()
 
    elif estado == "jogo":
        teclas = pygame.key.get_pressed()
        pos_antes = jogador.rect.topleft
        jogador.mover(teclas)
        if jogador.rect.topleft != pos_antes:
            camera_ativa = True
 
        agora = pygame.time.get_ticks()
        for f in FAIXAS:
            f.gerar(agora, inimigos)
        for i in inimigos:
            i.mover()
        inimigos = [i for i in inimigos if not i.saiu()]
 
        # a câmera só começa a subir depois do primeiro passo do jogador
        if camera_ativa:
            camera_y -= VELOCIDADE_CAMERA
            alvo_camera = jogador.rect.centery - ALTURA // 2
            if alvo_camera < camera_y:
                camera_y += (alvo_camera - camera_y) * SUAVIZACAO_CAMERA
            camera_y = max(0, camera_y)
 
        # a câmera engoliu o jogador ou um inimigo o atingiu: volta ao começo
        engolido = jogador.rect.top > camera_y + ALTURA
        atingido = any(
            jogador.rect.inflate(-20, -20).colliderect(i.rect.inflate(-10, -10))
            for i in inimigos)
        if engolido or atingido:
            reinicio -= 1
            jogador.rect.topleft = fase.posicao_inicial()
            camera_y = CAMERA_INICIAL
            camera_ativa = False
 
        if fase.chegou_no_fim(jogador.rect):
            estado = "vitoria"
 
        desenhar_jogo()
 
    else:  # vitoria
        desenhar_jogo()
        escurecer = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        escurecer.fill((0, 0, 0, 150))
        tela.blit(escurecer, (0, 0))
        texto_com_sombra("Fase concluída!", fonte_titulo,
                         (LARGURA // 2, ALTURA // 2 - 40))
        texto_com_sombra("Pressione qualquer tecla para voltar ao menu",
                         fonte_menu, (LARGURA // 2, ALTURA // 2 + 40))
 
    pygame.display.flip()
    relogio.tick(60)
pygame.quit()
 
