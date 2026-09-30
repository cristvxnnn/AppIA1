import cv2
import mediapipe as mp
import time
import winsound
from vision.angles import calcular_angulo

# Configuración estándar de MediaPipe
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

def main():
    cap = cv2.VideoCapture(0)
    print("Iniciando motor visual... presiona 'q' para salir.")
    
    # Variables de Estados
    estado_reto = "ANALIZANDO"
    tiempo_inicio = 0
    tiempo_objetivo = 3.0  # 3 segundos de sostenimiento
    ultimo_tick = 0        # Para controlar el sonido del tick-tock
    
    with mp_pose.Pose(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as pose:
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                continue
            
            image = cv2.flip(image, 1)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = pose.process(image_rgb)
            
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    image, 
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
                )
                
                h, w, _ = image.shape
                landmarks = results.pose_landmarks.landmark
                
                # Coordenadas del Brazo Izquierdo
                hombro = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x * w, 
                          landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y * h]
                codo = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x * w, 
                        landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y * h]
                muneca = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x * w, 
                          landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y * h]
                
                angulo = calcular_angulo(hombro, codo, muneca)
                
                # Evaluación Visual del "Semáforo"
                if 160 <= angulo <= 180:
                    color = (0, 255, 0)
                    estado_postura = "APROBADO"
                elif 140 <= angulo < 160:
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
                            
                            # temporizador os
                            cv2.putText(image, f"Sostener: {tiempo_restante}s", (50, 100), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3, cv2.LINE_AA)
                            
                            #sonido tick
                            if int(tiempo_transcurrido) > ultimo_tick:
                                winsound.Beep(1000, 200) # Frecuencia 1000Hz, 200ms
                                ultimo_tick = int(tiempo_transcurrido)
                            
                            # Validar
                            if tiempo_transcurrido >= tiempo_objetivo:
                                estado_reto = "EXITO"
                                winsound.Beep(2000, 500) 
                    else:
                        # Si pierde la postura, se reinicia todo inmediatamente
                        if estado_reto == "SOSTENIENDO":
                            estado_reto = "ANALIZANDO"
                            winsound.Beep(300, 300)
                # fin estados
                
                # Dibuja textos cerca del codo
                posicion_texto = (int(codo[0]) + 20, int(codo[1]) - 20)
                posicion_estado = (int(codo[0]) + 20, int(codo[1]) + 20)
                
                cv2.putText(image, f"{int(angulo)} grados", posicion_texto, 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)
                cv2.putText(image, estado_postura, posicion_estado, 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2, cv2.LINE_AA)
            
            cv2.imshow('Estatuas Inteligentes - Fase 4', image)
            
            if cv2.waitKey(5) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()