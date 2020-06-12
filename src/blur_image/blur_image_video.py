import numpy as np
import argparse
import time
import cv2
import os
import ntpath

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True, help="path to input image")

args = vars(ap.parse_args())
net = cv2.dnn.readNet(os.path.abspath('./src/blur_image/face_detector/deploy.prototxt'), os.path.abspath('./src/blur_image/face_detector/res10_300x300_ssd_iter_140000.caffemodel'))

def blur_face_simple(image, factor=3.0):
	(h, w) = image.shape[:2]
	k_w = int(w / factor)
	k_h = int(h / factor)

	if k_w % 2 == 0:
		k_w -= 1

	if k_h % 2 == 0:
		k_h -= 1

	return cv2.GaussianBlur(image, (k_w, k_h), 0)

def blur_video(cap, out, confidence = 0.5, blocks = 20):
  while cap.isOpened():
    ret, frame = cap.read()

    if (ret):
      (h, w) = frame.shape[:2]
      blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), (104.0, 177.0, 123.0))

      net.setInput(blob)
      detections = net.forward()

      for i in range(0, detections.shape[2]):
        confidence_detected = detections[0, 0, i, 2]

        if confidence_detected > confidence:
          box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
          (start_x, start_y, end_x, end_y) = box.astype("int")

          face = frame[start_y:end_y, start_x:end_x]
          face = blur_face_simple(face, factor=3.0)

          frame[start_y:end_y, start_x:end_x] = face

      out.write(frame)
    else:
      break

head, tail = ntpath.split(args["image"])
name = tail or ntpath.basename(head)

cap = cv2.VideoCapture(args["image"])
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))

out = cv2.VideoWriter(
  os.path.abspath('./processed_files/{0}'.format(name)),
  cv2.VideoWriter_fourcc('m', 'p', '4', 'v'),
  10,
  (frame_width,frame_height)
)

blur_video(cap, out)

print(os.path.abspath('./processed_files/{0}'.format(name)))
print("video wrote")

