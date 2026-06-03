import os
import sys
import time
from datetime import datetime
import subprocess

# 1. 依赖库自动检查和安装
def install_dependencies():
    print("[环境] 正在检查并自动安装缺失的依赖库，请稍候...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "pyautogui", "keyboard", "opencv-python", "pillow", "--quiet", "--disable-pip-version-check"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print("[环境] 依赖库检查/安装成功！")
    except Exception as e:
        print(f"[错误] 自动安装依赖失败，请手动运行命令: pip install pyautogui keyboard opencv-python pillow")
        print(f"错误信息: {e}")
        input("按回车键退出...")
        sys.exit(1)

# 尝试导入所需库，若失败则自动安装
try:
    import cv2
    import numpy as np
    import pyautogui
    import keyboard
    from PIL import Image
except ImportError:
    install_dependencies()
    import cv2
    import numpy as np
    import pyautogui
    import keyboard

import ctypes
from ctypes import wintypes

# 强行声明 Windows DPI 兼容性，使 Python 进程直接对齐物理像素
try:
    ctypes.windll.user32.SetProcessDPIAware()
except Exception:
    pass

# Win32 API 常量定义
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
MK_LBUTTON = 0x0001

# Win32 键盘常量定义
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
VK_RETURN = 0x0D

class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]

# 设定蓝色的 HSV 范围（大幅度放宽，覆盖各种主题下的亮蓝、灰蓝、淡蓝）
lower_blue = np.array([85, 40, 40])
upper_blue = np.array([135, 255, 255])

exit_flag = False
is_paused = False  # 全局暂停标志

def get_active_window_rect_and_title():
    """使用 Win32 原生 API 获取当前最前台活动窗口的 Rect 和标题，保证 100% 成功率与进程穿透性"""
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        if not hwnd:
            return None, ""
            
        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
        title = ""
        if length > 0:
            buffer = ctypes.create_unicode_buffer(length + 1)
            ctypes.windll.user32.GetWindowTextW(hwnd, buffer, length + 1)
            title = buffer.value.lower()
            
        rect = wintypes.RECT()
        if ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect)):
            return (rect.left, rect.top, rect.right, rect.bottom), title
    except Exception:
        pass
    return None, ""

def is_point_in_windows(x, y, window_list):
    """判断某个物理坐标 (x, y) 是否落在白名单开发窗口的边界范围内"""
    for (left, top, right, bottom) in window_list:
        if left <= x <= right and top <= y <= bottom:
            return True
    return False

def toggle_pause():
    """切换暂停与恢复状态"""
    global is_paused
    is_paused = not is_paused
    status_str = "[暂停] 已暂停自动监控 (按 + 键可随时恢复)" if is_paused else "[恢复] 已恢复自动监控"
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] [状态] {status_str}")

def background_click(x, y):
    """尝试使用 Windows 底层消息通道直接投递点击指令，物理鼠标指针完全不动"""
    try:
        user32 = ctypes.windll.user32
        pt = POINT(x, y)
        
        # 1. 查找包含该坐标的 Windows 窗口句柄
        hwnd = user32.WindowFromPoint(pt)
        if not hwnd:
            return False
            
        # 2. 将屏幕坐标转换为该窗口的客户区相对坐标
        user32.ScreenToClient(hwnd, ctypes.byref(pt))
        
        # 3. 构造 Windows 消息坐标参数
        lParam = (pt.y << 16) | (pt.x & 0xFFFF)
        
        # 4. 投递鼠标按下和弹起的消息
        user32.PostMessageW(hwnd, WM_LBUTTONDOWN, MK_LBUTTON, lParam)
        time.sleep(0.05)
        user32.PostMessageW(hwnd, WM_LBUTTONUP, 0, lParam)
        return True
    except Exception as e:
        print(f"[警告] 发送 Win32 后台点击消息失败: {e}")
        return False

def background_enter(x, y):
    """尝试向坐标所在的窗口直接投递键盘回车（Enter）按键消息"""
    try:
        user32 = ctypes.windll.user32
        pt = POINT(x, y)
        hwnd = user32.WindowFromPoint(pt)
        if not hwnd:
            return False
            
        # 投递回车键按下和弹起的消息
        user32.PostMessageW(hwnd, WM_KEYDOWN, VK_RETURN, 0)
        time.sleep(0.05)
        user32.PostMessageW(hwnd, WM_KEYUP, VK_RETURN, 0xC0000001)
        return True
    except Exception as e:
        print(f"[警告] 发送 Win32 后台回车按键失败: {e}")
        return False

