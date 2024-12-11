# Import libraries
import os
import typer

from loguru import logger
from roboflow import Roboflow
# from src.config import PROCESSED_DATA_DIR, RAW_DATA_DIR
from config import PROCESSED_DATA_DIR, ROBOFLOW_API, PROJECT_WORKSPACE, PROJECT_NAME, DATASET_VERSION, DATASET_FORMAT

app = typer.Typer()

@app.command()
def main():
    download_path = os.path.join(PROCESSED_DATA_DIR, f'ppe_dataset_v{DATASET_VERSION}')

    # ---- REPLACE THIS WITH YOUR OWN CODE ----
    logger.info("Processing dataset...")

    try:
        rf = Roboflow(api_key=ROBOFLOW_API)
        project = rf.workspace(PROJECT_WORKSPACE).project(PROJECT_NAME)
        version = project.version(DATASET_VERSION)
        dataset = version.download(model_format=DATASET_FORMAT, location=download_path, overwrite=True)
    except:
        print('Something went wrong with download dataset from Roboflow')

    logger.success("Processing dataset complete.")
    # -----------------------------------------

if __name__ == "__main__":
    app()
