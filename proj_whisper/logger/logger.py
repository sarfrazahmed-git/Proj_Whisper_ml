import logging
from datetime import datetime
import os
File_path = f"{datetime.now().strftime('%Y-%m-%d')}.log"
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
File_path = os.path.join(log_dir, File_path)
logging.basicConfig(
    filename=File_path,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
