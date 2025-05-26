import cv2
import time
import numpy as np
import speech_recognition as sr
import webbrowser
import threading # For non-blocking speech recognition

# Import custom modules
from hand_detector import HandDetector
from virtual_keyboard import VirtualKeyboard

# --- Configuration ---
WEBCAM_ID = 0
REQUESTED_WIDTH = 1280
REQUESTED_HEIGHT = 720
VOICE_COMMAND_PHRASE = "bilgisayar" # Wake word for voice commands
GOOGLE_SEARCH_PHRASE = "google'da ara"

# --- Global Variables ---
typed_text = ""
last_char_time = 0
char_add_delay = 0.5 # Seconds to wait before adding the same char again
listening_active = False # To control when speech recognition is active
status_message = "" # To display messages to the user

# --- Speech Recognition Setup ---
recognizer = sr.Recognizer()
microphone = sr.Microphone()

with microphone as source:
    recognizer.adjust_for_ambient_noise(source, duration=0.5)

def set_status(message, duration=3):
    global status_message
    status_message = message
    # Simple way to clear status after a while, can be improved with a timer if needed
    # For now, relies on main loop redraws

def listen_for_commands_thread():
    global typed_text, listening_active, VOICE_COMMAND_PHRASE, GOOGLE_SEARCH_PHRASE
    while True:
        if not listening_active:
            time.sleep(0.1)
            continue

        # print("Listening for wake word...")
        set_status(f"'{VOICE_COMMAND_PHRASE}' bekleniyor...")
        with microphone as source:
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
            except sr.WaitTimeoutError:
                # print("No speech detected for wake word.")
                set_status("")
                listening_active = False # Stop listening if no wake word
                continue
        
        try:
            set_status("Komut işleniyor...")
            command = recognizer.recognize_google(audio, language="tr-TR").lower()
            print(f"Algılanan komut: {command}")

            if VOICE_COMMAND_PHRASE in command:
                command_after_wake_word = command.split(VOICE_COMMAND_PHRASE, 1)[-1].strip()
                print(f"Komut (uyandırma kelimesinden sonra): {command_after_wake_word}")
                
                if command_after_wake_word.startswith(GOOGLE_SEARCH_PHRASE):
                    search_query = command_after_wake_word.replace(GOOGLE_SEARCH_PHRASE, "").strip()
                    if search_query:
                        print(f"Google'da aranıyor: {search_query}")
                        set_status(f"Google'da '{search_query}' aranıyor...")
                        webbrowser.open(f"https://www.google.com/search?q={search_query}")
                    else:
                        print("Arama sorgusu boş.")
                        set_status("Arama sorgusu belirtilmedi.")
                # Add other commands here if needed
                else:
                    print(f"Bilinmeyen komut: {command_after_wake_word}")
                    set_status(f"Bilinmeyen komut: {command_after_wake_word}")
            else:
                # Wake word not detected in the phrase, ignore
                set_status("Uyandırma kelimesi algılanmadı.")
                pass

        except sr.UnknownValueError:
            print("Google Speech Recognition sesi anlayamadı.")
            set_status("Ses anlaşılamadı.")
        except sr.RequestError as e:
            print(f"Google Speech Recognition servisinden sonuç istenemedi; {e}")
            set_status("Konuşma servisi hatası.")
        except Exception as e:
            print(f"Komut işlenirken hata: {e}")
            set_status("Komut işleme hatası.")
        finally:
            listening_active = False # Reset after processing or error
            set_status("") # Clear status after command processing


