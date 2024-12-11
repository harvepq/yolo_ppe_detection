# Import libraries
import os

from dotenv import load_dotenv
from loguru import logger
from pathlib import Path

# Load environment variables from .env file if it exists
load_dotenv()

# Paths
PROJ_ROOT = Path(__file__).resolve().parents[1]
logger.info(f"PROJ_ROOT path is: {PROJ_ROOT}")

# Data dir
DATA_DIR = PROJ_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
INTERIM_DATA_DIR = DATA_DIR / "interim"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXTERNAL_DATA_DIR = DATA_DIR / "external"

# Models dir
MODELS_DIR = PROJ_ROOT / "models"

# Report dir
REPORTS_DIR = PROJ_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

# Roboflow dataset
ROBOFLOW_API = os.getenv("ROBOFLOW_API")
PROJECT_WORKSPACE = os.getenv("PROJECT_WORKSPACE")
PROJECT_NAME = os.getenv("PROJECT_NAME")
DATASET_VERSION = os.getenv("DATASET_VERSION")
DATASET_FORMAT = os.getenv("DATASET_FORMAT")

# If tqdm is installed, configure loguru with tqdm.write
# https://github.com/Delgan/loguru/issues/135
# try:
#     from tqdm import tqdm

#     logger.remove(0)
#     logger.add(lambda msg: tqdm.write(msg, end=""), colorize=True)
# except ModuleNotFoundError:
#     pass
