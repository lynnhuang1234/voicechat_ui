import os
import streamlit as st
from audio_recorder_streamlit import audio_recorder
import base64
import requests
# import asyncio
# import pyaudio 
# from tts_ws_client import TTSWsHandler
# from ws_multi_round_chat import func
# import whisper
from openai import OpenAI
API_KEY = st.secrets["OPENAI_API_KEY"]
# address info for ASR and TTS servers
IP = '121.196.204.181'
PORT = 8192

# def callback(in_data, frame_count = 208, time_info, status):
#     global data_bytes
#     data_bytes += in_data
#     return b"", pyaudio.paContinue

def transcribe_text_to_voice(audio_location):
    client = OpenAI(api_key=API_KEY)
    # model = whisper.load_model("tiny")
    audio_file= open(audio_location, "rb")
    # result = model.transcribe(audio_location, language='Chinese')
    transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
    return transcript.text
    # return result["text"]

# def transcribe_text_to_voice(audio_location):
#     audio = pyaudio.PyAudio()
#     pformat = pyaudio.paInt16
#     channels = 1
#     rate = 16000
#     stream = audio.open(
#         format=pformat,
#         channels=channels,
#         rate=rate,
#         input=True,
#         stream_callback=callback
#     )
#     stream.start_stream()

#     url = f"ws://{IP}:{PORT}"
#     asyncio.run(func(url))

#     stream.stop_stream()
#     return text

def chat_completion_call(user_input, isend):
    # voiceflow dialog API key
    api_key = "VF.DM.65743e7b227e5e000821cefc.MymOmL30eiCrQ7kL"
    # Unique ID used to track conversation state
    user_id = "user_1256789101254678"
    body = {"action": {"type": "text", "payload": user_input}}

    # Start a conversation
    response = requests.post(
        f"https://general-runtime.voiceflow.com/state/user/{user_id}/interact",
        json=body,
        headers={"Authorization": api_key},
    )

    # Log the response
    js = response.json()
    answer = ''
    for i, element in enumerate(js):
        if element['type'] == 'text':
            answer += element['payload']['message']
        if element['type'] == 'end':
            isend = True
            break

    if response.status_code == 200:
        answer = answer.replace('滴答','嘀嗒')
    else:
        answer = "智能客服没有回应，请重试"
    return answer, isend

def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio controls autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(
            md,
            unsafe_allow_html=True,
        )

def text_to_speech_ai(speech_file_path, api_response):
    # tts = TTSWsHandler(IP, port=int(PORT), play=True) 
    # if api_response.strip() != "":
    #     asyncio.run(tts.run(api_response, output=speech_file_path)) 
    client = OpenAI(api_key=API_KEY)
    response = client.audio.speech.create(model="tts-1",voice="shimmer",input=api_response)
    response.stream_to_file(speech_file_path)

    # print("一轮结束")
    # autoplay_audio(speech_file_path)

# st.write("# Auto-playing Audio!")

# autoplay_audio("local_audio.mp3")

st.title("TalkCustomer")

"""
你好，我是你的客服助手！请点击话筒，开始你的提问。注意：如果重复返回“转接人工客服”，请说“没有了”，来结束对话。
"""

# init the data
text = ""
ended = False
data_bytes = b''  
rec_message = ""     
isend = False

audio_bytes = audio_recorder()
if audio_bytes:
    ##Save the Recorded File
    audio_location = "audio_file.wav"
    with open(audio_location, "wb") as f:
        f.write(audio_bytes)

    #Transcribe the saved file to text
    text = transcribe_text_to_voice(audio_location)
    # print(text.keys())
    if text.strip() == "":
        st.write("没说话，结束")
    else:
        st.write(text)
    user_input = text.strip()

    #Use API to get an AI response
    api_response, isend = chat_completion_call(user_input,isend)
    st.write(api_response)
    if isend:
        st.write("多轮对话结束！")

    # Read out the text response using tts
    speech_file_path = 'audio_response.mp3'
    text_to_speech_ai(speech_file_path, api_response)
    autoplay_audio(speech_file_path)


