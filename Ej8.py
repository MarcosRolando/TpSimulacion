import random as rd
import math as mt
import os
import time as tm
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np


const_proporcion_contagiados = 0.03
const_probabilidad_inicial_contagio = 0.65
const_probabilidad_final_contagio = 0.15
const_instantes_de_tiempo = 5000
const_tamanio_matriz = 250

class Persona:

    #tipo_de_persona: "A","B" o "C"
    #esta_enfermo: bool
    #se_mueve: bool
    def __init__(self, tipo_de_persona, esta_enfermo, se_mueve):
        instantes = {"A":1, "B":2, "C":4}
        if se_mueve:
            self._instantes_de_espera = instantes[tipo_de_persona]
        else:
            self._instantes_de_espera = mt.inf
        self._instantes_esperados = 0
        self._esta_enfermo = esta_enfermo
        self._estuvo_enfermo = False
        self._turnos_enfermo = 0
        self._se_contagio_este_turno = False
        self._prob_moverse_derecha = rd.uniform(0.25, 0.75)
        self._prob_moverse_arriba = rd.uniform(0.25, 0.75)

    def puede_contagiar(self):
        return (self._esta_enfermo and (not self._se_contagio_este_turno))

    #Hace un update del estado de la persona e indica si se debe mover o no
    #Hace el chequeo de si se debe curar
    def intentar_moverse(self, min_turnos_enfermo_chance_sanar, probabilidad_de_cura):
        self._instantes_esperados += 1

        if (self._esta_enfermo and (not self._se_contagio_este_turno)):
            self._turnos_enfermo += 1

            if (self._turnos_enfermo >= min_turnos_enfermo_chance_sanar) and \
               (rd.uniform(0, 1) <= probabilidad_de_cura):
                self._turnos_enfermo = 0
                self._esta_enfermo = False

        self._se_contagio_este_turno = False
        if self._instantes_esperados == self._instantes_de_espera:
            self._instantes_esperados = 0
            return True

        return False

    def intentar_contagiar(self, probabilidad, hay_recontagio):
        if ((not self._esta_enfermo) and ((not self._estuvo_enfermo) or (hay_recontagio))):
            if rd.uniform(0, 1) <= probabilidad:
                self._esta_enfermo = True
                self._estuvo_enfermo = True
                self._turnos_enfermo = 0
                self._se_contagio_este_turno = True


#ver si agregamos parametros para generar poblacion random
def generar_region(filas, columnas):
    region = []
    for i in range(filas):
        region.append([])
        for j in range(columnas):
            region[i].append(None)
    return region

#Retorna una persona aleatoria de todas las personas que faltan generar, resta
#1 a la cantidad de personas que falta generar para el tipo de persona generado
#cantidades: cantidad que falta generar de cada tipo de persona
#esta_enferma: bool
#se_mueve: bool
def _generar_persona_random(cantidades, esta_enferma, se_mueve):
    cantidad_actual = cantidades["A"] + cantidades["B"] + cantidades["C"]
    rand_num = rd.randint(1, cantidad_actual)
    tipo = 0

    if (rand_num <= cantidades["A"]):
        tipo = "A"
    elif ((rand_num > cantidades["A"]) and (rand_num <= cantidades["A"] + cantidades["B"])):
        tipo = "B"
    else:
        tipo = "C"

    cantidades[tipo] -= 1
    return Persona(tipo, esta_enferma, se_mueve)

def _posicion_no_ocupada(region):
    i, j = rd.randint(1, len(region) - 1), rd.randint(1, len(region[0]) - 1)
    while(not (region[i][j] is None)):
        i, j = rd.randint(1, len(region) - 1), rd.randint(1, len(region[0]) - 1)
    return i, j


def _generar_personas(region, cantidades, proporcion_contagiados, proporcion_caminantes):
    lista_personas = []
    contagiados_generados = 0
    caminantes_generados = 0
    cantidad_de_gente = cantidades["A"] + cantidades["B"] + cantidades["C"]
    caminantes_a_generar = int(cantidad_de_gente * proporcion_caminantes)
    contagiados_totales = int(cantidad_de_gente * proporcion_contagiados)

    probabilidad_caminante = proporcion_caminantes
    probabilidad_contagiado = proporcion_contagiados
    for k in range(cantidad_de_gente):
        #Esto de se_mueve y esta_contagiado esta copiado y pegado porque python
        #no tiene punteros asique no puedo tocar las variables adentro de una funcion
        #Lo que hace esta parte es asegurarse de que tanto el estado de contagiado
        #como el de caminante se distribuya con la probabilidad que deriva de la proporcion
        #pedida, para evitar que se favorezca alguna combinacion de (se_mueve, esta_contagiado)
        se_mueve = rd.uniform(0, 1) <= probabilidad_caminante
        if (se_mueve):
            caminantes_generados += 1
        if (caminantes_generados == caminantes_a_generar):
            probabilidad_caminante = -1
        elif ((caminantes_a_generar - caminantes_generados) == (cantidad_de_gente - k - 1)):
            probabilidad_caminante = 1
        esta_contagiado = rd.uniform(0, 1) <= probabilidad_contagiado
        if (esta_contagiado):
            contagiados_generados += 1
        if (contagiados_generados == contagiados_totales):
            probabilidad_contagiado = -1
        elif ((contagiados_totales - contagiados_generados) == (cantidad_de_gente - k - 1)):
            probabilidad_contagiado = 1
        persona = _generar_persona_random(cantidades, esta_contagiado, se_mueve)
        i,j = _posicion_no_ocupada(region)
        lista_personas.append([persona, (i, j)])
        region[i][j] = persona
    return lista_personas


