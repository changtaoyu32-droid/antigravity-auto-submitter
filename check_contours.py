import os
import cv2
import numpy as np

brain_dir = r"C:\Users\19091\.gemini\antigravity\brain\0aca2041-e63c-4328-877c-17a0917d1f3c"
filename = "media__1780320054104.png"
src_path = os.path.join(brain_dir, filename)

img = cv2.imread(src_path)
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

lower_blue = np.array([90, 100, 100])
upper_blue = np.array([125, 255, 255])
mask = cv2.inRange(hsv, lower_blue, upper_blue)

contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
print(f"检测到 {len(contours)} 个蓝色区域的轮廓：")
for i, cnt in enumerate(contours):
    x, y, w, h = cv2.boundingRect(cnt)
    aspect_ratio = float(w) / h
    area = w * h
    print(f"轮廓 #{i}: 坐标=({x},{y}), 宽高=({w},{h}), 面积={area}, 宽高比={aspect_ratio:.2f}")