def check_geometry(w, h, aspect_ratio, area):
    """校验按钮的几何特征是否符合预期，若不符合返回具体原因"""
    if not (1.2 <= aspect_ratio <= 6.0):
        return f"宽高比 {aspect_ratio:.2f} 不在 [1.2, 6.0] 范围内"
    if not (30 <= w <= 400):
        return f"宽度 {w} 不在 [30, 400] 像素范围内"
    if not (12 <= h <= 120):
        return f"高度 {h} 不在 [12, 120] 像素范围内"
    if not (300 <= area <= 50000):
        return f"面积 {area} 不在 [300, 50000] 像素范围内"
    return None

def find_blue_buttons(diagnose=False):
    """使用 OpenCV 智能检索全屏幕中的亮蓝色圆角按钮"""
    try:
        screenshot = pyautogui.screenshot()
        img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # 生成蓝色掩膜
        mask = cv2.inRange(hsv, lower_blue, upper_blue)
        
        # 提取外部边缘轮廓
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        buttons = []
        for cnt in contours:
            x_rel, y_rel, w, h = cv2.boundingRect(cnt)
            aspect_ratio = float(w) / h
            area = w * h
            
            abs_cx = x_rel + (w // 2)
            abs_cy = y_rel + (h // 2)
            
            geom_error = check_geometry(w, h, aspect_ratio, area)
            
            btn_data = {
                "abs_center": (abs_cx, abs_cy),
                "rel_box": (x_rel, y_rel, w, h),
                "size": (w, h),
                "aspect_ratio": aspect_ratio,
                "area": area,
                "geom_error": geom_error
            }
            
            if diagnose:
                buttons.append(btn_data)
            else:
                if geom_error is None:
                    buttons.append(btn_data)
        return buttons
    except Exception:
        return []

def execute_click_with_fallback(btn_info):
    """底层消息点击 + 静默回车 + 物理激活与 Enter 按键强送 的三层保障方案"""
    cx, cy = btn_info["abs_center"]
    
    # 第一层：后台静默直接点击
    background_click(cx, cy)
    time.sleep(0.05)
    
    # 第二层：后台静默回车投递
    background_enter(cx, cy)
    
    # 等待 0.35 秒，等窗口和渲染树更新
    time.sleep(0.35)
    
    # 重新检测该按钮是否依然存在
    recheck_btns = find_blue_buttons()
    still_exists = False
    for r_btn in recheck_btns:
        rcx, rcy = r_btn["abs_center"]
        if abs(rcx - cx) < 15 and abs(rcy - cy) < 15:
            still_exists = True
            break
            
    if still_exists:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [警告] 静默确认未生效，执行 1:1 DPI 物理激活并强送物理 Enter 回车...")
        orig_x, orig_y = pyautogui.position()
        
        pyautogui.click(cx, cy)
        time.sleep(0.1)
        
        pyautogui.press('enter')
        pyautogui.moveTo(orig_x, orig_y)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [成功] 物理激活与物理 Enter 模拟执行完毕。")
    else:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [成功] 后台静默确认已成功完成。")

def monitor_loop(is_silent=False):
    """按钮监控主循环"""
    global exit_flag, is_paused
    
    try:
        keyboard.add_hotkey('+', toggle_pause, suppress=False)
    except Exception as e:
        if not is_silent:
            print(f"[警告] 注册键盘暂停快捷键失败: {e}")
            
    if not is_silent:
        print("\n[监控] 智能自适应全屏扫描已开启。")
        print("正在持续扫描屏幕以定位 [Submit] 或 [Retry] 按钮...")
        print("已启用安全双重保险: 任务栏坐标避让 + 前台开发窗口限定")
        print("=" * 60)
        
    last_diagnose_time = 0
    screen_width, screen_height = pyautogui.size()
    
    while not exit_flag:
        try:
            if is_paused:
                time.sleep(0.5)
                continue
                
            all_detected = find_blue_buttons(diagnose=True)
            valid_btns = [b for b in all_detected if b["geom_error"] is None]
            
            valid_btn_found = False
            if len(valid_btns) > 0:
                # 获取当前处于前台焦点的窗口
                active_rect, active_title = get_active_window_rect_and_title()
                
                # 检查前台活动窗口是否属于白名单开发工具
                keywords = ["visual studio code", "vscode", "cursor", "windsurf", "antigravity", "反重力", "自动提交"]
                is_active_dev = any(kw in active_title for kw in keywords) if active_title else False
                
                for btn in valid_btns:
                    cx, cy = btn["abs_center"]
                    w, h = btn["size"]
                    
                    # 第一重保险：避让屏幕最底部的 Windows 任务栏区域（天气栏、右下角系统托盘），防止误触
                    if cy > (screen_height - 75):
                        continue
                        
                    # 第二重保险：前台活动窗口约束
                    # 如果用户当前正在反重力/VS Code中编写代码或挂机运行：按钮坐标必须在前台窗口的矩形范围内
                    # 如果当前最前台不是反重力/VS Code（比如切去浏览器查资料），则进入安全退避，暂时不点击，100%防误触
                    if is_active_dev and active_rect:
                        left, top, right, bottom = active_rect
                        if not (left - 5 <= cx <= right + 5 and top - 5 <= cy <= bottom + 5):
                            continue
                    elif not is_active_dev:
                        # 活动窗口是非开发类窗口，暂时静默忽略
                        continue
                        
                    # 通过所有安全策略，执行点击
                    if not is_silent:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] [定位] 成功定位到开发窗口范围内的目标按钮! 坐标: ({cx}, {cy})，尺寸: {w}x{h}")
                    execute_click_with_fallback(btn)
                    valid_btn_found = True
                    break
            
            # 前台测试模式下的诊断限频输出
            if not is_silent and not valid_btn_found and (time.time() - last_diagnose_time > 3.0):
                filtered_btns = [b for b in all_detected if b["geom_error"] is not None]
                active_rect, active_title = get_active_window_rect_and_title()
                keywords = ["visual studio code", "vscode", "cursor", "windsurf", "antigravity", "反重力", "自动提交"]
                is_active_dev = any(kw in active_title for kw in keywords) if active_title else False
                
                taskbar_filtered = 0
                bg_filtered = 0
                
                for btn in valid_btns:
                    cx, cy = btn["abs_center"]
                    if cy > (screen_height - 75):
                        taskbar_filtered += 1
                    elif not is_active_dev:
                        bg_filtered += 1
                    elif active_rect:
                        left, top, right, bottom = active_rect
                        if not (left - 5 <= cx <= right + 5 and top - 5 <= cy <= bottom + 5):
                            bg_filtered += 1
                            
                if taskbar_filtered > 0 or bg_filtered > 0:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] [安全] 拦截到 {taskbar_filtered} 个系统任务栏蓝色色块，拦截到 {bg_filtered} 个非前台活动开发窗口的疑似色块。")
                    
                if len(filtered_btns) > 0:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] [诊断] 屏幕上存在 {len(filtered_btns)} 个被几何条件过滤的蓝色块:")
                    for idx, fb in enumerate(filtered_btns[:2]):
                        cx, cy = fb["abs_center"]
                        w, h = fb["size"]
                        print(f"  - 疑似块 #{idx+1}: 中心({cx}, {cy}), 宽高({w}x{h}), 过滤原因: {fb['geom_error']}")
                    last_diagnose_time = time.time()
                        
            if valid_btn_found:
                time.sleep(2.0)
            else:
                time.sleep(0.5)
        except KeyboardInterrupt:
            if not is_silent:
                print("\n[调试] 检测到退出信号，正在停止前台测试...")
            break
        except Exception:
            time.sleep(1.0)
            
    try:
        keyboard.unhook_all()
    except Exception:
        pass

