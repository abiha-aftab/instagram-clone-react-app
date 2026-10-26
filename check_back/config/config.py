# importing teh env


import os
from dotenv import load_dotenv



BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
# SECURITY WARNING: keep the secret key used in production

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'your-default-secret-key')

# for the setting of the databes
DATABASE_NAME= os.getenv('DB_NAME')
DATABASE_USER= os.getenv('DB_USER')
DATABASE_PASSWORD= os.getenv('DB_PASSWORD')
DATABASE_HOST= os.getenv('DB_HOST')
DATABASE_PORT= os.getenv('DB_PORT')


CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME')
CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')



