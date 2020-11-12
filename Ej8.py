import random as rd
import math as mt


#PREGUNTAR BIEN QUE ES LO DE MOVIMIENTO SIN RESTRICCIONES
#PREGUNTAR SI EL CAMINO ALEATORIO ESTA PREDEFINIDO O SI SE DECIDE EN CADA ESTADO

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
        self.turnos_enfermo = 0
        self.se_contagio_este_turno = False

    def puede_contagiar(self):
        return _esta_enfermo and (not se_contagio_este_turno)

    #Hace un update del estado de la persona e indica si se debe mover o no
    #Hace el chequeo de si se debe curar
    def intentar_moverse(self, min_turnos_enfermo_chance_sanar, probabilidad_de_cura):
        self.se_contagio_este_turno = False
        self._instantes_esperados += 1

        if self._esta_enfermo:
            self.turnos_enfermo += 1
            if (self.turnos_enfermo >= min_turnos_enfermo_chance_sanar) and \
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
def _generar_region():
    region = []
    for i in range(250):
        region.append([])
        for j in range(250):
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
    return Persona(tipo, esta_enferma)

def _posicion_no_ocupada(region):
    i, j = rd.randint(1, len(region) - 1), rd.randint(1, len(region[0]) - 1)
    while(not (region[i][j] is None)):
        i, j = rd.randint(1, len(region) - 1), rd.randint(1, len(region[0]) - 1)
    return i, j


def _generar_personas(cantidades, proporcion_contagiados, proporcion_caminantes):
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
    return _generar_personas(cantidades, int(cantidad_de_gente * 0.03), proporcion_caminantes)

def posicion_es_valida(region, pos_x, pos_y):
    return (pos_x >= 0) and (pos_x < len(region)) and (pos_y >= 0) \
            and (pos_y < len(region[0])):


#Variables globales generales para la configuracion
probabilidad_de_contagio = 0.65
hay_recontagio = False
prob_moverse_derecha = 0.7
prob_moverse_arriba = 0.6

#funcion para contagiar a la gente cercana al contagiado, recibe el mapa (region) y posicion del contagiado
def contagiar_cercanos(region, pos_persona_contagiada):
    global probabilidad_de_contagio
    global hay_recontagio
    k = -1
    for i in range(-5, 6):
        k += 2 if i < 1 else k -= 2
        limite_j = mt.floor(k/2)
        for j in range(-limite_j, limite_j + 1):
            pos_x = pos_persona_contagiada[0] + i
            pos_y = pos_persona_contagiada[1] + j
            if (posicion_es_valida(region, pos_x, pos_y)) and (region[pos_x][pos_y] is not None):
                region[pos_x][pos_y].intentar_contagiar(probabilidad_de_contagio, hay_recontagio)

def posicion_esta_libre(region, posicion):
    return region[posicion[0]][posicion[1]] is not None

def actualizar_probabilidad_movimiento(region, posicion):
    global prob_moverse_arriba
    global prob_moverse_derecha
    lim_i = len(region) - 1
    lim_j = len(region[0]) - 1

    if (posicion[0] == 0) or (posicion[1] == lim_i):
        prob_moverse_arriba = 1 - prob_moverse_arriba

    if ( (posicion[0] == 0) and (posicion[1] == 0) ) or ( (posicion[0] == 0) and (posicion[1] == lim_i) )

def mover_persona(region, persona):
    global prob_moverse_arriba
    global prob_moverse_derecha
    if rd.uniform(0, 1) < 0.5: #Se mueve horizontalmente

        if (rd.uniform(0, 1) < prob_moverse_derecha) and (posicion_esta_libre(region, (persona[1][0] + 1, persona[1][1]))):
            persona[1] = (persona[1][0] + 1, persona[1][1])
        elif posicion_esta_libre(region, (persona[1][0] - 1, persona[1][1])):
            persona[1] = (persona[1][0] - 1, persona[1][1])

    else: #Se mueve verticalmente

        if (rd.uniform(0, 1) < prob_moverse_arriba) and (posicion_esta_libre(region, (persona[1][0], persona[1][1] - 1))):
            persona[1] = (persona[1][0], persona[1][1] - 1)
        elif posicion_esta_libre(region, (persona[1][0], persona[1][1] + 1)):
            persona[1] = (persona[1][0], persona[1][1] + 1)

    actualizar_probabilidad_movimiento(region, persona[1])





#N: cant de personas
#alfa: instantes de tiempo minimos para que una persona enferma empiece a tener chance de sanar en cada siguiente instante de tiempo
#beta: probabilidad de sanar
#T: instante de tiempo en el que la probabilidad de contagio se reduce un 15%
def main(N, alfa, beta, T):
    region = generar_region() #Genero el array
    cantidad_de_gente = 100
    personas = poblar_region(region, cantidad_de_gente) #Me mete en la region las personitas generadas
    #Las personas es una lista donde cada elemento es una lista con una persona y una tupla con las coordenadas
    for persona in personas:

        if persona[0].puede_contagiar():
            contagiar_cercanos(region, persona[1])

        if persona[0].intentar_moverse(alfa, beta):
            mover_persona(region, persona)








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
