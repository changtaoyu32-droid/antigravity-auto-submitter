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

### 💻 菜单功能与推荐使用教程
双击运行桌面上的批处理后，即可进入命令行管理器。我们提供了多种模式：

> [!IMPORTANT]
> **🌟 核心推荐：极力建议您使用 `[5] 运行前台测试模式`！**
> 
> 虽然小助手提供了后台静默服务（选项 1），但在 Windows 环境下，**选项 [5]（前台测试模式）是最推荐且最稳定的日常使用模式**：
> - **透明直观**：命令行会实时显示小助手的每次检测、定位和点击动作，能够清晰掌握它的运行状态。
> - **性能最佳**：前台模式拥有更高的进程优先级和系统截屏树刷新响应速度。
> - **防冻结设计**：小助手已从底层禁用了 CMD 控制台的 QuickEdit 快速编辑，防止您无意点击命令行窗口导致线程挂起。
> - **极速退出**：随时可在黑窗口中按 `Ctrl + C` 安全返回主菜单，没有任何残留进程。

* **`[1] 立即启动后台监控服务`**：运行完全静默、无黑黑命令行窗口的后台服务（适合极度洁癖且挂机时间极长的用户）。
* **`[2] 立即停止后台监控服务`**：关闭后台正在运行的静默监控实例。
* **`[5] 运行前台测试模式`**：【核心推荐】直接在当前窗口显示监控日志，观察检测反应最直观。
* **`[6] 生成一键诊断报告`**：在桌面生成标记图 `submitter_diagnose.png` 与分析文本，供排查识别故障。

### 📦 部署与运行方法
1. 安装 Python 3.8+ (请务必在安装时勾选 **Add Python to PATH**)。
2. 将本项目的所有文件下载或克隆至本地。
3. 双击运行 **`自动提交一键配置助手.bat`**。
4. 初次运行时会静默补全环境依赖，随后即可在弹出的菜单中**输入 `5` 并按回车**开启前台测试监控模式！

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

### 💻 Menu Options & Recommendation
Double-click the batch file to enter the interactive console menu:

> [!IMPORTANT]
> **🌟 Recommendation: Highly recommended to use `[5] Run Foreground Test Mode`!**
> 
> Although a silent background service is provided (Option 1), **Option [5] (Foreground Test Mode) is the most stable and visual way for daily coding**:
> - **Full Visibility**: Prints live `[Locate]`, `[Success]`, and `[Diagnose]` logs in real-time, giving you total awareness.
> - **Highest Priority**: Foreground terminal execution receives superior CPU scheduling and desktop screenshot refresh rates.
> - **Freeze-Proof**: Windows Console QuickEdit is automatically disabled by the script to prevent thread freezes caused by accidental clicks.
> - **Easy Control**: Press `Ctrl + C` anytime in the console to safely return to the main menu.

* **`[1] Start Background Service`**: Runs the monitor silently in the background with no terminal windows visible.
* **`[2] Stop Background Service`**: Instantly terminates active silent background monitors.
* **`[5] Run Foreground Test Mode`**: [Highly Recommended] Starts the monitor inside the current terminal with live debug output.
* **`[6] Generate Diagnostic Report`**: Exports diagnostic data and bounding-box screenshots to your desktop for debugging.

### 📦 Installation & Execution
1. Install Python 3.8+ (ensure you check **"Add Python to PATH"**).
2. Clone or download this repository to a local directory.
3. Double-click **`自动提交一键配置助手.bat`** (first-time launch auto-installs requirements).
4. In the console menu, **enter `5` and press Enter** to launch the foreground monitoring mode!

