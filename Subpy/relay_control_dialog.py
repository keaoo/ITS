#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
继电器控制界面 - 340芯片继电器控制
提供串口选择、通道选择、开关控制功能
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QComboBox, QPushButton, QTextEdit, QMessageBox, QFormLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import serial.tools.list_ports
import time

try:
    from Subpy.relay_subprogram import control_relay
except ImportError:
    # 如果导入失败，定义一个简单版本
    def control_relay(port, baudrate, channel, action):
        """简单的继电器控制函数（备用）"""
        try:
            channel = int(channel)
        except ValueError:
            return False
        
        if action == 'on':
            checksum = 0xA0 + channel + 0x01
            cmd = bytes([0xA0, channel, 0x01, checksum])
        else:
            checksum = 0xA0 + channel + 0x00
            cmd = bytes([0xA0, channel, 0x00, checksum])
        
        try:
            ser = serial.Serial(port, baudrate, timeout=1)
            ser.write(cmd)
            time.sleep(0.1)
            ser.close()
            return True
        except Exception as e:
            print(f"继电器控制失败: {e}")
            return False


class RelayControlDialog(QDialog):
    """继电器控制对话框"""
    
    # 信号：继电器状态变化
    relay_status_changed = Signal(int, bool)  # (通道号, 状态)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.current_port = None
        self.relay_status = {i: False for i in range(1, 9)}  # 1-8通道状态
        
        self.init_ui()
        self.refresh_ports()  # 初始化时刷新串口列表
    
    def get_ch340_ports(self):
        """只获取 CH340 芯片的串口"""
        import time
        time.sleep(0.1)  # 等100ms，让系统刷新设备列表
        # 强制刷新两次（避免pyserial的缓存问题）
        serial.tools.list_ports.comports()  # 第一次，刷新缓存
        time.sleep(0.05)
        ports = serial.tools.list_ports.comports()  # 第二次，获取刷新后的列表
        ch340_ports = []
        for port in ports:
            # 匹配描述中包含 CH340 的（不区分大小写）
            if "CH340" in port.description or "ch340" in port.description:
                ch340_ports.append(port.device)
        
        return ch340_ports
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("继电器控制 - CH340芯片")
        self.setMinimumWidth(380)
        self.setMinimumHeight(650)
        
        layout = QVBoxLayout(self)
        
        # ========== 1. 串口选择组 ==========
        port_group = QGroupBox("串口设置")
        port_layout = QVBoxLayout(port_group)
        port_layout.setSpacing(10)
        
        port_row1 = QHBoxLayout()
        port_row1.addWidget(QLabel("选择串口:"))
        self.port_combo = QComboBox()
        self.port_combo.setMinimumHeight(35)
        self.port_combo.setMinimumWidth(300)
        port_row1.addWidget(self.port_combo)
        
        port_row2 = QHBoxLayout()
        port_row2.addStretch()
        self.refresh_btn = QPushButton("刷新串口")
        self.refresh_btn.setMinimumHeight(30)
        self.refresh_btn.clicked.connect(self.refresh_ports)
        port_row2.addWidget(self.refresh_btn)
        
        port_layout.addLayout(port_row1)
        port_layout.addLayout(port_row2)
        
        layout.addWidget(port_group)
        
        # ========== 2. 通道选择组 ==========
        channel_group = QGroupBox("通道选择 (1-8)")
        channel_layout = QHBoxLayout(channel_group)
        
        self.channel_combo = QComboBox()
        self.channel_combo.setMinimumHeight(35)
        self.channel_combo.setMinimumWidth(80)
        self.channel_combo.addItems([str(i) for i in range(1, 9)])
        
        channel_layout.addWidget(QLabel("通道号:"))
        channel_layout.addWidget(self.channel_combo)
        channel_layout.addStretch()
        
        layout.addWidget(channel_group)
        
        # ========== 3. 控制按钮组 ==========
        control_group = QGroupBox("继电器控制")
        control_layout = QVBoxLayout(control_group)
        control_layout.setSpacing(12)
        
        # 单个通道控制
        single_layout = QHBoxLayout()
        single_layout.setSpacing(10)
        
        self.on_btn = QPushButton("🔴 打开继电器")
        self.on_btn.setMinimumHeight(42)
        self.on_btn.setMinimumWidth(160)
        self.on_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff4444;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #ff6666;
            }
            QPushButton:pressed {
                background-color: #cc0000;
            }
        """)
        self.on_btn.clicked.connect(self.turn_on_relay)
        
        self.off_btn = QPushButton("🟢 关闭继电器")
        self.off_btn.setMinimumHeight(42)
        self.off_btn.setMinimumWidth(160)
        self.off_btn.setStyleSheet("""
            QPushButton {
                background-color: #44ff44;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #66ff66;
            }
            QPushButton:pressed {
                background-color: #00cc00;
            }
        """)
        self.off_btn.clicked.connect(self.turn_off_relay)
        
        single_layout.addWidget(self.on_btn)
        single_layout.addWidget(self.off_btn)
        
        control_layout.addLayout(single_layout)
        
        # 脉冲控制
        pulse_layout = QHBoxLayout()
        pulse_layout.setSpacing(10)
        
        self.pulse_btn = QPushButton("⚡ 脉冲控制 (打开1秒后关闭)")
        self.pulse_btn.setMinimumHeight(40)
        self.pulse_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff9900;
                color: white;
                font-size: 13px;
                font-weight: bold;
                border-radius: 8px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #ffaa33;
            }
        """)
        self.pulse_btn.clicked.connect(self.pulse_control)
        
        pulse_layout.addWidget(self.pulse_btn)
        control_layout.addLayout(pulse_layout)
        
        layout.addWidget(control_group)
        
        # ========== 4. 全部通道控制 ==========
        all_group = QGroupBox("全部通道控制")
        all_layout = QHBoxLayout(all_group)
        
        self.all_on_btn = QPushButton("🔴 全部打开")
        self.all_on_btn.setMinimumHeight(40)
        self.all_on_btn.clicked.connect(self.turn_on_all)
        
        self.all_off_btn = QPushButton("🟢 全部关闭")
        self.all_off_btn.setMinimumHeight(40)
        self.all_off_btn.clicked.connect(self.turn_off_all)
        
        all_layout.addWidget(self.all_on_btn)
        all_layout.addWidget(self.all_off_btn)
        
        layout.addWidget(all_group)
        
        # ========== 5. 状态显示组 ==========
        status_group = QGroupBox("通道状态")
        status_layout = QVBoxLayout(status_group)
        
        # 第一行：CH1-CH4
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(15)
        # 第二行：CH5-CH8
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(15)
        
        self.status_labels = {}
        for i in range(1, 9):
            label = QLabel(f"CH{i}: ⚪")
            label.setFont(QFont("Arial", 11))
            self.status_labels[i] = label
            if i <= 4:
                row1_layout.addWidget(label)
            else:
                row2_layout.addWidget(label)
        
        status_layout.addLayout(row1_layout)
        status_layout.addLayout(row2_layout)
        
        layout.addWidget(status_group)
        
        # ========== 6. 日志输出 ==========
        log_group = QGroupBox("操作日志")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setReadOnly(True)
        
        log_layout.addWidget(self.log_text)
        layout.addWidget(log_group)
        
        # ========== 7. 关闭按钮 ==========
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        
        self.close_btn = QPushButton("关闭")
        self.close_btn.setMinimumHeight(40)
        self.close_btn.clicked.connect(self.close)
        
        close_layout.addWidget(self.close_btn)
        layout.addLayout(close_layout)
        
        # 添加一条欢迎日志
        self.append_log("继电器控制界面已启动")
        self.append_log("请先选择串口，然后选择通道进行控制")
    
    def refresh_ports(self):
        """刷新串口列表（只显示CH340芯片）"""
        self.port_combo.clear()
        
        ports = self.get_ch340_ports()
        
        if not ports:
            self.port_combo.addItem("未找到CH340设备")
            self.append_log("⚠️ 未检测到CH340串口设备")
            return
        
        for port in ports:
            self.port_combo.addItem(port, port)
        
        self.append_log(f"✅ 已刷新串口列表，共 {len(ports)} 个CH340串口")
    
    def get_selected_port(self):
        """获取当前选择的串口"""
        index = self.port_combo.currentIndex()
        if index < 0:
            return None
        
        port_data = self.port_combo.itemData(index)
        if port_data:
            return port_data
        
        # 如果没有数据，尝试从文本中提取
        port_text = self.port_combo.currentText()
        if " - " in port_text:
            return port_text.split(" - ")[0]
        
        return None
    
    def get_selected_channel(self):
        """获取当前选择的通道号"""
        try:
            return int(self.channel_combo.currentText())
        except ValueError:
            return 1
    
    def update_status_label(self, channel, status):
        """更新通道状态标签"""
        if channel in self.status_labels:
            if status:
                self.status_labels[channel].setText(f"CH{channel}: 🔴")
            else:
                self.status_labels[channel].setText(f"CH{channel}: ⚪")
        self.relay_status[channel] = status
        self.relay_status_changed.emit(channel, status)
    
    def append_log(self, message):
        """添加日志"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
    
    def turn_on_relay(self):
        """打开继电器"""
        port = self.get_selected_port()
        if not port:
            QMessageBox.warning(self, "提示", "请先选择串口！")
            return
        
        channel = self.get_selected_channel()
        
        self.append_log(f"📤 正在打开通道 {channel} (串口: {port})")
        
        if control_relay(port, 9600, channel, 'on'):
            self.append_log(f"✅ 通道 {channel} 已打开")
            self.update_status_label(channel, True)
        else:
            self.append_log(f"❌ 通道 {channel} 打开失败")
            QMessageBox.warning(self, "错误", "继电器打开失败，请检查串口连接！")
    
    def turn_off_relay(self):
        """关闭继电器"""
        port = self.get_selected_port()
        if not port:
            QMessageBox.warning(self, "提示", "请先选择串口！")
            return
        
        channel = self.get_selected_channel()
        
        self.append_log(f"📤 正在关闭通道 {channel} (串口: {port})")
        
        if control_relay(port, 9600, channel, 'off'):
            self.append_log(f"✅ 通道 {channel} 已关闭")
            self.update_status_label(channel, False)
        else:
            self.append_log(f"❌ 通道 {channel} 关闭失败")
            QMessageBox.warning(self, "错误", "继电器关闭失败，请检查串口连接！")
    
    def pulse_control(self):
        """脉冲控制：打开1秒后自动关闭"""
        port = self.get_selected_port()
        if not port:
            QMessageBox.warning(self, "提示", "请先选择串口！")
            return
        
        channel = self.get_selected_channel()
        
        self.append_log(f"⚡ 脉冲控制：通道 {channel} 打开1秒后自动关闭")
        
        # 打开
        if control_relay(port, 9600, channel, 'on'):
            self.append_log(f"✅ 通道 {channel} 已打开")
            self.update_status_label(channel, True)
            
            # 等待1秒
            from PySide6.QtCore import QTimer
            QTimer.singleShot(1000, lambda: self.pulse_off(port, channel))
        else:
            self.append_log(f"❌ 通道 {channel} 打开失败")
            QMessageBox.warning(self, "错误", "继电器打开失败，请检查串口连接！")
    
    def pulse_off(self, port, channel):
        """脉冲控制的关闭部分"""
        if control_relay(port, 9600, channel, 'off'):
            self.append_log(f"✅ 通道 {channel} 已关闭（脉冲完成）")
            self.update_status_label(channel, False)
        else:
            self.append_log(f"❌ 通道 {channel} 关闭失败")
    
    def turn_on_all(self):
        """全部打开"""
        port = self.get_selected_port()
        if not port:
            QMessageBox.warning(self, "提示", "请先选择串口！")
            return
        
        self.append_log("🔴 正在打开全部通道...")
        
        success_count = 0
        for channel in range(1, 9):
            if control_relay(port, 9600, channel, 'on'):
                self.update_status_label(channel, True)
                success_count += 1
        
        self.append_log(f"✅ 已打开 {success_count}/8 个通道")
    
    def turn_off_all(self):
        """全部关闭"""
        port = self.get_selected_port()
        if not port:
            QMessageBox.warning(self, "提示", "请先选择串口！")
            return
        
        self.append_log("🟢 正在关闭全部通道...")
        
        success_count = 0
        for channel in range(1, 9):
            if control_relay(port, 9600, channel, 'off'):
                self.update_status_label(channel, False)
                success_count += 1
        
        self.append_log(f"✅ 已关闭 {success_count}/8 个通道")


if __name__ == "__main__":
    """测试继电器控制界面"""
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    dialog = RelayControlDialog()
    dialog.show()
    sys.exit(app.exec())
