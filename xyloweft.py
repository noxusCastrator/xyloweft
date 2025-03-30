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
device = 'cuda' if torch.cuda.is_available() else 'cpu'
def load_voice_model():
    voice_model=whisper.load_model('turbo').to(device)
    print("voice model loaded")
    return voice_model
current_dir = os.path.dirname(os.path.abspath(__file__))
json_store_location="C:\\Users\\Mark\\Desktop\\xyloweft\\object_system\\XyloMail"
voice_location="C:\\Users\\Mark\\Desktop\\xyloweft\\voices\\test.m4a"
#string=main.voice_to_str(main.voice_location)


def run():
    import main
    print("Successfully imported main.py")
    voice_model=load_voice_model()
    count=0
    client = genai.Client(api_key=gemini_api_key)
    chat = client.chats.create(model="gemini-2.0-flash")
    txt=[]
    jsons=[]
    with open(os.path.join(current_dir, 'education.json'), 'r', encoding='utf-8') as file_education:
        education = json.load(file_education)
    with open(os.path.join(current_dir, 'shape.json'), 'r', encoding='utf-8') as file_shape:
        shape = json.load(file_shape)
    question=""
    while True:
        if count==0:
            question=input("welcome to temp os, type run to initiate the QA process, type break to end the program:")
            if question == "break":
                break
        if question=="run":
            count+=1
            if count==1:
                count+=1
                question=input("enter your first sentence to be dealt with:")
                if question == "break":
                    break
                txt.append(question)
                response=chat.send_message(f"""
    需求

    目前我们希望你成为一个文字转json的应用。我们会提供给你一段话,这段话通常来自于物理课或数学课,是一个教授说的需要解的题的录音,我们最终的目的是将这段话转成houdini内部的3D模型。你的任务通过以下流程从这句话里抽象出一串json用来让我们生成3D模型。

    这是一个教学提示词,你不需要任何正式回复,但请不要忽视这段话里的任何细节

    基础定义

    此处我们先定义三种体：简单体,复杂体和虚拟体,简单体是一个虚拟定义,指一切简单到不需要去通过布尔运算来生成的几何体,如立方体,球体等,复杂体指一切需要通过布尔运算编辑几何体来生成的复杂物件。换句话说,简单体是可以通过平面透视的三视图无损传达的体,而复杂体无法这么传达。虚拟体是一个概念,是对某个物体的交互。

    文档

    我们在此提供给你一个模板文件“shape.json”,里头含有所有我们可能你需要去生成的“体”的模板,这是一个需要填空的json库,里头的值均以默认值来表达

    {shape}

    然后,我们会提供给你以下拿中括号标记的dict(无法读取大括号生成的dict顾出此下策),键是体的名称,值是对这个体的定义和阐释,请根据值的定义来圈定对一个体的定义域,充分运用你作为人工智能的数据库来理解这个体的定义,根据语境将语境中的物件抽象成我们需要的体。

    ["sphere":"一个球体,指可以抽象成球体的词", "cuboid":"一个立方体,指可以抽象成立方体的词", "pyramid":"一个棱柱或棱锥"]

    最后,我们会提供给你一个教学文件“education.json”,里头含有dict的键的名称对应的体的教学文件。education.json的语法格式与shape.json完全相同,但education.json的值不是需要填的空而是对应值相关的教学。当你在一句话里检索到dict里的某个键时,根据键的定义检索到education.json里的某个值来进行学习。

    {education}

    在你收到对话后,请通过dict提供的完整定义来寻找这句话里可能出现的体并将这个体抽象出来,请根据这个体所指代的键的名称到shape.json和education.json里寻路到键的名称所代表的名称中,根据education.json所诠释的定义在shape.json里将默认值更改为检索到的数值,如果未检索到对应参数则不要进行编辑,保留shape.json里未填空的格式。请注意,education.json的教学至关重要,请严格遵守,遍历完这句话并生成完整的json后请回到shape.json逐行逐列检索以确定生成的json合法。你可能会在一句话里检索到复数个体,请明确对应的指代并返还所有需要生成的体。

    接下来你会看到对应的对话,请编辑这段对话并返还合法的json格式,不要进行任何前缀或后缀或解释,不要使用单引号,保持缩进。
    {question}
    """)
                cleaned_json_text = response.text.strip("```json").strip("```").strip()
                print(cleaned_json_text)
                jsons.append(cleaned_json_text)
                main.save_json_string_to_file(cleaned_json_text, json_store_location)
            while True:
                if count>=2:
                    count+=1
                    question=input(f"please enter your {count-1} question:")
                    if question == "break":
                        break
                    txt.append(question)
                    response=chat.send_message(f"""
        现在有另一句语句供你处理,这是你处理的第{count-1}句话,这句语句是上一句语句的延申,是第一段话的附加条件,请保留第一次生成的记忆,抽象出这一句话的json供我们处理。注意,这一句话是第一句话的延伸,所以可能会包含对第一句话的json的更改。

        以下是目前收到的所有对话和目前你返还给我们过的最后一个json,请根据这些信息创造一个包含所有对话信息的新json。

        {txt}

        {jsons[-1]}

        """)
                    cleaned_json_text = response.text.strip("```json").strip("```").strip()
                    print(cleaned_json_text)
                    jsons.append(cleaned_json_text)
                    main.save_json_string_to_file(cleaned_json_text, json_store_location)
                    
        elif question=="break":
            break

run()

