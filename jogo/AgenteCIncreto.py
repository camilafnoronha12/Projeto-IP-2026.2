import pygame
pygame.init()
tela=pygame.display.set_mode((1366, 720))
pygame.display.set_caption("janela")
relogio = pygame.time.Clock()
rodando=True
# Personagem: por enquanto um retângulo (x, y, largura, altura)
jogador = pygame.Rect(683, 360, 50, 50)
velocidade = 5
while rodando:# Eventos (fechar janela, teclado, mouse...)
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
    # Movimento com as setas ou WASD
    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
        jogador.x -= velocidade
    if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
        jogador.x += velocidade
    if teclas[pygame.K_UP] or teclas[pygame.K_w]:
        jogador.y -= velocidade
    if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
        jogador.y += velocidade
    # Impede de sair da tela
    jogador.clamp_ip(tela.get_rect())
    # desenhos
    tela.fill((0, 0, 0))  # cor de fundo em RGB
    pygame.draw.rect(tela, (251, 126, 0), jogador)
    pygame.display.flip()
    relogio.tick(60)#limita o jogo a 60fps
pygame.quit()
