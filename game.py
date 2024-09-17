import cv2
import mediapipe as mp
import pygame
import numpy as np
import random

# Initialize MediaPipe Hands and Pygame
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)

# Initialize Pygame
pygame.init()
screen_width, screen_height = 800, 600
game_window = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Hand Gesture Control")

# Font for text
font = pygame.font.Font(None, 74)

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)

# Button settings
button_color = (0, 255, 0)  # Green color for buttons
button_width, button_height = 200, 50

def draw_button(surface, text, x, y):
    pygame.draw.rect(surface, button_color, pygame.Rect(x, y, button_width, button_height))
    draw_text(text, font, (255, 255, 255), surface, x + button_width // 2, y + button_height // 2)

# Pixel settings
pixel_color = (255, 0, 0)  # Red color for the pixel
pixel_size = 10
movement_speed = 10

def get_fingers_up(hand_landmarks):
    fingers_up = [False] * 5
    landmarks = hand_landmarks.landmark

    # Thumb
    #fingers_up[0] = landmarks[mp_hands.HandLandmark.THUMB_TIP].y < landmarks[mp_hands.HandLandmark.THUMB_IP].y
    # Index
    fingers_up[1] = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP].y < landmarks[mp_hands.HandLandmark.INDEX_FINGER_PIP].y
    # Middle
    fingers_up[2] = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y < landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y
    # Ring
    fingers_up[3] = landmarks[mp_hands.HandLandmark.RING_FINGER_TIP].y < landmarks[mp_hands.HandLandmark.RING_FINGER_PIP].y
    # Pinky
    fingers_up[4] = landmarks[mp_hands.HandLandmark.PINKY_TIP].y < landmarks[mp_hands.HandLandmark.PINKY_PIP].y

    print("Fingers up:", fingers_up)  # Debug print to check detection
    return fingers_up

def display_game_over():
    game_window.fill((0, 0, 0))
    draw_text("Game Over", font, (255, 0, 0), game_window, screen_width // 2, screen_height // 2 - 50)
    draw_button(game_window, "Retry", screen_width // 2 - button_width // 2, screen_height // 2 + 10)
    draw_button(game_window, "Exit", screen_width // 2 - button_width // 2, screen_height // 2 + 70)
    pygame.display.flip()

def main_game_loop():
    global pixel_x, pixel_y, pixel_width, pixel_height
    pixel_x, pixel_y = screen_width // 2, screen_height // 2
    movement_speed = 10

    # Initialize snake segments
    snake_segments = [(pixel_x, pixel_y)]
    segment_width = 10
    segment_height = 10

    # Generate the first random pixel
    random_pixel_x = random.randint(0, screen_width - segment_width)
    random_pixel_y = random.randint(0, screen_height - segment_height)

    game_running = True
    while game_running:
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        image = cv2.flip(image, 1)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image_rgb)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # Exit the main game loop

        move_left = move_right = move_up = move_down = False

        if results.multi_hand_landmarks:
            left_hand_landmarks = right_hand_landmarks = None
            
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                if hand_landmarks:
                    if len(results.multi_hand_landmarks) == 2:
                        if results.multi_hand_landmarks.index(hand_landmarks) == 0:
                            left_hand_landmarks = hand_landmarks
                        else:
                            right_hand_landmarks = hand_landmarks

            if left_hand_landmarks:
                fingers_left = get_fingers_up(left_hand_landmarks)
                if sum(fingers_left) == 1:  # Only move if exactly one finger is up
                    if fingers_left[1]:  # Left hand index finger up -> Move up
                        move_down = True
                    elif fingers_left[2]:  # Left hand middle finger up -> Move down
                        move_up = True

            if right_hand_landmarks:
                fingers_right = get_fingers_up(right_hand_landmarks)
                if sum(fingers_right) == 1:  # Only move if exactly one finger is up
                    if fingers_right[1]:  # Right hand index finger up -> Move left
                        move_left = True
                    elif fingers_right[2]:  # Right hand middle finger up -> Move right
                        move_right = True

        if move_left:
            pixel_x -= movement_speed
        if move_right:
            pixel_x += movement_speed
        if move_up:
            pixel_y -= movement_speed
        if move_down:
            pixel_y += movement_speed
            
            
        # Wrap around the screen boundaries (loop around feature)
        if pixel_x < 0:
            pixel_x = screen_width - pixel_size
        elif pixel_x > screen_width - pixel_size:
            pixel_x = 0

        if pixel_y < 0:
            pixel_y = screen_height - pixel_size
        elif pixel_y > screen_height - pixel_size:
            pixel_y = 0

        # Move the snake
        new_head = (pixel_x, pixel_y)
        snake_segments = [new_head] + snake_segments[:-1]

        # Check for collision with random pixel (snake head)
        if abs(pixel_x - random_pixel_x) < segment_width and abs(pixel_y - random_pixel_y) < segment_height:
            # Collision detected: Add a new segment to the snake
            snake_segments.append(snake_segments[-1])  # Add a new segment at the tail

            # Random pixel vanishes and a new one is generated
            random_pixel_x = random.randint(0, screen_width - segment_width)
            random_pixel_y = random.randint(0, screen_height - segment_height)

        # Clear the Pygame window
        game_window.fill((0, 0, 0))

        # Draw the random external pixel
        pygame.draw.rect(game_window, (0, 255, 0), pygame.Rect(random_pixel_x, random_pixel_y, segment_width, segment_height))

        # Draw the snake (each segment)
        for segment in snake_segments:
            pygame.draw.rect(game_window, pixel_color, pygame.Rect(segment[0], segment[1], segment_width, segment_height))

        pygame.display.flip()

        # Display the camera feed with hand landmarks and connections
        cv2.imshow('Camera Feed', image)

        # Check if 'q' is pressed or OpenCV window is closed
        if cv2.waitKey(1) & 0xFF == ord('q') or cv2.getWindowProperty('Camera Feed', cv2.WND_PROP_VISIBLE) < 1:
            return False



def main():
    global cap
    cap = cv2.VideoCapture(0)
    
    running = True
    while running:
        game_window.fill((0, 0, 0))
        draw_text("Press Enter to Start", font, (255, 255, 255), game_window, screen_width // 2, screen_height // 2)
        pygame.display.flip()
        
        waiting_for_start = True
        while waiting_for_start:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    waiting_for_start = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    waiting_for_start = False
                    game_over = False
                    while not game_over:
                        game_over = main_game_loop()
                    display_game_over()
                    
                    retry = True
                    while retry:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                retry = False
                                running = False
                            elif event.type == pygame.MOUSEBUTTONDOWN:
                                mouse_x, mouse_y = event.pos
                                if screen_width // 2 - button_width // 2 <= mouse_x <= screen_width // 2 + button_width // 2:
                                    if screen_height // 2 + 10 <= mouse_y <= screen_height // 2 + 60:
                                        retry = False  # Retry the game
                                        break
                                    elif screen_height // 2 + 70 <= mouse_y <= screen_height // 2 + 120:
                                        retry = False  # Exit the game
                                        running = False
                                        break
                        pygame.time.wait(100)  # Reduce CPU usage

    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()

if __name__ == "__main__":
    main()