def main():
    global typed_text, last_char_time, char_add_delay, listening_active, status_message

    cap = cv2.VideoCapture(WEBCAM_ID)
    if not cap.isOpened():
        print(f"Kamera {WEBCAM_ID} açılamadı.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, REQUESTED_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, REQUESTED_HEIGHT)
    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Kamera çözünürlüğü: {actual_width}x{actual_height}")

    detector = HandDetector(maxHands=1, detectionCon=0.7, trackCon=0.7)
    keyboard = VirtualKeyboard() # Using default layout

    # Start the voice command listener thread
    voice_thread = threading.Thread(target=listen_for_commands_thread, daemon=True)
    voice_thread.start()

    # Text display area properties
    text_area_height = 50
    text_area_y_start = actual_height - text_area_height - 10 # 10px margin from bottom
    text_font = cv2.FONT_HERSHEY_SIMPLEX
    text_font_scale = 0.8
    text_color = (200, 200, 200) # Light gray text
    text_bg_color = (50, 50, 50) # Dark gray background for text area
    status_font_scale = 0.6
    status_color = (255, 255, 0) # Yellow status

    cv2.namedWindow("AirType", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("AirType", actual_width, actual_height)

    last_selected_char = None 
    tipIds = [8] # Thumb, Index, Middle, Ring, Pinky tips

    while True:
        # print("Ana döngü başladı.") # DEBUG - Kaldırıldı
        success, img = cap.read()
        # print(f"Kamera okuma başarısı: {success}") # DEBUG - Kaldırıldı
        if not success:
            print("Kare alınamadı, döngü sonlandırılıyor.") 
            break
        img = cv2.flip(img, 1)

        img = detector.findHands(img, draw=True) # Draw hand skeleton
        lmList = detector.findPosition(img, draw=False) # We'll draw our own cursors for tips

        img = keyboard.draw_keyboard(img)

        final_selected_char = None # Character selected in this frame

        if lmList: 
            for tip_id in tipIds:
                if len(lmList) > tip_id: # Ensure the landmark exists
                    fx, fy = lmList[tip_id][1], lmList[tip_id][2]
                    cv2.circle(img, (fx, fy), 8, (255, 0, 255 - (tip_id * 10)), cv2.FILLED) # Draw cursor for each tip (slightly different colors)

                    if final_selected_char is None: # Process only one selection per frame
                        char_from_this_finger = keyboard.check_hover((fx, fy), img)
                        if char_from_this_finger:
                            final_selected_char = char_from_this_finger
            
            # print(f"Debug: selected_char='{final_selected_char}'")

            if final_selected_char:
                # print(f"Debug: last_selected_char='{last_selected_char}', current_time - last_char_time = {time.time() - last_char_time}")
                if final_selected_char != last_selected_char or (time.time() - last_char_time > char_add_delay):
                    if final_selected_char == "<": 
                        typed_text = typed_text[:-1]
                    elif final_selected_char == "_": 
                        typed_text += " "
                    else:
                        typed_text += final_selected_char
                    last_char_time = time.time()
                    last_selected_char = final_selected_char # Update last_selected_char with the char that was actually typed
                    # print(f"Debug: typed_text güncellendi: '{typed_text}'") 
            # else: # This else was for the old logic where only one finger was checked
                # last_selected_char = None # Reset if no key is hovered by the single checked finger
                                        # Now, last_selected_char is updated only when a char is typed.
        
        # Draw the typed text area
        # print(f"Debug: Metin çiziliyor: typed_text='{typed_text}', y_start={text_area_y_start}") 
        # print(f"Debug: typed_text='{typed_text}', text_area_y_start={text_area_y_start}, actual_width={actual_width}, actual_height={actual_height}")
        cv2.rectangle(img, (0, text_area_y_start), (actual_width, actual_height), text_bg_color, cv2.FILLED)
        cv2.putText(img, typed_text, (10, text_area_y_start + int(text_area_height/2) + 10),
                    text_font, text_font_scale, text_color, 2)

        # Display status messages (e.g., for voice commands)
        if status_message:
            cv2.putText(img, status_message, (10, 30), text_font, status_font_scale, status_color, 1)

        cv2.imshow("AirType", img)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            print("Çıkılıyor...")
            break
        if key == ord('v'): # Press 'v' to activate voice listening for one command cycle
            if not listening_active:
                listening_active = True
                print("Sesli komut dinleme etkinleştirildi (bir sonraki komut için).")
                set_status("Sesli komut için hazır. '" + VOICE_COMMAND_PHRASE + "' deyin.")
            else:
                listening_active = False # Toggle off if already active
                print("Sesli komut dinleme devre dışı bırakıldı.")
                set_status("")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main() 