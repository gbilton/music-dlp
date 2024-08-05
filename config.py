import os
from dotenv import load_dotenv

# Function to check if the app is running inside Docker
def is_docker():
    path = '/proc/self/cgroup'
    return (
        os.path.exists('/.dockerenv') or
        os.path.isfile(path) and any('docker' in line for line in open(path))
    )

# Load the .env file
load_dotenv()

# Select the appropriate environment variables
if is_docker():
    MUSIC_PATH = os.getenv('DOCKER_MUSIC_PATH')
    DB_PATH = os.getenv('DOCKER_DB_PATH')
else:
    MUSIC_PATH = os.getenv('LOCAL_MUSIC_PATH')
    DB_PATH = os.getenv('LOCAL_DB_PATH')

