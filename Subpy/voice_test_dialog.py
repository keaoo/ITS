#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语音测试配置界面
"""
import sys
import os
import json
import re
import threading
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout,
    QLabel, QComboBox, QPushButton, QCheckBox, QListWidget,
    QSplitter, QFileDialog, QMessageBox, QWidget, QSpinBox, QLineEdit
)
from PySide6.QtCore import Qt, QThread, Signal


class VoiceTestDialog(QDialog):
    """语音测试配置对话框"""

    def __init__(self, parent=None, vehicle_platform="8295"):
        super().__init__(None)
        self.parent = parent
        self.vehicle_platform = str(vehicle_platform or "8295").strip()
        self.setWindowTitle("语音测试设置")
        self.setMinimumSize(1000, 700)
        self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        
        # 🎯 基准采集线程相关
        self.baseline_worker = None
        
        # 🎯 本地声音缓存
        self.local_voices = []
        
        self.init_ui()
        self.load_local_voices()
        self.load_instructions()
        self.load_config()

    def init_ui(self):
        """初始化界面"""
        main_layout = QHBoxLayout(self)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        left_widget = self.create_left_panel()
        left_widget.setMinimumWidth(600)
        splitter.addWidget(left_widget)

        right_widget = self.create_right_panel()
        right_widget.setMaximumWidth(350)
        splitter.addWidget(right_widget)

        splitter.setSizes([650, 350])
        main_layout.addWidget(splitter)

    def load_local_voices(self):
        """加载本地声音列表"""
        try:
            import pyttsx3
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            self.local_voices = [(v.name, v.id) for v in voices]
        except Exception as e:
            self.local_voices = [("默认女声", "")]
        
        # 初始化声音列表
        self.refresh_voice_list()
    
    def refresh_voice_list(self):
        """刷新声音列表"""
        library = self.tts_library_combo.currentText()
        self.voice_combo.clear()
        
        if library == "本地TTS (pyttsx3)":
            self.language_combo.setEnabled(True)
            self.speed_combo.setEnabled(True)
            
            for name, vid in self.local_voices:
                self.voice_combo.addItem(name, vid)
            
            if self.local_voices:
                self.voice_combo.setCurrentIndex(0)
        else:
            self.voice_combo.addItem("女声 - Xiaoxiao", "zh-CN-XiaoxiaoNeural")
            self.voice_combo.addItem("男声 - Yunjian", "zh-CN-YunjianNeural")
            
            self.language_combo.setEnabled(True)
            self.speed_combo.setEnabled(True)
    
    def on_play_mode_changed(self, mode):
        """播放模式切换时更新TTS设置状态"""
        if mode == "播放录音":
            # 播放录音时，除了输出设备其他都禁用
            self.tts_library_combo.setEnabled(False)
            self.voice_combo.setEnabled(False)
            self.language_combo.setEnabled(False)
            self.speed_combo.setEnabled(False)
            self.device_combo.setEnabled(True)
        else:
            # TTS播放时，全部启用
            self.tts_library_combo.setEnabled(True)
            self.voice_combo.setEnabled(True)
            self.language_combo.setEnabled(True)
            self.speed_combo.setEnabled(True)
            self.refresh_voice_list()
    
    def on_tts_library_changed(self, library):
        """TTS库切换时更新声音列表"""
        self.refresh_voice_list()

    def load_instructions(self):
        """从voice_test_config.py加载所有语音测试指令到选择器"""
        try:
            from Subpy.voice_test_config import get_instruction_names
            instruction_names = get_instruction_names(self.vehicle_platform)
            self.selector.add_left_items(instruction_names)
            self.selector.update_labels()
        except Exception as e:
            print(f"加载语音测试指令失败: {e}")

    def create_left_panel(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title_label = QLabel("📋 语音测试指令")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)

        from Subpy.list_selector import ListSelector
        self.selector = ListSelector(left_items=[], insert_after_selected_right=True)
        self.selector.set_vehicle_platform(self.vehicle_platform)
        layout.addWidget(self.selector)

        combo_btn_layout = QHBoxLayout()
        self.save_combo_btn = QPushButton("💾 保存组合")
        self.save_combo_btn.clicked.connect(self.save_combination)
        self.save_combo_btn.setMinimumHeight(25)
        combo_btn_layout.addWidget(self.save_combo_btn)

        self.load_combo_btn = QPushButton("📂 加载组合")
        self.load_combo_btn.clicked.connect(self.load_combination)
        self.load_combo_btn.setMinimumHeight(25)
        combo_btn_layout.addWidget(self.load_combo_btn)

        layout.addLayout(combo_btn_layout)

        return widget

    def create_right_panel(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 1. 播放方式
        play_group = QGroupBox("🎵 播放方式")
        play_layout = QFormLayout(play_group)
        self.play_mode_combo = QComboBox()
        self.play_mode_combo.addItems(["TTS播放", "播放录音"])
        self.play_mode_combo.currentTextChanged.connect(self.on_play_mode_changed)
        play_layout.addRow("播放方式:", self.play_mode_combo)
        layout.addWidget(play_group)

        # 2. TTS设置
        tts_group = QGroupBox("🔊 TTS设置")
        tts_layout = QFormLayout(tts_group)

        self.tts_library_combo = QComboBox()
        self.tts_library_combo.addItems(["本地TTS (pyttsx3)", "云端TTS (edge-tts)"])
        self.tts_library_combo.currentTextChanged.connect(self.on_tts_library_changed)
        tts_layout.addRow("TTS库:", self.tts_library_combo)

        self.voice_combo = QComboBox()
        tts_layout.addRow("声音:", self.voice_combo)

        self.language_combo = QComboBox()
        self.language_combo.addItems(["中文", "英语"])
        tts_layout.addRow("语言:", self.language_combo)

        self.speed_combo = QComboBox()
        self.speed_combo.addItems(["慢速", "正常", "快速"])
        self.speed_combo.setCurrentIndex(1)
        tts_layout.addRow("语速:", self.speed_combo)

        self.device_combo = QComboBox()
        self.device_combo.setMinimumWidth(200)
        self.device_combo.setEditable(False)
        self.device_combo.addItem("使用系统默认输出设备", 0)
        tts_layout.addRow("输出设备:", self.device_combo)

        layout.addWidget(tts_group)

        # 3. 录音文件设置
        audio_group = QGroupBox("🎤 录音文件设置")
        audio_layout = QVBoxLayout(audio_group)

        audio_path_layout = QHBoxLayout()
        audio_path_layout.addWidget(QLabel("录音文件夹:"))
        self.audio_path_edit = QLineEdit("(未设置)")
        self.audio_path_edit.setReadOnly(True)
        audio_path_layout.addWidget(self.audio_path_edit)
        audio_select_btn = QPushButton("选择文件夹")
        audio_select_btn.clicked.connect(self.select_audio_folder)
        audio_path_layout.addWidget(audio_select_btn)
        audio_layout.addLayout(audio_path_layout)

        self.audio_file_list = QListWidget()
        audio_layout.addWidget(self.audio_file_list)

        layout.addWidget(audio_group)

        # 3.5 语音测试文件夹路径
        test_folder_group = QGroupBox("📂 语音测试文件夹路径")
        test_folder_layout = QVBoxLayout(test_folder_group)

        test_folder_path_layout = QHBoxLayout()
        test_folder_path_layout.addWidget(QLabel("测试记录文件夹:"))
        self.test_folder_path_edit = QLineEdit("(未设置)")
        self.test_folder_path_edit.setReadOnly(True)
        test_folder_path_layout.addWidget(self.test_folder_path_edit)
        test_folder_select_btn = QPushButton("选择文件夹")
        test_folder_select_btn.clicked.connect(self.select_test_folder)
        test_folder_path_layout.addWidget(test_folder_select_btn)
        test_folder_layout.addLayout(test_folder_path_layout)

        layout.addWidget(test_folder_group)

        # 4. 循环测试设置
        loop_test_group = QGroupBox("🔄 循环测试设置")
        loop_test_layout = QFormLayout(loop_test_group)
        
        self.cycle_count_spin = QSpinBox()
        self.cycle_count_spin.setMinimum(1)
        self.cycle_count_spin.setMaximum(9999)
        self.cycle_count_spin.setValue(10)
        loop_test_layout.addRow("循环次数:", self.cycle_count_spin)
        
        layout.addWidget(loop_test_group)

        # 5. 自动基准测试
        auto_test_group = QGroupBox("🎯 自动基准测试")
        auto_test_layout = QVBoxLayout(auto_test_group)
        
        btn_layout = QHBoxLayout()
        
        self.run_test_btn = QPushButton("执行并保存基准")
        self.run_test_btn.clicked.connect(self.run_batch_test)
        self.run_test_btn.setMinimumHeight(25)
        btn_layout.addWidget(self.run_test_btn)
        
        self.stop_test_btn = QPushButton("停止测试")
        self.stop_test_btn.clicked.connect(self.stop_batch_test)
        self.stop_test_btn.setMinimumHeight(25)
        self.stop_test_btn.setEnabled(False)
        btn_layout.addWidget(self.stop_test_btn)
        
        self.reset_baseline_btn = QPushButton("重新采集基准")
        self.reset_baseline_btn.clicked.connect(self.reset_selected_baselines)
        self.reset_baseline_btn.setMinimumHeight(25)
        btn_layout.addWidget(self.reset_baseline_btn)
        
        auto_test_layout.addLayout(btn_layout)
        layout.addWidget(auto_test_group)

        layout.addStretch()
        return widget

    def save_combination(self):
        from PySide6.QtWidgets import QFileDialog
        filename, _ = QFileDialog.getSaveFileName(
            self, "保存指令组合", "", "TXT文件 (*.txt);;JSON文件 (*.json)"
        )
        if filename:
            # 获取右侧已选项
            selected_items = self.selector.get_selected_items()
            data = {"selected_instructions": selected_items}
            try:
                # 确保文件扩展名正确
                if not filename.lower().endswith(('.txt', '.json')):
                    filename += '.txt'
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                QMessageBox.information(self, "成功", "指令组合已保存!")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"保存失败: {str(e)}")

    def load_combination(self):
        from PySide6.QtWidgets import QFileDialog
        filename, _ = QFileDialog.getOpenFileName(
            self, "加载指令组合", "", "TXT文件 (*.txt);;JSON文件 (*.json)"
        )
        if filename:
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    data = json.load(f)
                selected_items = data.get("selected_instructions", [])
                self.selector.set_selected_items(selected_items)
                QMessageBox.information(self, "成功", "指令组合已加载!")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"加载失败: {str(e)}")

    def select_audio_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择录音文件夹")
        if folder:
            self.audio_path_edit.setText(folder)
            self.refresh_audio_list(folder)

    def select_test_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择语音测试记录文件夹")
        if folder:
            self.test_folder_path_edit.setText(folder)

    def refresh_audio_list(self, folder):
        self.audio_file_list.clear()
        if not os.path.exists(folder):
            return
        for filename in os.listdir(folder):
            if filename.lower().endswith((".wav", ".mp3", ".m4a", ".flac")):
                self.audio_file_list.addItem(filename)

    def load_config(self):
        if self.parent and "voice_test" in self.parent.config:
            config = self.parent.config["voice_test"]

            supported = set()
            try:
                from Subpy.voice_test_config import get_instruction_names
                supported = set(get_instruction_names(self.vehicle_platform))
            except Exception:
                supported = set()
            selected_instructions = [
                name for name in config.get("selected_instructions", [])
                if not supported or name in supported
            ]
            self.selector.set_selected_items(selected_instructions)
            self.selector.update_labels()

            # 加载播放方式
            play_mode = config.get("play_mode", "TTS播放")
            index = self.play_mode_combo.findText(play_mode)
            if index >= 0:
                self.play_mode_combo.setCurrentIndex(index)
            
            # 加载TTS设置
            tts_library = config.get("tts_library", "本地TTS (pyttsx3)")
            index = self.tts_library_combo.findText(tts_library)
            if index >= 0:
                self.tts_library_combo.setCurrentIndex(index)
            
            voice = config.get("voice", "")
            index = self.voice_combo.findText(voice)
            if index >= 0:
                self.voice_combo.setCurrentIndex(index)
            
            language = config.get("language", "中文")
            index = self.language_combo.findText(language)
            if index >= 0:
                self.language_combo.setCurrentIndex(index)
            
            speed = config.get("speed", "正常")
            index = self.speed_combo.findText(speed)
            if index >= 0:
                self.speed_combo.setCurrentIndex(index)
            
            # 加载循环次数
            cycle_count = config.get("cycle_count", 10)
            self.cycle_count_spin.setValue(cycle_count)
            
            if "audio_folder" in config:
                self.audio_path_edit.setText(config["audio_folder"])
                self.refresh_audio_list(config["audio_folder"])
            
            if "test_folder" in config:
                self.test_folder_path_edit.setText(config["test_folder"])
            
            # 关键：根据播放方式更新TTS设置状态
            self.on_play_mode_changed(play_mode)

    def append_log(self, text):
        if self.parent and hasattr(self.parent, "append_log"):
            from datetime import datetime
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.parent.append_log(f"[{timestamp}] {text}")
        elif self.parent and hasattr(self.parent, "text_edit1"):
            from datetime import datetime
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.parent.text_edit1.append(f"[{timestamp}] {text}")

    def run_batch_test(self):
        selected_instructions = self.selector.get_selected_items()
        if not selected_instructions:
            QMessageBox.warning(self, "提示", "请先在选择器中选择要执行的指令")
            return
        
        self.run_test_btn.setEnabled(False)
        self.stop_test_btn.setEnabled(True)
        
        self.append_log("="*60)
        self.append_log(f">>> 开始采集基准，共 {len(selected_instructions)} 条指令")
        
        tts_library = self.tts_library_combo.currentText()
        language = self.language_combo.currentText()
        speed = self.speed_combo.currentText()
        voice_name = self.voice_combo.currentText()
        voice_id = self.voice_combo.currentData()
        
        # 获取播放模式和音频文件夹
        play_mode = self.play_mode_combo.currentText()
        audio_folder = self.audio_path_edit.text() if self.audio_path_edit.text() != "(未设置)" else ""
        
        self.baseline_worker = BaselineWorker(
            selected_instructions, self, tts_library, language, speed, voice_name, voice_id, play_mode, audio_folder
        )
        self.baseline_worker.log_signal.connect(self.append_log)
        self.baseline_worker.finished_signal.connect(self._on_baseline_finished)
        self.baseline_worker.start()

    def stop_batch_test(self):
        if self.baseline_worker and self.baseline_worker.isRunning():
            self.baseline_worker.stop()
            self.append_log("\n⚠️ 正在停止测试...")
    
    def reset_selected_baselines(self):
        self.reset_baseline_btn.setEnabled(False)
        self.run_batch_test()

    def _on_baseline_finished(self, success_count):
        self.run_test_btn.setEnabled(True)
        self.stop_test_btn.setEnabled(False)
        self.reset_baseline_btn.setEnabled(True)
        
        total = len(self.selector.get_selected_items())
        failed = total - success_count
        
        if self.baseline_worker and self.baseline_worker._stop_flag:
            self.append_log("="*60 + "\n")
            QMessageBox.information(self, "提示", "已手动停止")
        else:
            self.append_log("\n" + "="*60)
            self.append_log(f"📊 基准采集完成:")
            self.append_log(f"   总指令数: {total}")
            self.append_log(f"   成功: {success_count}")
            self.append_log(f"   失败: {failed}")
            self.append_log("="*60 + "\n")
            
            summary_msg = f"基准采集完成!\n\n总指令数: {total}\n成功: {success_count}\n失败: {failed}"
            if failed > 0:
                QMessageBox.warning(self, "完成", summary_msg)
            else:
                QMessageBox.information(self, "完成", summary_msg)
        
        self.baseline_worker = None

    def closeEvent(self, event):
        self.save_config()
        event.accept()

    def save_config(self):
        config = {}
        config["selected_instructions"] = self.selector.get_selected_items()
        config["vehicle_platform"] = self.vehicle_platform
        
        # 保存播放方式
        config["play_mode"] = self.play_mode_combo.currentText()
        
        # 保存TTS设置
        config["tts_library"] = self.tts_library_combo.currentText()
        config["voice"] = self.voice_combo.currentText()
        config["language"] = self.language_combo.currentText()
        config["speed"] = self.speed_combo.currentText()
        
        # 保存循环次数
        config["cycle_count"] = self.cycle_count_spin.value()
        
        audio_path = self.audio_path_edit.text()
        if audio_path != "(未设置)":
            config["audio_folder"] = audio_path
        
        test_folder_path = self.test_folder_path_edit.text()
        if test_folder_path != "(未设置)":
            config["test_folder"] = test_folder_path
        
        if self.parent:
            self.parent.config.update({"voice_test": config})
            self.parent.save_config()


class BaselineWorker(QThread):
    log_signal = Signal(str)
    finished_signal = Signal(int)
    
    def __init__(self, instruction_names, dialog_parent=None, tts_library="本地TTS (pyttsx3)", language="中文", speed="正常", voice_name="", voice_id="", play_mode="TTS播放", audio_folder=""):
        super().__init__(dialog_parent)
        self.instruction_names = instruction_names
        self._stop_flag = False
        self.dialog_parent = dialog_parent
        self.vehicle_platform = getattr(dialog_parent, "vehicle_platform", "8295")
        self.tts_library = tts_library
        self.language = language
        self.speed = speed
        self.voice_name = voice_name
        self.voice_id = voice_id
        self.play_mode = play_mode
        self.audio_folder = audio_folder
        self.log_path = ""
        self.test_folder = ""
        if dialog_parent and dialog_parent.parent:
            main_win = dialog_parent.parent
            if "zonghe_test" in main_win.config:
                self.log_path = main_win.config["zonghe_test"].get("fold_path1", "")
            if "voice_test" in main_win.config:
                self.test_folder = main_win.config["voice_test"].get("test_folder", "")
        
        # 日志抓取相关
        self.log_capture_thread = None
        self.log_file_path = None
        self.log_capture_proc = None
        self._stop_log_capture = False
    
    def run(self):
        success_count = 0
        
        # 在开始前就启动日志抓取
        self.start_log_capture()
        
        try:
            for name in self.instruction_names:
                if self._stop_flag:
                    break
                
                self.log_signal.emit(f"\n--- {name} ---")
                
                try:
                    from Subpy.voice_test_config import get_instruction_config
                    config = get_instruction_config(name, self.vehicle_platform)
                    if not config:
                        self.log_signal.emit(f"❌ 找不到指令配置: {name}")
                        continue
                    
                    # 检查是否是特殊指令
                    if config.get("mode") == "special" and config.get("special_type") == "audio_detection":
                        # 音频探测指令
                        self.log_signal.emit("🎵 执行音频探测指令")
                        self.execute_audio_detection(config)
                        success_count += 1
                        continue
                    
                    # 记录当前文件位置，用于后续读取新日志
                    last_position = self.get_log_file_position()
                    
                    if config.get("mode") == "tts":
                        # 根据播放模式决定播放方式
                        if self.play_mode == "播放录音":
                            # 播放录音文件
                            self.log_signal.emit(f"🎤 播放录音: {name}")
                            self.log_signal.emit(f"📁 音频文件夹: {self.audio_folder}")
                            self.play_audio_file(name)
                        else:
                            # 播放TTS
                            if self.language == "中文":
                                play_text = config["tts_text"]
                            else:
                                play_text = config.get("tts_text_en", config["tts_text"])
                            
                            self.log_signal.emit(f"🎤 播放: {play_text}")
                            self.log_signal.emit(f"🔊 TTS库: {self.tts_library} | 语言: {self.language} | 语速: {self.speed} | 声音: {self.voice_name}")
                            
                            if self.tts_library == "本地TTS (pyttsx3)":
                                self.play_pyttsx3(play_text)
                            else:
                                self.play_edge_tts(play_text)
                    
                    wait_seconds = config.get("wait_seconds", 3)
                    self.log_signal.emit(f"⏳ 等待 {wait_seconds} 秒...")
                    import time
                    time.sleep(wait_seconds)
                    
                    # 从日志文件读取新增内容
                    self.log_signal.emit(f"📡 从日志文件读取新增内容...")
                    log_content = self.read_new_log_content(last_position)
                    
                    if log_content:
                        from Subpy.voice_test_config import parse_logs_for_baseline
                        baseline_data = parse_logs_for_baseline(log_content, instruction_name=name)
                        
                        # 输出所有提取的信息
                        self.log_signal.emit(f"✅ 识别结果: {baseline_data.get('recognition', '')}")
                        self.log_signal.emit(f"✅ 车机响应: {baseline_data.get('response', '')}")
                        if baseline_data.get("response_time_ms"):
                            self.log_signal.emit(f"✅ 响应时间: {baseline_data.get('response_time_ms')} ms")
                        if baseline_data.get("voice_zone"):
                            self.log_signal.emit(f"✅ 响应区域: {baseline_data.get('voice_zone')}")
                        
                        # 获取并保存信号值
                        signal_values = {}
                        verify_signals = config.get("verify_signals", [])
                        for signal_item in verify_signals:
                            if len(signal_item) >= 2:
                                signal_name = signal_item[0]
                                adb_cmd = signal_item[1]
                                actual_value = self._get_signal_value(adb_cmd)
                                
                                # 获取容差（默认3）
                                tolerance = 3
                                if len(signal_item) >= 3:
                                    tolerance = signal_item[2]
                                
                                # 保存信号值和容差
                                signal_values[signal_name] = {
                                    "value": actual_value,
                                    "tolerance": tolerance
                                }
                                
                                # 只显示信号状态和容差，不做对比（第三个元素是容差，不是期望值）
                                self.log_signal.emit(f"📡 {signal_name} 状态: {actual_value} (容差: {tolerance})")
                        
                        self.save_voice_baseline(name, baseline_data, signal_values)
                        success_count += 1
                    else:
                        self.log_signal.emit(f"⚠️ 未获取到日志，保存空基准")
                        self.save_voice_baseline(name, {"recognition": "", "response": "", "response_time_ms": 0, "voice_zone": ""})
                        success_count += 1
                    
                except Exception as e:
                    self.log_signal.emit(f"❌ 执行失败: {e}")
                    import traceback
                    self.log_signal.emit(f"📋 错误详情: {traceback.format_exc()}")
        finally:
            # 所有指令执行完成后才停止日志抓取
            self.log_signal.emit(f"📡 所有指令执行完成，停止日志抓取...")
            self.stop_log_capture()
        
        self.finished_signal.emit(success_count)
    
    def get_speed_rate(self):
        if self.speed == "慢速":
            return 0.8
        elif self.speed == "快速":
            return 1.2
        else:
            return 1.0
    
    def play_pyttsx3(self, play_text):
        try:
            import pyttsx3
            engine = pyttsx3.init()
            
            if self.voice_id:
                engine.setProperty('voice', self.voice_id)
            
            engine.setProperty('rate', int(200 * self.get_speed_rate()))
            
            self.log_signal.emit("🔊 开始播放...")
            engine.say(play_text)
            engine.runAndWait()
            self.log_signal.emit("✅ 播放完成!")
        except ImportError:
            self.log_signal.emit("⚠️ pyttsx3 未安装，请执行: pip install pyttsx3")
        except Exception as e:
            self.log_signal.emit(f"❌ 播放失败: {e}")
    
    def play_edge_tts(self, play_text):
        try:
            import edge_tts
            import tempfile
            import pygame.mixer
            import asyncio
            
            voice_map = {
                "女声 - Xiaoxiao": "zh-CN-XiaoxiaoNeural",
                "男声 - Yunjian": "zh-CN-YunjianNeural"
            }
            
            vid = voice_map.get(self.voice_name, "zh-CN-XiaoxiaoNeural")
            
            rate_str = "+0%"
            if self.speed == "慢速":
                rate_str = "-20%"
            elif self.speed == "快速":
                rate_str = "+20%"
            
            self.log_signal.emit("🔊 正在生成音频...")
            
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            temp_file.close()
            
            async def generate_audio():
                communicate = edge_tts.Communicate(play_text, vid, rate=rate_str)
                await communicate.save(temp_file.name)
            
            asyncio.run(generate_audio())
            
            self.log_signal.emit("🔊 开始播放...")
            
            pygame.mixer.init()
            pygame.mixer.music.load(temp_file.name)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            
            pygame.mixer.quit()
            os.unlink(temp_file.name)
            
            self.log_signal.emit("✅ 播放完成!")
        except ImportError:
            self.log_signal.emit("⚠️ edge-tts 或 pygame 未安装，请执行: pip install edge-tts pygame")
        except Exception as e:
            self.log_signal.emit(f"❌ 播放失败: {e}")
    
    def execute_audio_detection(self, config):
        """执行音频探测"""
        try:
            from Subpy.audio_detection import AudioDetector
            
            # 获取音频探测设置（从主程序配置读取）
            # 默认采集时间和音量下限
            duration_seconds = 10  # 默认10秒
            threshold_percent = 30  # 默认30%
            
            # 尝试从主程序配置读取
            if self.dialog_parent and hasattr(self.dialog_parent, 'parent'):
                main_win = self.dialog_parent.parent
                if 'voice_test' in main_win.config:
                    vt_config = main_win.config.get('voice_test', {})
                    duration_seconds = vt_config.get('detection_duration', 10)
                    threshold_percent = vt_config.get('volume_threshold', 30)
            
            # 使用主程序的保存文件夹
            save_folder = self.log_path
            
            if not save_folder:
                self.log_signal.emit(f"⚠️ 未设置保存文件夹，使用默认路径")
                import sys
                if hasattr(sys, '_MEIPASS'):
                    save_folder = os.path.dirname(os.path.abspath(sys.executable))
                else:
                    save_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            self.log_signal.emit(f"🎵 音频探测开始")
            self.log_signal.emit(f"⏱️ 采集时长: {duration_seconds} 秒")
            self.log_signal.emit(f"🎯 音量下限: {threshold_percent} %")
            self.log_signal.emit(f"📁 保存文件夹: {save_folder}")
            
            # 创建探测器并执行
            detector = AudioDetector(self.log_signal.emit)
            result = detector.detect(duration_seconds, save_folder, threshold_percent)
            
            if result["success"]:
                self.log_signal.emit(f"✅ 音频探测成功")
                self.log_signal.emit(f"📊 平均音量: {result['avg_volume']:.2f} %")
                self.log_signal.emit(f"🎯 音量下限: {threshold_percent} %")
                if result["is_silent"]:
                    self.log_signal.emit(f"🔇 判断结果: 环境静音 (平均音量 < 下限)")
                else:
                    self.log_signal.emit(f"🔊 判断结果: 环境有声音 (平均音量 >= 下限)")
                
                if result["audio_file"]:
                    self.log_signal.emit(f"💾 音频已保存: {result['audio_file']}")
                
                # 保存基准数据
                baseline_data = {
                    "recognition": "音频探测",
                    "response": "完成",
                    "avg_volume": result["avg_volume"],
                    "is_silent": result["is_silent"],
                    "threshold": threshold_percent,
                    "duration": duration_seconds,
                    "audio_file": result["audio_file"]
                }
                
                self.save_voice_baseline("音频探测", baseline_data)
                
            else:
                self.log_signal.emit(f"❌ 音频探测失败: {result['error']}")
                # 即使失败也保存空基准
                self.save_voice_baseline("音频探测", {"recognition": "失败", "response": result["error"]})
            
        except ImportError as e:
            self.log_signal.emit(f"❌ 缺少模块导入失败: {e}")
            self.log_signal.emit(f"💡 请确保 audio_detection.py 文件存在")
        except Exception as e:
            self.log_signal.emit(f"❌ 音频探测执行失败: {e}")
            import traceback
            self.log_signal.emit(f"📋 错误详情: {traceback.format_exc()}")
    
    def play_audio_file(self, instruction_name):
        """播放音频文件"""
        try:
            import pygame.mixer
            import time
            
            if not self.audio_folder or not os.path.exists(self.audio_folder):
                self.log_signal.emit(f"❌ 音频文件夹不存在: {self.audio_folder}")
                return
            
            # 清理文件名中的非法字符
            import re
            safe_name = re.sub(r'[\\/:*?"<>|]', '_', instruction_name)
            
            # 查找匹配的音频文件
            audio_file = None
            matched_filename = None
            
            # 获取所有音频文件
            audio_files = []
            for filename in os.listdir(self.audio_folder):
                if filename.lower().endswith(('.wav', '.mp3', '.m4a', '.flac')):
                    audio_files.append(filename)
            
            if not audio_files:
                self.log_signal.emit(f"❌ 文件夹中没有音频文件")
                return
            
            self.log_signal.emit(f"📁 文件夹中的音频文件: {', '.join(audio_files[:5])}")
            if len(audio_files) > 5:
                self.log_signal.emit(f"   ... 还有 {len(audio_files) - 5} 个文件")
            
            # 方式1: 精确匹配（包含扩展名）
            for filename in audio_files:
                name_without_ext = os.path.splitext(filename)[0]
                if name_without_ext == instruction_name:
                    audio_file = os.path.join(self.audio_folder, filename)
                    matched_filename = filename
                    self.log_signal.emit(f"🎯 方式1匹配: {filename}")
                    break
            
            # 方式2: 精确匹配（清理后的文件名）
            if not audio_file:
                for filename in audio_files:
                    name_without_ext = os.path.splitext(filename)[0]
                    safe_name_without_ext = re.sub(r'[\\/:*?"<>|]', '_', name_without_ext)
                    if safe_name_without_ext == safe_name:
                        audio_file = os.path.join(self.audio_folder, filename)
                        matched_filename = filename
                        self.log_signal.emit(f"🎯 方式2匹配: {filename}")
                        break
            
            # 方式3: 文件名包含指令名
            if not audio_file:
                for filename in audio_files:
                    name_without_ext = os.path.splitext(filename)[0]
                    if instruction_name in name_without_ext:
                        audio_file = os.path.join(self.audio_folder, filename)
                        matched_filename = filename
                        self.log_signal.emit(f"🎯 方式3匹配: {filename}")
                        break
            
            # 方式4: 指令名包含文件名
            if not audio_file:
                for filename in audio_files:
                    name_without_ext = os.path.splitext(filename)[0]
                    if name_without_ext in instruction_name:
                        audio_file = os.path.join(self.audio_folder, filename)
                        matched_filename = filename
                        self.log_signal.emit(f"🎯 方式4匹配: {filename}")
                        break
            
            # 方式5: 部分关键词匹配（从指令名提取关键词）
            if not audio_file:
                # 提取关键词（去掉前缀，比如"唤醒："）
                keywords = []
                if "：" in instruction_name:
                    keywords.append(instruction_name.split("：", 1)[1].strip())
                elif ":" in instruction_name:
                    keywords.append(instruction_name.split(":", 1)[1].strip())
                keywords.append(instruction_name)
                
                self.log_signal.emit(f"🔍 尝试关键词匹配: {keywords}")
                
                for filename in audio_files:
                    name_without_ext = os.path.splitext(filename)[0]
                    for keyword in keywords:
                        if keyword and keyword in name_without_ext:
                            audio_file = os.path.join(self.audio_folder, filename)
                            matched_filename = filename
                            self.log_signal.emit(f"🎯 方式5匹配: {filename} (关键词: {keyword})")
                            break
                    if audio_file:
                        break
            
            if not audio_file:
                self.log_signal.emit(f"❌ 未找到音频文件: {instruction_name}")
                self.log_signal.emit(f"💡 支持的格式: .wav, .mp3, .m4a, .flac")
                self.log_signal.emit(f"💡 提示: 文件名可以是指令名的一部分，或者包含指令名的关键词")
                return
            
            self.log_signal.emit(f"🎵 播放文件: {os.path.basename(audio_file)}")
            self.log_signal.emit(f"🔊 开始播放...")
            
            # 播放音频
            pygame.mixer.init()
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            
            pygame.mixer.quit()
            
            self.log_signal.emit(f"✅ 播放完成!")
            
        except ImportError:
            self.log_signal.emit(f"⚠️ pygame 未安装，请执行: pip install pygame")
        except Exception as e:
            self.log_signal.emit(f"❌ 播放失败: {e}")
    
    def save_voice_baseline(self, name, data, signal_values=None):
        import sys
        import os
        if hasattr(sys, '_MEIPASS'):
            base_path = os.path.dirname(os.path.abspath(sys.executable))
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # 统一保存到 all_baselines.json 文件中
        baseline_dir = os.path.join(base_path, "配置基准文件")
        if not os.path.exists(baseline_dir):
            os.makedirs(baseline_dir)
        
        all_baseline_file = os.path.join(baseline_dir, "all_baselines.json")
        
        import json
        from datetime import datetime
        
        # 加载现有的基准
        if os.path.exists(all_baseline_file):
            try:
                with open(all_baseline_file, "r", encoding="utf-8") as f:
                    all_baselines = json.load(f)
            except:
                all_baselines = {}
        else:
            all_baselines = {}
        
        # 保存语音测试基准（前缀区分）
        baseline_name = f"语音_{name}"
        baseline_data = {
            "type": "voice_test",
            "instruction": name,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "results": data
        }
        
        if signal_values:
            baseline_data["signal_values"] = signal_values
        
        all_baselines[baseline_name] = baseline_data
        
        # 保存到文件
        with open(all_baseline_file, "w", encoding="utf-8") as f:
            json.dump(all_baselines, f, ensure_ascii=False, indent=2)
        
        self.log_signal.emit(f"✅ 基准已保存: {baseline_name}")
    
    def start_log_capture(self):
        """启动日志抓取，使用shell重定向直接写入文件"""
        try:
            # 确定测试文件夹路径
            if not self.test_folder or not os.path.exists(self.test_folder):
                import sys
                if hasattr(sys, '_MEIPASS'):
                    self.test_folder = os.path.dirname(os.path.abspath(sys.executable))
                else:
                    self.test_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            self.log_file_path = os.path.join(self.test_folder, "语音日志.txt")
            
            # 清空现有日志文件或创建新文件
            with open(self.log_file_path, "w", encoding="utf-8") as f:
                f.write("")
            
            self.log_signal.emit(f"📡 启动日志抓取...")
            self.log_signal.emit(f"📝 日志文件: {self.log_file_path}")
            
            # 启动日志抓取线程
            self._stop_log_capture = False
            self.log_capture_thread = threading.Thread(target=self._log_capture_loop, daemon=True)
            self.log_capture_thread.start()
            
            import time
            time.sleep(1)
            
        except Exception as e:
            self.log_signal.emit(f"❌ 启动日志抓取失败: {e}")
    
    def _log_capture_loop(self):
        """日志抓取循环，使用shell重定向"""
        import subprocess
        import time
        import tempfile
        import os

        # 记录当前时间戳，用于去重（避免重复写入相同日志）
        last_log_lines = set()
        first_iteration = True
        
        while not self._stop_log_capture:
            try:
                # 使用shell重定向直接写入临时文件，然后去重后追加到主日志
                
                # 先写入临时文件
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as tmp_file:
                    tmp_file_path = tmp_file.name
                
                # 第一次迭代时先清理旧的adb连接
                if first_iteration:
                    try:
                        subprocess.run(["adb", "-host", "kill-server"], capture_output=True, timeout=5)
                        time.sleep(0.5)
                    except Exception as e:
                        pass
                    first_iteration = False
                
                # 执行命令 - 使用 logctl -b main -d 和 grep 过滤
                cmd = f'adb -host shell "logctl -b main -d | grep -iE \'voice_handleASRKeyWord|play tts:|OrchASR4BMSp: word =|remote dialog result|totalCost\'" > "{tmp_file_path}"'
                proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                proc.wait(timeout=3)
                
                # 读取临时文件内容，去重后追加到主日志
                if os.path.exists(tmp_file_path):
                    try:
                        with open(tmp_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            new_lines = f.readlines()
                        
                        # 去重（只添加之前没有出现过的行）
                        unique_new_lines = []
                        for line in new_lines:
                            line_stripped = line.strip()
                            if line_stripped and line_stripped not in last_log_lines:
                                unique_new_lines.append(line)
                                last_log_lines.add(line_stripped)
                        
                        # 限制内存使用，只保留最近1000行
                        if len(last_log_lines) > 1000:
                            last_log_lines = set(list(last_log_lines)[-1000:])
                        
                        # 追加新内容到主日志
                        if unique_new_lines:
                            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                                f.writelines(unique_new_lines)
                        
                    except Exception as e:
                        pass
                    
                    # 删除临时文件
                    try:
                        os.unlink(tmp_file_path)
                    except:
                        pass

            except subprocess.TimeoutExpired:
                try:
                    proc.kill()
                except:
                    pass
            except Exception as e:
                pass

            # 稍作延迟后继续
            time.sleep(0.5)
    
    def get_log_file_position(self):
        """获取当前日志文件位置"""
        if self.log_file_path and os.path.exists(self.log_file_path):
            return os.path.getsize(self.log_file_path)
        return 0
    
    def read_new_log_content(self, start_position):
        """从日志文件读取新增内容"""
        if not self.log_file_path or not os.path.exists(self.log_file_path):
            return ""
        
        try:
            # 以二进制模式读取，然后解码
            with open(self.log_file_path, "rb") as f:
                f.seek(start_position)
                content_bytes = f.read()
            
            # 尝试多种编码解码
            return self._decode_bytes(content_bytes)
            
        except Exception as e:
            self.log_signal.emit(f"⚠️ 读取日志文件失败: {e}")
            return ""
    
    def _decode_bytes(self, data):
        """尝试多种编码解码字节数据"""
        encodings = ['utf-8', 'gbk', 'gb18030', 'gb2312', 'big5', 'latin-1']
        
        for encoding in encodings:
            try:
                return data.decode(encoding)
            except UnicodeDecodeError:
                continue
        
        # 如果都失败，使用latin-1强制解码
        return data.decode('latin-1', errors='ignore')
    
    def stop_log_capture(self):
        """停止日志抓取"""
        self._stop_log_capture = True
        
        if self.log_capture_thread and self.log_capture_thread.is_alive():
            self.log_capture_thread.join(timeout=2)
        
        # 最后才执行 kill-server
        self.adb_kill_server()
        self.log_signal.emit(f"✅ 日志抓取已停止")
    
    def adb_kill_server(self):
        try:
            import subprocess
            subprocess.run(
                ["adb", "-host", "kill-server"],
                capture_output=True,
                timeout=5
            )
        except Exception as e:
            pass
    
    def _get_signal_value(self, adb_cmd):
        """获取信号值 - 参考综合测试的解析逻辑，从 sigVal 提取实际值"""
        try:
            import subprocess
            import re
            result = subprocess.run(
                adb_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )
            output = result.stdout.strip()
            
            # 🎯 方法1：直接匹配 sigVal 后面的数字（支持小数和负数）
            match = re.search(r'sigVal[^0-9.-]*(-?\d+(?:\.\d+)?)', output)
            if match:
                val_str = match.group(1)
                return float(val_str) if '.' in val_str else int(val_str)
            
            # 🎯 方法2：兼容旧格式
            match = re.search(r'vapisend -get value:\s*(-?\d+(?:\.\d+)?)', output)
            if match:
                val_str = match.group(1)
                return float(val_str) if '.' in val_str else int(val_str)
            
            return output
            
        except Exception as e:
            return None
    
    def stop(self):
        self._stop_flag = True


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    dialog = VoiceTestDialog()
    dialog.show()
    sys.exit(app.exec())
