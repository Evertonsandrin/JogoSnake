import pygame
import random
from db_utils import conectar_bd, criar_tabela, inserir_recorde, obter_melhores_recordes

# Configurações iniciais
pygame.init()
pygame.display.set_caption("Jogo da Cobra Branca (Evertinho)")
largura, altura = 1200, 800
tela = pygame.display.set_mode((largura, altura))
relogio = pygame.time.Clock()

# Música de fundo
pygame.mixer.music.load("D:\\Programação\\Python\\JogoSnake\\Data\\Snake8b.mp3")
pygame.mixer.music.play(-1)

# Cores RGB
preta = (0, 0, 0)
branca = (255, 255, 255)
vermelha = (200, 0, 100)
verde = (0, 200, 100)
azul_claro = (173, 216, 230)  # Azul claro

# Parâmetros da cobrinha
tamanho_quadrado = 20
velocidade_jogo = 15

# Conectar ao banco de dados SQLite
conn, c = conectar_bd()
criar_tabela(c)

def gerar_comida():
    comida_x = round(random.randrange(0, largura - tamanho_quadrado) / float(tamanho_quadrado)) * tamanho_quadrado
    comida_y = round(random.randrange(0, altura - tamanho_quadrado) / float(tamanho_quadrado)) * tamanho_quadrado
    return comida_x, comida_y

def desenhar_comida(tamanho, comida_x, comida_y):
    pygame.draw.rect(tela, verde, [comida_x, comida_y, tamanho, tamanho])

def desenhar_cobra(tamanho, pixels):
    for pixel in pixels:
        pygame.draw.rect(tela, branca, [pixel[0], pixel[1], tamanho, tamanho])

def desenhar_pontuacao(pontuacao):
    fonte = pygame.font.SysFont("Helvetica", 25)
    texto = fonte.render(f"Pontos: {pontuacao}", True, vermelha)
    tela.blit(texto, [1, 1])

def selecionar_velocidade(tecla, velocidade_atual):
    if tecla == pygame.K_DOWN and velocidade_atual != (0, -tamanho_quadrado):
        return 0, tamanho_quadrado
    elif tecla == pygame.K_UP and velocidade_atual != (0, tamanho_quadrado):
        return 0, -tamanho_quadrado
    elif tecla == pygame.K_LEFT and velocidade_atual != (tamanho_quadrado, 0):
        return -tamanho_quadrado, 0
    elif tecla == pygame.K_RIGHT and velocidade_atual != (-tamanho_quadrado, 0):
        return tamanho_quadrado, 0
    return velocidade_atual

def exibir_game_over(pontuacao, melhores_recordes):
    tela.fill(preta)
    fonte = pygame.font.SysFont("Helvetica", 50)
    fonte_menor = pygame.font.SysFont("Helvetica", 30)

    # Informações do jogo à esquerda
    texto_game_over = fonte.render("Game Over", True, vermelha)
    texto_pontuacao = fonte.render(f"Pontos: {pontuacao}", True, vermelha)
    texto_reiniciar = fonte.render("Pressione R para reiniciar", True, vermelha)
    
    tela.blit(texto_game_over, [largura // 8, altura // 3])
    tela.blit(texto_pontuacao, [largura // 8, altura // 2])
    tela.blit(texto_reiniciar, [largura // 8, altura // 1.2])

    # Tabela de recordes à direita
    texto_recorde = fonte.render("Top 10 Recordes:", True, vermelha)
    tela.blit(texto_recorde, [largura // 1.5, altura // 3])
    
    for i, (nome, pontuacao) in enumerate(melhores_recordes):
        texto_recorde_individual = fonte_menor.render(f"{i+1}. {nome} - {pontuacao}", True, azul_claro)
        tela.blit(texto_recorde_individual, [largura // 1.5, altura // 2.5 + (i * 30)])
    
    pygame.display.update()

def solicitar_nome():
    fonte = pygame.font.SysFont("Helvetica", 50)
    nome = ""
    solicitando_nome = True

    while solicitando_nome:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    solicitando_nome = False
                elif evento.key == pygame.K_BACKSPACE:
                    nome = nome[:-1]
                else:
                    nome += evento.unicode
        
        tela.fill(preta)
        texto = fonte.render(f"Digite seu nome: {nome}", True, vermelha)
        tela.blit(texto, [largura // 4, altura // 2])
        pygame.display.update()
    
    return nome

def rodar_jogo():
    fim_jogo = False
    reiniciar = False

    x = largura / 2
    y = altura / 2

    velocidade_x = 0
    velocidade_y = 0

    tamanho_cobra = 1
    pixels = []

    comida_x, comida_y = gerar_comida()

    while not fim_jogo:
        tela.fill(preta)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                fim_jogo = True
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r and reiniciar:
                    rodar_jogo()
                    return
                velocidade_x, velocidade_y = selecionar_velocidade(evento.key, (velocidade_x, velocidade_y))

        # Atualizar a posição da cobra
        if x < 0 or x >= largura or y < 0 or y >= altura:
            fim_jogo = True

        x += velocidade_x
        y += velocidade_y
        
        # Verifica se a cobra bateu no corpo
        for pixel in pixels[:-1]:
            if pixel == (x, y):
                fim_jogo = True

        pixels.append((x, y))
        if len(pixels) > tamanho_cobra:
            del pixels[0]

        # Desenhar cobra e comida
        desenhar_comida(tamanho_quadrado, comida_x, comida_y)
        desenhar_cobra(tamanho_quadrado, pixels)
        desenhar_pontuacao(tamanho_cobra - 1)

        pygame.display.update()

        # Verifica se a cobra comeu a comida
        if x == comida_x and y == comida_y:
            tamanho_cobra += 1
            comida_x, comida_y = gerar_comida()

        relogio.tick(velocidade_jogo)

    # Solicitar o nome do jogador
    nome = solicitar_nome()
    inserir_recorde(c, conn, nome, tamanho_cobra - 1)

    melhores_recordes = obter_melhores_recordes(c)
    exibir_game_over(tamanho_cobra - 1, melhores_recordes)
    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:
                    rodar_jogo()
                    return

rodar_jogo()

# Fechar a conexão com o banco de dados ao terminar o jogo
conn.close()