#Genera personas en la matriz con las proporciones pedidas por el enunciado
# 10 <= cantidad_de_gente <= 250 * 250 para que funcionen bien las proporciones
def poblar_region(region, cantidad_de_gente, proporcion_caminantes):
    cupos_restantes = cantidad_de_gente
    cantidad_A = int(cantidad_de_gente * 0.7)
    cantidad_B = int(cantidad_de_gente * 0.2)
    cupos_restantes -= (cantidad_A + cantidad_B)
    cantidades = {"A":cantidad_A, "B":cantidad_B, "C":cupos_restantes}
    return _generar_personas(region, cantidades, const_proporcion_contagiados, proporcion_caminantes)


def posicion_es_valida(region, pos_x, pos_y):
    return (pos_x >= 0) and (pos_x < len(region)) and (pos_y >= 0) \
            and (pos_y < len(region[0]))


#funcion para contagiar a la gente cercana al contagiado, recibe el mapa (region) y posicion del contagiado
def contagiar_cercanos(region, pos_persona_contagiada, probabilidad_de_contagio, hay_recontagio):
    #global probabilidad_de_contagio
    #global hay_recontagio
    k = -1
    for i in range(-4, 5):
        if i < 1:
            k += 2
        else:
            k -= 2
        limite_j = mt.floor(k/2)
        for j in range(-limite_j, limite_j + 1):
            pos_x = pos_persona_contagiada[0] + i
            pos_y = pos_persona_contagiada[1] + j
            if (posicion_es_valida(region, pos_x, pos_y)) and (region[pos_x][pos_y] is not None):
                region[pos_x][pos_y].intentar_contagiar(probabilidad_de_contagio, hay_recontagio)

def posicion_esta_libre(region, posicion):
    return region[posicion[0]][posicion[1]] is None

def actualizar_probabilidad_movimiento(region, posicion, persona):
    lim_i = len(region) - 1
    lim_j = len(region[0]) - 1

    if (posicion[0] == 0) or (posicion[0] == lim_i):
        persona._prob_moverse_arriba = 1 - persona._prob_moverse_arriba

    if (posicion[1] == 0) or (posicion[1] == lim_j):
        persona._prob_moverse_derecha = 1 - persona._prob_moverse_derecha

def mover_persona(region, persona):
    anterior_pos = persona[1]
    logro_moverse = False

    if rd.uniform(0, 1) < 0.5: #Se mueve horizontalmente

        if (rd.uniform(0, 1) < persona[0]._prob_moverse_derecha) and (posicion_es_valida(region, anterior_pos[0], anterior_pos[1] + 1)) \
            and (posicion_esta_libre(region, (anterior_pos[0], anterior_pos[1] + 1))):

            persona[1] = (anterior_pos[0], anterior_pos[1] + 1)
            logro_moverse = True

        elif (posicion_es_valida(region, anterior_pos[0], anterior_pos[1] - 1)) \
                and (posicion_esta_libre(region, (anterior_pos[0], anterior_pos[1] - 1))):

            persona[1] = (anterior_pos[0], anterior_pos[1] - 1)
            logro_moverse = True

    else: #Se mueve verticalmente

        if (rd.uniform(0, 1) < persona[0]._prob_moverse_arriba) and (posicion_es_valida(region, anterior_pos[0] - 1, anterior_pos[1])) \
            and (posicion_esta_libre(region, (anterior_pos[0] - 1, anterior_pos[1]))):

            persona[1] = (anterior_pos[0] - 1, anterior_pos[1])
            logro_moverse = True

        elif (posicion_es_valida(region, anterior_pos[0] + 1, anterior_pos[1])) \
            and (posicion_esta_libre(region, (anterior_pos[0] + 1, anterior_pos[1]))):

            persona[1] = (anterior_pos[0] + 1, anterior_pos[1])
            logro_moverse = True

    if logro_moverse:
        region[persona[1][0]][persona[1][1]] = persona[0]
        region[anterior_pos[0]][anterior_pos[1]] = None

    actualizar_probabilidad_movimiento(region, persona[1], persona[0])

def obtener_contagiados_y_sanos(lista_personas):
    contagiados = 0
    sanos = 0
    for persona in lista_personas:
        if (persona[0].puede_contagiar()):
            contagiados += 1
        else:
            sanos += 1
    return contagiados, sanos


