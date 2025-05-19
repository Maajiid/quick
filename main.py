import pygame
import sys
import random

pygame.init()

# Taille fixe pour pygbag/web
largeur, hauteur = 1000, 600
screen = pygame.display.set_mode((largeur, hauteur))
pygame.display.set_caption('Quick Aim Web')

# Couleurs
blanc = (255, 255, 255)
rouge = (255, 0, 0)
noir = (0, 0, 0)

# Paramètres du jeu
taille_cible = 80
temps_total = 10  # secondes
zone_limite_y = 100

font = pygame.font.SysFont(None, 36)
large_font = pygame.font.SysFont(None, 50)

# Chargement images (prépares les images en 80x80 px avant)
try:
    target_image = pygame.image.load('ci.png')
except:
    # Si pas d'image, on dessine un rond
    target_image = None

try:
    fond_image = pygame.image.load('fond.png')
    fond_image = pygame.transform.scale(fond_image, (largeur, hauteur))
except:
    fond_image = None

class Cible:
    def __init__(self, largeur, hauteur, y, vitesse_max=4):
        self.largeur = largeur
        self.hauteur = hauteur
        self.y = y
        self.taille = taille_cible
        self.x = random.randint(0, largeur - self.taille)
        self.vx = random.choice([-vitesse_max, vitesse_max])
        self.visible = True
        self.cooldown = 1.5
        self.disparition_start = None

    def move(self):
        if not self.visible:
            if pygame.time.get_ticks() - self.disparition_start > self.cooldown * 1000:
                self.visible = True
                self.x = random.randint(0, self.largeur - self.taille)
                self.vx = random.choice([-4, 4])
            return
        self.x += self.vx
        if self.x < 0:
            self.x = 0
            self.vx = -self.vx
        elif self.x > self.largeur - self.taille:
            self.x = self.largeur - self.taille
            self.vx = -self.vx

    def draw(self, screen):
        if not self.visible:
            return
        if target_image:
            img_scaled = pygame.transform.scale(target_image, (self.taille, self.taille))
            screen.blit(img_scaled, (self.x, self.y))
        else:
            pygame.draw.circle(screen, rouge, (self.x + self.taille//2, self.y + self.taille//2), self.taille//2)

    def is_hit(self, pos):
        if not self.visible:
            return False
        mx, my = pos
        return self.x <= mx <= self.x + self.taille and self.y <= my <= self.y + self.taille

    def disappear(self):
        self.visible = False
        self.disparition_start = pygame.time.get_ticks()


def reset_game():
    global score, temps_restant, start_ticks, cibles, game_over
    score = 0
    temps_restant = temps_total
    start_ticks = pygame.time.get_ticks()
    game_over = False
    # Créer 3 cibles sur des lignes différentes
    cibles = [
        Cible(largeur, hauteur, zone_limite_y + i*100) for i in range(3)
    ]

reset_game()
clock = pygame.time.Clock()

game_started = False
meilleur_score = 0
nouveau_record = False
red_screen = False
red_frames = 0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if not game_started:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                game_started = True
                reset_game()
        else:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                touchee = False
                for cible in cibles:
                    if cible.is_hit(pos):
                        score += 1
                        cible.disappear()
                        touchee = True
                        break
                if not touchee and score > 0:
                    score -= 1
                    red_screen = True
                    red_frames = 0

            if event.type == pygame.KEYDOWN and event.key == pygame.K_r and game_over:
                nouveau_record = False
                reset_game()

    screen.fill(noir)
    if fond_image:
        screen.blit(fond_image, (0, 0))

    if not game_started:
        text = large_font.render("Appuie sur 'S' pour démarrer", True, blanc)
        screen.blit(text, text.get_rect(center=(largeur // 2, hauteur // 2)))
    else:
        # Calcul temps restant
        elapsed = (pygame.time.get_ticks() - start_ticks) / 1000
        temps_restant = max(0, int(temps_total - elapsed))

        if temps_restant <= 0:
            game_over = True
            if score > meilleur_score:
                meilleur_score = score
                nouveau_record = True
            game_started = False

        if not game_over:
            # Mouvement et affichage cibles
            for cible in cibles:
                cible.move()
                cible.draw(screen)

            # Affichage score et temps
            score_text = font.render(f"Score : {score}  Temps : {temps_restant}s", True, blanc)
            screen.blit(score_text, (20, 20))

            if red_screen:
                overlay = pygame.Surface((largeur, hauteur))
                overlay.set_alpha(100)
                overlay.fill(rouge)
                screen.blit(overlay, (0, 0))
                red_frames += 1
                if red_frames > 5:
                    red_screen = False
        else:
            # Écran de fin
            fin_text = large_font.render(f"Temps écoulé ! Score : {score}", True, blanc)
            screen.blit(fin_text, fin_text.get_rect(center=(largeur // 2, hauteur // 2 - 50)))

            meilleur_text = font.render(f"Meilleur Score : {meilleur_score}", True, blanc)
            screen.blit(meilleur_text, meilleur_text.get_rect(center=(largeur // 2, hauteur // 2)))

            if nouveau_record:
                rec_text = font.render("NOUVEAU RECORD !", True, rouge)
                screen.blit(rec_text, rec_text.get_rect(center=(largeur // 2, hauteur // 2 + 50)))
                y_restart = hauteur // 2 + 100
            else:
                y_restart = hauteur // 2 + 50

            restart_text = font.render("Appuie sur 'R' pour recommencer", True, blanc)
            screen.blit(restart_text, restart_text.get_rect(center=(largeur // 2, y_restart)))

    pygame.display.flip()
    clock.tick(60)