def kill_other_instances():
    """杀掉其它正在运行的监控后台实例"""
    current_pid = os.getpid()
    powershell_cmd = (
        f"Get-CimInstance Win32_Process -Filter \"CommandLine like '%auto_submitter.py%--service%'\" | "
        f"ForEach-Object {{ if ($_.ProcessId -ne {current_pid}) {{ Stop-Process -Id $_.ProcessId -Force }} }}"
    )
    subprocess.run(["powershell", "-Command", powershell_cmd], capture_output=True)

def start_background_service():
    """启动后台静默进程"""
    kill_other_instances()
    script_path = os.path.abspath(__file__)
    cmd = f"Start-Process python -ArgumentList '-u \"{script_path}\" --service' -WindowStyle Hidden"
    subprocess.run(["powershell", "-Command", cmd], capture_output=True)
    print("\n[成功] 自动提交服务已成功在后台启动！")
    print("       (它将在后台静默工作，不打扰您的正常操作。)")
    time.sleep(1.5)

def stop_background_service():
    """关闭后台进程"""
    kill_other_instances()
    print("\n[成功] 自动提交后台监控服务已成功关闭！")
    time.sleep(1.5)

def set_startup(enable=True):
    """设置或取消开机自动启动"""
    startup_file = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs", "Startup", "auto_submit_start.bat")
    if enable:
        script_path = os.path.abspath(__file__)
        content = (
            "@echo off\n"
            "chcp 65001 > nul\n"
            f'powershell -Command "Start-Process python -ArgumentList \'-u \\"{script_path}\\" --service\' -WindowStyle Hidden"\n'
        )
        try:
            with open(startup_file, "w", encoding="utf-8") as f:
                f.write(content)
            print("\n[成功] 开机自启配置成功！")
            print("       (以后每次开机登录 Windows，该服务都将自动在后台挂起工作。)")
        except Exception as e:
            print(f"\n[错误] 开机自启配置失败: {e}")
    else:
        if os.path.exists(startup_file):
            try:
                os.remove(startup_file)
                print("\n[成功] 已成功移除了开机自启配置。")
            except Exception as e:
                print(f"\n[错误] 移除开机自启配置失败: {e}")
        else:
            print("\n[提示] 之前并未配置过开机自启。")
    time.sleep(1.5)

