"""
mapa.py - Cenário das fases do Agente CIncreto

Cada fase cabe numa tela só (1366 x 720) e é dividida em 10 faixas
horizontais de 72 px: grama, calçada, rua e ciclovia.
A Perna começa na faixa de baixo e precisa chegar na faixa de cima.

O mapa também diz ONDE os inimigos passam: carros nas ruas,
bicicletas nas ciclovias. O AgenteCIncreto.py usa isso para criar as
Faixas de inimigos no lugar certo.
"""

import os
import pygame

LARGURA, ALTURA = 1366, 720
ALTURA_FAIXA = 72  # 720 / 72 = 10 faixas por tela

CAMINHO = os.path.dirname(os.path.abspath(__file__))
PASTA_ASSETS = os.path.join(CAMINHO, "assets", "mapa")  # imagens do cenário

# Cores provisórias de cada tipo de faixa.
CORES = {
    "grama": (70, 150, 70),
    "calcada": (170, 170, 170),
    "rua": (55, 55, 60),
    "ciclovia": (170, 60, 60),
    "chegada": (230, 200, 60),
}

# Quando tiver o desenho de uma faixa, coloque o arquivo em assets/mapa/
# e escreva o nome aqui. Ex.: "rua": "rua.png"
# Se o arquivo não existir, ele continua usando a cor.
IMAGENS = {}

# Qual inimigo passa em cada tipo de faixa (o resto é seguro)
INIMIGO_DA_FAIXA = {
    "rua": "carro",
    "ciclovia": "bicicleta",
}

# Letras usadas para desenhar as fases
LETRAS = {
    "G": "grama",
    "C": "calcada",
    "R": "rua",
    "B": "ciclovia",
    "F": "chegada",
}


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
        if self.imagem:
            tela.blit(self.imagem, self.rect)
            return
        pygame.draw.rect(tela, CORES[self.tipo], self.rect)
        if self.tipo == "rua":  # tracejado branco no meio da rua
            for x in range(0, LARGURA, 80):
                pygame.draw.rect(tela, (230, 230, 230),
                                 (x, self.rect.centery - 2, 40, 4))


class Mapa:
    """Uma fase inteira, montada a partir de uma lista de letras."""

    def __init__(self, nome, layout, velocidades):
        # layout: uma letra por faixa, de CIMA para BAIXO (como aparece na tela)
        self.nome = nome
        self.faixas = []
        for i, letra in enumerate(layout):
            self.faixas.append(FaixaMapa(LETRAS[letra], i * ALTURA_FAIXA))
        self.velocidades = velocidades  # {tipo_de_faixa: (velocidade, intervalo)}

    def desenhar(self, tela):
        for faixa in self.faixas:
            faixa.desenhar(tela)

    def posicao_inicial(self, tamanho_jogador=60):
        """Topleft da Perna no meio da faixa de baixo."""
        ultima = self.faixas[-1].rect
        return (LARGURA // 2 - tamanho_jogador // 2,
                ultima.centery - tamanho_jogador // 2)

    def chegou_no_fim(self, rect_jogador):
        """True quando a Perna entra na faixa de cima (chegada)."""
        return rect_jogador.colliderect(self.faixas[0].rect)

    def faixas_inimigos(self):
        """Lista com (y_centro, direcao, velocidade, intervalo, tipo_inimigo)
        para cada faixa perigosa. A direção vai alternando."""
        resultado = []
        direcao = 1
        for faixa in self.faixas:
            tipo_inimigo = INIMIGO_DA_FAIXA.get(faixa.tipo)
            if tipo_inimigo:
                velocidade, intervalo = self.velocidades[faixa.tipo]
                resultado.append((faixa.rect.centery, direcao,
                                  velocidade, intervalo, tipo_inimigo))
                direcao *= -1
        return resultado


def fase_ufpe():
    """Fase 1: saindo do CIn pelas ruas da UFPE (de cima para baixo)."""
    layout = [
        "F",  # saída da UFPE -> próxima fase
        "C",
        "R",  # avenida
        "R",
        "C",
        "B",  # ciclovia
        "G",
        "B",
        "C",
        "G",  # começo: em frente ao CIn
    ]
    velocidades = {
        "rua": (6, 1300),       # (velocidade, intervalo entre carros em ms)
        "ciclovia": (4, 1600),  # (velocidade, intervalo entre bicicletas)
    }
    return Mapa("UFPE", layout, velocidades)
