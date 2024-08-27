from flask import Flask, request, jsonify
import edge_tts
import subprocess
import time
import threading

app = Flask(__name__)

TEXT = 'Hello World! How are you guys doing? I hope great, cause I am having fun and honestly it has been a blast'
VOICE = "en-US-AndrewMultilingualNeural"

@app.route('/speak', methods=['POST'])
def speak():
    def stream_to_mpv(communicator):
        try:
            # Start mpv process
            mpv_process = subprocess.Popen(
                ["mpv", "--no-cache", "--no-terminal", "--", "fd://0"],
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            for chunk in communicator.stream_sync():
                if chunk["type"] == "audio" and chunk["data"]:
                    mpv_process.stdin.write(chunk["data"])
                    mpv_process.stdin.flush()
            
            mpv_process.stdin.close()
            mpv_process.wait()
        
        except BrokenPipeError:
            pass

    def handle_request(text, voice):
        communicator = edge_tts.Communicate(text, voice)
        start_time = time.time()
        
        # Start streaming in a separate thread
        stream_thread = threading.Thread(target=stream_to_mpv, args=(communicator,))
        stream_thread.start()
        stream_thread.join()

        return f"Audio streaming completed in {time.time() - start_time:.2f} seconds."

    data = request.get_json()
    text = data.get('text', TEXT)
    voice = data.get('voice', VOICE)

    result = handle_request(text, voice)
    return jsonify({"message": result})

if __name__ == "__main__":
    app.run(host='192.168.3.151',port='7878')
