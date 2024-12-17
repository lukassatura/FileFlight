import os
import configparser

from dotenv import load_dotenv

load_dotenv()

config = configparser.ConfigParser()

config.add_section("aws_s3")

config.set("aws_s3","name","s3")
config.set("aws_s3","region_name","eu-central-1")
config.set("aws_s3","bucket_name","knihy")
config.set("aws_s3","access_key",os.getenv("aws_access_key_id"))
config.set("aws_s3","access_secret",os.getenv("aws_secret_access_key"))


config.add_section("gdrive")

config.set("gdrive","scopes","https://www.googleapis.com/auth/drive")
config.set("gdrive","client_secret_file","client_secret.json")
config.set("gdrive","application_name","")
config.set("gdrive","folder_id","")

with open("config.ini","w") as file:
    config.write(file)