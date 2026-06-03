import os
import sys

def kill():
    try:
        # 使用 wmic 查找所有包含 auto_submitter.py 命令行的进程 ID
        output = os.popen('wmic process where "commandline like \'%auto_submitter.py%\'" get processid').read()
        pids = [line.strip() for line in output.splitlines() if line.strip().isdigit()]
        
        current_pid = str(os.getpid())
        killed_any = False
        for pid in pids:
            if pid != current_pid:
                print(f"[清理] 正在终止旧版本自动提交进程 (PID: {pid})...")
                os.system(f"taskkill /F /PID {pid}")
                killed_any = True
                
        if not killed_any:
            print("[清理] 未发现任何正在运行的旧版本自动提交进程。")
    except Exception as e:
        print(f"[错误] 清理旧进程失败: {e}")

if __name__ == "__main__":
    kill()
