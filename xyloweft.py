import os
import sys
import json
from typing import Dict, Any
import ffmpeg
import whisper
import torch
from pathlib import Path
import random
from openai import OpenAI
from google import genai
from dotenv import load_dotenv
from datetime import datetime

print("----------------------------林肯斯大头----------------------------")

base_dir = os.path.abspath(os.path.dirname(__file__))
lib_dir = os.path.join(base_dir, "lib")
sys.path.append(lib_dir)
load_dotenv()#读取AI api key
o3_api_key = os.getenv("O3_API_KEY")#open AI api key
gemini_api_key = os.getenv("GEMINI_API_KEY")#gemini api key

#string=main.voice_to_str(main.voice_location)



def main():
    import main
    print("Successfully imported main.py")
    count=0
    client = genai.Client(api_key=gemini_api_key)
    chat = client.chats.create(model="gemini-2.0-flash")
    with open(os.path.join(current_dir, 'education.json'), 'r', encoding='utf-8') as file_education:
        education = json.load(file_education)
    with open(os.path.join(current_dir, 'shape.json'), 'r', encoding='utf-8') as file_shape:
        shape = json.load(file_shape)
    while True:
        x=input("welcome to temp os, type run to initiate the QA process, type break to end the program")
        if x=="run":
            count+=1
            if count==1:
            response_
            print("json")
            print("done")



        elif x=="break":
            break




