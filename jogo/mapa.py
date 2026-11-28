"""
mapa.py - Cenário das fases do Agente CIncreto

O mapa é dividido em faixas horizontais de 72 px (grama, calçada, rua,
ciclovia...). A Perna começa na faixa de baixo e precisa chegar na de cima.

Fase 1: a Perna sai do pátio do CIn (embaixo, prédio no canto), atravessa ruas e
ciclovias da UFPE e chega no ponto de ônibus (em cima), onde pega o
ônibus para Boa Viagem.

Todo o cenário é desenhado por código, em "pixels grandes" (cada pixel do
desenho vira um quadrado de 2x2 na tela), para combinar com a pixel art
do jogo. Árvores, arbustos, postes etc. viram OBSTÁCULOS: o mapa guarda
os retângulos deles em self.obstaculos para o jogador não atravessá-los.

O mapa também diz ONDE os inimigos passam: carros nas ruas, bicicletas
nas ciclovias. O AgenteCIncreto.py usa isso para criar as Faixas de
inimigos no lugar certo.
"""

import os
import random
import pygame

LARGURA, ALTURA = 1366, 720
ALTURA_FAIXA = 72  # 720 / 72 = 10 faixas por tela

# O cenário é desenhado numa imagem menor e depois ampliada 2x
PIXEL = 2
LARG_P = LARGURA // PIXEL         # 683 "pixels de desenho" de largura
FAIXA_P = ALTURA_FAIXA // PIXEL   # 36 "pixels de desenho" por faixa

SEMENTE = 2026  # mesma semente = mesmo cenário toda vez que o jogo abre

CAMINHO = os.path.dirname(os.path.abspath(__file__))
PASTA_ASSETS = os.path.join(CAMINHO, "assets", "mapa")  # imagens do cenário

# Cores "resumo" de cada tipo de faixa (usadas pela FaixaMapa)
CORES = {
    "grama": (88, 160, 72),
    "calcada": (178, 176, 170),
    "rua": (58, 58, 64),
    "ciclovia": (176, 58, 52),
    "chegada": (230, 200, 60),
    "cin": (88, 160, 72),
    "entrada": (200, 194, 182),
    "ponto": (178, 176, 170),
}

# Quando tiver o desenho de uma faixa, coloque o arquivo em assets/mapa/
# e escreva o nome aqui. Ex.: "rua": "rua.png"
# Se o arquivo não existir, ele continua usando o desenho feito por código.
IMAGENS = {}

# Qual inimigo passa em cada tipo de faixa (o resto é seguro)
INIMIGO_DA_FAIXA = {
    "rua": "carro",
    "ciclovia": "bicicleta",
}

# Letras usadas para desenhar as fases
LETRAS = {
    "G": "grama",     # grama com árvores, coqueiros e arbustos
    "C": "calcada",   # calçada com postes e lixeiras
    "R": "rua",       # rua (carros)
    "B": "ciclovia",  # ciclovia (bicicletas)
    "F": "chegada",   # chegada genérica
    "I": "cin",       # pátio com o prédio do CIn no canto (use "I", "I")
    "E": "entrada",   # pátio do CIn onde a Perna começa
    "P": "ponto",     # ponto de ônibus (use "P", "P": ônibus + abrigo)
}

# ---------------------------------------------------------------------------
# Paleta de cores do cenário
# ---------------------------------------------------------------------------
COR = {
    "grama": (88, 160, 72), "grama_escura": (74, 142, 62),
    "grama_clara": (104, 176, 84), "grama_tufo": (64, 128, 56),
    "sombra_grama": (60, 118, 52),
    "calcada": (178, 176, 170), "calcada_escura": (166, 164, 158),
    "calcada_clara": (190, 188, 182), "junta": (150, 148, 142),
    "meio_fio": (128, 126, 122), "meio_fio_claro": (214, 212, 206),
    "sombra_calcada": (140, 138, 132),
    "asfalto": (58, 58, 64), "asfalto_claro": (68, 68, 74),
    "asfalto_escuro": (48, 48, 54), "remendo": (52, 52, 57),
    "branca": (232, 232, 226), "amarela": (240, 196, 40),
    "ciclo": (176, 58, 52), "ciclo_claro": (188, 70, 62),
    "ciclo_escuro": (160, 50, 46), "pintura": (238, 226, 220),
    "patio": (200, 194, 182), "patio_claro": (210, 204, 192),
    "patio_escuro": (188, 182, 170), "junta_patio": (172, 166, 154),
    "contorno": (40, 40, 48),
    "parede": (226, 224, 218), "parede_clara": (240, 238, 232),
    "parede_sombra": (200, 198, 192), "platibanda": (150, 152, 158),
    "vidro": (88, 146, 192), "vidro_escuro": (62, 112, 158),
    "reflexo": (176, 214, 238), "moldura": (70, 78, 92),
    "vermelho_cin": (196, 32, 46),
    "tronco": (116, 76, 42), "tronco_escuro": (88, 56, 32),
    "tronco_coqueiro": (156, 124, 80), "anel_coqueiro": (120, 94, 60),
    "folha_coqueiro": (60, 140, 60), "folha_coqueiro_esc": (36, 98, 44),
    "coco": (120, 84, 40),
    "poste": (78, 82, 90), "poste_claro": (120, 124, 132),
    "luz": (255, 236, 150), "madeira": (150, 98, 52),
    "metal": (120, 124, 132),
}

