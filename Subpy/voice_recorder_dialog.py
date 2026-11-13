#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎤 语音录音工具 - PySide6版本
录制人声并保存为WAV格式
"""
import sys
import os
import time
import threading
import queue
from datetime import datetime
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QFileDialog, QMessageBox, QTreeWidget, QTreeWidgetItem, QProgressBar,
    QGroupBox, QWidget
)
from PySide6.QtCore import Qt, QTimer, Signal, QObject
from PySide6.QtGui import QPainter, QColor, QPen

try:
    import pyaudio
    import wave
    import numpy as np
    HAS_AUDIO = True
except ImportError:
    HAS_AUDIO = False


class WaveformWidget(QWidget):
    """波形显示控件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.audio_data = np.zeros(1024)
        self.setMinimumHeight(150)
        
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
        
        if len(self.audio_data) == 0:
            return
            
        # 归一化数据
        normalized = self.audio_data / 32768.0
        
        # 获取画布尺寸
        width = self.width()
        height = self.height()
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


class VoiceRecorderWorker(QObject):
    """录音工作线程"""
    
    data_ready = Signal(bytes)
    finished = Signal()
    
    def __init__(self):
        super().__init__()
        self.is_recording = False
        self.frames = []
        self.audio = None
        self.stream = None
        
    def start_recording(self):
        """开始录音"""
        if not HAS_AUDIO:
            return False
            
        self.is_recording = True
        self.frames = []
        
        try:
            self.audio = pyaudio.PyAudio()
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=44100,
                input=True,
                frames_per_buffer=1024
            )
            
            # 启动录音线程
            self.record_thread = threading.Thread(target=self._record_loop, daemon=True)
            self.record_thread.start()
            
            return True
        except Exception as e:
            print(f"录音启动失败: {e}")
            return False
            
    def _record_loop(self):
        """录音循环"""
        while self.is_recording:
            try:
                data = self.stream.read(1024, exception_on_overflow=False)
                self.frames.append(data)
                self.data_ready.emit(data)
            except Exception as e:
                print(f"录音错误: {e}")
                break
                
    def stop_recording(self):
        """停止录音"""
        self.is_recording = False
        
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
                
        self.finished.emit()
        return self.frames