def generate_diagnose_report():
    """一键生成屏幕诊断分析报告及标记后的截图"""
    print("\n[诊断] 正在生成屏幕诊断报告，请确保此时屏幕上正显示着 [Submit] 或 [Retry] 按钮...")
    try:
        screenshot = pyautogui.screenshot()
        img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        mask = cv2.inRange(hsv, lower_blue, upper_blue)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        active_rect, active_title = get_active_window_rect_and_title()
        keywords = ["visual studio code", "vscode", "cursor", "windsurf", "antigravity", "反重力", "自动提交"]
        is_active_dev = any(kw in active_title for kw in keywords) if active_title else False
        
        diagnose_img = img.copy()
        screen_width, screen_height = pyautogui.size()
        
        report_lines = []
        report_lines.append("=== 自动点击与重试工具诊断报告 ===")
        report_lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"屏幕物理分辨率: {img.shape[1]}x{img.shape[0]}")
        report_lines.append(f"当前最前台活动窗口: Title=\"{active_title}\"")
        if active_rect:
            report_lines.append(f"  - 前台窗口范围: Left={active_rect[0]}, Top={active_rect[1]}, Right={active_rect[2]}, Bottom={active_rect[3]}")
        report_lines.append(f"  - 最前台是否属于开发工具白名单: {'是' if is_active_dev else '否'}")
            
        report_lines.append(f"\n检测到符合 HSV 蓝色区间的色块数量: {len(contours)}")
        
        match_count = 0
        for idx, cnt in enumerate(contours):
            x, y, w, h = cv2.boundingRect(cnt)
            aspect_ratio = float(w) / h
            area = w * h
            cx = x + (w // 2)
            cy = y + (h // 2)
            
            geom_error = check_geometry(w, h, aspect_ratio, area)
            
            # 安全逻辑检测
            in_taskbar = cy > (screen_height - 75)
            in_foreground = False
            if active_rect:
                left, top, right, bottom = active_rect
                in_foreground = (left - 5 <= cx <= right + 5 and top - 5 <= cy <= bottom + 5)
                
            report_lines.append(f"\n[色块 #{idx+1}]")
            report_lines.append(f"  - 坐标: 左上角 ({x}, {y})，中心点 ({cx}, {cy})")
            report_lines.append(f"  - 数据: 宽度={w}, 高度={h}, 宽高比={aspect_ratio:.2f}, 面积={area}")
            if geom_error:
                report_lines.append(f"  - 几何过滤: 失败 (原因: {geom_error})")
            else:
                report_lines.append("  - 几何过滤: 通过")
                
            report_lines.append(f"  - 是否处于底部系统任务栏区域: {'是 (已被拦截安全排他)' if in_taskbar else '否'}")
            report_lines.append(f"  - 是否处于最前台活动开发窗口内: {'是' if in_foreground else '否'}")
            
            # 计算最终点击判定
            is_valid = geom_error is None and not in_taskbar and (in_foreground or not is_active_dev)
            
            color = (0, 255, 0) if is_valid else (0, 0, 255)
            cv2.rectangle(diagnose_img, (x, y), (x + w, y + h), color, 2)
            cv2.putText(diagnose_img, f"#{idx+1} {w}x{h} {'OK' if is_valid else 'ERR'}", (x, max(y - 5, 15)), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
            
            if is_valid:
                match_count += 1
                
        report_lines.append(f"\n最终通过所有安全双重保险的可用按钮数量: {match_count}")
        
        desktop_dir = os.path.join(os.environ["USERPROFILE"], "Desktop")
        report_file = os.path.join(desktop_dir, "submitter_diagnose_report.txt")
        img_file = os.path.join(desktop_dir, "submitter_diagnose.png")
        
        with open(report_file, "w", encoding="utf-8") as f:
            f.write("\n".join(report_lines))
            
        cv2.imwrite(img_file, diagnose_img)
        
        print(f"\n[成功] 诊断完成！已在桌面生成以下两个诊断文件：")
        print(f"  1. 诊断报告: {report_file}")
        print(f"  2. 标记截图: {img_file}")
        print(f"  (请您打开诊断报告查看，或者告知 AI 助手诊断结果！)")
    except Exception as e:
        print(f"\n[错误] 生成诊断报告失败: {e}")
    input("\n按回车键返回主菜单...")

def show_interactive_menu():
    """交互菜单主循环"""
    while True:
        os.system('cls')
        print("=" * 60)
        print("      自动点击与重试工具 (Auto Submitter 反重力专属版)")
        print("============================================================")
        print("  已启用: [纯计算机视觉自适应检测] (无需任何截图和配置)")
        print("  已限制: [仅在反重力 / VS Code 活动窗口边界内激活] (100%防误触)")
        print("  支持类型: [Submit 授权弹窗] 及 [Retry 报错弹窗]")
        print("  安全技术: 物理像素1:1对齐 + 后台静默投递 + 键盘物理回车保底")
        print("============================================================")
        print("  [1] 立即启动后台监控服务 (完全静默 / 无黑窗后台运行)")
        print("  [2] 立即停止后台监控服务 (关闭正在运行的后台服务)")
        print("  [3] 开启开机自动启动 (每次开机后自动在后台挂起监控)")
        print("  [4] 关闭开机自动启动 (移除开机自启配置)")
        print("  [5] 运行前台测试模式 (当前窗口直接运行并显示检测日志)")
        print("  [6] 生成一键诊断报告 (当无法识别时在桌面输出分析图文)")
        print("  [7] 退出管理器")
        print("============================================================")
        
        choice = input("请输入您的选项 [1-7] 并按回车: ").strip()
        
        if choice == "1":
            start_background_service()
        elif choice == "2":
            stop_background_service()
        elif choice == "3":
            set_startup(enable=True)
        elif choice == "4":
            set_startup(enable=False)
        elif choice == "5":
            os.system('cls')
            print("=" * 60)
            print("                  前台调试与测试运行模式")
            print("============================================================")
            print("  此模式直接在当前窗口显示监控日志，方便您观察是否成功检测到按钮。")
            print("  测试方法: 触发弹窗后，观察此处是否打印 [定位] 等日志，按钮是否消掉。")
            print("  随时按 [Ctrl + C] 即可安全退出测试模式并返回主菜单。")
            print("============================================================")
            monitor_loop(is_silent=False)
        elif choice == "6":
            generate_diagnose_report()
        elif choice == "7":
            print("\n已退出管理器。")
            sys.exit(0)
        else:
            print("\n[错误] 输入无效，请输入 1 到 7 之间的数字！")
            time.sleep(1.0)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--service":
        monitor_loop(is_silent=True)
    else:
        try:
            show_interactive_menu()
        except KeyboardInterrupt:
            print("\n已安全退出管理器。")