VERDES_ARVORE = [
    ((34, 90, 44), (52, 128, 58), (92, 170, 80)),
    ((30, 84, 52), (46, 118, 70), (84, 160, 96)),
]
IPE_AMARELO = ((170, 120, 20), (225, 180, 40), (250, 220, 90))
VERDE_ARBUSTO = ((30, 92, 46), (46, 124, 58), (86, 166, 84))
CORES_FLORES = [(240, 240, 240), (250, 210, 60), (236, 110, 160), (220, 40, 50)]


def _pista(tipo):
    return tipo in ("rua", "ciclovia")


def _ruido(s, r, cores, densidade, rng):
    """Pontinhos de cor aleatórios para dar textura."""
    for _ in range(int(r.w * r.h * densidade)):
        s.set_at((rng.randrange(r.x, r.right), rng.randrange(r.y, r.bottom)),
                 rng.choice(cores))


def _texto(s, texto, cor, centro, larg_max, tam_max):
    """Escreve um texto centralizado, diminuindo a fonte até caber."""
    tam = tam_max
    while True:
        img = pygame.font.Font(None, tam).render(texto, False, cor)
        if img.get_width() <= larg_max or tam <= 8:
            break
        tam -= 1
    s.blit(img, img.get_rect(center=centro))


# ---------------------------------------------------------------------------
# Fundo de cada tipo de faixa
# ---------------------------------------------------------------------------
def _base_grama(s, r, rng):
    s.fill(COR["grama"], r)
    _ruido(s, r, (COR["grama_escura"], COR["grama_clara"]), 0.12, rng)
    for _ in range(r.w // 9):  # tufos de capim
        x = rng.randrange(r.x + 1, r.right - 1)
        y = rng.randrange(r.y + 3, r.bottom)
        for p in ((x, y), (x - 1, y - 1), (x + 1, y - 1), (x, y - 2)):
            s.set_at(p, COR["grama_tufo"])
    for _ in range(r.w // 45):  # florzinhas
        x = rng.randrange(r.x + 2, r.right - 2)
        y = rng.randrange(r.y + 2, r.bottom - 2)
        c = rng.choice(CORES_FLORES)
        for p in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            s.set_at(p, c)
        s.set_at((x, y), (250, 220, 80))


def _base_calcada(s, r, rng, borda_cima, borda_baixo):
    s.fill(COR["calcada"], r)
    _ruido(s, r, (COR["calcada_escura"], COR["calcada_clara"]), 0.06, rng)
    meio = r.y + r.h // 2
    pygame.draw.line(s, COR["junta"], (r.x, meio), (r.right, meio))
    for x in range(r.x, r.right, 24):  # placas de concreto desencontradas
        pygame.draw.line(s, COR["junta"], (x, r.y), (x, meio))
        pygame.draw.line(s, COR["junta"], (x + 12, meio), (x + 12, r.bottom))
    if borda_cima:  # meio-fio
        s.fill(COR["meio_fio"], (r.x, r.y, r.w, 3))
        s.fill(COR["meio_fio_claro"], (r.x, r.y, r.w, 1))
        s.fill(COR["sombra_calcada"], (r.x, r.y + 3, r.w, 1))
    if borda_baixo:
        s.fill(COR["meio_fio"], (r.x, r.bottom - 3, r.w, 3))
        s.fill(COR["meio_fio_claro"], (r.x, r.bottom - 3, r.w, 1))


def _base_rua(s, r, rng, linha_cima, linha_baixo, tracejado_cima):
    s.fill(COR["asfalto"], r)
    for _ in range(rng.randint(0, 2)):  # remendos no asfalto
        w, h = rng.randrange(14, 40), rng.randrange(5, 12)
        s.fill(COR["remendo"], (rng.randrange(0, r.w - w),
                                rng.randrange(r.y + 4, r.bottom - h - 4), w, h))
    _ruido(s, r, (COR["asfalto_claro"], COR["asfalto_escuro"]), 0.15, rng)
    if linha_cima:
        s.fill(COR["branca"], (r.x, r.y + 2, r.w, 1))
    if linha_baixo:
        s.fill(COR["branca"], (r.x, r.bottom - 3, r.w, 1))
        x = rng.randrange(30, 200)
        while x < r.right - 12:  # bueiros perto do meio-fio
            s.fill(COR["asfalto_escuro"], (x, r.bottom - 8, 10, 4))
            for k in range(x + 1, x + 10, 2):
                s.set_at((k, r.bottom - 7), (30, 30, 34))
                s.set_at((k, r.bottom - 6), (30, 30, 34))
            x += rng.randrange(260, 420)
    if tracejado_cima:  # duas mãos: linha amarela tracejada no meio
        for x in range(rng.randrange(0, 20), r.right, 30):
            s.fill(COR["amarela"], (x, r.y - 1, 16, 2))


def _bici_pintada(s, x, cy):
    c = COR["pintura"]
    pygame.draw.circle(s, c, (x - 6, cy + 3), 4, 1)
    pygame.draw.circle(s, c, (x + 6, cy + 3), 4, 1)
    pygame.draw.lines(s, c, False, [(x - 6, cy + 3), (x - 2, cy - 3),
                                    (x + 4, cy - 3), (x + 6, cy + 3)])
    pygame.draw.line(s, c, (x - 2, cy - 3), (x, cy + 3))
    pygame.draw.line(s, c, (x, cy + 3), (x + 4, cy - 3))
    pygame.draw.line(s, c, (x - 4, cy - 5), (x - 1, cy - 5))
    pygame.draw.line(s, c, (x + 4, cy - 3), (x + 5, cy - 6))


def _seta(s, x, cy, d):
    c = COR["pintura"]
    pygame.draw.line(s, c, (x - 6 * d, cy), (x + 4 * d, cy), 2)
    pygame.draw.polygon(s, c, [(x + 8 * d, cy), (x + 3 * d, cy - 4),
                               (x + 3 * d, cy + 4)])


def _base_ciclovia(s, r, rng, direcao, borda_cima, tracejado_cima, borda_baixo):
    s.fill(COR["ciclo"], r)
    _ruido(s, r, (COR["ciclo_claro"], COR["ciclo_escuro"]), 0.10, rng)
    if tracejado_cima:
        for x in range(rng.randrange(0, 12), r.right, 22):
            s.fill(COR["branca"], (x, r.y - 1, 12, 2))
    elif borda_cima:
        s.fill(COR["branca"], (r.x, r.y + 1, r.w, 1))
    if borda_baixo:
        s.fill(COR["branca"], (r.x, r.bottom - 2, r.w, 1))
    for x in range(rng.randrange(40, 120), r.right - 30, 190):
        _bici_pintada(s, x, r.centery)
        _seta(s, x + 26 * direcao, r.centery, direcao)


def _base_patio(s, r, rng):
    s.fill(COR["patio"], r)
    _ruido(s, r, (COR["patio_escuro"], COR["patio_claro"]), 0.05, rng)
    for x in range(r.x + 4, r.right, 18):
        pygame.draw.line(s, COR["junta_patio"], (x, r.y), (x, r.bottom))
    for y in range(r.y + 9, r.bottom, 18):
        pygame.draw.line(s, COR["junta_patio"], (r.x, y), (r.right, y))


def _chegada(s, r):
    """Faixa quadriculada de chegada (letra F)."""
    for x in range(0, r.w, 6):
        for k, y in enumerate(range(r.y, r.bottom, 6)):
            cor = (240, 240, 240) if (x // 6 + k) % 2 else (30, 30, 30)
            s.fill(cor, (x, y, 6, 6))


# ---------------------------------------------------------------------------
# Enfeites (desenhados por cima do fundo, de cima para baixo)
# ---------------------------------------------------------------------------
def _arvore(s, x, yb, verde):
    esc, med, cla = verde
    pygame.draw.ellipse(s, COR["sombra_grama"], (x - 12, yb - 3, 24, 6))
    s.fill(COR["tronco"], (x - 2, yb - 12, 5, 12))
    s.fill(COR["tronco_escuro"], (x + 1, yb - 12, 2, 12))
    bolas = ((0, -22, 12), (-8, -17, 8), (8, -17, 8), (0, -30, 7))
    for dx, dy, raio in bolas:
        pygame.draw.circle(s, esc, (x + dx, yb + dy), raio + 1)
    for dx, dy, raio in bolas:
        pygame.draw.circle(s, med, (x + dx, yb + dy), raio)
    for dx, dy, raio in ((-3, -26, 5), (-9, -19, 3), (4, -31, 3)):
        pygame.draw.circle(s, cla, (x + dx, yb + dy), raio)


def _coqueiro(s, x, yb, inclina):
    pygame.draw.ellipse(s, COR["sombra_grama"], (x - 9, yb - 3, 18, 5))
    pontos = [(x + int(inclina * (t / 11) ** 2), yb - t * 4) for t in range(12)]
    for i, (px, py) in enumerate(pontos):
        s.fill(COR["tronco_coqueiro"], (px - 2, py - 4, 4, 5))
        s.fill(COR["anel_coqueiro"], (px - 2, py - 4, 4, 1))
    tx, ty = pontos[-1][0], pontos[-1][1] - 4
    for dx, dy in ((-16, 8), (16, 8), (-12, -2), (12, -2), (-4, -8), (5, -8)):
        meio = (tx + dx // 2, ty + min(dy, 0) - 3)
        fim = (tx + dx, ty + dy + 2)
        pygame.draw.lines(s, COR["folha_coqueiro_esc"], False, [(tx, ty), meio, fim], 3)
        pygame.draw.lines(s, COR["folha_coqueiro"], False, [(tx, ty - 1), meio, fim], 1)
    pygame.draw.circle(s, COR["coco"], (tx - 2, ty + 3), 2)
    pygame.draw.circle(s, COR["coco"], (tx + 2, ty + 3), 2)


def _arbusto(s, x, yb, semente, flores=True, sombra=True):
    rng = random.Random(semente)
    esc, med, cla = VERDE_ARBUSTO
    if sombra:
        pygame.draw.ellipse(s, COR["sombra_grama"], (x - 11, yb - 3, 22, 5))
    bolas = ((-6, -5, 5), (6, -5, 5), (0, -8, 6), (-2, -4, 5), (3, -4, 5))
    for dx, dy, raio in bolas:
        pygame.draw.circle(s, esc, (x + dx, yb + dy), raio + 1)
    for dx, dy, raio in bolas:
        pygame.draw.circle(s, med, (x + dx, yb + dy), raio)
    for dx, dy in ((-3, -10), (4, -8)):
        pygame.draw.circle(s, cla, (x + dx, yb + dy), 2)
    if flores:  # ixora (cachos vermelhos, comum nos jardins do Recife)
        cor = rng.choice([(220, 40, 50), (240, 120, 40), (236, 110, 160)])
        for _ in range(4):
            fx, fy = x + rng.randint(-8, 7), yb + rng.randint(-12, -4)
            s.fill(cor, (fx, fy, 2, 2))


def _poste(s, x, yb):
    pygame.draw.ellipse(s, COR["sombra_calcada"], (x - 4, yb - 2, 9, 3))
    s.fill(COR["poste"], (x - 1, yb - 34, 3, 33))
    s.fill(COR["poste_claro"], (x - 1, yb - 34, 1, 33))
    s.fill(COR["poste"], (x - 1, yb - 35, 10, 2))
    s.fill((50, 52, 58), (x + 5, yb - 35, 7, 3))
    s.fill(COR["luz"], (x + 6, yb - 32, 5, 1))
    s.fill((60, 64, 70), (x - 2, yb - 2, 5, 2))


def _lixeira(s, x, yb):
    pygame.draw.ellipse(s, COR["sombra_calcada"], (x - 5, yb - 2, 11, 3))
    s.fill((40, 110, 66), (x - 3, yb - 9, 7, 8))
    s.fill((30, 80, 50), (x - 4, yb - 10, 9, 2))
    s.fill((70, 150, 96), (x - 2, yb - 8, 1, 6))


def _floreira(s, x, yb, semente):
    pygame.draw.ellipse(s, COR["sombra_calcada"], (x - 10, yb - 2, 20, 4))
    _arbusto(s, x, yb - 4, semente, flores=True, sombra=False)
    s.fill((150, 146, 140), (x - 8, yb - 5, 16, 5))
    s.fill((180, 176, 170), (x - 8, yb - 5, 16, 1))


def _bike_mini(s, x, yb, cor):
    pygame.draw.circle(s, (30, 30, 34), (x - 4, yb - 3), 3, 1)
    pygame.draw.circle(s, (30, 30, 34), (x + 4, yb - 3), 3, 1)
    pygame.draw.lines(s, cor, False, [(x - 4, yb - 3), (x - 1, yb - 7),
                                      (x + 3, yb - 7), (x + 4, yb - 3)])
    pygame.draw.line(s, cor, (x - 1, yb - 7), (x, yb - 3))
    s.fill((30, 30, 34), (x - 3, yb - 9, 3, 1))


def _bicicletario(s, x0, x1, yb):
    for x in range(x0, x1, 12):
        s.fill(COR["metal"], (x, yb - 10, 1, 10))
        s.fill(COR["metal"], (x + 6, yb - 10, 1, 10))
        s.fill(COR["metal"], (x, yb - 10, 7, 1))
    _bike_mini(s, x0 + 3, yb, (40, 90, 200))
    _bike_mini(s, x0 + 39, yb, (230, 180, 30))


def _banco(s, x, yb):
    pygame.draw.ellipse(s, COR["patio_escuro"], (x - 14, yb - 3, 28, 4))
    s.fill(COR["madeira"], (x - 12, yb - 12, 24, 2))
    s.fill(COR["madeira"], (x - 12, yb - 7, 24, 2))
    s.fill((60, 60, 64), (x - 11, yb - 10, 1, 9))
    s.fill((60, 60, 64), (x + 10, yb - 10, 1, 9))


def _totem_cin(s, x, yb):
    s.fill((70, 70, 76), (x - 1, yb - 8, 3, 8))
    placa = pygame.Rect(x - 11, yb - 22, 22, 14)
    s.fill(COR["vermelho_cin"], placa)
    pygame.draw.rect(s, COR["contorno"], placa, 1)
    _texto(s, "CIn", (255, 255, 255), placa.center, 18, 14)


def _janelas(s, x, y, w, h):
    s.fill(COR["moldura"], (x - 1, y - 1, w + 2, h + 2))
    s.fill(COR["vidro"], (x, y, w, h))
    s.fill(COR["vidro_escuro"], (x, y + h - 3, w, 3))
    for mx in range(x + 9, x + w, 10):
        s.fill(COR["moldura"], (mx, y, 1, h))
    for rx in range(x + 2, x + w - 6, 23):
        for k in range(min(h - 2, 6)):
            s.set_at((rx + 5 - k, y + 1 + k), COR["reflexo"])


def _predio_cin(s, x0, y0, x1, y1):
    """Fachada do Centro de Informática (estilizada)."""
    w, cx = x1 - x0, (x0 + x1) // 2
    # alas laterais
    ala = pygame.Rect(x0, y0 + 8, w, y1 - y0 - 8)
    s.fill(COR["parede"], ala)
    s.fill(COR["parede_sombra"], (ala.x, ala.bottom - 4, ala.w, 4))
    pygame.draw.rect(s, COR["contorno"], ala, 1)
    plat = pygame.Rect(x0 - 2, ala.y - 3, w + 4, 4)
    s.fill(COR["platibanda"], plat)
    s.fill((190, 192, 198), (plat.x, plat.y, plat.w, 1))
    pygame.draw.rect(s, COR["contorno"], plat, 1)
    for jy in (ala.y + 6, ala.y + 24):
        for a, b in ((x0 + 6, cx - 52), (cx + 52, x1 - 6)):
            _janelas(s, a, jy, b - a, 11)
    # bloco central, mais alto, com o letreiro
    centro = pygame.Rect(cx - 46, y0, 92, y1 - y0)
    s.fill(COR["parede_clara"], centro)
    pygame.draw.rect(s, COR["contorno"], centro, 1)
    s.fill(COR["platibanda"], (centro.x - 2, y0 - 2, centro.w + 4, 3))
    placa = pygame.Rect(cx - 36, y0 + 5, 72, 22)
    s.fill(COR["vermelho_cin"], placa)
    s.fill((222, 60, 72), (placa.x, placa.y, placa.w, 2))
    pygame.draw.rect(s, COR["contorno"], placa, 1)
    _texto(s, "CIn", (255, 255, 255), (placa.centerx, placa.centery + 1), 66, 30)
    _texto(s, "CENTRO DE INFORMÁTICA", (50, 50, 60), (cx, y0 + 32), 86, 12)
    _texto(s, "UFPE", (110, 110, 120), (cx, y0 + 40), 40, 11)
    # porta de vidro com marquise
    porta = pygame.Rect(cx - 13, y1 - 19, 26, 19)
    s.fill(COR["moldura"], porta)
    s.fill(COR["vidro"], (porta.x + 2, porta.y + 2, 10, porta.h - 2))
    s.fill(COR["vidro"], (porta.x + 14, porta.y + 2, 10, porta.h - 2))
    s.fill(COR["reflexo"], (porta.x + 3, porta.y + 3, 2, 6))
    s.fill(COR["reflexo"], (porta.x + 15, porta.y + 3, 2, 6))
    s.fill((220, 220, 220), (cx - 3, porta.y + 9, 1, 3))
    s.fill((220, 220, 220), (cx + 2, porta.y + 9, 1, 3))
    s.fill((90, 92, 100), (cx - 20, porta.y - 4, 40, 3))
    s.fill((140, 142, 150), (cx - 20, porta.y - 4, 40, 1))
    # jardineira de ixora ao pé da fachada
    for x in range(x0 + 8, x1 - 4, 12):
        if abs(x - cx) > 30:
            _arbusto(s, x, y1, x * 31, flores=True, sombra=False)


def _onibus(s, x, yb):
    """Ônibus parado no ponto, indo para Boa Viagem (fase 2)."""
    pygame.draw.ellipse(s, (36, 36, 40), (x - 2, yb - 4, 146, 6))
    corpo = pygame.Rect(x, yb - 32, 140, 28)
    s.fill((240, 240, 236), corpo)
    pygame.draw.rect(s, COR["contorno"], corpo, 1)
    s.fill((250, 190, 30), (x + 1, yb - 12, 138, 2))
    s.fill((30, 80, 160), (x + 1, yb - 10, 138, 4))
    s.fill(COR["vidro"], (x + 2, yb - 28, 10, 16))          # para-brisa
    s.fill(COR["reflexo"], (x + 3, yb - 27, 2, 6))
    s.fill(COR["moldura"], (x + 14, yb - 22, 11, 17))       # porta
    s.fill(COR["vidro_escuro"], (x + 15, yb - 21, 4, 15))
    s.fill(COR["vidro_escuro"], (x + 20, yb - 21, 4, 15))
    s.fill(COR["vidro"], (x + 28, yb - 22, 108, 9))         # janelas
    for jx in range(x + 28, x + 136, 15):
        s.fill(COR["moldura"], (jx, yb - 22, 1, 9))
    letreiro = pygame.Rect(x + 28, yb - 31, 70, 8)
    s.fill((20, 20, 20), letreiro)
    _texto(s, "BOA VIAGEM", (255, 160, 30), letreiro.center, 66, 10)
    s.fill((255, 230, 120), (x, yb - 9, 2, 3))              # farol
    s.fill(COR["contorno"], (x - 1, yb - 6, 3, 3))
    for rx in (x + 24, x + 114):
        pygame.draw.circle(s, (24, 24, 26), (rx, yb - 4), 5)
        pygame.draw.circle(s, (150, 150, 156), (rx, yb - 4), 2)


def _abrigo(s, cx, yb):
    """Abrigo do ponto de ônibus com banco e placa."""
    x0 = cx - 55
    pygame.draw.ellipse(s, COR["sombra_calcada"], (x0 - 4, yb - 3, 120, 5))
    vidro = pygame.Rect(x0 + 5, yb - 28, 100, 18)
    s.fill((170, 206, 228), vidro)
    for rx in range(vidro.x + 4, vidro.right - 8, 20):
        for k in range(6):
            s.set_at((rx + 6 - k, vidro.y + 2 + k), (220, 238, 248))
    pygame.draw.rect(s, COR["moldura"], vidro, 1)
    cartaz = pygame.Rect(x0 + 72, yb - 27, 28, 16)  # cartaz de cinema
    s.fill((40, 30, 60), cartaz)
    s.fill((250, 200, 60), (cartaz.x + 2, cartaz.y + 2, cartaz.w - 4, 3))
    _texto(s, "CINEMA", (250, 230, 200), (cartaz.centerx, cartaz.centery + 3), 26, 9)
    s.fill(COR["moldura"], (x0 + 2, yb - 30, 3, 30))        # colunas
    s.fill(COR["moldura"], (x0 + 105, yb - 30, 3, 30))
    s.fill(COR["madeira"], (x0 + 12, yb - 11, 52, 3))        # banco
    s.fill((60, 60, 64), (x0 + 14, yb - 8, 2, 7))
    s.fill((60, 60, 64), (x0 + 60, yb - 8, 2, 7))
    telhado = pygame.Rect(x0 - 4, yb - 37, 118, 7)
    s.fill((36, 66, 118), telhado)
    s.fill((70, 104, 160), (telhado.x, telhado.y, telhado.w, 1))
    pygame.draw.rect(s, COR["contorno"], telhado, 1)
    _texto(s, "PONTO DE ÔNIBUS", (255, 255, 255), telhado.center, 100, 10)
    px = x0 + 124                                           # placa de parada
    s.fill(COR["poste"], (px, yb - 34, 2, 34))
    placa = pygame.Rect(px - 7, yb - 42, 16, 11)
    s.fill((25, 80, 170), placa)
    pygame.draw.rect(s, COR["contorno"], placa, 1)
    s.fill((255, 255, 255), (px - 4, yb - 40, 10, 5))
    s.fill((25, 80, 170), (px - 3, yb - 39, 3, 2))
    s.fill((25, 80, 170), (px + 1, yb - 39, 3, 2))
    s.fill((255, 255, 255), (px - 3, yb - 35, 2, 2))
    s.fill((255, 255, 255), (px + 3, yb - 35, 2, 2))


# ---------------------------------------------------------------------------
class FaixaMapa:
    """Uma faixa horizontal do cenário."""

    def __init__(self, tipo, y):
        self.tipo = tipo
        self.rect = pygame.Rect(0, y, LARGURA, ALTURA_FAIXA)
        self.imagem = None
        if tipo in IMAGENS:
            caminho = os.path.join(PASTA_ASSETS, IMAGENS[tipo])
            if os.path.exists(caminho):
                self.imagem = pygame.transform.scale(
                    pygame.image.load(caminho).convert(), self.rect.size)

    def desenhar(self, tela):
        """Versão simples (só cor). O Mapa usa o desenho completo."""
        if self.imagem:
            tela.blit(self.imagem, self.rect)
        else:
            pygame.draw.rect(tela, CORES[self.tipo], self.rect)


class Mapa:
    """Uma fase inteira, montada a partir de uma lista de letras."""

    def __init__(self, nome, layout, velocidades):
        # layout: uma letra por faixa, de CIMA para BAIXO (como aparece na tela)
        self.nome = nome
        self.faixas = [FaixaMapa(LETRAS[letra], i * ALTURA_FAIXA)
                       for i, letra in enumerate(layout)]
        self.tipos = [f.tipo for f in self.faixas]
        self.velocidades = velocidades  # {tipo_de_faixa: (velocidade, intervalo)}
        self.direcoes = self._calcular_direcoes()
        self.obstaculos = []   # pygame.Rect (em pixels da tela) que bloqueiam
        self._enfeites = []    # (y_base, funcao, argumentos)
        self._imagem = None
        self._planejar_cenario(random.Random(SEMENTE))

    # ---------- interface usada pelo AgenteCIncreto.py ----------
    def desenhar(self, tela):
        if self._imagem is None:
            self._imagem = self._renderizar()
        tela.blit(self._imagem, (0, 0))

    def posicao_inicial(self, tamanho_jogador=60):
        """Topleft da Perna no meio da faixa de baixo."""
        ultima = self.faixas[-1].rect
        return (LARGURA // 2 - tamanho_jogador // 2,
                ultima.centery - tamanho_jogador // 2)

    def chegou_no_fim(self, rect_jogador):
        """True quando a Perna entra na faixa de cima (chegada)."""
        return rect_jogador.colliderect(self.faixas[0].rect)

    def bloqueia(self, rect):
        """True se o retângulo bate em algum obstáculo do cenário."""
        return rect.collidelist(self.obstaculos) != -1

    def faixas_inimigos(self):
        """Lista com (y_centro, direcao, velocidade, intervalo, tipo_inimigo)
        para cada faixa perigosa. A direção vai alternando."""
        resultado = []
        for i, faixa in enumerate(self.faixas):
            tipo_inimigo = INIMIGO_DA_FAIXA.get(faixa.tipo)
            if tipo_inimigo:
                velocidade, intervalo = self.velocidades[faixa.tipo]
                resultado.append((faixa.rect.centery, self.direcoes[i],
                                  velocidade, intervalo, tipo_inimigo))
        return resultado

    # ---------- montagem do cenário ----------
    def _calcular_direcoes(self):
        direcoes, d = {}, 1
        for i, tipo in enumerate(self.tipos):
            if tipo in INIMIGO_DA_FAIXA:
                direcoes[i] = d
                d *= -1
        return direcoes

    def _vizinho(self, i):
        return self.tipos[i] if 0 <= i < len(self.tipos) else None

    def _grupos(self):
        """Faixas iguais seguidas: [(tipo, primeira, ultima), ...]"""
        grupos, ini = [], 0
        for i in range(1, len(self.tipos) + 1):
            if i == len(self.tipos) or self.tipos[i] != self.tipos[ini]:
                grupos.append((self.tipos[ini], ini, i - 1))
                ini = i
        return grupos

    def _add(self, y_base, funcao, *args, hitbox=None):
        self._enfeites.append((y_base, funcao, args))
        if hitbox:
            x, y, w, h = hitbox
            self.obstaculos.append(pygame.Rect(x * PIXEL, y * PIXEL,
                                               w * PIXEL, h * PIXEL))

    def _planejar_cenario(self, rng):
        for tipo, ini, fim in self._grupos():
            if tipo == "cin":
                self._planejar_cin(ini, fim)
            elif tipo == "ponto":
                self._planejar_ponto(ini, fim)
            for i in range(ini, fim + 1):
                if tipo == "grama":
                    self._planejar_grama(i, rng)
                elif tipo == "calcada":
                    self._planejar_calcada(i, rng)
                elif tipo == "entrada":
                    self._planejar_entrada(i)

    def _planejar_grama(self, i, rng):
        yb = (i + 1) * FAIXA_P - 3
        alto_ok = not (_pista(self._vizinho(i - 1)) or self._vizinho(i - 1) == "ponto")
        # passo mínimo de 62 garante espaço para a Perna passar entre as coisas
        x = rng.randrange(8, 50)
        while x < LARG_P - 8:
            sorteio, y = rng.random(), yb - rng.randrange(0, 4)
            if sorteio < 0.38:
                verde = IPE_AMARELO if rng.random() < 0.12 else rng.choice(VERDES_ARVORE)
                self._add(y, _arvore, x, y, verde, hitbox=(x - 6, y - 8, 12, 8))
            elif sorteio < 0.52 and alto_ok:
                inclina = rng.choice((-1, 1)) * rng.randint(3, 7)
                self._add(y, _coqueiro, x, y, inclina, hitbox=(x - 3, y - 5, 6, 5))
            elif sorteio < 0.85:
                self._add(y, _arbusto, x, y, rng.randrange(10 ** 6),
                          hitbox=(x - 8, y - 6, 16, 6))
            x += rng.randrange(62, 130)

    def _planejar_calcada(self, i, rng):
        yb = (i + 1) * FAIXA_P - 5
        x = rng.randrange(30, 120)
        while x < LARG_P - 20:
            sorteio = rng.random()
            if sorteio < 0.55:
                self._add(yb, _poste, x, yb, hitbox=(x - 2, yb - 3, 5, 3))
            elif sorteio < 0.8:
                self._add(yb, _lixeira, x, yb, hitbox=(x - 4, yb - 4, 9, 4))
            else:
                self._add(yb, _floreira, x, yb, rng.randrange(10 ** 6),
                          hitbox=(x - 8, yb - 5, 16, 5))
            x += rng.randrange(150, 260)

    def _planejar_entrada(self, i):
        yb = (i + 1) * FAIXA_P - 6
        # tudo nas beiradas: o meio fica livre para a Perna subir
        self._add(yb, _totem_cin, 272, yb, hitbox=(269, yb - 4, 7, 4))
        self._add(yb, _bicicletario, LARG_P - 210, LARG_P - 120, yb,
                  hitbox=(LARG_P - 210, yb - 4, 90, 4))
        self._add(yb, _banco, LARG_P - 60, yb, hitbox=(LARG_P - 72, yb - 4, 24, 4))

    def _planejar_cin(self, ini, fim):
        """Prédio do CIn no canto esquerdo; o resto vira pátio livre."""
        topo, base = ini * FAIXA_P, (fim + 1) * FAIXA_P
        x0, x1 = 8, 250
        self._add(base, _predio_cin, x0, topo + 4, x1, base,
                  hitbox=(x0 - 2, topo + 4, x1 - x0 + 4, base - topo - 4))
        for i in range(ini, fim + 1):  # só enfeites na beirada direita
            yb = (i + 1) * FAIXA_P - 3
            x = LARG_P - 16
            self._add(yb, _arvore, x, yb, VERDES_ARVORE[i % 2],
                      hitbox=(x - 6, yb - 8, 12, 8))
        self._add(base - 4, _floreira, 272, base - 4, 7,
                  hitbox=(264, base - 9, 16, 5))

    def _planejar_ponto(self, ini, fim):
        cx = LARG_P // 2
        yb = (fim + 1) * FAIXA_P - 3
        self._add(yb, _abrigo, cx, yb)  # sem hitbox: é o objetivo da fase
        if fim > ini:
            yb_bus = fim * FAIXA_P - 3
            self._add(yb_bus, _onibus, cx - 205, yb_bus)

    # ---------- desenho ----------
    def _renderizar(self):
        rng = random.Random(SEMENTE + 1)
        s = pygame.Surface((LARG_P, len(self.tipos) * FAIXA_P))
        for i, tipo in enumerate(self.tipos):
            r = pygame.Rect(0, i * FAIXA_P, LARG_P, FAIXA_P)
            acima, abaixo = self._vizinho(i - 1), self._vizinho(i + 1)
            if tipo == "grama":
                _base_grama(s, r, rng)
            elif tipo == "cin":
                _base_patio(s, r, rng)
            elif tipo == "calcada":
                _base_calcada(s, r, rng, _pista(acima), _pista(abaixo))
            elif tipo == "rua":
                _base_rua(s, r, rng, acima != "rua", abaixo != "rua", acima == "rua")
            elif tipo == "ciclovia":
                _base_ciclovia(s, r, rng, self.direcoes[i], acima != "ciclovia",
                               acima == "ciclovia", abaixo != "ciclovia")
            elif tipo == "entrada":
                _base_patio(s, r, rng)
            elif tipo == "ponto":
                if abaixo == "ponto":   # pista onde o ônibus para
                    _base_rua(s, r, rng, False, False, False)
                else:                   # calçada do abrigo
                    _base_calcada(s, r, rng, acima == "ponto" or _pista(acima),
                                  _pista(abaixo))
            elif tipo == "chegada":
                _chegada(s, r)
        for _, funcao, args in sorted(self._enfeites, key=lambda e: e[0]):
            funcao(s, *args)

        imagem = pygame.transform.scale(
            s, (LARGURA, len(self.tipos) * ALTURA_FAIXA))
        for faixa in self.faixas:  # imagens prontas substituem o desenho
            if faixa.imagem:
                imagem.blit(faixa.imagem, faixa.rect)
        return imagem


# Fase 1 (a mesma lista usada no AgenteCIncreto.py)
LAYOUT_UFPE = [
    "P", "P", "C", "R", "R", "C", "G", "B", "B", "C",
    "G", "G", "C", "R", "R", "R", "C", "B", "G", "C",
    "R", "R", "C", "G", "B", "C", "G", "C", "I", "I", "E",
]
VELOCIDADES_UFPE = {
    "rua": (3, 1300),       # (velocidade, intervalo entre carros em ms)
    "ciclovia": (2, 1600),  # (velocidade, intervalo entre bicicletas)
}


def fase_ufpe():
    """Fase 1: saindo do CIn até o ponto de ônibus (de baixo para cima)."""
    return Mapa("UFPE", LAYOUT_UFPE, VELOCIDADES_UFPE)
