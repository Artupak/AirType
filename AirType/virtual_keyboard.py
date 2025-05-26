import cv2
import numpy as np

class VirtualKeyboard:
    def __init__(self, key_layout=None):
        if key_layout is None:
            self.key_layout = [
                ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "<"],
                ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
                ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"],
                ["_"]
            ]
        else:
            self.key_layout = key_layout
        
        self.keys = []
        self._initialize_keys()
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = 0.8
        self.font_thickness = 2
        self.key_bg_color = (180, 180, 180) # Light Gray
        self.key_border_color = (50, 50, 50) # Dark Gray
        self.key_text_color = (255, 255, 255) # White
        self.hover_bg_color = (0, 255, 0) # Green for hover/selection

    def _initialize_keys(self):
        start_x, start_y = 20, 30
        key_w, key_h = 40, 40
        key_margin = 5

        for r_idx, row in enumerate(self.key_layout):
            for k_idx, key_char in enumerate(row):
                x = start_x + k_idx * (key_w + key_margin)
                y = start_y + r_idx * (key_h + key_margin)
                self.keys.append({"char": key_char, "rect": (x, y, key_w, key_h), "hover_time": 0})

    def draw_keyboard(self, img):
        """Draws the virtual keyboard on the given image with enhanced visibility."""
        for key in self.keys:
            x, y, w, h = key["rect"]
            # Draw key background
            cv2.rectangle(img, (x, y), (x + w, y + h), self.key_bg_color, cv2.FILLED)
            # Draw key border
            cv2.rectangle(img, (x, y), (x + w, y + h), self.key_border_color, 2)
            
            # Calculate text size and position for centering
            text_size = cv2.getTextSize(key["char"], self.font, self.font_scale, self.font_thickness)[0]
            text_x = x + (w - text_size[0]) // 2
            text_y = y + (h + text_size[1]) // 2
            
            cv2.putText(img, key["char"], (text_x, text_y), 
                        self.font, self.font_scale, self.key_text_color, self.font_thickness)
        return img

    def check_hover(self, finger_tip_pos, img_shape):
        """
        Checks if a fingertip is hovering over a key.
        Updates hover time and returns the character of the hovered key if dwell time is met.
        Also provides visual feedback for hovering/selection.
        """
        selected_char = None
        current_time = cv2.getTickCount() / cv2.getTickFrequency()

        for key in self.keys:
            x, y, w, h = key["rect"]
            fx, fy = finger_tip_pos

            if x < fx < x + w and y < fy < y + h:
                # Visual feedback for hover
                cv2.rectangle(img_shape, (x, y), (x + w, y + h), self.hover_bg_color, 2) 
                if key["hover_time"] == 0:
                    key["hover_time"] = current_time
                elif (current_time - key["hover_time"]) > 0.75:
                    selected_char = key["char"]
                    key["hover_time"] = 0 
                    # Visual feedback for selection (stronger)
                    cv2.rectangle(img_shape, (x, y), (x + w, y + h), self.hover_bg_color, cv2.FILLED)
                    # Re-draw text on top of filled rectangle for selected key
                    text_size = cv2.getTextSize(key["char"], self.font, self.font_scale, self.font_thickness)[0]
                    text_x = x + (w - text_size[0]) // 2
                    text_y = y + (h + text_size[1]) // 2
                    cv2.putText(img_shape, key["char"], (text_x, text_y), 
                                self.font, self.font_scale, self.key_text_color, self.font_thickness)

            else:
                key["hover_time"] = 0
        
        return selected_char


if __name__ == '__main__':
    keyboard = VirtualKeyboard()
    
    desired_width = 1280
    desired_height = 720
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, desired_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, desired_height)

    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    if not cap.isOpened():
        print("Cannot open camera, using a dummy black image.")
        use_dummy_image = True
        # Use desired dimensions for dummy image if camera fails
        img_width, img_height = desired_width, desired_height
    else:
        use_dummy_image = False
        img_width, img_height = actual_width, actual_height
        if not (actual_width == desired_width and actual_height == desired_height):
            print(f"Warning: Camera might not support {desired_width}x{desired_height}. Effective resolution: {actual_width}x{actual_height}")

    window_name = "Virtual Keyboard Test"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL) 
    # Resize window to actual camera resolution or desired if dummy
    cv2.resizeWindow(window_name, img_width, img_height)


    while True:
        if use_dummy_image:
            test_img = np.zeros((img_height, img_width, 3), np.uint8)
        else:
            success, frame = cap.read()
            if not success:
                print("Failed to grab frame")
                break
            test_img = cv2.flip(frame, 1)

        # Draw keyboard on a copy of the image to avoid modifying the original frame used by other logic
        display_img = test_img.copy()
        display_img = keyboard.draw_keyboard(display_img)

        cv2.imshow(window_name, display_img)
        
        key_press = cv2.waitKey(1) & 0xFF
        if key_press == ord('q'):
            break
        elif key_press == ord('c'): 
            def get_mouse_coords(event,x_coord,y_coord,flags,param):
                if event == cv2.EVENT_LBUTTONDOWN:
                    # Need to pass the image on which hover effect will be drawn
                    # For testing, we draw hover effect directly on display_img
                    selected = keyboard.check_hover((x_coord,y_coord), display_img) 
                    if selected:
                        print(f"Selected by click: {selected}")
                    # Refresh the image to show hover effect immediately
                    cv2.imshow(window_name, display_img) 
            
            cv2.setMouseCallback(window_name, get_mouse_coords)
            print("Mouse callback set. Click on a key. Press 'q' to quit.")


    if cap.isOpened():
        cap.release()
    cv2.destroyAllWindows() 