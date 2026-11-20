import pygame
pygame.init()
tela=pygame.display.set_mode((800, 600))
pygame.display.set_caption("janela")
relogio = pygame.time.Clock()
rodando=True
while rodando:# Eventos (fechar janela, teclado, mouse...)
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
    tela.fill((30, 30, 40))  # cor de fundo em RGB
    pygame.display.flip()
    relogio.tick(60)#limita o jogo a 60fps
pygame.quit()
