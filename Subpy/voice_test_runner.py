#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语音测试执行引擎 - 循环测试
完全按照新方案实现：
1. 第一个指令前启动后台线程持续抓日志
2. 不清理日志，追加写入文件
3. 每个指令：播放 → 等待 → 分析日志文件
4. 全部完成后才 kill-server
"""

import os
import sys
import time
import json
import subprocess
import threading
from datetime import datetime
from PySide6.QtCore import QObject, Signal, QThread, QMutex, QMutexLocker

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from Subpy.voice_test_config import get_instruction_config, parse_logs_for_baseline, compare_test_result


class VoiceTestRunner(QObject):
    """语音测试执行引擎"""
    
    log_signal = Signal(str)
    cell_update_signal = Signal(int, int, str)
    finished_signal = Signal()
    instruction_failed_signal = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.commands = []      # 测试指令列表
        self.total_cycles = 1   # 总循环次数
        self.is_running = False
        self.is_paused = False  # 是否暂停
        self.current_cycle = 0  # 当前循环
        self.save_folder = ""   # 结果保存文件夹
        self.results = []       # 测试结果
        self._last_save_time = 0
        self.parent = parent
        self.vehicle_platform = getattr(parent, "vehicle_platform", "8295")
        
        # 日志抓取相关
        self.log_capture_thread = None
        self.log_file = ""
        self._stop_log_capture = False
        self.log_file_handle = None
        
        # 语音测试配置
        self.tts_library = "本地TTS (pyttsx3)"
        self.tts_voice = ""
        self.tts_language = "中文"
        self.tts_speed = "正常"
        self.play_mode = "TTS播放"
        self.audio_folder = ""
        self.baselines = {}  # 基准数据
        
    def set_commands(self, commands):
        """设置测试指令列表"""
        self.commands = commands
        
    def load_instructions(self, items):
        """加载测试指令列表（兼容旧接口）"""
        self.commands = items
        return True
        
    def set_total_cycles(self, cycles):
        """设置总循环次数"""
        self.total_cycles = cycles
        
    def set_save_folder(self, folder):
        """设置结果保存文件夹"""
        self.save_folder = folder
        
    def set_voice_config(self, tts_library, voice, tts_language, tts_speed, play_mode, audio_folder):
        """设置语音测试配置（兼容旧接口，voice=tts_voice）"""
        self.tts_library = tts_library
        self.tts_voice = voice
        self.tts_language = tts_language
        self.tts_speed = tts_speed
        self.play_mode = play_mode
        self.audio_folder = audio_folder
        
    def load_baselines(self):
        """加载基准数据"""
        try:
            if hasattr(sys, '_MEIPASS'):
                base_dir = os.path.dirname(os.path.abspath(sys.executable))
            else:
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            baseline_dir = os.path.join(base_dir, "配置基准文件")
            baseline_file = os.path.join(baseline_dir, "all_baselines.json")
            
            if not os.path.exists(baseline_file):
                self.log_signal.emit(f"⚠️ 基准文件不存在: {baseline_file}")
                return
            
            with open(baseline_file, "r", encoding="utf-8") as f:
                self.baselines = json.load(f)
            
            voice_count = sum(1 for k in self.baselines.keys() if k.startswith("语音_"))
            self.log_signal.emit(f"✅ 加载基准数据: {len(self.baselines)} 条 (语音: {voice_count} 条)")
            
        except Exception as e:
            self.log_signal.emit(f"❌ 加载基准数据失败: {e}")
            import traceback
            self.log_signal.emit(f"📋 错误详情: {traceback.format_exc()}")
        
    def load_previous_results(self):
        """
        检查上次运行到第几次循环，但不加载历史记录到内存
        Returns:
            tuple: (has_history, last_cycle, 表头是否匹配)
        """
        if not self.save_folder:
            return False, 0, True
        
        file_path = os.path.join(self.save_folder, "语音压测.csv")
        
        if not os.path.exists(file_path):
            self.log_signal.emit(f"ℹ️ 未找到历史结果文件，从第1次开始")
            return False, 0, True
        
        try:
            # 读取表头检查是否匹配
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                lines = f.readlines()
            
            if len(lines) <= 1:  # 只有表头或空
                self.log_signal.emit(f"ℹ️ 历史结果文件为空，从第1次开始")
                return False, 0, True
            
            # 检查表头
            headers = ["序号"] + [cmd[0] if isinstance(cmd, (list, tuple)) else cmd for cmd in self.commands]
            csv_header = lines[0].strip()
            
            header_match = True
            try:
                import csv
                from io import StringIO
                f = StringIO(csv_header)
                reader = csv.reader(f)
                csv_header_list = next(reader)
                if csv_header_list != headers:
                    header_match = False
            except:
                header_match = False
            
            if not header_match:
                self.log_signal.emit(f"⚠️ 测试指令已变更，无法使用历史数据")
                return False, 0, False
            
            # 读最后一行获取循环次数
            last_line = lines[-1].strip()
            if last_line:
                last_cycle = int(last_line.split(',')[0])
            else:
                last_line = lines[-2].strip()
                last_cycle = int(last_line.split(',')[0])
            
            self.log_signal.emit(f"ℹ️ 上次运行到第 {last_cycle} 次，从第 {last_cycle + 1} 次继续")
            self.log_signal.emit(f"ℹ️ 不加载历史记录到内存，避免缓慢")
            return True, last_cycle, True
            
        except Exception as e:
            self.log_signal.emit(f"⚠️ 检查历史结果失败: {str(e)}，从第1次开始")
            return False, 0, True
        
    def start(self, start_cycle=1):
        """开始执行"""
        if not self.commands:
            self.log_signal.emit("❌ 测试指令列表为空")
            return
        
        self.is_running = True
        self.is_paused = False
        self.current_cycle = start_cycle
        self.results = []
        
        # 先尝试加载历史结果（断点续跑）
        has_history, last_cycle, _ = self.load_previous_results()
        actual_start_cycle = last_cycle + 1 if has_history else start_cycle
        history_count = 0  # 不加载历史记录到内存
        
        # 加载基准数据
        self.load_baselines()
        
        # 启动工作线程
        self.worker = VoiceTestWorker(
            self.commands,
            self.total_cycles,
            self.save_folder,
            self,
            actual_start_cycle,
            history_count
        )
        self.worker.tts_library = self.tts_library
        self.worker.tts_voice = self.tts_voice
        self.worker.tts_language = self.tts_language
        self.worker.tts_speed = self.tts_speed
        self.worker.play_mode = self.play_mode
        self.worker.audio_folder = self.audio_folder
        self.worker.baselines = self.baselines
        
        self.worker.log_signal.connect(self.log_signal)
        self.worker.cell_update_signal.connect(self.cell_update_signal)
        self.worker.finished_signal.connect(self._on_finished)
        self.worker.instruction_failed_signal.connect(self.instruction_failed_signal)
        
        # 确定日志文件路径
        if self.save_folder:
            self.log_file = os.path.join(self.save_folder, "语音日志.txt")
        else:
            if hasattr(sys, '_MEIPASS'):
                base_dir = os.path.dirname(os.path.abspath(sys.executable))
            else:
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.log_file = os.path.join(base_dir, "语音日志.txt")
        
        # 启动日志抓取
        self.log_signal.emit("="*60)
        self.log_signal.emit(">>> 语音测试开始")
        self.log_signal.emit("="*60)
        self.log_signal.emit("")
        self.log_signal.emit(f"📡 启动日志抓取...")
        self.log_signal.emit(f"📝 日志文件: {self.log_file}")
        
        self._stop_log_capture = False
        self.log_capture_thread = threading.Thread(target=self._log_capture_loop, daemon=True)
        self.log_capture_thread.start()
        time.sleep(1)
        
        # 启动工作线程
        self.worker.log_file = self.log_file
        self.worker.start()
        
    def _log_capture_loop(self):
        """日志抓取循环（沿用基线保存的方案：logctl -d 轮询 + 去重）"""
        self.log_signal.emit("📡 启动后台日志抓取...")
        
        import subprocess as _sp
        import tempfile
        
        # 记录已见过的行，用于去重
        last_log_lines = set()
        first_iteration = True
        
        while not self._stop_log_capture:
            try:
                # 第一次迭代时先清理旧的adb连接
                if first_iteration:
                    try:
                        _sp.run(["adb", "-host", "kill-server"], capture_output=True, timeout=5)
                        time.sleep(0.5)
                    except:
                        pass
                    first_iteration = False
                
                # 写入临时文件（避免直接写主日志时因中断导致损坏）
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as tmp_file:
                    tmp_path = tmp_file.name
                
                cmd = f'adb -host shell "logctl -d | grep -iE \'voice_handleASRKeyWord|play tts:|OrchASR4BMSp: word =|remote dialog result|totalCost\'" > "{tmp_path}"'
                proc = _sp.Popen(cmd, shell=True, stdout=_sp.DEVNULL, stderr=_sp.DEVNULL)
                proc.wait(timeout=3)
                
                # 读取临时文件，去重后追加到主日志
                if os.path.exists(tmp_path):
                    try:
                        with open(tmp_path, 'r', encoding='utf-8', errors='ignore') as f:
                            new_lines = f.readlines()
                        
                        unique_lines = []
                        for line in new_lines:
                            line_stripped = line.strip()
                            if line_stripped and line_stripped not in last_log_lines:
                                unique_lines.append(line)
                                last_log_lines.add(line_stripped)
                        
                        # 限制内存使用
                        if len(last_log_lines) > 10000:
                            last_log_lines = set(list(last_log_lines)[-5000:])
                        
                        if unique_lines and self.log_file:
                            with open(self.log_file, 'a', encoding='utf-8') as f:
                                f.writelines(unique_lines)
                    except:
                        pass
                    try:
                        os.unlink(tmp_path)
                    except:
                        pass
            
            except _sp.TimeoutExpired:
                try:
                    proc.kill()
                except:
                    pass
            except Exception:
                pass
            
            time.sleep(0.5)
        
    def pause(self):
        """暂停"""
        if hasattr(self, 'worker'):
            self.worker.pause()
        self.is_paused = True
        
    def resume(self):
        """继续"""
        if hasattr(self, 'worker'):
            self.worker.resume()
        self.is_paused = False
        
    def stop(self):
        """停止"""
        if hasattr(self, 'worker'):
            self.worker.stop()
        
        self.stop_log_capture()
        
    def stop_log_capture(self):
        """停止日志抓取"""
        self._stop_log_capture = True
        
        if self.log_capture_thread and self.log_capture_thread.is_alive():
            self.log_capture_thread.join(timeout=2)
        
        self.log_signal.emit(f"📡 停止日志抓取...")
        self.adb_kill_server()
        self.log_signal.emit(f"✅ 日志抓取已停止")
        self.adb_kill_server()
        self.log_signal.emit(f"✅ 日志抓取已停止")
        
    def adb_kill_server(self):
        try:
            subprocess.run(["adb", "-host", "kill-server"], capture_output=True, timeout=5)
        except Exception as e:
            pass
        
    def _on_finished(self):
        """测试完成"""
        self.is_running = False
        
        self.stop_log_capture()
        # 清空结果，释放内存
        self.results = []
        self.log_signal.emit("ℹ️ 内存已释放")
        
        self.log_signal.emit("")
        self.log_signal.emit("="*60)
        self.log_signal.emit(">>> 语音测试完成")
        self.log_signal.emit("="*60)
        self.finished_signal.emit()
        
    def save_result_to_excel(self):
        """保存测试结果到CSV（直接追加）"""
        if not self.save_folder or not self.results:
            return
        
        try:
            import csv
            import os
            
            headers = ["序号"] + [cmd[0] if isinstance(cmd, (list, tuple)) else cmd for cmd in self.commands]
            file_path = os.path.join(self.save_folder, "语音压测.csv")
            
            # 只追加最新的一个循环
            latest_cycle = self.results[-1]
            
            # 检查是否存在旧文件
            if os.path.exists(file_path):
                try:
                    # 直接追加新行
                    with open(file_path, 'a', newline='', encoding='utf-8-sig') as f:
                        writer = csv.writer(f)
                        writer.writerow(latest_cycle)
                    self.log_signal.emit(f"💾 结果已追加保存: {file_path}")
                except Exception as e:
                    self.log_signal.emit(f"⚠️ 追加失败: {str(e)}")
            else:
                # 不存在旧文件，写入表头和所有结果
                try:
                    with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                        writer = csv.writer(f)
                        writer.writerow(headers)
                        for row in self.results:
                            writer.writerow(row)
                    self.log_signal.emit(f"💾 结果已保存: {file_path}")
                except Exception as e:
                    self.log_signal.emit(f"⚠️ 保存失败: {str(e)}")
            
        except Exception as e:
            self.log_signal.emit(f"⚠️ 保存结果失败: {e}")
            import traceback
            self.log_signal.emit(f"📋 错误详情: {traceback.format_exc()}")
        
    def write_fail_log(self, cycle, cmd_name, result, details=None):
        """写入失败日志"""
        if not self.save_folder:
            return
        
        try:
            log_path = os.path.join(self.save_folder, "错误日志.txt")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"\n{'='*60}\n")
                f.write(f"[{timestamp}] 第{cycle}次循环 - {cmd_name}: {result}\n")
                f.write(f"{'='*60}\n")
                
                if details:
                    for detail in details:
                        f.write(f"{detail}\n")
                
                f.write("\n")
            
        except Exception as e:
            self.log_signal.emit(f"⚠️ 写入失败日志失败: {e}")


class VoiceTestWorker(QThread):
    """语音测试工作线程"""
    
    log_signal = Signal(str)
    cell_update_signal = Signal(int, int, str)
    finished_signal = Signal()
    instruction_failed_signal = Signal(str)
    
    def __init__(self, commands, total_cycles, save_folder, runner, start_cycle=1, history_count=0):
        super().__init__(runner)
        self.commands = commands
        self.total_cycles = total_cycles
        self.save_folder = save_folder
        self.runner = runner
        self.start_cycle = start_cycle
        self.history_count = history_count  # 历史结果数量
        self._stop_flag = False
        self._pause_flag = False
        self._pause_mutex = QMutex()
        self.log_file = ""
        self.last_read_position = 0
        
        self.tts_library = "本地TTS (pyttsx3)"
        self.tts_voice = ""
        self.tts_language = "中文"
        self.tts_speed = "正常"
        self.play_mode = "TTS播放"
        self.audio_folder = ""
        self.baselines = {}
        
    def run(self):
        """执行测试"""
        self.log_signal.emit("="*60)
        if self.start_cycle > 1:
            self.log_signal.emit(f"🚀 继续执行测试，从第 {self.start_cycle} 次循环开始")
        else:
            self.log_signal.emit(f"🚀 开始执行测试")
        self.log_signal.emit("="*60)
        
        for cycle in range(self.start_cycle, self.total_cycles + 1):
            if self._stop_flag:
                break
                
            self.log_signal.emit("")
            self.log_signal.emit("="*60)
            self.log_signal.emit(f">>> 第 {cycle}/{self.total_cycles} 次循环")
            self.log_signal.emit("="*60)
            
            cycle_results = [f"{cycle}"]
            row_offset = cycle - self.start_cycle  # 从第0行开始显示新循环
            
            self.cell_update_signal.emit(row_offset, 0, f"{cycle}")
            
            for cmd_idx, item in enumerate(self.commands):
                if self._stop_flag:
                    break
                
                if self._pause_flag:
                    self.log_signal.emit(f"暂停中...")
                    while self._pause_flag:
                        if self._stop_flag:
                            break
                        time.sleep(0.1)
                    if self._stop_flag:
                        break
                
                if isinstance(item, (list, tuple)) and len(item) >= 1:
                    name = item[0]
                else:
                    name = item
                
                self.log_signal.emit("")
                self.log_signal.emit(f"--- {name} ---")
                
                col = cmd_idx + 1
                self.cell_update_signal.emit(row_offset, col, "⏳执行中")
                
                result_text = "✅ 通过"
                details_list = []
                try:
                    result_text, details_list = self._execute_voice_instruction(
                        name,
                        get_instruction_config(name, self.runner.vehicle_platform),
                    )
                except Exception as e:
                    self.log_signal.emit(f"❌ 执行失败: {e}")
                    import traceback
                    self.log_signal.emit(f"📋 错误详情: {traceback.format_exc()}")
                    result_text = "❌ 异常"
                
                cycle_results.append(result_text)
                self.cell_update_signal.emit(row_offset, col, result_text)
                
                if "❌" in result_text or "失败" in result_text:
                    self.runner.write_fail_log(cycle, name, result_text, details_list)
                    self.instruction_failed_signal.emit(name)
                
                time.sleep(0.01)
                
            # 一个循环完了再保存到results和Excel
            self.runner.results.append(cycle_results)
            self.runner.save_result_to_excel()
                
            if self._stop_flag:
                break
                
        self.finished_signal.emit()
        
    def _execute_voice_instruction(self, name, config):
        """执行单条语音测试指令"""
        try:
            details_list = []
            
            # 丢弃上次残留的日志，避免上一条指令的迟到日志混入本次分析
            discarded = self._read_log_file()
            if discarded:
                lines = len(discarded.strip().split('\n'))
                self.log_signal.emit(f"📥 丢弃残留日志: {lines} 行")
            
            if self.play_mode == "播放录音":
                self._play_audio_file(name, config)
            else:
                self._play_tts(name, config)
            
            wait_seconds = config.get("wait_seconds", 3)
            self.log_signal.emit(f"⏳ 等待 {wait_seconds} 秒...")
            time.sleep(wait_seconds)
            
            self.log_signal.emit(f"📡 从日志文件读取新增内容...")
            log_content = self._read_log_file()
            
            test_result = parse_logs_for_baseline(log_content, instruction_name=name)
            
            baseline_name = f"语音_{name}"
            baseline_data = self.baselines.get(baseline_name, {})
            baseline = baseline_data.get("results", {})
            baseline_signals = baseline_data.get("signal_values", {})
            
            result_text = "✅ 通过"
            
            self.log_signal.emit("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            detail_line = f"📝 识别结果: {test_result.get('recognition', '')}"
            details_list.append(detail_line)
            self.log_signal.emit(detail_line)
            
            detail_line = f"🔊 车机响应: {test_result.get('response', '')}"
            details_list.append(detail_line)
            self.log_signal.emit(detail_line)
            
            if test_result.get("response_time_ms"):
                detail_line = f"⏱️  响应时间: {test_result.get('response_time_ms')} ms"
                details_list.append(detail_line)
                self.log_signal.emit(detail_line)
                
            if test_result.get('voice_zone'):
                zone_text = {
                    "1": "主驾",
                    "2": "副驾",
                    "3": "左后",
                    "4": "右后"
                }.get(str(test_result.get('voice_zone')), test_result.get('voice_zone'))
                detail_line = f"📍 响应区域: {zone_text}"
                details_list.append(detail_line)
                self.log_signal.emit(detail_line)
                
            self.log_signal.emit("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            
            if baseline:
                actual_signals = {}
                verify_signals = config.get("verify_signals", [])
                for signal_item in verify_signals:
                    if len(signal_item) >= 2:
                        signal_name = signal_item[0]
                        adb_cmd = signal_item[1]
                        actual_val = self._get_signal_value(adb_cmd)
                        actual_signals[signal_name] = actual_val
                
                compare_result = compare_test_result(
                    test_result=test_result,
                    baseline=baseline,
                    instruction_name=name,
                    actual_signal_values=actual_signals,
                    baseline_signal_values=baseline_signals
                )
                
                for detail in compare_result["details"]:
                    self.log_signal.emit(detail)
                    details_list.append(detail)
                
                if compare_result["passed"]:
                    result_text = "✅ 通过"
                else:
                    result_text = "❌ 失败"
            else:
                detail_line = f"⚠️ 未找到基准数据: {baseline_name}"
                details_list.append(detail_line)
                self.log_signal.emit(detail_line)
                
                detail_line = f"💡 请先执行'执行并保存基准'"
                details_list.append(detail_line)
                self.log_signal.emit(detail_line)
                
                result_text = "❌ 无基准"
            
            return result_text, details_list
            
        except Exception as e:
            self.log_signal.emit(f"❌ 执行失败: {e}")
            import traceback
            self.log_signal.emit(f"📋 错误详情: {traceback.format_exc()}")
            return f"❌ 异常: {str(e)[:20]}", []
        
    def _read_log_file(self):
        """只读取新增的日志内容（从上次结束的位置开始）"""
        if not self.log_file or not os.path.exists(self.log_file):
            return ""
        
        try:
            file_size = os.path.getsize(self.log_file)
            
            if file_size <= self.last_read_position:
                return ""
            
            with open(self.log_file, "rb") as f:
                f.seek(self.last_read_position)
                new_bytes = f.read()
            
            self.last_read_position = file_size
            
            stdout = ""
            encodings = ['utf-8', 'gbk', 'gb18030']
            for encoding in encodings:
                try:
                    stdout = new_bytes.decode(encoding, errors='ignore')
                    break
                except:
                    continue
            if not stdout:
                stdout = new_bytes.decode('latin-1', errors='ignore')
            
            return stdout
        except Exception as e:
            return ""
        
    def _play_tts(self, name, config):
        """播放TTS"""
        try:
            if self.tts_language == "中文":
                play_text = config.get("tts_text", name)
            else:
                play_text = config.get("tts_text_en", config.get("tts_text", name))
            
            self.log_signal.emit(f"🎤 播放: {play_text}")
            self.log_signal.emit(f"🔊 TTS库: {self.tts_library}")
            
            if self.tts_library == "本地TTS (pyttsx3)":
                self._play_pyttsx3(play_text)
            else:
                self._play_edge_tts(play_text)
            
            self.log_signal.emit("✅ TTS播放完成")
            
        except Exception as e:
            self.log_signal.emit(f"❌ TTS播放失败: {e}")
        
    def _play_pyttsx3(self, text):
        """使用pyttsx3播放"""
        import pyttsx3
        
        engine = pyttsx3.init()
        
        if self.tts_voice:
            engine.setProperty('voice', self.tts_voice)
        
        speed_rate = 200
        if self.tts_speed == "慢速":
            speed_rate = 160
        elif self.tts_speed == "快速":
            speed_rate = 240
        
        engine.setProperty('rate', speed_rate)
        engine.say(text)
        engine.runAndWait()
        
    def _play_edge_tts(self, text):
        """使用edge-tts播放"""
        import edge_tts
        import tempfile
        import pygame.mixer
        import asyncio
        
        voice_map = {
            "女声 - Xiaoxiao": "zh-CN-XiaoxiaoNeural",
            "男声 - Yunjian": "zh-CN-YunjianNeural"
        }
        
        voice_id = voice_map.get(self.tts_voice, "zh-CN-XiaoxiaoNeural")
        
        rate_str = "+0%"
        if self.tts_speed == "慢速":
            rate_str = "-20%"
        elif self.tts_speed == "快速":
            rate_str = "+20%"
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        temp_file.close()
        
        async def generate_audio():
            communicate = edge_tts.Communicate(text, voice_id, rate=rate_str)
            await communicate.save(temp_file.name)
        
        asyncio.run(generate_audio())
        
        pygame.mixer.init()
        pygame.mixer.music.load(temp_file.name)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
        pygame.mixer.quit()
        os.unlink(temp_file.name)
        
    def _play_audio_file(self, name, config):
        """播放录音文件"""
        import pygame.mixer
        
        if not self.audio_folder or not os.path.exists(self.audio_folder):
            self.log_signal.emit(f"❌ 音频文件夹不存在: {self.audio_folder}")
            return
        
        audio_file = None
        audio_filename = config.get("audio_file", "")
        
        if audio_filename:
            candidate = os.path.join(self.audio_folder, audio_filename)
            if os.path.exists(candidate):
                audio_file = candidate
        
        if not audio_file:
            for filename in os.listdir(self.audio_folder):
                if filename.lower().endswith(('.wav', '.mp3', '.m4a', '.flac')):
                    name_without_ext = os.path.splitext(filename)[0]
                    if name in name_without_ext or name_without_ext in name:
                        audio_file = os.path.join(self.audio_folder, filename)
                        break
        
        if not audio_file:
            self.log_signal.emit(f"❌ 未找到音频文件: {name}")
            return
        
        self.log_signal.emit(f"🎵 播放文件: {os.path.basename(audio_file)}")
        
        pygame.mixer.init()
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
        pygame.mixer.quit()
        
    def _get_signal_value(self, adb_cmd):
        """获取信号值（支持小数）"""
        try:
            import re
            result = subprocess.run(
                adb_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )
            output = result.stdout.strip()
            
            # 方法1：直接匹配 sigVal 后面的数字（支持小数和负数）
            match = re.search(r'sigVal[^0-9.-]*(-?\d+(?:\.\d+)?)', output)
            if match:
                val_str = match.group(1)
                return float(val_str) if '.' in val_str else int(val_str)
            
            # 方法2：兼容旧格式
            match = re.search(r'vapisend -get value:\s*(-?\d+(?:\.\d+)?)', output)
            if match:
                val_str = match.group(1)
                return float(val_str) if '.' in val_str else int(val_str)
            
            return output
            
        except Exception as e:
            return None
        
    def pause(self):
        """暂停"""
        self._pause_flag = True
        
    def resume(self):
        """继续"""
        self._pause_flag = False
        
    def stop(self):
        """停止"""
        self._stop_flag = True


if __name__ == "__main__":
    print("语音测试执行引擎 - 请通过主程序调用")
