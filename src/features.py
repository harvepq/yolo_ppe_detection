# Import libraries
import os
import typer
import yaml

from config import DATASET_DIR
from loguru import logger

app = typer.Typer()

@app.command()
def main():
    # data yaml path
    data_yaml_path = os.path.join(DATASET_DIR, 'data.yaml')
    # ---- REPLACE THIS WITH YOUR OWN CODE ----
    logger.info("Generating features from dataset...")
    # Open the file
    with open(data_yaml_path, 'r+') as file:
        try:
            # Read the data yaml content
            data = yaml.safe_load(file)

            # Clear file
            file.seek(0)
            file.truncate()

            # Modify the train, test and validation path
            data['train'] = os.path.join(DATASET_DIR, 'train', 'images')
            data['test'] = os.path.join(DATASET_DIR, 'test', 'images')
            data['val'] = os.path.join(DATASET_DIR, 'val', 'images')

            # Save the modified content
            yaml.dump(data, file)

        except yaml.YAMLError as e:
            print('Error reading YAML:', e)
    # Close the file
    file.close()

    logger.success("Features generation complete.")
    # -----------------------------------------

if __name__ == "__main__":
    app()
