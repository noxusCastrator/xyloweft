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
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

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

def run():
    import main
    print("Successfully imported main.py")
    voice_model=load_voice_model()
    count=0
    client = genai.Client(api_key=gemini_api_key)
    chat = client.chats.create(model="gemini-2.5-pro-exp-03-25")
    #chat = client.chats.create(model="gemini-2.0-flash")
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
                time=main.get_current_time()
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

    ["sphere":"一个球体,一个半圆绕直径所在直线旋转一周所成的空间几何体,任何可被抽象成球体的物件", "cuboid":"一个所有面等角的六面体,任何可被直接抽象成等角六面体的物体", "pyramid":"一个棱柱或棱锥"]

    最后,我们会提供给你一个教学文件“education.json”,里头含有dict的键的名称对应的体的教学文件。education.json的语法格式与shape.json完全相同,但education.json的值不是需要填的空而是对应值相关的教学。当你在一句话里检索到dict里的某个键时,根据键的定义检索到education.json里的某个值来进行学习。

    {education}

    在你收到对话后,请通过dict提供的完整定义来寻找这句话里可能出现的体并将这个体抽象出来,请根据这个体所指代的键的名称到shape.json和education.json里寻路到键的名称所代表的名称中,根据education.json所诠释的定义在shape.json里将默认值更改为检索到的数值,如果未检索到对应参数则不要进行编辑,保留shape.json里未填空的格式。请注意,education.json的教学至关重要,请严格遵守,遍历完这句话并生成完整的json后请回到shape.json逐行逐列检索以确定生成的json合法。你可能会在一句话里检索到复数个体,请明确对应的指代并返还所有需要生成的体。请在生成一个体时根据该体在dict里的定义理解该体的碰撞箱,当出现“贴着”“放在上面”“on”“beside”“under”之类的关键词时理解体之间所接触的面,隐性通过公式计算后提供正确提供几何体的位置,确保体和体之间不重叠但没有缝隙。
    例:生成一个半径为3的在0, 0, 0的球体,然后在它上面生成一个边长为4的与球体接触但不重叠的立方体。此时,根据时间顺序先生成球体,通过球体在dict的定义确定其碰撞箱是在0,0,0的半径为3的一个球体,因此想在球体的正上方生成一个接触但不重叠的立方体的话需要首先通过关键词“上面理解到球体的顶面要和立方体的底面接触但不重叠,因此你需要计算立方体的几何中心点到立方体与球的接触面的距离,在此情况下即4/2=2。因此,根据几何中心点需要的距离立方体应该被放置在0,5,0。遇到类似的需求时请以相似思路去思考。类似的情况如对角线和顶点接触也请逻辑思考后再放置体。
    同理,想在一个位于0,0,0的半径为5的球体的四个角各生成一个竖边与球体接触但不重叠的边长为10的立方体的话,请先理解“四个角”和“竖边”的定义,计算立方体的竖边和几何中心点的距离,然后计算球体碰撞箱,最后通过勾股定理确定立方体合理的摆放位置。思路雷同。

    同时,我们在此对一个json里的每个体的命名方式有所要求:详情格式为 [体的geotype的首字母大写,S为简单体,C为复杂体,V为虚拟体]_[体的type的首字母小写]_[体在这句话里出现的顺序,注意仅限于这句话]_[现在的时间,以下是现在的时间],如一个在30号15点34分40秒生成的第一个立方体会被其名为S_s_1_30153440

    {time}
    
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
                    time=main.get_current_time()
                    response=chat.send_message(f"""
        现在有另一句语句供你处理,这是你处理的第{count-1}句话,这句语句是上一句语句的延申,是第一段话的附加条件,请保留第一次生成的记忆,抽象出这一句话的json供我们处理。注意,这一句话是第一句话的延伸,所以可能会包含对第一句话的json的更改。

        以下是目前收到的所有对话和目前你返还给我们过的最后一个json,请根据这些信息创造一个包含所有对话信息的新json。请保持之前要求的命名规律,但请记住这是一句新的话,我会再次提供给你现在的时间,但也请从新从1数起

        {txt}

        {jsons[-1]}

        {time}

        """)
                    cleaned_json_text = response.text.strip("```json").strip("```").strip()
                    print(cleaned_json_text)
                    jsons.append(cleaned_json_text)
                    main.save_json_string_to_file(cleaned_json_text, json_store_location)
                    
        elif question=="break":
            break

run()

