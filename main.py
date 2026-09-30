import cv2
import mediapipe as mp
import time
import winsound
import json
from vision.angles import calcular_angulo

# Configuración estándar de MediaPipe
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

def main():
    with open('ejercicios/ejercicios.json', 'r', encoding='utf-8') as f:
        datos_ejercicios = json.load(f)
    
    reto_actual = datos_ejercicios["estiramiento_brazo_izquierdo"]
    tiempo_objetivo = reto_actual["hold_time_seconds"]
    rango_min, rango_max = reto_actual["rango_esperado"]
    p1_name, p2_name, p3_name = reto_actual["puntos"]

    cap = cv2.VideoCapture(0)
    print("Iniciando motor visual... presiona 'q' para salir.")
    
    estado_reto = "ANALIZANDO"
    tiempo_inicio = 0
    ultimo_tick = 0
    
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                continue
            
            image = cv2.flip(image, 1)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = pose.process(image_rgb)
            
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
                )
                
                h, w, _ = image.shape
                landmarks = results.pose_landmarks.landmark
                
                p1_enum = getattr(mp_pose.PoseLandmark, p1_name).value
                p2_enum = getattr(mp_pose.PoseLandmark, p2_name).value
                p3_enum = getattr(mp_pose.PoseLandmark, p3_name).value
                
                punto_1 = [landmarks[p1_enum].x * w, landmarks[p1_enum].y * h]
                punto_2 = [landmarks[p2_enum].x * w, landmarks[p2_enum].y * h] # Vértice
                punto_3 = [landmarks[p3_enum].x * w, landmarks[p3_enum].y * h]
                
                angulo = calcular_angulo(punto_1, punto_2, punto_3)
                
                # 4. los estados con variables del JSON
                if rango_min <= angulo <= rango_max:
                    color = (0, 255, 0)
                    estado_postura = "APROBADO"
                elif (rango_min - 20) <= angulo < rango_min: 
                    color = (0, 255, 255)
                    estado_postura = "CORRIGIENDO"
                else:
                    color = (0, 0, 255)
                    estado_postura = "INCORRECTO"
                
                #inicio de estados
                if estado_reto == "EXITO":
                    cv2.putText(image, "RETO SUPERADO!", (50, 100), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3, cv2.LINE_AA)
                else:
                    if estado_postura == "APROBADO":
                        if estado_reto == "ANALIZANDO":
                            estado_reto = "SOSTENIENDO"
                            tiempo_inicio = time.time()
                            ultimo_tick = 0
                            
                        elif estado_reto == "SOSTENIENDO":
                            tiempo_transcurrido = time.time() - tiempo_inicio
                            tiempo_restante = int(tiempo_objetivo - tiempo_transcurrido) + 1
                            
                            cv2.putText(image, f"Sostener: {tiempo_restante}s", (50, 100), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3, cv2.LINE_AA)
                            
                            if int(tiempo_transcurrido) > ultimo_tick:
                                winsound.Beep(1000, 200)
                                ultimo_tick = int(tiempo_transcurrido)
                            
                            if tiempo_transcurrido >= tiempo_objetivo:
                                estado_reto = "EXITO"
                                winsound.Beep(2000, 500)
                    else:
                        if estado_reto == "SOSTENIENDO":
                            estado_reto = "ANALIZANDO"
                            winsound.Beep(300, 300)
                
                posicion_texto = (int(punto_2[0]) + 20, int(punto_2[1]) - 20)
                posicion_estado = (int(punto_2[0]) + 20, int(punto_2[1]) + 20)
                
                cv2.putText(image, f"{int(angulo)} grados", posicion_texto, 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)
                cv2.putText(image, estado_postura, posicion_estado, 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2, cv2.LINE_AA)
            
            cv2.imshow(f'Estatuas Inteligentes - {reto_actual["nombre"]}', image)
            
            if cv2.waitKey(5) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()