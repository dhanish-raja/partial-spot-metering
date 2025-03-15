import cv2
import numpy as np
import os

points = []
drawing = False
brightness = 50
image_copy = None
live_image = None

captured_image = None

def draw_lasso(event, x, y, flags, param):
    global points, drawing, image_copy

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        points = [(x, y)]

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            points.append((x, y))
            cv2.line(image_copy, points[-2], points[-1], (0, 255, 0), 2)
            cv2.imshow('Live Feed', image_copy)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        points.append((x, y))
        cv2.line(image_copy, points[-2], points[-1], (0, 255, 0), 2)
        cv2.imshow('Live Feed', image_copy)

def brighten_area(image, mask, brightness_value):
    result = image.copy()
    result[mask] = cv2.add(result[mask], np.array([brightness_value], dtype=np.uint8))
    return result

def create_mask_from_lasso(points, image_shape):
    mask = np.zeros(image_shape[:2], dtype=np.uint8)
    points_array = np.array(points, dtype=np.int32)
    cv2.fillPoly(mask, [points_array], 255)
    return mask

def save_image(image):
    while True:
        directory = input("Enter the directory path where you want to save the image (or press Enter for Desktop): ").strip()
        if directory == "":
            directory = os.path.join(os.path.expanduser("~"), "Desktop", "cv_image")
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
                print(f"Created directory: {directory}")
            except Exception as e:
                print(f"Error creating directory: {e}")
                continue
        file_name = input("Enter the file name (without extension): ").strip()
        if file_name == "":
            print("File name cannot be empty. Please try again.")
            continue
        save_path = os.path.join(directory, f"{file_name}.png")
        if os.path.exists(save_path):
            overwrite = input(f"File '{save_path}' already exists. Overwrite? (y/n): ").strip().lower()
            if overwrite != 'y':
                continue

        try:
            cv2.imwrite(save_path, image)
            print(f"Image saved at {save_path}")
            break
        except Exception as e:
            print(f"Error saving image: {e}")
            continue

def on_brightness_trackbar(val):
    global brightness
    brightness = val

def handle_captured_image(image):
    cv2.namedWindow('Captured Image')
    cv2.imshow('Captured Image', image)
    print("\nCaptured image displayed.")
    print("Press 's' to save the image or 'q' to quit without saving.")

    while True:
        key = cv2.waitKey(0) & 0xFF

        if key == ord('s'):
            save_image(image)
            print("Image saved. Exiting.")
            cv2.destroyWindow('Captured Image')
            break
        elif key == ord('q'):
            print("Exiting without saving.")
            cv2.destroyWindow('Captured Image')
            break
        else:
            print("Invalid key. Press 's' to save or 'q' to quit.")

def process_live_feed():

    global image_copy, live_image, brightness, captured_image

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    cv2.namedWindow('Live Feed')
    cv2.setMouseCallback('Live Feed', draw_lasso)


    cv2.createTrackbar('Brightness', 'Live Feed', 50, 100, on_brightness_trackbar)

    while True:
        ret, live_image = cap.read()
        if not ret:
            print("Error: Could not retrieve frame.")
            break

        image_copy = live_image.copy()

        if len(points) > 2:
            mask = create_mask_from_lasso(points, live_image.shape)
            brightened_image = brighten_area(live_image, mask.astype(bool), brightness)
            cv2.imshow('Live Feed', brightened_image)
        else:
            cv2.imshow('Live Feed', image_copy)

        key = cv2.waitKey(1) & 0xFF


        if key == ord('c') and len(points) > 2:
            mask = create_mask_from_lasso(points, live_image.shape)
            captured_image = brighten_area(live_image, mask.astype(bool), brightness)
            print("Image captured. Switch to 'Captured Image' window to save or quit.")
            handle_captured_image(captured_image)

        elif key == ord('q'):
            print("Exiting program.")
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    process_live_feed()