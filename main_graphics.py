from tkinter import *
import random as rd


class Game:
    matrice = reception = porte = player = energy_frame = None
    root = main_frame = console = control_image = control = None
    dict_room_coords = {}
    dict_case_coords = {}

    def __init__(self, basic: bool = True, difficulty: float = 1):
        Game.matrice = Game._gen_basic() if basic else Game._gen_random()

        for y in range(len(Game.matrice)):
            for x in range(len(Game.matrice[y])):
                current_case = Game.matrice[y][x]
                if current_case != " ":
                    Game.dict_case_coords["{} {}".format(x, y)] = Case(x, y, current_case)

                if current_case in ["┏", "⍈", "┏", "┣", "┗", "┓", "┫", "┛"]:
                    Game.dict_room_coords["{} {}".format(x, y)] = Room(x, y, current_case)

                if current_case == "x":
                    Game.reception = Room(x, y, current_case)

                elif current_case == "O":
                    Game.porte = Room(x, y, current_case)

        total_pinte = 5
        liste_pinte = []
        while total_pinte != 0:
            new_amount = rd.randint(1, 3 if total_pinte >= 3 else total_pinte)
            liste_pinte.append(new_amount)
            total_pinte -= new_amount

            # Détermination du nombre de monstres vis à vis de la difficulté donnée #

            if not difficulty:  # Si l'utilisateur ne précise pas la difficulté
                n_monster = 5  # 5 monstres de base
            elif difficulty < 1:
                n_monster = int(difficulty * (len(Game.dict_room_coords) - len(liste_pinte)))
            else:  # 1 ou plus ==> Que des monstres et des pintes
                n_monster = len(Game.dict_room_coords) - len(liste_pinte)

            # Choix aléatoire des salles contenant quelque chose #

            list_filled_room_coords = rd.sample(list(Game.dict_room_coords), n_monster + len(liste_pinte))

            # Remplissage de ces salles #
            n = 0
            for i in range(len(list_filled_room_coords)):
                if i == 0:  # Un seul LandLord
                    Game.dict_room_coords[list_filled_room_coords[i]].contenu = LandLord()
                elif i < 0.4 * n_monster:  # 40% du reste des monstres serons des Mad Scientist
                    Game.dict_room_coords[list_filled_room_coords[i]].contenu = MadScientist()
                elif i < n_monster:  # Le reste des monstres seront des Bibendum
                    Game.dict_room_coords[list_filled_room_coords[i]].contenu = Bibendum()
                else:  # Hors monstre ==> Energie définis par liste_pinte
                    Game.dict_room_coords[list_filled_room_coords[i]].contenu = Energy(liste_pinte[n])
                    n += 1

        Game.player = Player()

        # ====== GUI =======

        Game.root = Tk()
        Game.root.title("Fantom Escape")

        Game.main_frame = Frame(Game.root, bg="black", bd=0, height=15, width=50)
        Game.main_frame.pack()

        Game.energy_frame = Frame(Game.main_frame, bg="gray50")
        Game.energy_frame.pack()

        Game.energy = Label(Game.energy_frame, bg="black", fg="white",
                            text="{} pintes d'énergies".format(Game.player.energy))
        Game.energy.pack()

        Game.canvas = Canvas(Game.main_frame,
                             width=len(Game.matrice[0]) * 50,
                             height=len(Game.matrice) * 25,
                             bg="black", bd=0)
        Game.canvas.pack()

        Game.console = Label(Game.main_frame, bg="black", fg="white")
        Game.console.pack(side="left")

        control_image = PhotoImage(file="Ressources/gif/control.gif")
        control = Label(Game.main_frame, text="Controles", image=control_image)
        control.pack(side="right")

        self.show_surroundings()
        Game.root.bind_all("<Key>", self.turn)

        Game.root.mainloop()

    @staticmethod
    def turn(event):
        x = Game.player.x
        y = Game.player.y
        contour_coords = {"{} {}".format(x, y - 1): (("z", "Up", "KP_8"), Game.player.move_up),
                          "{} {}".format(x - 1, y): (("q", "Left", "KP_4"), Game.player.move_left),
                          "{} {}".format(x, y + 1): (("s", "Down", "KP_2"), Game.player.move_down),
                          "{} {}".format(x + 1, y): (("d", "Right", "KP_6"), Game.player.move_right)
                          }
        order = event.keysym
        Game.console["text"] = ""
        for contour_coord in contour_coords:
            if contour_coord in Game.dict_case_coords and order in contour_coords[contour_coord][0]:
                Game.dict_case_coords[Game.player.coords].clear()
                contour_coords[contour_coord][1]()
                Game.show_surroundings()

        for key in Game.player.surrounding_coords:
            if key in Game.dict_room_coords:
                Game.dict_room_coords[key].contenu.signature()

        if Game.player.coords in Game.dict_room_coords:
            Game.dict_room_coords[Game.player.coords].contenu.effect()
            Game.show_surroundings()

        if Game.player.coords == Game.porte.coords:
            Game.win()

        Game.energy["text"] = "{} pintes d'énergies".format(Game.player.energy)

    @staticmethod
    def _gen_basic():
        return [[" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
                [" ", " ", " ", "⌜", "─", "⌝", " ", "O", " ", " ", " "],
                [" ", " ", " ", "|", " ", "|", " ", "|", " ", " ", " "],
                [" ", "┏", "─", "+", "⍈", "+", "⍈", "+", "─", "┓", " "],
                [" ", "┊", " ", "|", " ", "|", " ", "|", " ", "┊", " "],
                [" ", "┣", "─", "+", "⍈", "+", "⍈", "+", "─", "┫", " "],
                [" ", "┊", " ", "|", " ", "|", " ", "|", " ", "┊", " "],
                [" ", "┗", "─", "+", "⍈", "+", "⍈", "⊥", "─", "┛", " "],
                [" ", " ", " ", "|", " ", "|", " ", " ", " ", " ", " "],
                [" ", " ", " ", "⌞", "x", "⌟", " ", " ", " ", " ", " "],
                [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "]]

    @staticmethod
    def show_surroundings():
        Game.canvas.delete("all")
        if Game.player.coords not in Game.dict_room_coords:
            for surounding in Game.player.surrounding_coords:
                if surounding in Game.dict_case_coords:
                    if surounding in Game.dict_room_coords:
                        Game.dict_case_coords[surounding].draw("gray22")
                    Game.dict_case_coords[surounding].draw("gray22")
        Game.dict_case_coords[Game.player.coords].draw()

    @staticmethod
    def show_map():
        for case in Game.dict_case_coords:
            Game.dict_case_coords[case].draw()

    @staticmethod
    def _gen_random():
        pass

    def __repr__(self):
        return "\n".join(["".join(line) for line in Game.matrice])

    @staticmethod
    def win():
        Affiche("Ressources/gif/stairway-to-heaven.gif", "Félicitations, vous êtes arrivés à la porte du Paradis !")
        Game.root.bind_all("<Key>", exit)

    @staticmethod
    def loose():
        Affiche("Ressources/gif/ghost_buster.gif",
                "Tu n'as plus d'énergie et tu erreras désormais à jamais dans les limbes")
        Game.root.bind_all("<Key>", exit)


class Case:
    def __init__(self, x, y, symbole):
        self.x = x
        self.y = y
        self.coords = "{} {}".format(x, y)
        self.type = symbole
        self.color = "white"

    def draw(self, color="white"):
        dict_drawings = {"⍈": self.t_h_room,

                         "x": self.reception,

                         "┏": self.c_tl_room,

                         "┣": self.tri_l_room,

                         "┗": self.c_bl_room,

                         "┓": self.c_tr_room,

                         "┫": self.tri_r_room,

                         "┛": self.c_br_room,

                         "┊": self.v_corridor,

                         "|": self.v_corridor,

                         "⌞": self.c_bl_corridor,

                         "⌟": self.c_br_corridor,

                         "+": self.cross_section,

                         "⌜": self.c_tl_corridor,

                         "─": self.h_corridor,

                         "⌝": self.c_tr_corridor,

                         "⊥": self.tri_b_corridor,

                         "O": self.porte

                         }
        self.color = color
        dict_drawings[self.type]()

    def base_room(self):
        x = self.x * 50 + 25
        y = self.y * 25 + 12.5
        for x_sign in (1, -1):
            for y_sign in (1, -1):
                Game.canvas.create_polygon(x + x_sign * 3, y + y_sign * 17,
                                           x + x_sign * 3, y + y_sign * 15,
                                           x + x_sign * 15, y + y_sign * 15,
                                           x + x_sign * 15, y + y_sign * 3,
                                           x + x_sign * 17, y + y_sign * 3,
                                           x + x_sign * 17, y + y_sign * 17,
                                           fill=self.color, tags=self.coords)

    def h_wall(self, top: bool):
        diff = 32 if top else 0
        x = self.x * 50
        y = self.y * 25 - 12.5
        Game.canvas.create_polygon(x + 22, y + 42 - diff,
                                   x + 28, y + 42 - diff,
                                   x + 28, y + 40 - diff,
                                   x + 22, y + 40 - diff,
                                   fill=self.color, tags=self.coords)

    def v_wall(self, left: bool):
        diff = 32 if left else 0
        x = self.x * 50
        y = self.y * 25 - 12.5
        Game.canvas.create_polygon(x + 42 - diff, y + 28,
                                   x + 42 - diff, y + 22,
                                   x + 40 - diff, y + 22,
                                   x + 40 - diff, y + 28,
                                   fill=self.color, tags=self.coords)

    def h_door(self, top: bool):
        diff = -1 if top else 1

        x = self.x * 50
        y = self.y * 25 + 12.5
        Game.canvas.create_polygon(x + 20, y + diff * 25,
                                   x + 20, y + diff * 17,
                                   x + 30, y + diff * 17,
                                   x + 30, y + diff * 25,
                                   x + 28, y + diff * 25,
                                   x + 28, y + diff * 18,
                                   x + 22, y + diff * 18,
                                   x + 22, y + diff * 25,
                                   fill=self.color, tags=self.coords)

    def v_door(self, left: bool):
        diff = -1 if left else 1

        x = self.x * 50
        y = self.y * 25 - 12.5
        Game.canvas.create_polygon(x + 25 + diff * 25, y + 20,
                                   x + 25 + diff * 17, y + 20,
                                   x + 25 + diff * 17, y + 30,
                                   x + 25 + diff * 25, y + 30,
                                   x + 25 + diff * 25, y + 28,
                                   x + 25 + diff * 18, y + 28,
                                   x + 25 + diff * 18, y + 22,
                                   x + 25 + diff * 25, y + 22,
                                   fill=self.color, tags=self.coords)

    def t_h_room(self):
        self.base_room()
        self.h_wall(top=True)
        self.h_wall(top=False)
        self.v_door(left=False)
        self.v_door(left=True)

    def reception(self):
        self.t_h_room()

        Game.canvas.create_text(self.x * 50 + 25, self.y * 25 + 12.5, text="R", fill=self.color, tags=self.coords)

    def c_tl_room(self):
        self.base_room()
        self.h_wall(top=True)
        self.v_wall(left=True)
        self.h_door(top=False)
        self.v_door(left=False)

    def c_bl_room(self):
        self.base_room()
        self.h_wall(top=False)
        self.v_wall(left=True)
        self.h_door(top=True)
        self.v_door(left=False)

    def c_br_room(self):
        self.base_room()
        self.h_wall(top=False)
        self.v_wall(left=False)
        self.h_door(top=True)
        self.v_door(left=True)

    def c_tr_room(self):
        self.base_room()
        self.h_wall(top=True)
        self.v_wall(left=False)
        self.h_door(top=False)
        self.v_door(left=True)

    def tri_l_room(self):
        self.base_room()
        self.v_wall(left=True)
        self.h_door(top=True)
        self.h_door(top=False)
        self.v_door(left=False)

    def tri_r_room(self):
        self.base_room()
        self.v_wall(left=False)
        self.h_door(top=True)
        self.h_door(top=False)
        self.v_door(left=True)

    def v_corridor(self):
        x = self.x * 50 + 25
        y = self.y * 25 + 6.25
        for diff in [1, -1]:
            Game.canvas.create_polygon(x + diff * 5, y + 12.5,
                                       x + diff * 5, y + 00,
                                       x + diff * 3, y + 00,
                                       x + diff * 3, y + 12.5,
                                       fill=self.color, tags=self.coords)

    def h_corridor(self):
        x = self.x * 50
        y = self.y * 25 + 12.5
        for diff in [1, -1]:
            Game.canvas.create_polygon(x + 50, y + diff * 5,
                                       x + 00, y + diff * 5,
                                       x + 00, y + diff * 3,
                                       x + 50, y + diff * 3,
                                       fill=self.color, tags=self.coords)

    def corner_corridor(self, left: bool, top: bool):
        l = 1 if left else -1
        t = 1 if top else -1

        x = self.x * 50 + 25
        y = self.y * 25 + 12.5
        Game.canvas.create_polygon(x + l * 3, y + t * 25,
                                   x + l * 5, y + t * 25,
                                   x + l * 5, y + t * 5,
                                   x + l * 25, y + t * 5,
                                   x + l * 25, y + t * 3,
                                   x + l * 3, y + t * 3,
                                   fill=self.color, tags=self.coords)
        Game.canvas.create_polygon(x + l * -3, y + t * 25,
                                   x + l * -5, y + t * 25,
                                   x + l * -5, y + t * -5,
                                   x + l * 25, y + t * -5,
                                   x + l * 25, y + t * -3,
                                   x + l * -3, y + t * -3,
                                   fill=self.color, tags=self.coords)

    def c_bl_corridor(self):
        self.corner_corridor(top=False, left=True)

    def c_tl_corridor(self):
        self.corner_corridor(top=True, left=True)

    def c_br_corridor(self):
        self.corner_corridor(top=False, left=False)

    def c_tr_corridor(self):
        self.corner_corridor(top=True, left=False)

    def cross_section(self):
        x = self.x * 50 + 25
        y = self.y * 25 + 12.5
        for x_sign in (1, -1):
            for y_sign in (1, -1):
                Game.canvas.create_polygon(x + x_sign * 3, y + y_sign * 25,
                                           x + x_sign * 3, y + y_sign * 3,
                                           x + x_sign * 25, y + y_sign * 3,
                                           x + x_sign * 25, y + y_sign * 5,
                                           x + x_sign * 5, y + y_sign * 5,
                                           x + x_sign * 5, y + y_sign * 25,
                                           fill=self.color, tags=self.coords)

    def tri_b_corridor(self):
        x = self.x * 50 + 25
        y = self.y * 25 + 12.5
        Game.canvas.create_polygon(x + 25, y + 5,
                                   x - 25, y + 5,
                                   x - 25, y + 3,
                                   x + 25, y + 3,
                                   fill=self.color, tags=self.coords)
        for sign in [1, -1]:
            Game.canvas.create_polygon(x + sign * 3, y - 25,
                                       x + sign * 3, y - 3,
                                       x + sign * 25, y - 3,
                                       x + sign * 25, y - 5,
                                       x + sign * 5, y - 5,
                                       x + sign * 5, y - 25,
                                       fill=self.color, tags=self.coords)

    def porte(self):
        self.base_room()
        self.h_wall(top=True)
        self.v_wall(left=True)
        self.v_wall(left=False)
        self.h_door(top=False)

    def change_color(self, new_color):
        Game.canvas.itemconfig(self.coords, fill=new_color)

    def clear(self):
        Game.canvas.delete(self.coords)


class Contenu:
    def __repr__(self):
        return "Salle vide"

    def effect(self):
        pass

    def signature(self):
        pass


class Room(Case):
    def __init__(self, x, y, symbole, contenu=Contenu()):
        super(Room, self).__init__(x, y, symbole)
        self.contenu = contenu
        Game.dict_case_coords["{} {}".format(x, y)] = self


class Enemy(Contenu):
    pass


class LandLord(Enemy):
    def signature(self):
        Game.console["text"] += "Cling cling\n"

    def effect(self):
        Affiche("Ressources/gif/majordome.gif", "Retourne donc à la Réception mon très cher Gasper !")
        Game.player.move(Game.reception.x, Game.reception.y)

    def __repr__(self):
        return "LandLord"


class MadScientist(Enemy):
    def signature(self):
        Game.console["text"] += "Mwah ah ah !\n"

    def effect(self):
        Affiche("Ressources/gif/Mad_Scientist.gif", "Tu es téléporté dans une salle aléatoire et tu perd 1 énergie")
        Game.player.energy -= 1
        chosen_case = Game.dict_case_coords[rd.choice(list(Game.dict_case_coords))]
        Game.player.move(chosen_case.x, chosen_case.y)

        if chosen_case.coords in Game.dict_room_coords:
            Game.dict_room_coords[chosen_case.coords].contenu.effect()

    def __repr__(self):
        return "MadScientist"


class Bibendum(Enemy):
    def signature(self):
        Game.console["text"] += "Ça sent bon par ici !\n"

    def effect(self):
        Affiche("Ressources/gif/bibendum.gif", "Vous êtes paralysés et perdez 2 énergies")
        Game.player.energy -= 2

    def __repr__(self):
        return "Bibbendum"


class Energy(Contenu):
    def __init__(self, amount):
        self.amount = amount

    def __repr__(self):
        return "{} pintes vertes d'énergie".format(self.amount)

    def effect(self):
        if self.amount:
            Affiche("Ressources/gif/beer.gif", "Vous avez trouver {} pintes d'ectoplasme vert".format(self.amount))
            Game.player.energy += self.amount
            self.amount = 0


class Affiche:
    def __init__(self, file, text):
        self.affiche = Toplevel(Game.root)
        self.frame = Frame(self.affiche, bg="black")
        self.frame.pack()
        self.image = PhotoImage(file=file)

        self.image_label = Label(self.frame, image=self.image)
        self.image_label.pack()
        self.label = Label(self.frame, bg="black", fg="white", text=text, font=("Helvetica", "16"))
        self.label.pack()
        Game.root.bind_all("<Key>", self._close)

    def _close(self, event):
        self.affiche.destroy()
        Game.root.bind_all("<Key>", Game.turn)
        if Game.player.energy <= 0:
            Game.loose()


class Player:

    def __init__(self):
        self.x = Game.reception.x
        self.y = Game.reception.y
        self.energy = 3

    def move(self, x=None, y=None):
        self.x = x if x else self.x
        self.y = y if y else self.y

    def move_up(self):
        self.y -= 1

    def move_down(self):
        self.y += 1

    def move_left(self):
        self.x -= 1

    def move_right(self):
        self.x += 1

    @property
    def coords(self):
        return "{} {}".format(self.x, self.y)

    @property
    def surrounding_coords(self):
        return ["{} {}".format(self.x, self.y - 1),
                "{} {}".format(self.x - 1, self.y),
                "{} {}".format(self.x, self.y + 1),
                "{} {}".format(self.x + 1, self.y)]


if __name__ == "__main__":
    Game()
