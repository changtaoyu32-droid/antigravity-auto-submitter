# 🛠️ 反重力 Submit & Retry 智能小助手 | Antigravity Auto Submitter

<p align="center">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python Version" />
  <img src="https://img.shields.io/badge/platform-windows-lightgrey.svg" alt="Platform Windows" />
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License MIT" />
</p>

---

## 📖 语言导航 / Language Navigation
- [华语 / 中文说明书](#-中文说明书)
- [English / User Manual](#-english-manual)

---

## 🇨🇳 中文说明书

### 🎯 核心解决痛点
在使用**反重力 (Antigravity)**、**VS Code**、**Cursor** 或 **Windsurf** 等编辑器进行 AI 自动编程时，由于执行命令或报错，屏幕上经常会弹出：
- **`Allow running this command?` (右下角亮蓝色 Submit 确认弹窗)**
- **`Agent terminated due to error` (右下角亮蓝色 Retry 报错重试弹窗)**

本小助手通过 **DPI 物理像素 1:1 的 OpenCV 计算机视觉检测**，实时精准捕捉屏幕上的亮蓝色按钮，并采用 **Win32 消息队列后台投递 + 物理键盘 Enter 模拟** 的双层保障方案，帮您秒消弹窗，实现 100% 脱手挂机自动编程！

### ✨ 核心亮点与技术特性
1. **🍀 纯自适应 CV 轮廓检测**：基于 OpenCV 的亮蓝色 HSV 轮廓匹配算法，智能对齐 2K、4K 等各种高分辨率及 DPI 屏幕缩放比例，零人工配置，开箱即用。
2. **🚀 三层点击保障方案 (0% 鼠标抢夺)**：
   - **第一层**：Win32 底层 `PostMessage` 发送鼠标点击消息，物理鼠标完全不动、不发生位移。
   - **第二层**：Win32 底层直接向焦点窗口投递 `Enter` 键盘回车消息，实现双管齐下。
   - **第三层 (物理保底)**：若按钮未消失，触发 DPI 物理降级，瞬间将物理鼠标移至按钮中心点击并发送物理回车，然后极速闪回原位置。
3. **🔒 原生 Win32 窗口枚举与保底机制**：
   - 弃用不稳定的封装库，改用 Windows 底层原生的 `EnumWindows` 和 `GetWindowTextW` 接口，在管理员权限运行下成功穿透进程安全隔离。
   - **智能兜底**：若由于系统会话隔离导致获取的白名单窗口为 0，小助手自动切换至保底策略对全屏唯一符合几何特征的蓝色按钮进行点击，确保挂机不罢工。
4. **⌨️ 无干扰快捷暂停**：支持非拦截式全局快捷键。按一下键盘上的 `+` 键即可随时挂起/恢复小助手，打字写代码 0 干扰。
5. **📊 一键截图诊断分析**：菜单选项 `6` 可瞬间截屏，用红框标出所有检测到的蓝色块及过滤参数，快速排查故障。

### 🖼️ 诊断分析截图示例
当您触发一键诊断时，小助手会输出带红绿框线标记的诊断图像到您的桌面上，帮您秒懂识别状态：
![诊断示例](assets/diagnose_example.png)

### 💻 菜单功能说明
双击运行桌面上的批处理后，即可进入由 Python 渲染的稳定命令行菜单：
- `[1] 立即启动后台监控服务`：运行完全静默、无任何黑黑命令行窗口的后台常驻服务。
- `[5] 运行前台测试模式`：直接在当前窗口显示监控日志，方便直观观察检测反应（按 `Ctrl + C` 可退回主菜单）。
- `[6] 生成一键诊断报告`：在桌面生成标记图 `submitter_diagnose.png` 与分析文本 `submitter_diagnose_report.txt`，供故障排查。

### 📦 部署方法
- 安装 Python 3.8+ (请务必勾选 Add Python to PATH)。
- 将本项目的所有文件下载或克隆至本地。
- 双击运行 **`自动提交一键配置助手.bat`** 即可。初次运行时，小助手会自动检查并静默为您补全 `pyautogui`, `opencv-python`, `pillow` 等依赖。

---

## 🇺🇸 English Manual

### 🎯 Core Problem Solved
When using AI auto-programming editors such as **Antigravity**, **VS Code**, **Cursor**, or **Windsurf**, the system frequently prompts:
- **`Allow running this command?` (Bright blue "Submit" authorization pop-up)**
- **`Agent terminated due to error` (Bright blue "Retry" error recovery pop-up)**

This assistant uses **OpenCV Computer Vision with 1:1 physical pixel alignment** to capture the bright blue buttons in real-time. By leveraging **Win32 message queue background delivery + physical keyboard Enter simulation**, it automatically dismisses these dialogs for a fully hands-free AI coding experience.

### ✨ Key Features & Technical Highlights
1. **🍀 Adaptive CV Contour Detection**: Uses OpenCV contour matching on the blue HSV color space. It automatically adapts to various screen resolutions (2K, 4K) and DPI scaling settings (125%, 150%, etc.) with zero configuration.
2. **🚀 Three-Tier Click Insurance (Zero Cursor Theft)**:
   - **Tier 1 (Silent Click)**: Uses Win32 API `PostMessage` to deliver mouse click signals directly to the window, keeping the physical mouse cursor static.
   - **Tier 2 (Silent Enter)**: Posts standard `Enter` key events directly to the target window queue.
   - **Tier 3 (Physical Fallback)**: If the button persists, physical degradation is triggered—moving the mouse to the center, clicking, pressing Enter, and instantly returning the cursor.
3. **🔒 Win32 Native Window Enumeration & Fallback**:
   - Replaces unstable wrapper libraries with Windows native C-level APIs (`EnumWindows` and `GetWindowTextW`) to bypass security isolation when running under Administrator privileges.
   - **Smart Fallback**: If the detected whitelist window count is 0 (due to OS session isolation), it automatically falls back to click the single blue button matching the geometry on the screen.
4. **⌨️ Global Non-Intrusive Pause**: Binds a non-blocking hotkey. Pressing the `+` key instantly pauses or resumes the monitor without affecting standard typing or coding.
5. **📊 One-Click Screenshot Diagnostics**: Option `6` in the menu takes an instant screenshot, outlines all detected blue areas in red/green bounding boxes, and exports parameters for swift debugging.

### 🖼️ Diagnostic Analysis Screenshot
When running the diagnostic tool, it exports a visual report with green (valid) and red (filtered) bounding boxes to your desktop:
![Diagnostic Screenshot](assets/diagnose_example.png)

### 💻 Menu Options Description
Double-click the batch file to enter the interactive console menu:
- `[1] Start Background Service`: Runs the monitor silently in the background with no terminal windows visible.
- `[5] Run Foreground Test Mode`: Starts the monitor inside the current window, printing live detection logs. Press `Ctrl + C` to return to the main menu.
- `[6] Generate Diagnostic Report`: Generates `submitter_diagnose.png` and `submitter_diagnose_report.txt` on the desktop for debugging.

### 📦 Deployment
- Install Python 3.8+ (Make sure to check "Add Python to PATH").
- Clone or download this repository to your local directory.
- Double-click **`自动提交一键配置助手.bat`**. On first launch, it will check and silently install dependencies like `pyautogui`, `opencv-python`, and `pillow`.
