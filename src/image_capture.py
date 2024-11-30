# Import libraries
import cv2
from datetime import datetime
import os
import time

# Function to initialize a camera conection
def initialize_cameras(opt, url_camera):
  cameras = []
  # Capture Cameras
  if (opt == '1' or opt == '3'):
    cap1 = cv2.VideoCapture(url_camera['channel1'])
    # Verify is camera 1 is opened
    if not cap1.isOpened():
      print(f'Error: Could not open the camera in channel 101')
    # Add camera into list
    else:
      cameras.append(
        {'cap': cap1,
         'name': 'Camera 1',
         'channel': '1',
         'capture': True,
         'capture_num': 0,
         'last_attempt': time.time()
        }
      )

  if (opt == '2' or opt == '3'):
    cap2 = cv2.VideoCapture(url_camera['channel2'])
    # Verify is camera 2 is opened
    if not cap2.isOpened():
      print(f'Error: Could not open the camera in channel 201')
    # Add camera into list
    else:
      cameras.append(
        {'cap': cap2,
         'name': 'Camera 2',
         'capture': False,
         'channel': '2',
         'capture_num': 0,
         'last_attempt': time.time()
        }
      )

  return cameras

# Camera menu option
def menu (level):
  if level == 1:
    print('DATA CAPTURE FOR DETECTION OF PPE')
    print('----------------------------------')
    print('')
    print('1 -> Only Capture Images')
    print('2 -> Only View Real Time Video')
    print('3 -> Both, Capture Images and View Real Time Video')
    opt = input('Select one option (1, 2, or 3): ')

  # Ask the user whether to use one or two cameras, or both
  else:
    print('Select the cameras!')
    print('1 -> Camera 1')
    print('2 -> Camera 2')
    print('3 -> Both, Camera 1 and Camera 2')
    opt = input('Select one option (1, 2, or 3): ')

  while not (opt in ['1', '2', '3']):
    opt = input('Select one correct option again (1, 2, or 3): ')

  # Return option
  return opt

# Ask menu
opt_1 = menu(1)
ip_num = input('Enter the IP point: ')
opt_2 = menu(2)

# Define cameras
protocol = f'rtsp://admin:fypsfa24$$@192.168.188.{ip_num}/Streaming/channels/'
url_camera = {
  'channel1': f'{protocol}101',
  'channel2': f'{protocol}201'
}

# Define parameters
# Set a timeout threshold for detecting no-responsive cameras
timeout_threshold = 30

# List of initialized cameras
cameras = initialize_cameras(opt_2, url_camera)

# Create folder to save images
current_dir = os.path.dirname(__file__)
folder_name = datetime.now().strftime("%Y_%m_%d")
folder_path = os.path.join(current_dir, f'../data/captures/{folder_name}')
os.makedirs(folder_path, exist_ok=True)
print(f"Folder '{folder_name}' created successfully on data.")

try:
  while True:
    for camera in cameras:
      cap = camera['cap']

      time.sleep(60)
      ret, frame = cap.read()

      if not ret:
        # Check for camera response timeout
        if (time.time() - camera['last_attempt']) >= timeout_threshold:
          print(f'Error: The {camera["name"]} is not repsonding.')
          print('Reinitializing camera connection ...')

          # Release and reinitialize camera
          cap.release()
          time.sleep(2)

          camera['cap'] = cv2.VideoCapture(url_camera[f'channel{camera["channel"]}'])
          camera['last_attempt']= time.time()
        continue

      else:
          # Capture current date
          now = datetime.now()

          # Extract current hour, minute, and second as string
          current_time = now.strftime('%H_%M_%S')

          # Save the frame as an image file
          camera['capture_num'] += 1
          image_name = f'{folder_path}/Cam{camera["channel"]}_frame_{camera["capture_num"]}_{current_time}.jpg'
          cv2.imwrite(image_name, frame)
          print(f'{camera["name"]} - Captured {camera["capture_num"]}')

      # break the loop if 'q' is pressed
      if cv2.waitKey(1) & 0xFF == ord('q'):
        break

except KeyboardInterrupt:
  # Handle the situation when the user interrupts the program (Ctrl+C)
  for camera in cameras:
    camera['cap'].release()
  print('Image capture interrupted.')

# Release the camera and close any Opencv windows
for camera in cameras:
  camera['cap'].release()

cv2.destroyAllWindows()