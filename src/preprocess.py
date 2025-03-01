# Import libraries
import os
import shutil

from datetime import datetime
from PIL import Image, ImageOps

from config import DATA_DIR, RAW_DATA_DIR, INTERIM_DATA_DIR

# Main section
def main(resize=True):
    # Initialize variables
    image_counter = 0
    processed_dirs = []
    time_processed = 0

    # Read raw data directories
    raw_data_dirs = os.listdir(RAW_DATA_DIR)

    # Processed file name and path
    processed_file = 'processed.txt'
    processed_file_path = os.path.join(DATA_DIR, processed_file)

    # Create a new file and open to append content
    if processed_file not in os.listdir(DATA_DIR):
        file = open(processed_file_path, '+a')
    else:
        file = open(processed_file_path, 'r+')
        # Get the processed dirs names
        file_list = file.read().splitlines()
        processed_dirs = file_list[:-2]

        if len(processed_dirs) > 0:
            # Get the number of processed images
            image_counter = int(file_list[-2])
            time_processed = int(file_list[-1])

        # Delete the last line of the file
        file.seek(0)
        file.truncate()
        for dir in processed_dirs:
            file.write(f'{dir}\n')

    # Verify if there are any raw data to process
    dirs_to_process = [e for e in raw_data_dirs if os.path.isdir(os.path.join(RAW_DATA_DIR, e)) and e not in processed_dirs]

    if len(dirs_to_process) == 0:
        print('There are not any data to process')
    else:
        print('There are raw data to process')
        # Add time processed
        time_processed += 1

        # Create new folder
        current_day = datetime.now().strftime('%Y_%m_%d')
        folder_name = f'{time_processed:02}_{current_day}'
        interim_folder_path = os.path.join(INTERIM_DATA_DIR, folder_name)
        os.makedirs(interim_folder_path, exist_ok=True)

        # Read all images dirs from raw data dir
        for dir in dirs_to_process:
            raw_data_dir = os.path.join(RAW_DATA_DIR, dir)

            raw_images_name = os.listdir(raw_data_dir)

            # Read all images
            for image_name in raw_images_name:

                # Increase image counter
                image_counter += 1

                # Image path
                image_path = os.path.join(raw_data_dir, image_name)

                # Create image name
                new_image_name = f'{image_counter:06}.jpg'

                # Create image path
                new_image_path = os.path.join(interim_folder_path, new_image_name)

                # Copy images without resizing
                if not resize:
                    shutil.copyfile(image_path, new_image_path)

                # Resize images
                else:
                    # Read the image
                    image = Image.open(image_path)
                    # Image dimensions
                    w, h = image.size

                    # Desired dimensions
                    desired_h = 640
                    desired_w = 640

                    # Dimensions difference
                    diff_h = desired_h - h
                    diff_w = desired_w - w

                    # Resizing image
                    if diff_h < 0 or diff_w < 0:
                        resizing_h = desired_h if diff_h < 0 else h
                        resizing_w = desired_w if diff_w < 0 else w
                        image = image.resize((resizing_w, resizing_h), Image.LANCZOS)

                    # Add padding
                    if diff_h > 0 or diff_w > 0:
                        pd_top = diff_h // 2 if diff_h > 0 else 0
                        pd_bottom = diff_h - diff_h // 2 if diff_h > 0 else 0
                        pd_left = diff_w // 2 if diff_w > 0 else 0
                        pd_right = diff_w - diff_w // 2 if diff_w > 0 else 0

                        # Add padding with white color (255, 255, 255)
                        image = ImageOps.expand(image, border=(pd_left, pd_top, pd_right, pd_bottom), fill="white")

                    # Save the new image into intermediate data
                    image.save(new_image_path)

            # Append dir into processed file
            file.write(f'{dir}\n')

    # Append the image counter and time processed into processed file
    file.write(f'{image_counter}\n')
    file.write(f'{time_processed}\n')

    # Close the processed file
    file.close()

if __name__ == "__main__":
    resize = True
    print('Enter one option')
    print('0. Dont resize images')
    print('1. Resize images to 640 x 640')
    op = int(input('Option: '))
    if op == 0:
        resize = False

    main(resize=resize)