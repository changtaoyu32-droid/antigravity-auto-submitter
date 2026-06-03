import os
import cv2
import numpy as np

# 图片所在的 brain 目录和目标用户家目录
brain_dir = r"C:\Users\19091\.gemini\antigravity\brain\0aca2041-e63c-4328-877c-17a0917d1f3c"
user_home = os.path.expanduser('~')

# 设定蓝色的 HSV 范围（覆盖 VS Code 的两种亮蓝色）
lower_blue = np.array([90, 100, 100])
upper_blue = np.array([125, 255, 255])

# 需要提取的目标图片及其对应输出路径
targets = {
    "media__1780318498425.png": os.path.join(user_home, ".auto_submitter_template_submit.png"),
    "media__1780320054104.png": os.path.join(user_home, ".auto_submitter_template_retry.png")
}

def extract():
    print("=" * 60)
    print(" 正在执行智能特征提取算法...")
    print("=" * 60)
    
    for filename, dest in targets.items():
        src_path = os.path.join(brain_dir, filename)
        if not os.path.exists(src_path):
            print(f"[错误] 找不到用户截图文件: {filename}")
            continue
            
        # 读取截图
        img = cv2.imread(src_path)
        if img is None:
            print(f"[错误] 无法读取图片: {filename}")
            continue
            
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # 蓝色掩膜
        mask = cv2.inRange(hsv, lower_blue, upper_blue)
        
        # 查找外部轮廓
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        found = False
        # 按照面积从大到小排序，优先检测较大连通域
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            aspect_ratio = float(w) / h
            area = w * h
            
            # 按钮几何过滤：宽高比 1.5-4.5，面积在 800 - 15000 像素之间
            if 1.5 <= aspect_ratio <= 4.5 and 800 <= area <= 15000:
                # 适当外扩 2 像素边缘，确保捕获圆角及抗锯齿边界
                pad = 2
                x_start = max(0, x - pad)
                y_start = max(0, y - pad)
                x_end = min(img.shape[1], x + w + pad)
                y_end = min(img.shape[0], y + h + pad)
                
                # 裁剪并保存
                crop = img[y_start:y_end, x_start:x_end]
                cv2.imwrite(dest, crop)
                print(f"[SUCCESS] 成功从 {filename} 提取特征 -> {os.path.basename(dest)} (尺寸: {w}x{h})")
                found = True
                break
                
        if not found:
            print(f"[FAIL] 未能在 {filename} 中寻找到符合大小和蓝色的圆角按钮轮廓。")

if __name__ == "__main__":
    extract()
