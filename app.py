from flask import Flask, jsonify, render_template, Response, request
import cv2
import numpy as np
import base64
import os
from dotenv import load_dotenv
import openai

application = Flask(__name__)
app = application

load_dotenv('.env')

api_key = os.getenv('OPEN_AI_KEY')
openai.api_key = api_key
cfg_path = 'yolov3.cfg'
weights_path = 'yolov3.weights'

if not os.path.exists(cfg_path):
    raise FileNotFoundError(f"{cfg_path} not found")

if not os.path.exists(weights_path):
    raise FileNotFoundError(f"{weights_path} not found")

net = cv2.dnn.readNetFromDarknet(cfg_path, weights_path)

layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

def process_frames(filePath):
    try:
        print("Outside process frames " + filePath)
        if filePath != '':
            print("In if process frames " + filePath)
            video = cv2.VideoCapture(filePath)
        else:
            raise Exception("File path must be specified")

        if not video.isOpened():
            raise Exception("Could not open video file")

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

        base64Frames = []
        if person_detected:
            try:
                print("Outside person_detected " + filePath)
                video = cv2.VideoCapture(filePath)
                if not video.isOpened():
                    raise Exception("Could not open video file")

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
                            "These are frames from a video that I want to upload. Categorize this video in crime or not crime. Do not make any text bold. If it is a crime generate a description. If crime is detected provide response with a title as Category: Crime. If crime is not detetcted then provide title as Category: Nothing to worry!",
                            *map(lambda x: {"image": x, "resize": 768}, base64Frames[0::50]),
                        ],
                    },
                ]

                result = openai.ChatCompletion.create(
                    model="gpt-4o",
                    messages=PROMPT_MESSAGES,
                    max_tokens=200
                )
                response_text = result.choices[0].message['content']
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


def process_frames_with_gpt(frames):
    try:
        base64Frames = []

        for frame in frames:
            _, buffer = cv2.imencode(".jpg", frame)
            base64Frames.append(base64.b64encode(buffer).decode("utf-8"))

        PROMPT_MESSAGES = [
            {
                "role": "user",
                "content": [
                    "These are frames from a video that I want to upload. Categorize this video in crime or not crime. Do not make any text bold. If it is a crime generate a description. If crime is detected provide response with a title as Category: Crime. If crime is not detected then provide title as Category: Nothing to worry!",
                    *map(lambda x: {"image": x, "resize": 768}, base64Frames[0::50]),
                ],
            },
        ]

        result = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=PROMPT_MESSAGES,
            max_tokens=200
        )

        response_text = result.choices[0].message['content']
        print(response_text)
        return jsonify({"message": response_text})
    except Exception as e:
        print(f"Error processing frames with GPT: {e}")
        return jsonify({"error": str(e)}), 500



@app.route('/process_webcam', methods=['POST'])
def process_webcam():
    try:
        camera = cv2.VideoCapture(0)  # Open webcam
        if not camera.isOpened():
            raise Exception("Could not open webcam")

        person_detected = False
        frames_to_process = []
        
        while True:
            ret, frame = camera.read()
            if not ret:
                print("Failed to capture image from webcam")
                break
            frame_resized = cv2.resize(frame, (416, 416))
            blob = cv2.dnn.blobFromImage(frame_resized, scalefactor=1/255.0, size=(416, 416), swapRB=True, crop=False)
            net.setInput(blob)
            outs = net.forward(output_layers)
            for out in outs:
                for detection in out:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]
                    if confidence > 0.5 and class_id == 0:
                        person_detected = True
                        frames_to_process.append(frame)
                        break
                if person_detected:
                    break
            if person_detected and len(frames_to_process) >= 5:
                break

        camera.release()

        if person_detected:
            print("Person detected from webcam. Processing frames with GPT-4...")
            return process_frames_with_gpt(frames_to_process)
        else:
            return jsonify({"message": "No person detected in webcam video"})
    except cv2.error as e:
        print(f"OpenCV error: {e}")
        return jsonify({"error": f"OpenCV error: {e}"}), 500
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

def gen_frames():
    camera = cv2.VideoCapture(0)  # use 0 for web camera
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/process_video_sent', methods=['POST'])
def send_path():
    data = request.get_json()
    print(data)
    if not data:
        return jsonify({"error": "No data provided"}), 400
    return process_frames(data.get('file_path', ''))

@app.route('/process_webcam_frame', methods=['POST'])
def process_webcam_frame():
    data = request.get_json()
    frame_data = data.get('frame')
    if not frame_data:
        return jsonify({"error": "No frame data provided"}), 400
    return process_frame_from_webcam(frame_data)

def process_frame_from_webcam(frame_data):
    try:
        frame = base64.b64decode(frame_data.split(',')[1])
        np_frame = np.frombuffer(frame, dtype=np.uint8)
        img = cv2.imdecode(np_frame, cv2.IMREAD_COLOR)
        frame_resized = cv2.resize(img, (416, 416))
        blob = cv2.dnn.blobFromImage(frame_resized, scalefactor=1/255.0, size=(416, 416), swapRB=True, crop=False)
        net.setInput(blob)
        outs = net.forward(output_layers)
        person_detected = False
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5 and class_id == 0:
                    person_detected = True
                    break
            if person_detected:
                break
        if person_detected:
            return jsonify({"message": "Person detected"})
        else:
            return jsonify({"message": "No person detected"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
