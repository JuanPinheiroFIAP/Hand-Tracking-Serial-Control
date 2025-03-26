import cv2
import mediapipe as mp
import serial
import time
import json

arduino = serial.Serial('COM5', 9600, timeout=1)
time.sleep(2)

# Inicializa o Mediapipe Hands
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Inicializa a captura de vídeo
cap = cv2.VideoCapture(0)

def dedos_levantados(hand_landmarks):
    """
    Retorna uma lista de quais dedos estão levantados, incluindo o polegar.
    """
    dedos = []
    
    # Pontos dos dedos (incluindo polegar)
    dedos_ids = [4, 8, 12, 16, 20]

    # Verificando se o polegar está levantado
    if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:  # Polegar
        dedos.append(1)  # Polegar levantado
    else:
        dedos.append(0)  # Polegar abaixado

    # Verificando os outros dedos (indicador, médio, anelar, mindinho)
    for id in dedos_ids[1:]:  # Começando do dedo 8 (indicador)
        if hand_landmarks.landmark[id].y < hand_landmarks.landmark[id - 2].y:
            dedos.append(1)  # Dedo levantado
        else:
            dedos.append(0)  # Dedo abaixado

    return dedos

# Variável para armazenar o último valor enviado
ultimo_valor = -1

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Converte a imagem para RGB (necessário para o Mediapipe)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Processa a imagem para detectar mãos
    results = hands.process(frame_rgb)

    # Se detectar mãos
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Verifica quais dedos estão levantados
            dedos = dedos_levantados(hand_landmarks)

            # Se apenas os dedos indicador e médio estiverem levantados, printa "Número 2"
            if dedos:
                quantidade = dedos.count(1)
                print(f"Temos {quantidade} dedos levantados")

                # Se o valor for diferente do último valor enviado, envia o novo valor
                if quantidade != ultimo_valor:
                    ultimo_valor = quantidade  # Atualiza o último valor
                    pacote = json.dumps({"valor": quantidade}) + "\n"  # Envia o JSON completo com a chave "valor"
                    arduino.write(pacote.encode('utf-8'))
                    print("Enviado:", pacote.strip())

    # Exibe o vídeo com as marcações
    cv2.imshow("Hand Tracking", frame)

    # Pressione 'q' para sair
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libera a captura e fecha as janelas
cap.release()
cv2.destroyAllWindows()
