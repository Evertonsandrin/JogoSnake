import pygame
import random
from db_utils import conectar_bd, criar_tabela, inserir_recorde, obter_melhores_recordes

# Configurações iniciais do Pygame
pygame.init()
pygame.display.set_caption("Jogo da Cobra Branca (Evertinho)")
largura, altura = 1200, 800
tela = pygame.display.set_mode((largura, altura))
relogio = pygame.time.Clock()

# Música de fundo
pygame.mixer.music.load("D:\\Programação\\Python\\JogoSnake\\Data\\Snake8b.mp3")
pygame.mixer.music.play(-1)

# Cores RGB
preto = (0, 0, 0)
branco = (255, 255, 255)
vermelho = (200, 0, 100)
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

def desenhar_comida(comida_x, comida_y):
    pygame.draw.rect(tela, verde, [comida_x, comida_y, tamanho_quadrado, tamanho_quadrado])

def desenhar_cobra(pixels):
    for pixel in pixels:
        pygame.draw.rect(tela, branco, [pixel[0], pixel[1], tamanho_quadrado, tamanho_quadrado])

def desenhar_pontuacao(pontuacao):
    fonte = pygame.font.SysFont("Helvetica", 25)
    texto = fonte.render(f"Pontos: {pontuacao}", True, vermelho)
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

def tela_inicial():
    fonte_grande = pygame.font.Font(None, 100)
    fonte_pequena = pygame.font.Font(None, 50)
    
    texto_grande = fonte_grande.render("Jogo da Cobra Branca", True, branco)
    texto_pequeno = fonte_pequena.render("Para iniciar, pressione qualquer tecla de movimento", True, branco)

    tela.fill(preto)
    tela.blit(texto_grande, (largura // 2 - texto_grande.get_width() // 2, altura // 3))
    tela.blit(texto_pequeno, (largura // 2 - texto_pequeno.get_width() // 2, altura // 2))

    pygame.display.update()
    
    espera_tecla()

def espera_tecla():
    esperando = True
    while esperando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                    esperando = False

def rodar_jogo():
    tela_inicial()

    while True:
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
            tela.fill(preto)

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
            desenhar_comida(comida_x, comida_y)
            desenhar_cobra(pixels)
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

        # Obter e exibir os melhores recordes
        melhores_recordes = obter_melhores_recordes(c)
        exibir_game_over(tamanho_cobra - 1, melhores_recordes)

        # Aguardar a tecla 'R' para reiniciar
        reiniciando = True
        while reiniciando:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_r:
                        reiniciar = True
                        reiniciando = False
                        break

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
        
        tela.fill(preto)
        texto = fonte.render(f"Digite seu nome: {nome}", True, vermelho)
        tela.blit(texto, [largura // 4, altura // 2])
        pygame.display.update()
    
    return nome

def exibir_game_over(pontuacao, melhores_recordes):
    tela.fill(preto)
    fonte_grande = pygame.font.SysFont(None, 100)
    fonte_pequena = pygame.font.SysFont(None, 50)

    # Mensagem de game over à esquerda
    texto_grande = fonte_grande.render("Game Over", True, branco)
    texto_pequeno = fonte_pequena.render(f"Sua pontuação: {pontuacao}", True, branco)
    tela.blit(texto_grande, (largura // 4, altura // 3))
    tela.blit(texto_pequeno, (largura // 4, altura // 2))

    # Recordistas à direita
    texto_recordes = fonte_pequena.render("Melhores Recordes:", True, azul_claro)
    tela.blit(texto_recordes, (3 * largura // 4 - texto_recordes.get_width() // 2, altura // 4))

    linha_y = altura // 4 + 50
    for i, recorde in enumerate(melhores_recordes[:20]):  # Limita a exibição aos 20 melhores resultados
        texto_recorde = fonte_pequena.render(f"{i + 1}. {recorde[0]} - {recorde[1]}", True, azul_claro)
        tela.blit(texto_recorde, (3 * largura // 4 - texto_recorde.get_width() // 2, linha_y))
        linha_y += 50

    # Instrução de reinício à esquerda
    texto_instrucao = fonte_pequena.render("Pressione 'R' para reiniciar", True, branco)
    tela.blit(texto_instrucao, (largura // 4, altura // 2 + 200))

    pygame.display.update()

# Iniciar o jogo
rodar_jogo()

# Fechar a conexão com o banco de dados ao terminar o jogo
conn.close()