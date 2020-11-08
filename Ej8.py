import random as rd
import math as mt


#PREGUNTAR BIEN QUE ES LO DE MOVIMIENTO SIN RESTRICCIONES

class Persona:

    #tipo_de_persona: "A","B" o "C"
    #esta_enfermo: bool
    def __init__(self, tipo_de_persona, esta_enfermo):
        instantes = {"A":1, "B":2, "C":4}
        self._instantes_de_espera = instantes[tipo_de_persona]
        self._instantes_esperados = 0
        self._esta_enfermo = esta_enfermo
        self._estuvo_enfermo = False
        self.turnos_enfermo = 0

    def esta_enfermo(self):
        return _esta_enfermo

    #Hace un update del estado de la persona e indica si se debe mover o no
    #Hace el chequeo de si se debe curar
    def intentar_moverse(self, max_turnos_enfermo, probabilidad_de_cura):
        self._instantes_esperados += 1

        if self._esta_enfermo:
            self.turnos_enfermo += 1
            if (self.turnos_enfermo >= max_turnos_enfermo) and \
               (rd.uniform(0, 1) <= probabilidad_de_cura):
                self.turnos_enfermo = 0
                self.esta_enfermo = False

        if self._instantes_esperados == self._instantes_de_espera:
            self._instantes_esperados = 0
            return True

        return False

    def intentar_contagiar(self, probabilidad, hay_recontagio):
        if (not self._estuvo_enfermo) or (hay_recontagio):
            if rd.uniform(0, 1) <= probabilidad:
                self._esta_enfermo = True
                self._estuvo_enfermo = True



#ver si agregamos parametros para generar poblacion random
def generar_region():
    region = []
    for i in range(250):
        region.append([])
        for j in range(250):
            region[i].append(None)
    return region


def _tipo_de_persona_random(cantidades):
    cantidad_actual = cantidades["A"] + cantidades["B"] + cantidades["C"]
    rand_num = #random % cantidad_actual

#Genera personas en la matriz con las proporciones pedidas por el enunciado
# 10 <= cantidad_de_gente <= 250 * 250
def poblar_region(region, cantidad_de_gente):
    cupos_restantes = cantidad_de_gente
    cantidad_A = int(cantidad_de_gente * 0.7)
    cantidad_B = int(cantidad_de_gente * 0.2)
    cupos_restantes -= (cantidad_A + cantidad_B)
    cantidades = {"A":cantidad_A, "B":cantidad_B, "C":cupos_restantes}



def posicion_es_valida(region, pos_x, pos_y):
    return (pos_x >= 0) and (pos_x < len(region)) and (pos_y >= 0) \
            and (pos_y < len(region[0])):


#Variables globales generales para la configuracion
probabilidad_de_contagio = 0.65
hay_recontagio = False


#funcion para contagiar a la gente cercana al contagiado, recibe el mapa (region) y posicion del contagiado
def contagiar_cercanos(region, pos_persona_contagiada):
    k = -1
    for i in range(-5, 6):
        k += 2 if i < 1 else k -= 2
        limite_j = mt.floor(k/2)
        for j in range(-limite_j, limite_j + 1):
            pos_x = pos_persona_contagiada[0] + i
            pos_y = pos_persona_contagiada[1] + j
            if posicion_es_valida(region, pos_x, pos_y):
                region[pos_x][pos_y].intentar_contagiar(probabilidad_de_contagio, hay_recontagio)





                    - - - - - - - - - - -
                    - - - - - + - - - - -
                    - - - - + + + - - - -
                    - - - + + + + + - - -
                    - - + + + + + + + - -
                    - + + + + + + + + + -
                    + + + + + / + + + + +
                    - + + + + + + + + + -
                    - - + + + + + + + - -
                    - - - + + + + + - - -
                    - - - - + + + - - - -
                    - - - - - + - - - - -
                    - - - - - - - - - - -
