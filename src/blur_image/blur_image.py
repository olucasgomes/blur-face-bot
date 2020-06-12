import numpy as np
from matplotlib import pyplot as plt
import ntpath
import cv2
import os
import argparse

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

def blur (image, confidence = 0.5, blocks = 20):
	blob = cv2.dnn.blobFromImage(image, 1.0, (300, 300), (104.0, 177.0, 123.0))
	net.setInput(blob)
	detections = net.forward()
	for i in range(0, detections.shape[2]):
		confidence_detected = detections[0, 0, i, 2]

		if confidence_detected > confidence:
			box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
			(start_x, start_y, end_x, end_y) = box.astype("int")

			face = image[start_y:end_y, start_x:end_x]
			face = blur_face_simple(face, factor=3.0)

			image[start_y:end_y, start_x:end_x] = face

image = cv2.imread(args["image"])
(h, w) = image.shape[:2]

blur(image)

head, tail = ntpath.split(args["image"])
name = tail or ntpath.basename(head)

cv2.imwrite(os.path.abspath('./processed_files/{0}'.format(name)), image)

print("image wrote")