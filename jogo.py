import cv2
import mediapipe as mp

video = cv2.VideoCapture('pedra-papel-tesoura.mp4')
mp_drawing = mp.solutions.drawing_utils
# estilos para tracar linhas e formas
mp_drawing_styles = mp.solutions.drawing_styles
# detectar as mãos
mp_hands = mp.solutions.hands

# identificar os gestos das maos
def obterGestoDaMao(hand_landmarks):
    landmarks = hand_landmarks.landmark

    # calculo da distância entre os dedos
    dist1 = ((landmarks[8].x - landmarks[12].x)**2 +
             (landmarks[8].y - landmarks[12].y)**2)**0.5
    dist2 = ((landmarks[8].x - landmarks[4].x)**2 +
             (landmarks[8].y - landmarks[4].y)**2)**0.5

    # verifica se é  pedra, papel ou tesoura
    if dist1 < 0.04 and dist2 < 0.04:
        return "pedra"
    elif dist1 > 0.06 and dist2 > 0.06:
        return "tesoura"
    else:
        return "papel"


# desenha as linhas e os pontos nas maos
def desenharLinhasMao(mhl):
    for hand_landmarks in mhl:
        mp_drawing.draw_landmarks(
            img,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS,
            mp_drawing_styles.get_default_hand_landmarks_style(),
            mp_drawing_styles.get_default_hand_connections_style()
        )


# identifica a mao do primeiro e do segundo jogador
def detectarMaosJogadores(mhl):
    primeiraMao, segundaMao = mhl
    # menor valor de X da primeira mao detectada
    minMao1 = min(list(
        map(lambda l: l.x, primeiraMao.landmark)))
    # menor valor de X da segunda mao detectada
    minMao2 = min(list(
        map(lambda l: l.x, segundaMao.landmark)))

    # a primeira mão é a que inicia na menor posição de X na tela
    maoPrimeiroJogador = primeiraMao if minMao1 < minMao2 else segundaMao
    maoSegundoJogador = segundaMao if minMao1 < minMao2 else primeiraMao

    return maoPrimeiroJogador, maoSegundoJogador


# define o vencedor
def definirVencedor(gestoUm, gestoDois):
    if gestoUm == gestoDois:
        return 0
    elif gestoUm == "papel":
        return 1 if gestoDois == "pedra" else 2
    elif gestoUm == "pedra":
        return 1 if gestoDois == "tesoura" else 2
    elif gestoUm == "tesoura":
        return 1 if gestoDois == "papel" else 2


gestoPrimeiroJogador = None
gestoSegundoJogador = None
jogadorVencedor = None  # vencedor
scores = [0, 0]

# detecta as mãos a partir de imagens
hands = mp_hands.Hands(
    model_complexity=0, min_detection_confidence=0.5, min_tracking_confidence=0.5)

while True:
    success, img = video.read()

    # quando terminar o video encerra o loop
    if not success:
        break

    # recebe uma imagem e retorna informações como a posição e orientação das mãos
    posicao = hands.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    # lista dos pontos de referencia das mãos detectadas
    mhl = posicao.multi_hand_landmarks

    # se nenhuma mao for detectada ou diferente de duas o loop é pulado
    if not mhl or len(mhl) != 2:
        continue

    desenharLinhasMao(mhl)

    maoPrimeiroJogador, maoSegundoJogador = detectarMaosJogadores(mhl)

    # verifica quem venceu em todas as rodadas
    novoGesto1 = obterGestoDaMao(maoPrimeiroJogador)
    novoGesto2 = obterGestoDaMao(maoSegundoJogador)

    if (novoGesto1 != gestoPrimeiroJogador or novoGesto2 != gestoSegundoJogador):
        gestoPrimeiroJogador = novoGesto1
        gestoSegundoJogador = novoGesto2

        jogadorVencedor = definirVencedor(
            gestoPrimeiroJogador, gestoSegundoJogador)

        if jogadorVencedor == 1:
            scores[0] += 1
        elif jogadorVencedor == 2:
            scores[1] += 1

        resultadoRodada = "Empate" if jogadorVencedor == 0 else f"Jogador {jogadorVencedor} venceu"
        print(f"{gestoPrimeiroJogador} x {gestoSegundoJogador} = {resultadoRodada}")

    # exibindo os textos na tela
    font = cv2.FONT_HERSHEY_COMPLEX

    # exibindo o placar
    textoResultado = f"{scores[0]} x {scores[1]}"
    tamanhoResultado, _ = cv2.getTextSize(textoResultado, font, 5, 3)
    cv2.putText(img, textoResultado, [(img.shape[1] - tamanhoResultado[0]) // 1, 50], font,
                2, (255, 0, 0), 6)

    # exibindo o resultado
    resultado, _ = cv2.getTextSize(resultadoRodada, font, 2, 2)
    cv2.putText(img, resultadoRodada, [(img.shape[1] - resultado[0]) // 2, img.shape[0] - resultado[1]], font,
                2, (255, 0, 0), 2)

    # exibindo as jogadas do primeiro jogador
    textoJogador1 = "Jogador 1"
    tamanhoJogador1, _ = cv2.getTextSize(textoJogador1, font, 2, 2)
    cv2.putText(img, textoJogador1, (50, img.shape[0] // 2 - tamanhoJogador1[1]),
                font, 1.2, (255, 0, 0), 2)
    cv2.putText(img, gestoPrimeiroJogador, (50, img.shape[0] // 2 - tamanhoJogador1[1] + 70),
                font, 2, (255, 0, 0), 2)

    # exibindo as jogadas do segundo jogador
    textoJogador2 = "Jogador 2"
    tamanhoJogador2, _ = cv2.getTextSize(
        textoJogador2, font, 2, 2)
    cv2.putText(img, textoJogador2, (img.shape[1] - tamanhoJogador2[0], img.shape[0] // 2 - tamanhoJogador2[1]),
                font, 1.2, (255, 0, 0), 2)
    cv2.putText(img, gestoSegundoJogador, (img.shape[1] - tamanhoJogador2[0], img.shape[0] // 2 - tamanhoJogador2[1] + 70),
                font, 2, (255, 0, 0), 2)

    # cria uma janela
    cv2.namedWindow('Pedra, papel e tesoura', cv2.WINDOW_NORMAL)
    cv2.imshow('Pedra, papel e tesoura', img)
    cv2.waitKey(10)

video.release()
cv2.destroyAllWindows()