import cv2
import os
import face_recognition
import numpy as np
import time
from collections import defaultdict
from dotenv import load_dotenv
import requests

API_ENDPOINT = os.getenv('API_ENDPOINT')

# 表示フラグ
DISPLAY_VIDEO = False
# 検知の最小間隔（秒）
DETECTION_INTERVAL = 30  
# 最後の検知時刻を記録する辞書
last_detection_times = defaultdict(float)

def post_to_api(name, timestamp):
    """検出した顔の情報をAPIにPOSTする"""
    try:
        data = {
            "name": name,
            "detected_at": timestamp
        }
        response = requests.post(API_ENDPOINT, json=data)
        if response.status_code == 200:
            print(f"APIへの送信成功: {name}")
        else:
            print(f"APIへの送信失敗: {response.status_code}")
    except Exception as e:
        print(f"APIエラー: {str(e)}")

# This is a demo of running face recognition on live video from your webcam. It's a little more complicated than the
# other example, but it includes some basic performance tweaks to make things run a lot faster:
#   1. Process each video frame at 1/4 resolution (though still display it at full resolution)
#   2. Only detect faces in every other frame of video.

# PLEASE NOTE: This example requires OpenCV (the `cv2` library) to be installed only to read from your webcam.
# OpenCV is *not* required to use the face_recognition library. It's only required if you want to run this
# specific demo. If you have trouble installing it, try any of the other demos that don't require it instead.

# Get a reference to webcam #0 (the default one)
video_capture = cv2.VideoCapture(0)

def load_known_faces():
    global known_face_encodings, known_face_names
    # 既存のデータをクリア
    known_face_encodings = []
    known_face_names = []
    
    # /data/input ディレクトリから画像を読み込む
    input_dir = "/data/input"
    for image_file in os.listdir(input_dir):
        if image_file.lower().endswith(('.png', '.jpg', '.jpeg')):
            # 画像ファイルのフルパス
            image_path = os.path.join(input_dir, image_file)
            # 画像を読み込み、顔エンコーディングを取得
            image = face_recognition.load_image_file(image_path)
            face_encodings = face_recognition.face_encodings(image)
            
            if len(face_encodings) > 0:
                # 最初に検出された顔を使用
                known_face_encodings.append(face_encodings[0])
                # ファイル名から拡張子を除いたものを名前として使用
                name = os.path.splitext(image_file)[0]
                known_face_names.append(name)
                print(f"Loaded face: {name}")

# 初回の顔データ読み込み
load_known_faces()

# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

while True:
    # Grab a single frame of video
    ret, frame = video_capture.read()

    # Only process every other frame of video to save time
    if process_this_frame:
        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]
        
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            # # If a match was found in known_face_encodings, just use the first one.
            # if True in matches:
            #     first_match_index = matches.index(True)
            #     name = known_face_names[first_match_index]

            # Or instead, use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]

                 # 現在時刻を取得
                current_time = time.time()
                # 前回の検知からの経過時間をチェック
                if current_time - last_detection_times[name] > DETECTION_INTERVAL:
                    last_detection_times[name] = current_time
                    face_names.append(name)
                    print(f"Detected face: {name}")
                    post_to_api(name, current_time)

                else:
                    # インターバル内は検知をスキップ
                    continue

            face_names.append(name)

    process_this_frame = not process_this_frame


    if DISPLAY_VIDEO:
        # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        # Display the resulting image
        cv2.imshow('Video', frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()