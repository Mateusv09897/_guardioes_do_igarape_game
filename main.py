import os
import random
import pygame
import sys  # Importante para o executável encontrar os arquivos

# =====================================================================
# 1. INICIALIZAÇÃO DO SISTEMA
# =====================================================================
pygame.init()

LARGURA = 800
ALTURA = 600
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Guardião do Igarapé - Versão Windows")

# Paleta de Cores
COR_FUNDO = (28, 135, 212)
COR_TEXTO = (255, 255, 255)
COR_JOGADOR = (46, 204, 113)
COR_LIXO = (231, 76, 60)
COR_INIMIGO = (142, 68, 173)
COR_VIDA = (241, 196, 15)
COR_SOMBRA = (0, 0, 0)
COR_LIXEIRAS = (100, 100, 100)
COR_ALERTA = (255, 100, 100)

FPS = 60
RELOGIO = pygame.time.Clock()

FONTE_HUD = pygame.font.SysFont("arial", 20, bold=True)
FONTE_TITULO = pygame.font.SysFont("arial", 40, bold=True)

# =====================================================================
# 2. GERENCIADOR DE ASSETS (AJUSTADO PARA O EXECUTÁVEL)
# =====================================================================
def carregar_imagem(nome_arquivo, largura, altura, cor_fallback, subpasta="objects"):
    # Verifica se estamos rodando dentro do .exe (congelado)
    if getattr(sys, 'frozen', False):
        caminho_base = sys._MEIPASS
    else:
        caminho_base = os.path.abspath(".")

    caminho = os.path.join(caminho_base, "assets", "sprites", subpasta, nome_arquivo)
    
    if os.path.exists(caminho):
        try:
            img = pygame.image.load(caminho).convert_alpha()
            return pygame.transform.scale(img, (largura, altura))
        except:
            pass
    
    # Fallback caso a imagem não carregue
    sup = pygame.Surface((largura, altura))
    sup.fill(cor_fallback)
    return sup

# Carregamento de Cenários
FUNDO_LIMPO = carregar_imagem("fundo_limpo.png", LARGURA, ALTURA, COR_FUNDO, subpasta="levels")
FUNDO_POLUIDO = carregar_imagem("fundo_poluido.png", LARGURA, ALTURA, COR_FUNDO, subpasta="levels")
CHAO_JOGO = carregar_imagem("chao.png", LARGURA, 60, (100, 50, 0), subpasta="levels")

# =====================================================================
# 3. MAPEAMENTO DE ITENS
# =====================================================================
DICIONARIO_LIXOS = {
    "pet.png": "Plástico", "sacola.png": "Plástico", "copo_plastico.png": "Plástico",
    "canudo.png": "Plástico", "garrafa_plastica.png": "Plástico", "embalagem_plastica.png": "Plástico",
    "embralagem_iorgute.png": "Plástico", "carrinho_de_brinquedo.png": "Plástico",
    "perfume.png": "Vidro", "garrafa_roxa.png": "Vidro", "garrafa_vidro.png": "Vidro", "pote_vidro.png": "Vidro",
    "laranja.png": "Orgânico", "maca.png": "Orgânico", "banana.png": "Orgânico",
    "lata_suco.png": "Metal", "lata_refri.png": "Metal",
    "caderno.png": "Papel", "cigarro.png": "Papel", "copo_porcelana_quebrado.png": "Papel",
}
LISTA_ARQUIVOS_LIXO = list(DICIONARIO_LIXOS.keys())

# =====================================================================
# 4. CLASSES
# =====================================================================
class Lixeira(pygame.sprite.Sprite):
    def __init__(self, nome_arquivo, posicao_x, categoria):
        super().__init__()
        self.categoria = categoria
        self.image = carregar_imagem(nome_arquivo, 60, 70, COR_LIXEIRAS, subpasta="objects")
        self.rect = self.image.get_rect()
        self.rect.centerx = posicao_x
        self.rect.bottom = ALTURA - 55