class VoiceRecorderDialog(QDialog):
    """语音录音对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("语音录音工具")
        self.resize(700, 600)
        
        # 初始化录音器
        self.recorder = VoiceRecorderWorker()
        self.recorder.data_ready.connect(self.on_data_ready)
        self.recorder.finished.connect(self.on_recording_finished)
        
        self.is_recording = False
        self.start_time = 0
        self.recorded_frames = []
        
        # 默认保存目录：执行文件所在目录下的"录音"文件夹
        if hasattr(sys, 'frozen'):
            # 打包后：exe文件所在目录
            base_dir = os.path.dirname(os.path.abspath(sys.executable))
        else:
            # 开发模式：脚本所在目录
            base_dir = os.path.dirname(os.path.abspath(__file__))
            # 向上找到项目根目录
            while not os.path.exists(os.path.join(base_dir, 'ITS_app.py')) and os.path.dirname(base_dir) != base_dir:
                base_dir = os.path.dirname(base_dir)
        
        self.output_dir = os.path.join(base_dir, "录音")
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        self.init_ui()
        self.refresh_file_list()
        
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 波形显示区域
        wave_group = QGroupBox("音频波形")
        wave_layout = QVBoxLayout(wave_group)
        self.waveform_widget = WaveformWidget()
        wave_layout.addWidget(self.waveform_widget)
        layout.addWidget(wave_group)
        
        # 音量和时间显示
        info_layout = QHBoxLayout()
        
        info_layout.addWidget(QLabel("音量:"))
        self.volume_bar = QProgressBar()
        self.volume_bar.setMaximum(100)
        self.volume_bar.setValue(0)
        self.volume_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 3px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #00ff88;
                border-radius: 2px;
            }
        """)
        info_layout.addWidget(self.volume_bar)
        
        self.volume_label = QLabel("0%")
        info_layout.addWidget(self.volume_label)
        
        info_layout.addSpacing(30)
        
        info_layout.addWidget(QLabel("录音时长:"))
        self.time_label = QLabel("00:00")
        self.time_label.setStyleSheet("font-family: Consolas; font-size: 16px; font-weight: bold;")
        info_layout.addWidget(self.time_label)
        
        layout.addLayout(info_layout)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.record_button = QPushButton("🔴 开始录音")
        self.record_button.setMinimumHeight(40)
        self.record_button.clicked.connect(self.toggle_recording)
        self.record_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
            }
        """)
        button_layout.addWidget(self.record_button)
        
        self.save_button = QPushButton("💾 保存录音")
        self.save_button.setMinimumHeight(40)
        self.save_button.clicked.connect(self.save_recording)
        self.save_button.setEnabled(False)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QPushButton:disabled {
                background-color: #ccc;
            }
        """)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
        
        # 保存目录设置
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("保存目录:"))
        self.dir_edit = QLineEdit(self.output_dir)
        dir_layout.addWidget(self.dir_edit)
        
        browse_button = QPushButton("浏览...")
        browse_button.clicked.connect(self.browse_dir)
        dir_layout.addWidget(browse_button)
        layout.addLayout(dir_layout)
        
        # 文件列表
        file_group = QGroupBox("录音文件")
        file_layout = QVBoxLayout(file_group)
        
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(["文件名", "时长", "创建时间"])
        self.file_tree.setColumnWidth(0, 300)
        self.file_tree.setColumnWidth(1, 100)
        self.file_tree.setColumnWidth(2, 200)
        file_layout.addWidget(self.file_tree)
        
        layout.addWidget(file_group)
        
        # 更新定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer_display)
        
    def toggle_recording(self):
        """切换录音状态"""
        if not HAS_AUDIO:
            QMessageBox.warning(self, "错误", "缺少音频库！请安装: pip install pyaudio numpy")
            return
            
        if not self.is_recording:
            # 开始录音
            if self.recorder.start_recording():
                self.is_recording = True
                self.start_time = time.time()
                self.record_button.setText("⏹️ 停止录音")
                self.record_button.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        padding: 10px 20px;
                        font-size: 14px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #388E3C;
                    }
                    QPushButton:pressed {
                        background-color: #2E7D32;
                    }
                """)
                self.save_button.setEnabled(False)
                self.timer.start(100)
        else:
            # 停止录音
            self.is_recording = False
            self.timer.stop()
            self.recorded_frames = self.recorder.stop_recording()
            self.record_button.setText("🔴 开始录音")
            self.record_button.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 10px 20px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #d32f2f;
                }
                QPushButton:pressed {
                    background-color: #b71c1c;
                }
            """)
            self.save_button.setEnabled(True)
            
    def on_data_ready(self, data):
        """音频数据就绪"""
        # 更新波形
        self.waveform_widget.update_waveform(data)
        
        # 计算音量
        audio_data = np.frombuffer(data, dtype=np.int16)
        rms = np.sqrt(np.mean(audio_data.astype(np.float32) ** 2))
        level = min(100, int(rms / 327.68))
        
        self.volume_bar.setValue(level)
        self.volume_label.setText(f"{level}%")
        
        # 更新音量条颜色
        if level < 30:
            self.volume_bar.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #ccc;
                    border-radius: 3px;
                    text-align: center;
                    height: 20px;
                }
                QProgressBar::chunk {
                    background-color: #00ff88;
                    border-radius: 2px;
                }
            """)
        elif level < 70:
            self.volume_bar.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #ccc;
                    border-radius: 3px;
                    text-align: center;
                    height: 20px;
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
                    height: 20px;
                }
                QProgressBar::chunk {
                    background-color: #ff4444;
                    border-radius: 2px;
                }
            """)
            
    def on_recording_finished(self):
        """录音完成"""
        pass
        
    def update_timer_display(self):
        """更新时间显示"""
        if self.is_recording:
            duration = time.time() - self.start_time
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            self.time_label.setText(f"{minutes:02d}:{seconds:02d}")
            
    def save_recording(self):
        """保存录音"""
        if not self.recorded_frames:
            QMessageBox.warning(self, "警告", "没有录音数据！")
            return
            
        # 生成默认文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"录音_{timestamp}.wav"
        default_path = os.path.join(self.output_dir, default_filename)
        
        # 选择保存路径
        path, _ = QFileDialog.getSaveFileName(
            self,
            "保存录音",
            default_path,
            "WAV文件 (*.wav);;所有文件 (*.*)"
        )
        
        if path:
            try:
                # 确保目录存在
                os.makedirs(os.path.dirname(path), exist_ok=True)
                
                # 保存WAV文件
                wf = wave.open(path, 'wb')
                wf.setnchannels(1)
                wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
                wf.setframerate(44100)
                wf.writeframes(b''.join(self.recorded_frames))
                wf.close()
                
                QMessageBox.information(self, "成功", f"录音已保存到:\n{path}")
                self.refresh_file_list()
                
                # 更新输出目录
                self.output_dir = os.path.dirname(path)
                self.dir_edit.setText(self.output_dir)
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存录音失败:\n{str(e)}")
                
    def browse_dir(self):
        """浏览目录"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "选择保存目录",
            self.output_dir
        )
        if directory:
            self.output_dir = directory
            self.dir_edit.setText(directory)
            self.refresh_file_list()
            
    def refresh_file_list(self):
        """刷新文件列表"""
        self.file_tree.clear()
        
        if not os.path.exists(self.output_dir):
            return
            
        # 扫描目录
        wav_files = []
        for file in os.listdir(self.output_dir):
            if file.endswith('.wav'):
                filepath = os.path.join(self.output_dir, file)
                try:
                    stat = os.stat(filepath)
                    
                    # 获取音频时长
                    duration = 0
                    try:
                        with wave.open(filepath, 'rb') as wf:
                            frames = wf.getnframes()
                            rate = wf.getframerate()
                            duration = frames / rate
                    except:
                        pass
                        
                    wav_files.append({
                        'path': filepath,
                        'name': file,
                        'duration': duration,
                        'mtime': stat.st_mtime
                    })
                except:
                    pass
                    
        # 按时间排序，最新的在前面
        wav_files.sort(key=lambda x: x['mtime'], reverse=True)
        
        # 添加到列表
        for wav in wav_files:
            # 格式化时长
            if wav['duration'] > 0:
                minutes = int(wav['duration'] // 60)
                seconds = int(wav['duration'] % 60)
                duration_str = f"{minutes:02d}:{seconds:02d}"
            else:
                duration_str = "未知"
                
            # 格式化时间
            date_str = datetime.fromtimestamp(wav['mtime']).strftime("%Y-%m-%d %H:%M:%S")
            
            item = QTreeWidgetItem([wav['name'], duration_str, date_str])
            self.file_tree.addTopLevelItem(item)
            
    def closeEvent(self, event):
        """关闭事件"""
        if self.is_recording:
            self.is_recording = False
            self.recorder.stop_recording()
            
        event.accept()
