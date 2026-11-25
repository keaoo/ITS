import ctypes
import json
import sys
import os
import traceback
from Subpy.cmd_thread import CommandThread
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QDialog, QFileDialog, QMessageBox, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QGroupBox, QFormLayout, QTextEdit, QComboBox)
from PySide6.QtGui import QAction, QDoubleValidator, QIntValidator
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QSplitter
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import QTableWidget
from PySide6.QtWidgets import QHeaderView
import serial.tools.list_ports
from Subpy.list_selector import ListSelector
from Subpy.test_runner import TestRunner
from Subpy.test_executor import TestExecutor


class BaselineWorker(QThread):
    log_signal = Signal(str)
    finished_signal = Signal(int)
    
    def __init__(self, executor, instruction_names, delay_time=0, save_folder=""):
        super().__init__()
        self.executor = executor
        self.instruction_names = instruction_names
        self.delay_time = delay_time
        self.save_folder = str(save_folder or "").strip()
        self._stop_flag = False
    
    def stop(self):
        self._stop_flag = True
    
    def run(self):
        success_count = 0
        try:
            for instruction_name in self.instruction_names:
                if self._stop_flag:
                    break

                self.log_signal.emit(f"\n--- {instruction_name} ---")

                try:
                    # 基准采集也使用压测参数配置中的文件夹路径。
                    self.executor._screenshot_save_folder = self.save_folder
                    self.executor._screenshot_current_cycle = 0
                    self.executor._save_folder = self.save_folder
                    self.executor._lastmode_current_cycle = 0

                    actual_results, tolerance, error = self.executor.execute_and_collect(
                        instruction_name, extra_wait=self.delay_time
                    )

                    if error:
                        self.log_signal.emit(f"❌ 执行失败: {error}")
                        continue

                    save_ok = self.executor.save_baseline(instruction_name, actual_results)
                    if save_ok:
                        success_count += 1
                        self.log_signal.emit("✅ 已保存基准")
                        for name, val in actual_results.items():
                            self.log_signal.emit(f"   {name}: {val}")
                    else:
                        self.log_signal.emit("❌ 保存失败，读取结果包含无效值")
                        self.log_signal.emit(f"   实际读取结果: {actual_results}")
                except Exception as exc:
                    self.log_signal.emit(
                        f"❌ 指令 {instruction_name} 基准采集异常，已跳过: {exc}"
                    )
                    self.log_signal.emit(traceback.format_exc())

        except Exception as exc:
            # 防止 QThread.run() 未处理异常导致整个 GUI 进程退出。
            self.log_signal.emit(f"❌ 基准测试线程异常: {exc}")
            self.log_signal.emit(traceback.format_exc())
        finally:
            self.finished_signal.emit(success_count)