class MonstroLixo(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.img_idle = carregar_imagem("bossidle.png", 110, 100, COR_INIMIGO, subpasta="enemies")
        self.img_dano = carregar_imagem("bosstakedamage.png", 110, 100, COR_ALERTA, subpasta="enemies")
        self.image = self.img_idle
        self.rect = self.image.get_rect()
        self.rect.centerx = LARGURA // 2
        self.rect.top = 50
        self.velocidade_x = 3
        self.tempo_dano = 0

    def sofrer_dano(self):
        self.image = self.img_dano
        self.tempo_dano = pygame.time.get_ticks() + 500

    def update(self):
        self.rect.x += self.velocidade_x
        if self.rect.left <= 50 or self.rect.right >= LARGURA - 50:
            self.velocidade_x *= -1
        if pygame.time.get_ticks() > self.tempo_dano and self.image == self.img_dano:
            self.image = self.img_idle

class Jogador(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.velocidade = 8
        self.lixo_carregado = None
        self.animacoes = {"espera":[], "direita":[], "esquerda":[], "apanhar":[], "vitoria":[]}
        for i in range(1, 5): self.animacoes["espera"].append(carregar_imagem(f"Espera{i}.png", 80, 80, COR_JOGADOR, subpasta="objects"))
        for i in range(1, 7): self.animacoes["direita"].append(carregar_imagem(f"CorridaDireita{i}.png", 80, 80, COR_JOGADOR, subpasta="objects"))
        for i in range(1, 4): self.animacoes["esquerda"].append(carregar_imagem(f"CorridaEsquerda{i}.png", 80, 80, COR_JOGADOR, subpasta="objects"))
        for i in range(1, 6): self.animacoes["apanhar"].append(carregar_imagem(f"Apanhar{i}.png", 80, 80, COR_JOGADOR, subpasta="objects"))
        for i in range(1, 3): self.animacoes["vitoria"].append(carregar_imagem(f"Vitoria{i}.png", 80, 80, COR_JOGADOR, subpasta="objects"))
        
        self.estado_atual = "espera"
        self.frame_atual = 0.0
        self.velocidade_animacao = 0.25
        self.tempo_acao_especial = 0
        self.image = self.animacoes[self.estado_atual][0]
        self.rect = self.image.get_rect()
        self.rect.centerx = LARGURA // 2
        self.rect.bottom = ALTURA - 55

    def animar_coleta(self):
        self.estado_atual = "apanhar"
        self.frame_atual = 0.0
        self.tempo_acao_especial = pygame.time.get_ticks() + 350

    def animar_vitoria(self):
        self.estado_atual = "vitoria"
        self.frame_atual = 0.0
        self.tempo_acao_especial = pygame.time.get_ticks() + 1200

    def update(self):
        agora = pygame.time.get_ticks()
        teclas = pygame.key.get_pressed()
        if agora > self.tempo_acao_especial:
            if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
                self.rect.x -= self.velocidade
                self.estado_atual = "esquerda"
            elif teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
                self.rect.x += self.velocidade
                self.estado_atual = "direita"
            else:
                self.estado_atual = "espera"
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > LARGURA: self.rect.right = LARGURA
        self.frame_atual += self.velocidade_animacao
        lista_quadros = self.animacoes[self.estado_atual]
        if self.frame_atual >= len(lista_quadros):
            self.frame_atual = 0.0
            if self.estado_atual in ["apanhar", "vitoria"] and agora > self.tempo_acao_especial:
                self.estado_atual = "espera"
        self.image = lista_quadros[int(self.frame_atual)]

class Item(pygame.sprite.Sprite):
    def __init__(self, x_origem, y_origem):
        super().__init__()
        self.arquivo_escolhido = random.choice(LISTA_ARQUIVOS_LIXO)
        self.categoria = DICIONARIO_LIXOS[self.arquivo_escolhido]
        self.image = carregar_imagem(self.arquivo_escolhido, 45, 45, COR_LIXO, subpasta="objects")
        self.rect = self.image.get_rect()
        self.rect.centerx = x_origem
        self.rect.top = y_origem
        self.velocidade_y = random.randint(2, 4)

    def update(self):
        self.rect.y += self.velocidade_y

# =====================================================================
# 5. EXECUÇÃO
# =====================================================================
todos_sprites = pygame.sprite.Group()
grupo_itens = pygame.sprite.Group()
grupo_lixeiras = pygame.sprite.Group()
monstro = MonstroLixo()
todos_sprites.add(monstro)
config_lixeiras = [("lixeira_plastico.png", 100, "Plástico"), ("lixeira_vidro.png", 250, "Vidro"), 
                   ("lixeira_organico.png", 400, "Orgânico"), ("lixeira_metal.png", 550, "Metal"), ("lixeira_papel.png", 700, "Papel")]
for arq, x, cat in config_lixeiras: grupo_lixeiras.add(Lixeira(arq, x, cat))
jogador = Jogador()
todos_sprites.add(jogador)

GERAR_ITEM = pygame.USEREVENT + 1
pygame.time.set_timer(GERAR_ITEM, 1800)

pontuacao, vidas, vida_monstro = 0, 3, 10
rodando, game_over, vitoria_final = True, False, False

def desenhar_texto_hud(texto, x, y, cor=COR_TEXTO):
    sombra = FONTE_HUD.render(texto, True, COR_SOMBRA)
    principal = FONTE_HUD.render(texto, True, cor)
    TELA.blit(sombra, (x+2, y+2))
    TELA.blit(principal, (x, y))

while rodando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT: rodando = False
        if not game_over and not vitoria_final:
            if evento.type == GERAR_ITEM:
                if len(grupo_itens) == 0 and jogador.lixo_carregado is None:
                    novo_item = Item(monstro.rect.centerx, monstro.rect.bottom)
                    todos_sprites.add(novo_item); grupo_itens.add(novo_item)
            if evento.type == pygame.KEYDOWN and evento.key in [pygame.K_SPACE, pygame.K_DOWN] and jogador.lixo_carregado:
                lixeira_attingida = pygame.sprite.spritecollideany(jogador, grupo_lixeiras)
                if lixeira_attingida and lixeira_attingida.categoria == jogador.lixo_carregado["categoria"]:
                    pontuacao += 10; vida_monstro -= 1; monstro.sofrer_dano(); jogador.animar_vitoria()
                    if vida_monstro <= 0: vitoria_final = True
                elif lixeira_attingida:
                    vidas -= 1
                    if vidas <= 0: game_over = True
                jogador.lixo_carregado = None
        else:
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_SPACE:
                pontuacao, vidas, vida_monstro = 0, 3, 10
                game_over = vitoria_final = False
                jogador.lixo_carregado = None
                for s in grupo_itens: s.kill()
                jogador.rect.centerx = LARGURA // 2
                monstro.rect.centerx = LARGURA // 2

    if not game_over and not vitoria_final:
        todos_sprites.update()
        for item in grupo_itens:
            if item.rect.bottom >= ALTURA - 60:
                item.kill(); vidas -= 1
                if vidas <= 0: game_over = True
        for item_coletado in pygame.sprite.spritecollide(jogador, grupo_itens, True):
            if jogador.lixo_carregado is None:
                jogador.lixo_carregado = {"arquivo": item_coletado.arquivo_escolhido, "categoria": item_coletado.categoria}
                jogador.animar_coleta()

    if game_over: TELA.blit(FUNDO_POLUIDO, (0, 0))
    else: TELA.blit(FUNDO_LIMPO, (0, 0))
    TELA.blit(CHAO_JOGO, (0, ALTURA - 60)); grupo_lixeiras.draw(TELA)
    if not game_over and not vitoria_final:
        todos_sprites.draw(TELA)
        desenhar_texto_hud(f"Lixo Coletado: {pontuacao}", 20, 10)
        desenhar_texto_hud(f"Energia Igarapé: {'♥ ' * vidas}", LARGURA - 220, 10, COR_VIDA)
        desenhar_texto_hud(f"Monstro de Lixo: {'█ ' * vida_monstro}", 20, 35, COR_ALERTA)
        if jogador.lixo_carregado: desenhar_texto_hud(f"NA REDE: {jogador.lixo_carregado['categoria'].upper()} -> ESPAÇO/BAIXO!", LARGURA//2 - 200, ALTURA - 25, COR_VIDA)
        else: desenhar_texto_hud("REDE VAZIA -> Aguarde o resíduo!", LARGURA//2 - 150, ALTURA - 25)
    elif vitoria_final or game_over:
        msg = "MONSTRO DERROTADO!" if vitoria_final else "O IGARAPÉ FOI POLUÍDO!"
        txt = FONTE_TITULO.render(msg, True, COR_VIDA if vitoria_final else COR_LIXO)
        TELA.blit(txt, (LARGURA//2 - txt.get_width()//2, ALTURA//2 - 60))
    pygame.display.flip(); RELOGIO.tick(FPS)

pygame.quit()
