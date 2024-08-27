
import os
import asyncio
import edge_tts
from flask import Flask, Response, jsonify, request, send_file
from flask_cors import CORS

# Define the directory and ensure it exists
AUDIO_DIR = "/home/haloocom/Bots/shriram/Nre-early-debit"
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

# Use the directory for the default output file
DEFAULT_OUTPUT_FILE = os.path.join(AUDIO_DIR, "test.mp3")

app = Flask(__name__)
CORS(app, supports_credentials=True)


async def stream_audio(text, voice) -> None:
    communicate = edge_tts.Communicate(text, voice)
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            yield chunk["data"]


def audio_generator(text, voice):
    loop = asyncio.new_event_loop()
    coroutine = stream_audio(text, voice)
    while True:
        try:
            chunk = loop.run_until_complete(coroutine.__anext__())
            yield chunk
        except StopAsyncIteration:
            break


def make_response(code, message, data=None):
    response = {
        'code': code,
        'message': message,
    }
    if data is not None:
        response['data'] = data
    return jsonify(response)


@app.route('/tts', methods=['POST'])
async def tts():
    data = request.get_json()
    text = data['text']
    voice = data.get('voice', 'zh-CN-YunxiNeural')
    file_name = data.get('file_name', 'output.mp3')

    # Ensure the file path includes the directory
    file_path = os.path.join(AUDIO_DIR, file_name)

    # Save the TTS to a file
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(file_path)
    
    # Return the full path and filename in one key
    # return make_response(200, 'File created successfully', {
    #     'file_path/filename': file_path
    # })
    return file_name


@app.route('/tts/stream', methods=['POST'])
async def stream_audio_route():
    data = request.get_json()
    text = data['text']
    voice = data.get('voice', 'zh-CN-YunxiNeural')

    return Response((audio_generator(text, voice)), content_type='application/octet-stream')


@app.route('/voices', methods=['GET'])
async def voices():
    try:
        voices = await edge_tts.list_voices()
        return make_response(200, 'OK', voices)
    except Exception as e:
        return make_response(500, str(e))


if __name__ == "__main__":
    app.run(host='192.168.3.151',port=7777)