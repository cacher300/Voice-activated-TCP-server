import time
import sounddevice as sd
import queue
import vosk
import json
import socket

value = 0
HOST = '10.5.5.102'
PORT = 8888
response_A = '<A><111>'
response_B = "<A><112>"




data_dict = {
    "A": '<A><111>',
    "B": '<B><"str">',
    "C": "<C><[6,5,4,3,2,1]>"
}

q = queue.Queue()


def callback(indata, frames, time, status):
    q.put(bytes(indata))

def handle_request():
    return data_dict["A"]



def live_transcription():
    global value
    model = vosk.Model(r"C:\Users\Admin\Downloads\yo\vosk-model-small-en-us-0.15")

    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        print("Microphone is ready, start speaking!")
        rec = vosk.KaldiRecognizer(model, 16000)

        while True:
            data = q.get()

            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                transcript = result['text']

                print(f"You said: {transcript}")

                if "hello" in transcript.lower():
                    print("The word 'hello' was detected!")
                    value = 1
                    break
                if "bob" in transcript.lower():
                    print("The word 'bob' was detected!")
                    value = 2
                    break

            else:
                partial_result = json.loads(rec.PartialResult())
                print(f"Partial: {partial_result['partial']}")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"Server is listening on {HOST}:{PORT}")

    while True:
        try:
            conn, addr = server_socket.accept()
            with conn:
                print(f"Connected by {addr}")

                while True:
                    data = conn.recv(1024)
                    if not data:
                        print(f"Client {addr} disconnected")
                        break

                    decoded_data = data.decode('utf-8').strip()
                    print(f"Received from client: {decoded_data}")

                    live_transcription()
                    if value == 1:
                        response = response_A
                    else:
                        response = response_B
                    print(f"Sending response: {response}")



                    print("yo")

                    conn.sendall(response.encode('utf-8'))
                    time.sleep(1)
                    conn.sendall(response.encode('utf-8'))


        except ConnectionResetError as e:
            print(f"Connection was forcibly closed by the client. Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
