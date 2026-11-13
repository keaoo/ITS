import subprocess
import sys
from PySide6.QtCore import QThread, Signal


class CommandThread(QThread):
    """执行命令的线程类"""
    output_signal = Signal(str)       # 实时输出信号
    finished_signal = Signal(int)     # 完成信号，带返回码

    def __init__(self, command):
        super().__init__()
        self.command = command
        self._stop_flag = False       # 停止标记
        self.process = None

    def stop(self):
        """停止执行命令"""
        self._stop_flag = True
        if self.process and self.process.poll() is None:
            self.process.terminate()  # 终止进程
            self.process.wait()

    def run(self):
        """执行命令并发送输出"""
        try:
            # Windows 自动检测编码，避免乱码
            if sys.platform == "win32":
                # 优先检测控制台编码，避免中文乱码
                encoding = "gbk" if sys.stdout.encoding and "UTF" in sys.stdout.encoding.upper() else sys.stdout.encoding
                encoding = encoding or "gbk"
            else:
                encoding = "utf-8"

            self.process = subprocess.Popen(
                self.command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                encoding=encoding,
                bufsize=1
            )

            # 实时读取输出
            while True:
                line = self.process.stdout.readline()
                if not line:
                    break
                if self._stop_flag:
                    break

                line = line.rstrip()  # 去掉末尾换行
                if line:
                    self.output_signal.emit(line)

            # 等待命令完成
            if not self._stop_flag:
                self.process.wait()

            return_code = self.process.returncode
            self.output_signal.emit(f"\n命令执行完成，返回码: {return_code}")
            self.finished_signal.emit(return_code)

        except Exception as e:
            self.output_signal.emit(f"执行命令时出错: {str(e)}")
            self.finished_signal.emit(-1)

    @staticmethod
    def CMDMessage(command):
        """创建并返回命令线程（工厂方法）"""
        return CommandThread(command)


# ========== 使用示例 ==========
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # 方式1：直接创建
    # cmd_thread = CommandThread("ping www.baidu.com -n 4")

    # 方式2：用你原来的 CMDMessage 方式创建（推荐这个！）
    cmd_thread = CommandThread.CMDMessage("ping www.baidu.com -n 4")

    # 连接信号，接收输出
    cmd_thread.output_signal.connect(lambda text: print(f"收到输出: {text}"))
    cmd_thread.finished_signal.connect(lambda code: (
        print(f"命令结束，返回码: {code}"),
        app.quit()  # 命令结束后退出程序
    ))

    # 启动线程
    cmd_thread.start()

    sys.exit(app.exec())