def generar_graficos(lista_instantes, lista_contagiados, lista_sanos):
    plt.close()
    #plt.clf()
    plt.plot(lista_instantes, lista_contagiados)
    plt.xlabel("Tiempo")
    plt.ylabel("Cantidad contagiados")
    plt.title("Contagiados en funcion del tiempo")
    plt.savefig("Contagiados en funcion del tiempo.png")
    plt.clf()
    plt.plot(lista_instantes, lista_sanos)
    plt.xlabel("Tiempo")
    plt.ylabel("Cantidad sanos")
    plt.title("Sanos en funcion del tiempo")
    plt.savefig("Sanos en funcion del tiempo.png")


class Simulacion:

    def __init__(self, N, alfa, beta, T, hay_recontagio, filas, columnas):
        self.proporcion_caminantes = 1
        self.filas = filas
        self.columnas = columnas
        self.region = generar_region(filas, columnas) #Genero el array
        self.personas = poblar_region(self.region, N, self.proporcion_caminantes) #Me mete en la region las personitas generadas
        self.alfa = alfa
        self.beta = beta
        self.hay_recontagio = hay_recontagio
        self.probabilidad_de_contagio = const_probabilidad_inicial_contagio
        self.T = T
        self.lista_instantes = []
        self.lista_contagiados = []
        self.lista_sanos = []
        self.instantes_pasados = 0
        #Las personas es una lista donde cada elemento es una lista con una persona y una tupla con las coordenadas

    def datos_personas(self):
        posicion_x = []
        posicion_y = []
        estado = []

        for persona in self.personas:
            posicion_y.append( (persona[1][0] + 0.5 - mt.floor(self.filas / 250)) / (self.filas / 250) ) #Centro las posiciones en 0 ya que asi se maneja el grafico
            posicion_x.append( (persona[1][1] + 0.5 - mt.floor(self.columnas / 250)) / (self.columnas / 250) ) #Centro las posiciones en 0 ya que asi se maneja el grafico
            if persona[0].puede_contagiar(): #el + 0.5 es solo para ajustar un poco la posicion para que no se solape con el rectangulo del dibujo
                estado.append('red')
            else:
                estado.append('green')

        return posicion_x, posicion_y, estado

    def siguiente_instante(self):

        self.lista_instantes.append(self.instantes_pasados)
        contagiados, sanos = obtener_contagiados_y_sanos(self.personas)
        self.lista_contagiados.append(contagiados)
        self.lista_sanos.append(sanos)

        if (self.instantes_pasados == self.T):
            self.probabilidad_de_contagio = const_probabilidad_final_contagio

        for persona in self.personas:

            if persona[0].puede_contagiar():
                contagiar_cercanos(self.region, persona[1], self.probabilidad_de_contagio, self.hay_recontagio)

            if persona[0].intentar_moverse(self.alfa, self.beta):
                mover_persona(self.region, persona)

        self.instantes_pasados += 1

    def simular_pandemia(self): #funcion principal
        #------------------------------------------------------------
        # set up figure and animation
        #plt.clf()
        fig = plt.figure()
        fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
        ax = fig.add_subplot(111, aspect='equal') #equal pone los ejes

        personas = plt.scatter([], [])

        # rect es el marco de la region
        rect = plt.Rectangle([0, 0], 250, 250, ec='none', lw=1, fc='none')
        ax.add_patch(rect)

        def init():
            nonlocal rect, personas
            datos_personas = self.datos_personas() #retorna tres listas, la primera tiene las posiciones de fila (x), la segunda las de columnas (y) y la tercera el estado
            personas = plt.scatter(datos_personas[0], datos_personas[1], c=datos_personas[2])
            rect.set_edgecolor('black')
            return personas, rect

        def animate(i):
            nonlocal rect, ax, fig, personas
            self.siguiente_instante()

            ms = int(fig.dpi * 2 * 2 * fig.get_figwidth()
                     / np.diff(ax.get_xbound())[0])

            # update pieces of the animation
            rect.set_edgecolor('black')
            datos_personas = self.datos_personas() #retorna tres listas, la primera tiene las posiciones de fila (x), la segunda las de columnas (y) y la tercera el estado
            personas.remove() #esto es para que el video quede bien, sin superposicion de imagenes. basicamente borro el anterior scatterplot
            personas = plt.scatter(datos_personas[0], datos_personas[1], c=datos_personas[2], s=ms)
            return personas, rect

        ani = animation.FuncAnimation(fig, animate, interval=1, blit=True, init_func=init, frames=const_instantes_de_tiempo, repeat=False)


        # save the animation as an mp4.  This requires ffmpeg or mencoder to be
        # installed.  The extra_args ensure that the x264 codec is used, so that
        # the video can be embedded in html5.  You may need to adjust this for
        # your system: for more information, see
        # http://matplotlib.sourceforge.net/api/animation_api.html
        ani.save('particle_box.mp4', fps=60)
        generar_graficos(self.lista_instantes, self.lista_contagiados, self.lista_sanos)


simu = Simulacion(200, 2000, 0.9, 1500, True, filas=250, columnas=250)
simu.simular_pandemia()

