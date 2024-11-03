# Import libraries
import cv2
from datetime import datetime
import os
import time

# Ask the user whether to use one or two cameras
num_cameras = int(input('Enter the number of cameras to use (1 or 2): '))

# Define cameras
camera1 = 'rtsp://admin:fypsfa24$$@192.168.188.104/Streaming/channels/101'
camera2 = 'rtsp://admin:fypsfa24$$@192.168.188.104/Streaming/channels/201' if num_cameras == 2 else None

# Function to initialize a camera conection
def initialize_camera(camera):
  cap = cv2.VideoCapture(camera)
  # Check if the camera opened successfully
  if not cap.isOpened():
    print(f'Error: Could not open {camera}')
  return cap

# Initialize cameras
cap1 = initialize_camera(camera1) if num_cameras >= 1 else None
cap2 = initialize_camera(camera2) if num_cameras == 2 else None

# Set a timeout threshold for detecting no-responsive cameras
timeout_threshold = 10
last_attempt_1 = time.time()
last_attempt_2 = time.time()

# Set interval in seconds
interval = 60
image_count_cam1 = 0 # Counter to name saved images from camera 1
image_count_cam2 = 0 # Counter to name saved images from camera 2
last_capture_time = time.time()
first_camera_capture = True

# Create folder to save images
current_dir = os.path.dirname(__file__)
folder_name = datetime.now().strftime("%Y_%m_%d")
folder_path = os.path.join(current_dir, f'../data/captures/{folder_name}')
os.makedirs(folder_path, exist_ok=True)
print(f"Folder '{folder_name}' created successfully on data.")

try:
  while cap1 or cap2:
    # Capture frame-by-frame
    ret1, frame1 = cap1.read()
    ret2, frame2 = cap2.read() if cap2 else (None, None)

    # Check for camera response timeout
    if ret1 == False:
      if (time.time() - last_attempt_1) >= timeout_threshold:
        print(f'Error: {camera1} is not responding.')
        print('Reinitializing camera connection ...')

        # Release and reinitialize camera 1
        cap1.release()
        time.sleep(2)

        cap1 = initialize_camera(camera1)
        last_attempt_1 = time.time()

    if ret2 == False:
      if (time.time() - last_attempt_2) >= timeout_threshold:
        print(f'Error: {camera2} is not responding.')
        print('Reinitializing camera connection ...')

        # Release and reinitialize camera 1
        cap2.release()
        time.sleep(2)

        cap2 = initialize_camera(camera2)
        last_attempt_2 = time.time()

    # Check if the interval time has passed
    current_time = time.time()

    if current_time - last_capture_time >= interval:
      if first_camera_capture:
        if ret1:
          # Capture de current date
          now = datetime.now()

          # Extract current hour, minute, and second as string
          current_time = now.strftime('%H_%M_%S')

          # Save the frame as an image file
          image_name = f'{folder_path}/cam1_frame_{image_count_cam1}_{current_time}.jpg'
          cv2.imwrite(image_name, frame1)
          print(f'Cam1 - Captured {image_count_cam1}')

          image_count_cam1 += 1
        last_capture_time = time.time()
        first_camera_capture = not first_camera_capture
      else:
        if ret2:
          # Capture de current date
          now = datetime.now()

          # Extract current hour, minute, and second as string
          current_time = now.strftime('%H_%M_%S')

          # Save the frame as an image file
          image_name = f'{folder_path}/cam2_frame_{image_count_cam2}_{current_time}.jpg'
          cv2.imwrite(image_name, frame2)
          print(f'Cam2 - Captured {image_count_cam2}')

          image_count_cam2 += 1
        last_capture_time = time.time()
        first_camera_capture = not first_camera_capture

    # break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
      break
except KeyboardInterrupt:
  # Handle the situation when the user interrupts the program (Ctrl+C)
  print('Image capture interrupted.')

# Release the camera and close any Opencv windows
cap1.release() if cap1 else None
cap2.release() if cap2 else None
cv2.destroyAllWindows()



