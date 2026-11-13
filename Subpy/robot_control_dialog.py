# -*- coding: utf-8 -*-
"""
机器人TCP控制界面
"""
import sys
import socket
import time
from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QTextEdit, QGroupBox
)
from PySide6.QtCore import Qt


class RobotControlDialog(QDialog):
    """机器人TCP控制对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("机器人TCP控制")
        self.setMinimumWidth(400)
        self.setMinimumHeight(300)
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        main_layout = QVBoxLayout(self)
        
        # ========== 连接设置 ==========
        conn_group = QGroupBox("连接设置")
        conn_layout = QHBoxLayout()
        
        # IP地址
        conn_layout.addWidget(QLabel("IP地址:"))
        self.ip_input = QLineEdit("192.168.1.10")
        self.ip_input.setPlaceholderText("请输入机器人IP地址")
        conn_layout.addWidget(self.ip_input)
        
        # 端口
        conn_layout.addWidget(QLabel("端口:"))
        self.port_input = QLineEdit("2000")
        self.port_input.setPlaceholderText("请输入端口号")
        self.port_input.setMaximumWidth(80)
        conn_layout.addWidget(self.port_input)
        
        conn_group.setLayout(conn_layout)
        main_layout.addWidget(conn_group)
        
        # ========== 指令输入 ==========
        cmd_group = QGroupBox("指令输入")
        cmd_layout = QVBoxLayout()
        
        # 指令输入框
        self.cmd_input = QLineEdit()
        self.cmd_input.setPlaceholderText('请输入指令，例如：run(lock.jspf)')
        cmd_layout.addWidget(self.cmd_input)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        
        self.send_btn = QPushButton("发送指令")
        self.send_btn.clicked.connect(self.send_command)
        self.send_btn.setMinimumHeight(35)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                border-radius: 5px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        btn_layout.addWidget(self.send_btn)
        
        self.clear_btn = QPushButton("清空结果")
        self.clear_btn.clicked.connect(self.clear_result)
        self.clear_btn.setMinimumHeight(35)
        btn_layout.addWidget(self.clear_btn)
        
        cmd_layout.addLayout(btn_layout)
        cmd_group.setLayout(cmd_layout)
        main_layout.addWidget(cmd_group)
        
        # ========== 结果返回 ==========
        result_group = QGroupBox("结果返回")
        result_layout = QVBoxLayout()
        
        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)
        self.result_output.setPlaceholderText("指令执行结果将显示在这里...")
        self.result_output.setMinimumHeight(200)
        result_layout.addWidget(self.result_output)
        
        result_group.setLayout(result_layout)
        main_layout.addWidget(result_group)
    
    def send_command(self):
        """发送指令"""
        ip = self.ip_input.text().strip()
        port_str = self.port_input.text().strip()
        cmd = self.cmd_input.text().strip()
        
        # 验证输入
        if not ip:
            self.append_result("❌ 错误：请输入IP地址")
            return
        
        if not port_str:
            self.append_result("❌ 错误：请输入端口号")
            return
        
        if not cmd:
            self.append_result("❌ 错误：请输入指令")
            return
        
        try:
            port = int(port_str)
        except ValueError:
            self.append_result("❌ 错误：端口号必须是数字")
            return
        
        # 显示发送信息
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.append_result(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.append_result(f"📤 [{timestamp}] 发送指令")
        self.append_result(f"   IP: {ip}:{port}")
        self.append_result(f"   指令: {cmd}")
        
        # 发送TCP指令
        try:
            self.append_result("🔗 正在连接...")
            
            # 创建socket连接
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)  # 5秒超时
            sock.connect((ip, port))
            
            self.append_result("✅ 连接成功")
            self.append_result(f"📤 正在发送指令...")
            
            # 发送指令
            sock.sendall(cmd.encode('utf-8'))
            
            self.append_result("✅ 指令发送成功")
            self.append_result(f"⏳ 等待响应...")
            
            # 接收响应
            try:
                response = sock.recv(4096)  # 最多接收4KB
                if response:
                    response_text = response.decode('utf-8', errors='ignore')
                    self.append_result(f"📥 收到响应:")
                    self.append_result(f"   {response_text}")
                else:
                    self.append_result("📭 没有收到响应")
            except socket.timeout:
                self.append_result("⏱️ 等待响应超时")
            except Exception as e:
                self.append_result(f"❌ 接收响应失败: {e}")
            finally:
                sock.close()
                self.append_result("🔌 连接已关闭")
                
        except ConnectionRefusedError:
            self.append_result(f"❌ 连接失败：连接被拒绝")
            self.append_result(f"   请检查机器人是否开启，IP和端口是否正确")
        except socket.timeout:
            self.append_result(f"❌ 连接失败：连接超时")
        except Exception as e:
            self.append_result(f"❌ 连接失败: {e}")
    
    def clear_result(self):
        """清空结果"""
        self.result_output.clear()
    
    def append_result(self, text):
        """添加结果到输出框"""
        self.result_output.append(text)
        # 滚动到底部
        scrollbar = self.result_output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())


def show_robot_control_dialog(parent=None):
    """显示机器人控制对话框"""
    dialog = RobotControlDialog(parent)
    dialog.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = RobotControlDialog()
    dialog.show()
    sys.exit(app.exec())
