## Run this file in terminal using the command: python app.py


from flask import Flask, jsonify, render_template, Response, request
import cv2
import numpy as np
import base64
import os
from dotenv import load_dotenv
import openai
from openai import OpenAI

app = Flask(__name__)

load_dotenv('.env')

api_key = os.getenv('OPEN_AI_KEY')
openai.api_key = api_key
# net = cv2.dnn.readNetFromDarknet('/Users/sameet/Projects/Crime-GPT/yolov3/yolov3.cfg', '/Users/sameet/Projects/Crime-GPT/yolov3/yolov3.weights')
net = cv2.dnn.readNetFromDarknet('yolov3.cfg', 'yolov3.weights')

layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

def generate_frames():
    video = cv2.VideoCapture(0)
    if not video.isOpened():
        raise Exception("Could not open video device")

    while True:
        success, frame = video.read()
        if not success:
            break

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def process_frames(filePath):
    try:
        print("Outside process frames"+filePath)
        if filePath != '':
            print("In if process frames"+filePath)
            video = cv2.VideoCapture(filePath)
        else:
            video = cv2.VideoCapture(0)  

        if not video.isOpened():
            raise Exception("Could not open video device")

        person_detected = False

        while True:
            try:
                ret, frame = video.read()
                if not ret:
                    print("Failed to capture image")
                    break

                frame_resized = cv2.resize(frame, (416, 416))

                blob = cv2.dnn.blobFromImage(frame_resized, scalefactor=1/255.0, size=(416, 416), swapRB=True, crop=False)

                net.setInput(blob)

                outs = net.forward(output_layers)

                person_detected = False
                for out in outs:
                    for detection in out:
                        scores = detection[5:]
                        class_id = np.argmax(scores)
                        confidence = scores[class_id]
                        # print(f"Detection: class_id={class_id}, confidence={confidence}")
                        if confidence > 0.5 and class_id == 0: 
                            person_detected = True  
                            break
                    if person_detected:
                        break

                if person_detected:
                    break  
            except cv2.error as e:
                print(f"OpenCV error: {e}")
                break
            except Exception as e:
                print(f"Error processing frame: {e}")
                break

        # If a person is detected, process the video frames for categorization
        base64Frames = []
        if person_detected:
            try:
                print("Outside person_detected"+filePath)
                if filePath != '':
                    print("In if person_detected"+filePath)
                    video = cv2.VideoCapture(filePath)
                else:
                    video = cv2.VideoCapture(0)   

                if not video.isOpened():
                    raise Exception("Could not open video device")

                # Set the start and end time for trimming GPT-4o do have a limitation so I personally suggest 1 miniute or less
                start_time = 0  
                end_time = 7  

                fps = video.get(cv2.CAP_PROP_FPS)
                start_frame = int(start_time * fps)
                end_frame = int(end_time * fps)

                for _ in range(start_frame):
                    success, _ = video.read()
                    if not success:
                        break

                for _ in range(start_frame, end_frame):
                    success, frame = video.read()
                    if not success:
                        break
                    _, buffer = cv2.imencode(".jpg", frame)
                    base64Frames.append(base64.b64encode(buffer).decode("utf-8"))

                video.release()
                print(len(base64Frames), "frames read.")

                PROMPT_MESSAGES = [
                    {
                        "role": "user",
                        "content": [
                            "These are frames from a video that I want to upload. Categorize this video in crime or not crime. Do not make any text bold. If it is a crime generate a description. If crime is detected provide response with a title asCategory: Crime. If crime is not detetcted then provide title as Category: Nothing to worry!",
                            *map(lambda x: {"image": x, "resize": 768}, base64Frames[0::50]),
                        ],
                    },
                ]
                params = {
                    "model": "gpt-4o",
                    "messages": PROMPT_MESSAGES,
                    "max_tokens": 200,
                }

                api_key = os.getenv('OPEN_AI_KEY')
                client = OpenAI(api_key=api_key)
                result = client.chat.completions.create(**params)
                response_text = (result.choices[0].message.content)
                print(response_text)

                return jsonify({"message": response_text})
            except cv2.error as e:
                print(f"OpenCV error: {e}")
                return jsonify({"error": f"OpenCV error: {e}"}), 500
            except Exception as e:
                print(f"Error processing frames: {e}")
                return jsonify({"error": f"Error processing frames: {e}"}), 500
        else:
            return jsonify({"message": "No person detected"})
    except cv2.error as e:
        print(f"OpenCV error: {e}")
        return jsonify({"error": f"OpenCV error: {e}"}), 500
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/process_video', methods=['POST'])
def process_video():
    return process_frames('')

@app.route('/process_video_sent',methods=['POST'])
def send_path():
    data = request.get_json()
    print(data)
    if not data:
        return jsonify({"error": "No data provided"}), 400
    return process_frames(data)   

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
