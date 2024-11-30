import cv2
from datetime import datetime
import os

from config import RAW_DATA_DIR, INTERIM_DATA_DIR

def main():
  # Initialize variables
  image_counter = 0
  processed_dirs = []
  time_processed = 0

  # Read raw data directories
  raw_data_dirs = os.listdir(RAW_DATA_DIR)

  # Processed file name and path
  processed_file = 'processed.txt'
  processed_file_path = os.path.join(RAW_DATA_DIR, processed_file)

  # Create a new file and open to append content
  if processed_file not in raw_data_dirs:
    file = open(processed_file_path, '+a')

  # Read the file and opend to append content
  else:
    file = open(processed_file_path, 'r+')
    # Get the processed dirs names
    processed_dirs = file.read().splitlines()

    if len(processed_dirs) > 1:
      # Get the number of processed images
      image_counter = int(processed_dirs[-2])
      time_processed = int(processed_dirs[-1])


    # Delete the last line of the file
    file.seek(0)
    file.truncate()
    for dir in processed_dirs[:-2]:
      file.write(f'{dir}\n')

  # Add time processed
  time_processed += 1

  # Create new folder
  current_day = datetime.now().strftime('%Y_%m_%d')
  folder_name = f'{time_processed:02}_{current_day}'
  interim_folder_path = os.path.join(INTERIM_DATA_DIR, folder_name)
  os.makedirs(interim_folder_path, exist_ok=True)

  # Read all images dirs from raw data dir
  for dir in raw_data_dirs:
    # Verify if some dirs was processed
    if dir not in processed_dirs:
      raw_data_dir = os.path.join(RAW_DATA_DIR, dir)

      # Verify if is directory
      if os.path.isdir(raw_data_dir):

        # Read all images
        for image_name in os.listdir(raw_data_dir):
          image_path = os.path.join(raw_data_dir, image_name)

          # Read the image
          image = cv2.imread(image_path)

          # Image dimensions
          (h, w) = image.shape[:2]

          # Desired dimensions
          desired_h = 640
          desired_w = 640

          # Dimensions difference
          diff_h = desired_h - h
          diff_w = desired_w - w

          # Padding conf
          border_type = cv2.BORDER_CONSTANT
          border_color = [255, 255, 255] # White

          # Resizing image
          if diff_h < 0 or diff_w < 0:
            resizing_h = desired_h if diff_h < 0 else h
            resizing_w = desired_w if diff_w < 0 else w
            image = cv2.resize(image, (resizing_w, resizing_h))

          # Add padding
          if diff_h > 0 or diff_w:
            pd_top = diff_h // 2 if diff_h > 0 else 0
            pd_bottom = diff_h - diff_h // 2 if diff_h > 0 else 0
            pd_left = diff_w // 2 if diff_w > 0 else 0
            pd_right = diff_w - diff_w // 2 if diff_w > 0 else 0
            image = cv2.copyMakeBorder(image, pd_top, pd_bottom,pd_left, pd_right, border_type, None, border_color )

          # Increase image counter
          image_counter += 1

          # Create image name
          new_image_name = f'{image_counter:06}.jpg'

          # Create image path
          new_image_path = os.path.join(interim_folder_path, new_image_name)

          # Save the new image into intemediate data
          cv2.imwrite(new_image_path, image)

        # Append dir into processed file
        file.write(f'{dir}\n')

  # Append the image counter and time processed into processed file
  file.write(f'{image_counter}\n')
  file.write(f'{time_processed}\n')

  # Close the processed file
  file.close()

if __name__ == "__main__":
    main()