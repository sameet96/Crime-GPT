import cv2
import numpy as np
import base64
import openai
from IPython.display import display, Image, Audio
import time
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load the environment variables from the .env file
load_dotenv('.env')

# Now you can access the environment variables
api_key = os.getenv('OPEN_AI_KEY')
client = OpenAI(api_key=api_key)

# Load the YOLO model
net = cv2.dnn.readNetFromDarknet('/Users/sameet/Crime GPT/yolov3/yolov3.cfg', '/Users/sameet/Crime GPT/yolov3/yolov3.weights')

# Get the output layer names
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

# Open the webcam
video = cv2.VideoCapture(0)  # 0 is the default camera

# Flag to indicate if a person is detected
person_detected = False

# Loop through the frames from the webcam
while True:
    # Read the frame
    ret, frame = video.read()
    if not ret:
        print("Failed to capture image")
        break

    # Resize the frame
    frame_resized = cv2.resize(frame, (416, 416))
    
    # Convert the frame to a blob
    blob = cv2.dnn.blobFromImage(frame_resized, 1/255, (416, 416), swapRB=True, crop=False)
    
    # Set the input to the network
    net.setInput(blob)
    
    # Forward pass through the network
    outs = net.forward(output_layers)
    
    # Process the outputs
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5 and class_id == 0:  # Person class
                person_detected = True  # Set the flag to True if a person is detected
                break  # Exit the loop as a person is detected
        if person_detected:
            break  # Exit the loop as a person is detected

    # Display the frame in a window
    cv2.imshow('Webcam Feed', frame)
    
    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
    if person_detected:
        break  # Exit the main loop as a person is detected

# If a person is detected, process the video frames for categorization
if person_detected:
    # Reopen the webcam to process frames from the beginning
    video = cv2.VideoCapture(0)  # 0 is the default camera

    # Set the start and end time for trimming
    start_time = 0  # Start time in seconds
    end_time = 7  # End time in seconds

    # Convert time to frame indices
    fps = video.get(cv2.CAP_PROP_FPS)
    start_frame = int(start_time * fps)
    end_frame = int(end_time * fps)

    # Read and discard frames until the start frame
    for _ in range(start_frame):
        success, _ = video.read()
        if not success:
            break

    # Read and process frames within the desired range
    base64Frames = []
    for _ in range(start_frame, end_frame):
        success, frame = video.read()
        if not success:
            break
        _, buffer = cv2.imencode(".jpg", frame)
        base64Frames.append(base64.b64encode(buffer).decode("utf-8"))

    video.release()
    print(len(base64Frames), "frames read.")

    # Prepare the prompt messages
    PROMPT_MESSAGES = [
        {
            "role": "user",
            "content": [
                "These are frames from a video that I want to upload. Categorize this video in crime or not crime. If it is a crime generate a description",
                *map(lambda x: {"image": x, "resize": 768}, base64Frames[0::50]),
            ],
        },
    ]
    params = {
        "model": "gpt-4o",
        "messages": PROMPT_MESSAGES,
        "max_tokens": 200,
    }

    # Send the request to the GPT-4 model
    result = client.chat.completions.create(**params)
    print(result.choices[0].message.content)

# Release the video capture and close the windows
video.release()
cv2.destroyAllWindows()
