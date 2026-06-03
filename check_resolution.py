import os
import cv2

image_path = r"C:/Users/19091/.gemini/antigravity/brain/tempmediaStorage/media__1780326071137.png"
if os.path.exists(image_path):
    img = cv2.imread(image_path)
    h, w, c = img.shape
    print(f"用户屏幕截图的物理分辨率为: {w}x{h}")
else:
    print("图片不存在！")