class ZongheTestDialog(QDialog):
    auto_cycle_finished = Signal()

    def __init__(self, parent=None, vehicle_platform="8295"):
        super().__init__(None)
        self.setWindowTitle("综合压测配置")
        self.setMinimumSize(300, 700)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
        
        # 设置窗口图标，跟主窗口保持一致
        import os
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "image", "Car.ico")
        if os.path.exists(icon_path):
            from PySide6.QtGui import QIcon
            self.setWindowIcon(QIcon(icon_path))
        self.worker = None
        self.baseline_worker = None
        self._baseline_total_count = 0
        self._auto_start_cycle = False
        self._auto_cycle_ready = False
        self.test_executor = TestExecutor()
        self.parent = parent
        self.vehicle_platform = str(vehicle_platform or "8295").strip()
        self.test_executor.set_vehicle_platform(self.vehicle_platform)
        self.init_ui()
        self.set_vehicle_platform(vehicle_platform)
        
        if parent:
            parent_geo = parent.geometry()
            self.resize(parent_geo.width() // 2, 600)
            self.move(parent_geo.x(), parent_geo.y())
        
        instruction_names = self.test_executor.get_all_instruction_names(self.vehicle_platform)
        print(f"加载到的指令列表: {instruction_names}")
        self.selector.add_left_items(instruction_names)

    def set_vehicle_platform(self, platform):
        """更新可选指令区域的平台名称。"""
        self.vehicle_platform = str(platform or "").strip()
        self.selector.set_vehicle_platform(self.vehicle_platform)

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        zhiling_group = QGroupBox("指令选择")
        zhiling_layout = QVBoxLayout()
        self.selector = ListSelector(left_items=[], insert_after_selected_right=True)
        self.selector.set_numbered_repeat_items({
            self.test_executor.STEP_BOARD_STATUS_INSTRUCTION_NAME_8797,
        })
        zhiling_layout.addWidget(self.selector)
        
        combo_btn_layout = QHBoxLayout()
        self.save_combo_btn = QPushButton("💾 保存组合")
        self.save_combo_btn.clicked.connect(self.save_combination)
        self.save_combo_btn.setMinimumHeight(30)
        combo_btn_layout.addWidget(self.save_combo_btn)
        
        self.load_combo_btn = QPushButton("📂 加载组合")
        self.load_combo_btn.clicked.connect(self.load_combination)
        self.load_combo_btn.setMinimumHeight(30)
        combo_btn_layout.addWidget(self.load_combo_btn)
        
        zhiling_layout.addLayout(combo_btn_layout)
        zhiling_group.setLayout(zhiling_layout)
        main_layout.addWidget(zhiling_group)

        auto_test_group = QGroupBox("自动基准测试")
        auto_test_layout = QVBoxLayout()
        
        btn_layout = QHBoxLayout()
        
        self.run_test_btn = QPushButton("执行并保存基准")
        self.run_test_btn.clicked.connect(lambda: self.run_batch_test(False))
        self.run_test_btn.setMinimumHeight(25)
        btn_layout.addWidget(self.run_test_btn)

        self.run_and_cycle_btn = QPushButton("执行基准保存并循环")
        self.run_and_cycle_btn.clicked.connect(lambda: self.run_batch_test(True))
        self.run_and_cycle_btn.setMinimumHeight(25)
        btn_layout.addWidget(self.run_and_cycle_btn)
        
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
        auto_test_group.setLayout(auto_test_layout)
        main_layout.addWidget(auto_test_group)

        config_group = QGroupBox("压测参数配置")
        config_layout = QFormLayout()
        config_group.setLayout(config_layout)
        main_layout.addWidget(config_group)

        file1_layout = QHBoxLayout()

        fold_layout = QHBoxLayout()
        self.fold_path1 = QLineEdit()
        self.fold_path1.setPlaceholderText("测试文件夹路径...")
        fold_layout.addWidget(self.fold_path1)
        log_browse_btn = QPushButton("浏览...")
        log_browse_btn.clicked.connect(self.select_fold_path1)
        log_browse_btn.setMaximumWidth(80)
        fold_layout.addWidget(log_browse_btn)
        config_layout.addRow("文件夹路径:", fold_layout)

        file2_layout = QHBoxLayout()
        self.file_path2 = QLineEdit()
        self.file_path2.setPlaceholderText("黑屏脚本文件路径...")
        file2_layout.addWidget(self.file_path2)
        log_browse_btn = QPushButton("浏览...")
        log_browse_btn.clicked.connect(self.select_file_path2)
        log_browse_btn.setMaximumWidth(80)
        file2_layout.addWidget(log_browse_btn)
        config_layout.addRow("文件路径:", file2_layout)

        combo_layout = QHBoxLayout()
        self.relay_com = QComboBox()
        self.relay_com.setMinimumHeight(25)
        self.relay_com.clear()
        self.available_ports = self.get_ch340_ports()
        if self.available_ports:
            self.relay_com.addItems(self.available_ports)
        else:
            self.relay_com.addItem("未找到CH340设备")
        self.relay_com.setEditable(True)
        self.relay_com.lineEdit().setReadOnly(True)
        self.relay_com.lineEdit().setAlignment(Qt.AlignCenter)
        combo_layout.addWidget(self.relay_com)
        config_layout.addRow("继电器串口选择:", combo_layout)

        combo1_layout = QHBoxLayout()
        self.relayid1_combo = QComboBox()
        self.relayid1_combo.setMinimumHeight(25)
        self.relayid1_combo.addItems(["选择电机前进通道...","1", "2", "3", "4", "5", "6", "7", "8"])
        self.relayid1_combo.setCurrentIndex(1)
        self.relayid1_combo.setEditable(True)
        self.relayid1_combo.lineEdit().setReadOnly(True)
        self.relayid1_combo.lineEdit().setAlignment(Qt.AlignCenter)
        combo1_layout.addWidget(self.relayid1_combo)
        
        self.relayid2_combo = QComboBox()
        self.relayid2_combo.setMinimumHeight(25)
        self.relayid2_combo.addItems(["选择电机后退通道...","1", "2", "3", "4", "5", "6", "7", "8"])
        self.relayid2_combo.setCurrentIndex(2)
        self.relayid2_combo.setEditable(True)
        self.relayid2_combo.lineEdit().setReadOnly(True)
        self.relayid2_combo.lineEdit().setAlignment(Qt.AlignCenter)
        combo1_layout.addWidget(self.relayid2_combo)
        
        self.relayid3_combo = QComboBox()
        self.relayid3_combo.setMinimumHeight(25)
        self.relayid3_combo.addItems(["选择占座通道...","1", "2", "3", "4", "5", "6", "7", "8"])
        self.relayid3_combo.setCurrentIndex(3)
        self.relayid3_combo.setEditable(True)
        self.relayid3_combo.lineEdit().setReadOnly(True)
        self.relayid3_combo.lineEdit().setAlignment(Qt.AlignCenter)
        combo1_layout.addWidget(self.relayid3_combo)
        
        self.relayid4_combo = QComboBox()
        self.relayid4_combo.setMinimumHeight(25)
        self.relayid4_combo.addItems(["选择刹车通道...", "1", "2", "3", "4", "5", "6", "7", "8"])
        self.relayid4_combo.setCurrentIndex(1)
        self.relayid4_combo.setEditable(True)
        self.relayid4_combo.lineEdit().setReadOnly(True)
        self.relayid4_combo.lineEdit().setAlignment(Qt.AlignCenter)
        combo1_layout.addWidget(self.relayid4_combo)

        config_layout.addRow("继电器通道:", combo1_layout)

        delaytime_layout = QHBoxLayout()
        self.delaytime1 = QLineEdit()
        self.delaytime1.setPlaceholderText("延迟时间（s）...")
        self.delaytime1.setAlignment(Qt.AlignCenter)
        self.delaytime1.setValidator(QDoubleValidator())
        self.delaytime1.setFixedHeight(25)
        delaytime_layout.addWidget(self.delaytime1)
        
        self.delaytime2 = QLineEdit()
        self.delaytime2.setPlaceholderText("休眠唤醒延迟时间（s）...")
        self.delaytime2.setAlignment(Qt.AlignCenter)
        self.delaytime2.setValidator(QDoubleValidator())
        self.delaytime2.setFixedHeight(25)
        delaytime_layout.addWidget(self.delaytime2)
        
        self.delaytime3 = QLineEdit()
        self.delaytime3.setPlaceholderText("休眠唤醒递增时间（s）...")
        self.delaytime3.setAlignment(Qt.AlignCenter)
        self.delaytime3.setValidator(QDoubleValidator())
        self.delaytime3.setFixedHeight(25)
        delaytime_layout.addWidget(self.delaytime3)

        config_layout.addRow("时间设置:", delaytime_layout)

        cycle_layout = QHBoxLayout()
        self.cycle = QLineEdit()
        self.cycle.setPlaceholderText("循环次数设置...")
        self.cycle.setAlignment(Qt.AlignCenter)
        self.cycle.setValidator(QIntValidator())
        self.cycle.setFixedHeight(25)
        cycle_layout.addWidget(self.cycle)
        
        self.mode_combo = QComboBox()
        self.mode_combo.setMinimumHeight(25)
        self.mode_combo.addItems(["选择测试方法...", "JS脚本", "机器人", "VAPI"])
        self.mode_combo.setCurrentIndex(0)
        self.mode_combo.setEditable(True)
        self.mode_combo.lineEdit().setReadOnly(True)
        self.mode_combo.lineEdit().setAlignment(Qt.AlignCenter)
        cycle_layout.addWidget(self.mode_combo)

        config_layout.addRow("循环次数及模式设置:", cycle_layout)

    def get_selected_functions(self):
        return self.selector.get_selected_items()

    def set_selected_functions(self, items):
        self.selector.set_selected_items(items)

    def select_fold_path1(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择综合压测文件夹路径", "")
        if dir_path:
            self.fold_path1.setText(dir_path)

    def select_file_path2(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "黑屏log抓取脚本路径", "", "dat文件 (*.bat);;文本文件 (*.txt);;所有文件 (*.*)")
        if file_path:
            self.file_path2.setText(file_path)

    def get_ch340_ports(self):
        import time
        time.sleep(0.1)
        serial.tools.list_ports.comports()
        time.sleep(0.05)
        ports = serial.tools.list_ports.comports()
        ch340_ports = []
        for port in ports:
            if "CH340" in port.description or "ch340" in port.description:
                ch340_ports.append(port.device)
        return ch340_ports

    def append_log(self, text):
        if self.parent and hasattr(self.parent, 'append_log'):
            self.parent.append_log(text)
            QApplication.processEvents()
        elif self.parent and hasattr(self.parent, 'text_edit1'):
            self.parent.text_edit1.append(text)
            QApplication.processEvents()
    
    def stop_batch_test(self):
        if self.baseline_worker and self.baseline_worker.isRunning():
            self.baseline_worker.stop()
            self.append_log("\n⚠️ 正在停止测试...")
    
    def _on_baseline_finished(self, success_count):
        self.run_test_btn.setEnabled(True)
        self.run_and_cycle_btn.setEnabled(True)
        self.stop_test_btn.setEnabled(False)
        
        total = self._baseline_total_count or len(self.selector.get_selected_items())
        
        if self.baseline_worker and self.baseline_worker._stop_flag:
            self.append_log("="*60 + "\n")
            if self.isVisible():
                QMessageBox.information(self, "提示", "已手动停止")
        else:
            self.append_log("\n" + "="*60)
            self.append_log(f"✅ 完成：成功更新 {success_count}/{total} 条指令的基准")
            self.append_log("="*60 + "\n")
            
            if self._auto_start_cycle:
                self.append_log("✅ 基准保存完成，配置窗口即将关闭并开始循环测试")
                if success_count < total:
                    self.append_log(f"⚠️ 有 {total - success_count} 条指令基准保存失败，仍按设置开始循环测试")
                self.baseline_worker = None
                self._baseline_total_count = 0
                self._auto_cycle_ready = True
                self.auto_cycle_finished.emit()
                if self.isVisible():
                    self.accept()
                return

            summary_msg = f"基准更新完成！\n\n成功: {success_count}\n失败: {total - success_count}"
            if self.isVisible():
                QMessageBox.information(self, "完成", summary_msg)
        
        self.baseline_worker = None
        self._baseline_total_count = 0

    def _unique_baseline_instructions(self, instructions):
        """基准默认按指令去重，允许重复采集的指令保留全部实例。"""
        unique = []
        seen = set()
        duplicate_count = 0
        for instruction in instructions:
            name = str(instruction or "").strip()
            if not name:
                continue
            canonical = self.test_executor._canonical_instruction_name(name)
            baseline_name = self.test_executor._baseline_instruction_name(name)
            config = self.test_executor._get_instruction_config(canonical)
            repeat_baseline = (
                isinstance(config, dict)
                and config.get("repeat_baseline_for_duplicates", False)
            )
            if canonical in seen and not repeat_baseline:
                duplicate_count += 1
                continue
            seen.add(canonical)
            unique.append(baseline_name if repeat_baseline else canonical)
        return unique, duplicate_count
    
    def run_batch_test(self, auto_start_cycle=False):
        self._auto_start_cycle = bool(auto_start_cycle)
        self._auto_cycle_ready = False
        if auto_start_cycle:
            try:
                if int(self.cycle.text()) <= 0:
                    raise ValueError
            except ValueError:
                QMessageBox.warning(self, "提示", "请先设置大于 0 的循环次数")
                return
        selected_instructions, duplicate_count = self._unique_baseline_instructions(
            self.selector.get_selected_items()
        )
        if not selected_instructions:
            QMessageBox.warning(self, "提示", "请先在选择器中选择要执行的指令")
            return
        
        self.run_test_btn.setEnabled(False)
        self.run_and_cycle_btn.setEnabled(False)
        self.stop_test_btn.setEnabled(True)
        
        self.append_log("="*60)
        self.append_log(f">>> 开始采集基准，共 {len(selected_instructions)} 条指令")
        if duplicate_count:
            self.append_log(f"ℹ️ 已跳过 {duplicate_count} 条重复指令，基准只采集一次")
        
        try:
            delay_time = float(self.delaytime1.text()) if self.delaytime1.text() else 0
        except:
            delay_time = 0
        
        try:
            sleep_wake_delay = float(self.delaytime2.text()) if self.delaytime2.text() else 0
        except:
            sleep_wake_delay = 0
        try:
            increment_time = float(self.delaytime3.text()) if self.delaytime3.text() else 0
        except:
            increment_time = 0
        
        self.test_executor.set_wait_params(sleep_wake_delay, increment_time)
        self.append_log(f"⏱️ 等待参数已设置：休眠唤醒延迟={sleep_wake_delay}s, 递增时间={increment_time}s, 总等待={sleep_wake_delay + increment_time}s")
        
        def parse_channel(channel_text, default):
            if not channel_text:
                return str(default)
            import re
            match = re.search(r'\d+', channel_text)
            if match:
                return match.group()
            return str(default)
        
        relay_channel_map = {
            "踩刹车": parse_channel(self.relayid4_combo.currentText(), '1'),
            "占座": parse_channel(self.relayid3_combo.currentText(), '3'),
            "电机前进": parse_channel(self.relayid1_combo.currentText(), '1'),
            "电机后退": parse_channel(self.relayid2_combo.currentText(), '2'),
        }
        
        relay_port = self.relay_com.currentText()
        if relay_port and not relay_port.strip():
            relay_port = None
        
        self.test_executor.set_relay_config(port=relay_port, channel_map=relay_channel_map)
        
        # 🎵 直接从主程序config读取音频探测参数，然后强制传递给测试执行器！
        try:
            if self.parent and hasattr(self.parent, 'config'):
                voice_test_config = self.parent.config.get('voice_test', {})
                audio_duration = voice_test_config.get('detection_duration', 10)
                audio_threshold = voice_test_config.get('volume_threshold', 5)
                audio_duration = float(audio_duration)
                audio_threshold = float(audio_threshold)
            else:
                audio_duration = 10
                audio_threshold = 5
        except:
            audio_duration = 10
            audio_threshold = 5
        
        self.test_executor._audio_duration = audio_duration
        self.test_executor._audio_threshold = audio_threshold
        
        # 📂 设置保存路径
        self.test_executor._save_folder = self.fold_path1.text()
        self._baseline_total_count = len(selected_instructions)
        
        self.baseline_worker = BaselineWorker(
            self.test_executor,
            selected_instructions,
            delay_time,
            save_folder=self.fold_path1.text(),
        )
        self.baseline_worker.log_signal.connect(self.append_log)
        self.baseline_worker.finished_signal.connect(self._on_baseline_finished)
        self.baseline_worker.start()

    def reset_selected_baselines(self):
        self._auto_start_cycle = False
        self._auto_cycle_ready = False
        selected_instructions, duplicate_count = self._unique_baseline_instructions(
            self.selector.get_selected_items()
        )
        if not selected_instructions:
            QMessageBox.warning(self, "提示", "请先在选择器中选择要重新采集基准的指令")
            return
        
        reply = QMessageBox.question(self, "确认", f"确定要重新采集 {len(selected_instructions)} 条指令的基准吗？\n这将覆盖原有基准数据。", QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.run_test_btn.setEnabled(False)
            self.run_and_cycle_btn.setEnabled(False)
            self.reset_baseline_btn.setEnabled(False)
            self.stop_test_btn.setEnabled(True)
            
            self.append_log("="*60)
            self.append_log(f">>> 正在重新采集 {len(selected_instructions)} 条指令的基准...")
            if duplicate_count:
                self.append_log(f"ℹ️ 已跳过 {duplicate_count} 条重复指令，基准只采集一次")
            
            try:
                delay_time = float(self.delaytime1.text()) if self.delaytime1.text() else 0
            except:
                delay_time = 0
            
            try:
                sleep_wake_delay = float(self.delaytime2.text()) if self.delaytime2.text() else 0
            except:
                sleep_wake_delay = 0
            try:
                increment_time = float(self.delaytime3.text()) if self.delaytime3.text() else 0
            except:
                increment_time = 0
            
            self.test_executor.set_wait_params(sleep_wake_delay, increment_time)
            self.append_log(f"⏱️ 等待参数已设置：休眠唤醒延迟={sleep_wake_delay}s, 递增时间={increment_time}s, 总等待={sleep_wake_delay + increment_time}s")
            
            def parse_channel(channel_text, default):
                if not channel_text:
                    return str(default)
                import re
                match = re.search(r'\d+', channel_text)
                if match:
                    return match.group()
                return str(default)
            
            relay_channel_map = {
                "踩刹车": parse_channel(self.relayid4_combo.currentText(), '1'),
                "占座": parse_channel(self.relayid3_combo.currentText(), '3'),
                "电机前进": parse_channel(self.relayid1_combo.currentText(), '1'),
                "电机后退": parse_channel(self.relayid2_combo.currentText(), '2'),
            }
            
            relay_port = self.relay_com.currentText()
            if relay_port and not relay_port.strip():
                relay_port = None
            
            self.test_executor.set_relay_config(port=relay_port, channel_map=relay_channel_map)
            
            # 🎵 直接从主程序config读取音频探测参数，然后强制传递给测试执行器！
            try:
                if self.parent and hasattr(self.parent, 'config'):
                    voice_test_config = self.parent.config.get('voice_test', {})
                    audio_duration = voice_test_config.get('detection_duration', 10)
                    audio_threshold = voice_test_config.get('volume_threshold', 5)
                    audio_duration = float(audio_duration)
                    audio_threshold = float(audio_threshold)
                else:
                    audio_duration = 10
                    audio_threshold = 5
            except:
                audio_duration = 10
                audio_threshold = 5
            
            self.test_executor._audio_duration = audio_duration
            self.test_executor._audio_threshold = audio_threshold
            
            # 📂 设置保存路径
            self.test_executor._save_folder = self.fold_path1.text()
            self._baseline_total_count = len(selected_instructions)
            
            self.baseline_worker = BaselineWorker(
                self.test_executor,
                selected_instructions,
                delay_time,
                save_folder=self.fold_path1.text(),
            )
            self.baseline_worker.log_signal.connect(self.append_log)
            self.baseline_worker.finished_signal.connect(self._on_baseline_finished)
            self.baseline_worker.start()
    
    def _on_reset_finished(self, success_count):
        self.run_test_btn.setEnabled(True)
        self.reset_baseline_btn.setEnabled(True)
        self.stop_test_btn.setEnabled(False)
        
        total = len(self.selector.get_selected_items())
        
        if self.baseline_worker and self.baseline_worker._stop_flag:
            self.append_log("="*60 + "\n")
            QMessageBox.information(self, "提示", "已手动停止")
        else:
            self.append_log("\n" + "="*60)
            self.append_log(f"✅ 完成：成功更新 {success_count}/{total} 条指令的基准")
            self.append_log("="*60 + "\n")
            
            summary_msg = f"基准更新完成！\n\n成功: {success_count}\n失败: {total - success_count}"
            QMessageBox.information(self, "完成", summary_msg)
        
        self.baseline_worker = None


    def closeEvent(self, event):
        self.accept()
        super().closeEvent(event)
    
    def save_combination(self):
        selected_items = self.selector.get_selected_items()
        if not selected_items:
            QMessageBox.warning(self, "提示", "请先选择要保存的指令组合！")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(self, "保存指令组合", "", "文本文件 (*.txt);;所有文件 (*.*)")
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                for item in selected_items:
                    f.write(item + '\n')
            
            QMessageBox.information(self, "成功", f"指令组合已保存！\n共 {len(selected_items)} 条指令")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"保存失败：{e}")
    
    def load_combination(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "加载指令组合", "", "文本文件 (*.txt);;所有文件 (*.*)")
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            selected_items = [line.strip() for line in lines if line.strip()]
            
            if not selected_items:
                QMessageBox.warning(self, "提示", "文件中没有有效指令！")
                return
            
            self.selector.set_selected_items(selected_items)
            QMessageBox.information(self, "成功", f"指令组合已加载！\n共 {len(selected_items)} 条指令")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载失败：{e}")
    
    def _on_reset_finished(self, success_count):
        self.run_test_btn.setEnabled(True)
        self.reset_baseline_btn.setEnabled(True)
        self.stop_test_btn.setEnabled(False)
        
        total = len(self.selector.get_selected_items())
        
        if self.baseline_worker and self.baseline_worker._stop_flag:
            self.append_log("="*60 + "\n")
            QMessageBox.information(self, "提示", "已手动停止")
        else:
            self.append_log("\n" + "="*60)
            self.append_log(f"✅ 完成：成功更新 {success_count}/{total} 条指令的基准")
            self.append_log("="*60 + "\n")
            
            summary_msg = f"基准更新完成！\n\n成功: {success_count}\n失败: {total - success_count}"
            QMessageBox.information(self, "完成", summary_msg)
        
        self.baseline_worker = None

