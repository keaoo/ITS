#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音频探测工具 - 设置界面
"""
import sys
import os
import time
import threading
import numpy as np
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout,
    QLabel, QPushButton, QSpinBox, QProgressBar, QWidget,
    QMessageBox, QLCDNumber
)
from PySide6.QtCore import Qt, QTimer, Signal, QObject
from PySide6.QtGui import QPainter, QColor, QPen, QFont

try:
    import pyaudio
    HAS_AUDIO = True
except ImportError:
    HAS_AUDIO = False


class WaveformWidget(QWidget):
    """波形显示控件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.audio_data = np.zeros(1024)
        self.setMinimumHeight(150)
        self.setMinimumWidth(300)
        
    def update_waveform(self, data):
        """更新波形数据"""
        self.audio_data = np.frombuffer(data, dtype=np.int16)
        self.update()
        
    def clear_waveform(self):
        """清空波形"""
        self.audio_data = np.zeros(1024)
        self.update()
        
    def paintEvent(self, event):
        """绘制波形"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 背景
        painter.fillRect(self.rect(), QColor(26, 26, 46))
        
        # 绘制网格线
        painter.setPen(QPen(QColor(60, 60, 80), 1, Qt.DashLine))
        width = self.width()
        height = self.height()
        
        # 水平网格线
        for i in range(1, 5):
            y = height * i / 5
            painter.drawLine(0, y, width, y)
        
        # 垂直网格线
        for i in range(1, 10):
            x = width * i / 10
            painter.drawLine(x, 0, x, height)
        
        if len(self.audio_data) == 0:
            return
            
        # 归一化数据
        normalized = self.audio_data / 32768.0
        
        # 获取画布尺寸
        center_y = height // 2
        
        # 重采样到画布宽度
        step = max(1, len(normalized) // width)
        samples = normalized[::step]
        
        # 绘制波形
        for x in range(len(samples)):
            if x >= width:
                break
                
            y1 = center_y + int(samples[x] * center_y * 0.8)
            y2 = center_y - int(samples[x] * center_y * 0.8)
            
            # 颜色渐变
            if abs(samples[x]) < 0.2:
                color = QColor(0, 255, 136)
            elif abs(samples[x]) < 0.5:
                color = QColor(255, 255, 0)
            else:
                color = QColor(255, 68, 68)
                
            painter.setPen(QPen(color, 1))
            painter.drawLine(x, y1, x, y2)


class AudioDetectorWorker(QObject):
    """音频探测工作线程"""
    
    data_ready = Signal(bytes)
    volume_update = Signal(float)
    finished = Signal(float)
    
    def __init__(self, duration_seconds):
        super().__init__()
        self.duration_seconds = duration_seconds
        self.is_running = False
        self.volume_samples = []
        self.audio = None
        self.stream = None
        
    def start_detection(self):
        """开始探测"""
        if not HAS_AUDIO:
            return False
            
        self.is_running = True
        self.volume_samples = []
        
        try:
            self.audio = pyaudio.PyAudio()
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=44100,
                input=True,
                frames_per_buffer=1024
            )
            
            # 启动探测线程
            self.detect_thread = threading.Thread(target=self._detect_loop, daemon=True)
            self.detect_thread.start()
            
            return True
        except Exception as e:
            print(f"探测启动失败: {e}")
            return False
            
    def _detect_loop(self):
        """探测循环"""
        start_time = time.time()
        
        while self.is_running and (time.time() - start_time) < self.duration_seconds:
            try:
                data = self.stream.read(1024, exception_on_overflow=False)
                self.data_ready.emit(data)
                
                # 计算音量
                audio_data = np.frombuffer(data, dtype=np.int16)
                rms = np.sqrt(np.mean(audio_data.astype(np.float32) ** 2))
                volume = min(100, rms / 327.68)
                
                self.volume_samples.append(volume)
                self.volume_update.emit(volume)
                
            except Exception as e:
                print(f"探测错误: {e}")
                break
        
        # 计算平均音量
        if self.volume_samples:
            avg_volume = np.mean(self.volume_samples)
        else:
            avg_volume = 0
        
        self.finished.emit(avg_volume)
        
    def stop_detection(self):
        """停止探测"""
        self.is_running = False
        
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except:
                pass
                
        if self.audio:
            try:
                self.audio.terminate()
            except:
                pass


class AudioDetectorDialog(QDialog):
    """音频探测对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("音频探测工具")
        self.resize(700, 650)
        
        self.detector_worker = None
        self.is_detecting = False
        self.remaining_time = 0
        self.parent_window = parent
        
        self.init_ui()
        self.load_config()

    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)

        # 1. 波形显示区域
        wave_group = QGroupBox("📊 音频波形")
        wave_layout = QVBoxLayout(wave_group)
        self.waveform_widget = WaveformWidget()
        wave_layout.addWidget(self.waveform_widget)
        layout.addWidget(wave_group)

        # 2. 实时音量显示
        volume_group = QGroupBox("🔊 音量显示")
        volume_layout = QVBoxLayout(volume_group)
        
        # 当前音量条
        current_layout = QHBoxLayout()
        current_layout.addWidget(QLabel("当前音量:"))
        self.volume_bar = QProgressBar()
        self.volume_bar.setMaximum(100)
        self.volume_bar.setValue(0)
        self.volume_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 3px;
                text-align: center;
                height: 25px;
                font-size: 14px;
            }
            QProgressBar::chunk {
                background-color: #00ff88;
                border-radius: 2px;
            }
        """)
        current_layout.addWidget(self.volume_bar)
        self.volume_label = QLabel("0 %")
        self.volume_label.setStyleSheet("font-size: 16px; font-weight: bold; min-width: 60px;")
        current_layout.addWidget(self.volume_label)
        volume_layout.addLayout(current_layout)
        
        # 平均音量显示
        avg_layout = QHBoxLayout()
        avg_layout.addWidget(QLabel("平均音量:"))
        self.avg_volume_lcd = QLCDNumber()
        self.avg_volume_lcd.setDigitCount(5)
        self.avg_volume_lcd.display("0.00")
        self.avg_volume_lcd.setStyleSheet("""
            QLCDNumber {
                background-color: #1a1a2e;
                color: #00ff88;
                border: 2px solid #4a4a6e;
                border-radius: 5px;
                min-width: 150px;
                min-height: 50px;
            }
        """)
        avg_layout.addWidget(self.avg_volume_lcd)
        avg_layout.addWidget(QLabel("%"))
        avg_layout.addStretch()
        volume_layout.addLayout(avg_layout)
        
        layout.addWidget(volume_group)

        # 3. 设置区域
        settings_group = QGroupBox("⚙️ 设置")
        settings_layout = QFormLayout(settings_group)
        
        # 采集时间
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 3600)
        self.duration_spin.setValue(10)
        self.duration_spin.setSuffix(" 秒")
        self.duration_spin.setStyleSheet("""
            QSpinBox {
                font-size: 14px;
                padding: 5px;
                min-width: 150px;
            }
        """)
        settings_layout.addRow("采集时间:", self.duration_spin)
        
        # 音量下限（预留）
        self.threshold_spin = QSpinBox()
        self.threshold_spin.setRange(0, 100)
        self.threshold_spin.setValue(30)
        self.threshold_spin.setSuffix(" %")
        self.threshold_spin.setStyleSheet("""
            QSpinBox {
                font-size: 14px;
                padding: 5px;
                min-width: 150px;
            }
        """)
        settings_layout.addRow("音量下限:", self.threshold_spin)
        
        layout.addWidget(settings_group)

        # 4. 倒计时显示
        countdown_group = QGroupBox("⏱️ 倒计时")
        countdown_layout = QHBoxLayout(countdown_group)
        countdown_layout.addStretch()
        self.countdown_label = QLabel("00:00")
        self.countdown_label.setStyleSheet("""
            QLabel {
                font-size: 48px;
                font-weight: bold;
                color: #ff6b6b;
                font-family: Consolas, monospace;
            }
        """)
        countdown_layout.addWidget(self.countdown_label)
        countdown_layout.addStretch()
        layout.addWidget(countdown_group)

        # 5. 控制按钮
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("🎙️ 打开收音")
        self.start_button.setMinimumHeight(45)
        self.start_button.clicked.connect(self.start_detection)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #388E3C;
            }
            QPushButton:disabled {
                background-color: #ccc;
            }
        """)
        button_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("⏹️ 停止收音")
        self.stop_button.setMinimumHeight(45)
        self.stop_button.clicked.connect(self.stop_detection)
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
            }
            QPushButton:disabled {
                background-color: #ccc;
            }
        """)
        button_layout.addWidget(self.stop_button)
        
        layout.addLayout(button_layout)

        # 6. 状态标签
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #666;
                padding: 10px;
            }
        """)
        layout.addWidget(self.status_label)

        # 更新定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_countdown)

    def start_detection(self):
        """开始探测"""
        if not HAS_AUDIO:
            QMessageBox.warning(self, "错误", "缺少音频库！请安装: pip install pyaudio numpy")
            return
        
        if self.is_detecting:
            return
        
        duration = self.duration_spin.value()
        self.remaining_time = duration
        
        self.detector_worker = AudioDetectorWorker(duration)
        self.detector_worker.data_ready.connect(self.on_data_ready)
        self.detector_worker.volume_update.connect(self.on_volume_update)
        self.detector_worker.finished.connect(self.on_detection_finished)
        
        if self.detector_worker.start_detection():
            self.is_detecting = True
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.duration_spin.setEnabled(False)
            self.threshold_spin.setEnabled(False)
            
            self.status_label.setText(f"正在探测，时长 {duration} 秒...")
            self.status_label.setStyleSheet("color: #4CAF50; font-size: 14px; padding: 10px;")
            
            self.update_countdown_display()
            self.timer.start(100)
        else:
            QMessageBox.warning(self, "错误", "启动音频探测失败！")

    def stop_detection(self):
        """停止探测"""
        if not self.is_detecting:
            return
        
        self.is_detecting = False
        self.timer.stop()
        
        if self.detector_worker:
            self.detector_worker.stop_detection()
        
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.duration_spin.setEnabled(True)
        self.threshold_spin.setEnabled(True)
        
        self.status_label.setText("已停止")
        self.status_label.setStyleSheet("color: #f44336; font-size: 14px; padding: 10px;")

    def on_data_ready(self, data):
        """音频数据就绪"""
        self.waveform_widget.update_waveform(data)

    def on_volume_update(self, volume):
        """音量更新"""
        self.volume_bar.setValue(int(volume))
        self.volume_label.setText(f"{volume:.1f} %")
        
        # 更新音量条颜色
        if volume < 30:
            self.volume_bar.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #ccc;
                    border-radius: 3px;
                    text-align: center;
                    height: 25px;
                    font-size: 14px;
                }
                QProgressBar::chunk {
                    background-color: #00ff88;
                    border-radius: 2px;
                }
            """)
        elif volume < 70:
            self.volume_bar.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #ccc;
                    border-radius: 3px;
                    text-align: center;
                    height: 25px;
                    font-size: 14px;
                }
                QProgressBar::chunk {
                    background-color: #ffff00;
                    border-radius: 2px;
                }
            """)
        else:
            self.volume_bar.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #ccc;
                    border-radius: 3px;
                    text-align: center;
                    height: 25px;
                    font-size: 14px;
                }
                QProgressBar::chunk {
                    background-color: #ff4444;
                    border-radius: 2px;
                }
            """)

    def on_detection_finished(self, avg_volume):
        """探测完成"""
        self.is_detecting = False
        self.timer.stop()
        
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.duration_spin.setEnabled(True)
        self.threshold_spin.setEnabled(True)
        
        # 显示平均音量
        self.avg_volume_lcd.display(f"{avg_volume:.2f}")
        
        self.status_label.setText(f"探测完成！平均音量: {avg_volume:.2f} %")
        self.status_label.setStyleSheet("color: #2196F3; font-size: 14px; padding: 10px;")
        
        # 清空波形
        self.waveform_widget.clear_waveform()
        
        # 显示提示
        QMessageBox.information(
            self, 
            "探测完成", 
            f"音频探测完成！\n\n平均音量: {avg_volume:.2f} %"
        )

    def update_countdown(self):
        """更新倒计时"""
        if self.remaining_time > 0:
            self.remaining_time -= 0.1
            self.update_countdown_display()

    def update_countdown_display(self):
        """更新倒计时显示"""
        if self.remaining_time <= 0:
            self.countdown_label.setText("00:00")
            return
        
        minutes = int(self.remaining_time // 60)
        seconds = int(self.remaining_time % 60)
        tenths = int((self.remaining_time * 10) % 10)
        
        if minutes > 0:
            self.countdown_label.setText(f"{minutes:02d}:{seconds:02d}.{tenths:01d}")
        else:
            self.countdown_label.setText(f"{seconds:02d}.{tenths:01d}")
        
        # 根据剩余时间改变颜色
        if self.remaining_time <= 3:
            self.countdown_label.setStyleSheet("""
                QLabel {
                    font-size: 48px;
                    font-weight: bold;
                    color: #ff0000;
                    font-family: Consolas, monospace;
                }
            """)
        elif self.remaining_time <= 10:
            self.countdown_label.setStyleSheet("""
                QLabel {
                    font-size: 48px;
                    font-weight: bold;
                    color: #ff6b6b;
                    font-family: Consolas, monospace;
                }
            """)
        else:
            self.countdown_label.setStyleSheet("""
                QLabel {
                    font-size: 48px;
                    font-weight: bold;
                    color: #4CAF50;
                    font-family: Consolas, monospace;
                }
            """)

    def save_config(self):
        """保存配置"""
        if self.parent_window:
            config = {
                "detection_duration": self.duration_spin.value(),
                "volume_threshold": self.threshold_spin.value()
            }
            # 保存到主程序配置中
            if "voice_test" not in self.parent_window.config:
                self.parent_window.config["voice_test"] = {}
            self.parent_window.config["voice_test"].update(config)
            self.parent_window.save_config()
    
    def load_config(self):
        """加载配置"""
        if self.parent_window and "voice_test" in self.parent_window.config:
            config = self.parent_window.config["voice_test"]
            duration = config.get("detection_duration", 10)
            threshold = config.get("volume_threshold", 30)
            self.duration_spin.setValue(duration)
            self.threshold_spin.setValue(threshold)
    
    def closeEvent(self, event):
        """关闭事件"""
        if self.is_detecting:
            self.stop_detection()
        
        # 保存配置
        self.save_config()
        
        event.accept()


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    dialog = AudioDetectorDialog()
    dialog.show()
    sys.exit(app.exec())
