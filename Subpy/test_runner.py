#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试执行引擎 - 循环测试核心框架
负责：循环控制、指令调度、结果回写
"""
import os
import time
import threading
from datetime import datetime
from PySide6.QtCore import QObject, Signal, QThread
from Subpy.test_executor import TestExecutor
from Subpy.command_handlers import (
    TestContext, 
    COMMAND_HANDLERS, 
    DefaultCommandHandler
)


class TestRunner(QObject):
    """
    测试执行引擎
    
    信号说明：
    - log_signal: 输出日志文本
    - cell_update_signal: 单元格更新信号 (行, 列, 结果文本)
    - finished_signal: 全部执行完成
    """
    
    log_signal = Signal(str)
    cell_update_signal = Signal(int, int, str)
    finished_signal = Signal()
    instruction_failed_signal = Signal(str)  # 新增：指令失败信号，参数为指令名称
    cycle_wait_time_updated = Signal(float)  # 新增：每次循环结束后的累加等待时间
    cycle_result_signal = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.commands = []      
        self.total_cycles = 1   
        self.is_running = False
        self.is_paused = False  
        self.current_cycle = 0  
        self.save_folder = ""   
        self.results = []       
        self._last_save_time = 0
        self.start_cycle = 1
        self.parent = parent  # 保存父窗口引用
        
        # 🎯 线程锁：保护 results 的读写竞态
        self._results_lock = threading.Lock()
        
        # 基准测试相关
        self.test_executor = TestExecutor()  # 测试执行器
        self.test_executor.set_stop_check(lambda: not self.is_running)
        self.delay_time = 0  # 额外等待时间
        
        # ✅ 新架构：全局测试上下文
        self.context = TestContext()
        # 把日志输出函数挂到 context 上
        self.context.log_callback = self.log_signal.emit
        self.context.stop_check = lambda: not self.is_running
        self.upload_context = {}

    def set_upload_context(self, context):
        """Set metadata used when a cycle result is sent to ITMS."""
        self.upload_context = dict(context or {})
    
    def set_config(self, delay_time="", **kwargs):
        """设置测试配置"""
        try:
            self.delay_time = float(delay_time) if delay_time else 0
        except:
            self.delay_time = 0
    
    def load_from_instructions(self, instruction_names):
        """
        从内置指令列表加载（不从 Excel）
        instruction_names: 指令名称列表，如 ["车窗全开", "车窗全关"]
        """
        self.commands = []
        missing_names = []
        
        for name in instruction_names:
            cmd_name = str(name).strip()
            if not cmd_name:
                continue
            self.commands.append((cmd_name, "", ""))  # 后面两个参数留空
            canonical_name = self.test_executor._canonical_instruction_name(cmd_name)
            if canonical_name not in self.test_executor.instructions:
                missing_names.append(cmd_name)
        
        if len(self.commands) > 0:
            self.log_signal.emit(f"✅ 已加载 {len(self.commands)} 条测试指令")
            if missing_names:
                preview = "、".join(missing_names[:10])
                suffix = "..." if len(missing_names) > 10 else ""
                self.log_signal.emit(
                    f"⚠️ 其中 {len(missing_names)} 条未在内置指令表中找到，将按通用指令处理: {preview}{suffix}"
                )
            return True
        else:
            self.log_signal.emit(f"❌ 未找到有效的测试指令")
            return False

    def load_excel(self, excel_path):
        """
        从 Excel 加载指令列表
        Excel 格式：
        - 第1列：指令名称
        - 第2列：指令内容
        - 第3列：期望结果
        """
        import pandas as pd
        
        if not os.path.exists(excel_path):
            self.log_signal.emit(f"❌ 指令文件不存在: {excel_path}")
            return False
            
        try:
            df = pd.read_excel(excel_path, header=None)
            self.commands = []
            
            for idx, row in df.iterrows():
                cmd_name = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
                cmd_content = str(row.iloc[1]).strip() if len(row) > 1 and pd.notna(row.iloc[1]) else ""
                cmd_expect = str(row.iloc[2]).strip() if len(row) > 2 and pd.notna(row.iloc[2]) else ""
                
                if cmd_name:
                    self.commands.append((cmd_name, cmd_content, cmd_expect))
                    
            self.log_signal.emit(f"✅ 已加载 {len(self.commands)} 条测试指令")
            return True
            
        except Exception as e:
            self.log_signal.emit(f"❌ 加载指令失败: {str(e)}")
            return False
    
    def set_total_cycles(self, cycles):
        """设置总循环次数"""
        if isinstance(cycles, str):
            cycles = int(cycles) if cycles.isdigit() else 1
        self.total_cycles = max(1, cycles)
        self.log_signal.emit(f"🔄 总循环次数: {self.total_cycles}")
    
    def set_save_folder(self, folder_path):
        """设置测试结果保存文件夹"""
        self.save_folder = folder_path
        self.log_signal.emit(f"📂 结果保存路径: {folder_path}")
        
        # 🎯 循环测试开始时预创建"截图"文件夹（截图指令用）
        if folder_path:
            try:
                screenshot_folder = os.path.join(folder_path, "截图")
                os.makedirs(screenshot_folder, exist_ok=True)
                self.log_signal.emit(f"📸 截图文件夹: {screenshot_folder}")
            except Exception as e:
                self.log_signal.emit(f"⚠️ 创建截图文件夹失败: {e}")
    
    def set_config(
        self,
        delay_time=1.0,
        test_mode="CMD",
        adb_device="",
        relay_port=None,
        relay_channel_map=None,
        vehicle_platform="8295",
    ):
        """
        设置全局配置到 context 中
        :param delay_time: 基础延迟时间（秒）
        :param test_mode: 测试模式
        :param adb_device: ADB设备ID
        :param relay_port: 继电器串口号
        :param relay_channel_map: 继电器通道映射字典
        """
        # 设置到 context（新架构用）
        self.context.delay_time = float(delay_time) if delay_time else 1.0
        # 同时设置到 self.delay_time（执行时用）
        try:
            self.delay_time = float(delay_time) if delay_time else 0
        except:
            self.delay_time = 0
        self.context.test_mode = test_mode
        self.context.adb_device = adb_device
        self.test_executor.set_vehicle_platform(vehicle_platform)
        
        # 更新测试执行器的继电器配置
        if relay_port or relay_channel_map:
            self.test_executor.set_relay_config(
                port=relay_port,
                channel_map=relay_channel_map
            )
        
        self.log_signal.emit(f"⚙️  配置已更新:")
        self.log_signal.emit(f"   基础延迟: {self.context.delay_time:.1f}s")
        self.log_signal.emit(f"   测试模式: {self.context.test_mode}")
        if relay_port:
            self.log_signal.emit(f"   继电器串口: {relay_port}")
    
    def load_previous_results(self):
        """
        加载上次保存的测试结果，实现断点续跑
        与 save_result_to_excel 写入的 CSV 格式一致
        :return: (has_history, last_cycle, header_match, error_msg)
                 has_history:  是否成功加载了历史
                 last_cycle:   上次跑到的循环次数
                 header_match: 表头是否匹配（False 时需用户处理）
                 error_msg:    错误信息（空串=无错误）
        """
        # 🎯 先清空内存残留（防止 worker 线程残留数据污染）
        with self._results_lock:
            self.results = []
        
        if not self.save_folder:
            return False, 0, True, ""
            
        file_path = os.path.join(self.save_folder, "综合测试.csv")
        
        if not os.path.exists(file_path):
            self.log_signal.emit("ℹ️ 未找到历史测试结果，将从头开始")
            return False, 0, True, ""
        
        try:
            import csv

            expected_header = ["次数"] + [cmd[0] for cmd in self.commands]

            with open(file_path, 'r', newline='', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                try:
                    csv_header = next(reader)
                except StopIteration:
                    self.log_signal.emit("ℹ️ 历史测试结果为空，将从头开始")
                    return False, 0, True, ""

                if csv_header != expected_header:
                    self.log_signal.emit(
                        f"📋 CSV表头不匹配: 历史指令数={max(0, len(csv_header) - 1)}，当前指令数={len(self.commands)}"
                    )
                    with self._results_lock:
                        self.results = []
                    return False, 0, False, (
                        f"CSV表头不匹配：历史{len(csv_header)}列，当前{len(expected_header)}列"
                    )

                history_rows = [row for row in reader if any(cell.strip() for cell in row)]

            normalized_rows = []
            expected_cols = len(expected_header)
            load_note = ""
            for idx, row in enumerate(history_rows, start=2):
                actual_cols = len(row)
                if actual_cols == expected_cols:
                    normalized_rows.append(row)
                    continue

                cycle_label = row[0].strip() if row and row[0].strip() else str(len(normalized_rows) + 1)
                if actual_cols < expected_cols:
                    load_note = (
                        f"CSV第{idx}行（第 {cycle_label} 次循环）只有{actual_cols}/{expected_cols}列，"
                        "判断为上次停止时未完成，本次将从该循环重新执行"
                    )
                    self.log_signal.emit(f"ℹ️ {load_note}")
                    break

                self.log_signal.emit(
                    f"ℹ️ CSV第{idx}行列数={actual_cols} > 表头列数={expected_cols}，已忽略多余列"
                )
                normalized_rows.append(row[:expected_cols])

            if not normalized_rows:
                self.log_signal.emit("ℹ️ 历史测试结果只有表头，将从头开始")
                with self._results_lock:
                    self.results = []
                return False, 0, True, load_note
            
            # 加载历史结果到内存
            with self._results_lock:
                self.results = normalized_rows
            last_cycle = len(self.results)
            
            self.log_signal.emit(f"✅ 已加载历史测试结果，上次运行到第 {last_cycle} 次，共 {len(self.results)} 行")
            return True, last_cycle, True, load_note
            
        except Exception as e:
            err_msg = str(e)
            self.log_signal.emit(f"⚠️ 加载历史结果失败({err_msg})，将从头开始")
            # 读文件失败（如被 Excel 锁住）→ 不阻止继续，只是丢掉了历史
            return False, 0, True, err_msg
    
    def start(self, start_cycle=1):
        """
        开始执行测试
        :param start_cycle: 从第几次循环开始（用于断点续跑）
        """
        self.is_running = True
        self.current_cycle = start_cycle - 1
        self.start_cycle = start_cycle
        
        class TestWorker(QThread):
            def __init__(self, runner, start_cycle):
                super().__init__()
                self.runner = runner
                self.start_cycle = start_cycle
                
            def run(self):
                self.runner._run_loop(self.start_cycle)
        
        self.worker = TestWorker(self, start_cycle)
        self.worker.start()
    
    def stop(self):
        """停止执行：保存结果（不清空 results，防止 worker 后续保存覆盖丢数据）"""
        self.is_running = False
        self.is_paused = False
        self.log_signal.emit("⏹️ 正在停止测试...")
        # 保存当前结果（加锁 + 强制写入，无视2秒限频）
        with self._results_lock:
            self.save_result_to_excel(force=True)
        self.log_signal.emit("ℹ️ 测试已停止，下次启动新测试时会释放内存")
        # ⚠️ 不在这里 clear results：worker 线程退出前可能还会
        # 追加当前中断循环的部分结果并 save，如果 clear 了会导致
        # worker 写出只有部分循环的 CSV，把完整历史覆盖掉。
        # 内存释放交给 load_previous_results() 启动新测试时处理。
        # worker 线程感知 is_running=False 后会自然退出循环
        # 退出后通过 finished_signal 通知 GUI 恢复按钮
    
    def toggle_pause(self):
        """切换暂停/继续状态"""
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.log_signal.emit("⏸️ 测试已暂停")
            with self._results_lock:
                self.save_result_to_excel(force=True)
        else:
            self.log_signal.emit("▶️ 测试继续")
        return self.is_paused
    
    def save_result_to_excel(self, force=False):
        """保存测试结果到CSV（参考备份版，用CSV避免文件锁卡死）
        :param force: True=忽略2秒限频，强制保存（stop/pause时用）
        """
        if not self.save_folder:
            return
        
        # 在有锁保护的地方调用时，已经持有锁了，这里不再重复加锁
        if not self.results:
            return
        
        now = time.time()
        if not force and now - self._last_save_time < 2:
            return
        self._last_save_time = now
            
        import csv
        import os
        
        os.makedirs(self.save_folder, exist_ok=True)
        
        headers = ["次数"] + [cmd[0] for cmd in self.commands]
        
        file_path = os.path.join(self.save_folder, "综合测试.csv")
        try:
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                for row in self.results:
                    writer.writerow(row)
            self.log_signal.emit(f"💾 测试结果已保存: {file_path}")
        except Exception as e:
            self.log_signal.emit(f"⚠️ 保存失败: {str(e)}")
    
    def _write_fail_log(self, cycle, cmd_name, result):
        """写入失败日志到txt文件"""
        if not self.save_folder:
            return
            
        os.makedirs(self.save_folder, exist_ok=True)
        
        file_path = os.path.join(self.save_folder, "综合测试.txt")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_lines = [f"[{now}] 第{cycle}次循环 - {cmd_name}: {result}\n"]

        detail = getattr(self.test_executor, "last_execution_detail", None)
        canonical_cmd_name = self.test_executor._canonical_instruction_name(cmd_name)
        if isinstance(detail, dict) and detail.get("instruction") == canonical_cmd_name:
            import json

            def dump_value(value):
                if value is None:
                    return "None"
                try:
                    return json.dumps(value, ensure_ascii=False, indent=2, default=str)
                except Exception:
                    return str(value)

            log_lines.append(f"  基准结果: {dump_value(detail.get('baseline'))}\n")
            log_lines.append(f"  实际读取结果: {dump_value(detail.get('actual'))}\n")
            log_lines.append(f"  对比详情: {dump_value(detail.get('details'))}\n")

            if canonical_cmd_name == "Lastmode快速校验":
                comparison_details = detail.get("details")
                failed_items = {
                    name: item
                    for name, item in (comparison_details or {}).items()
                    if isinstance(item, dict) and item.get("status") != "pass"
                }
                if failed_items:
                    log_lines.append(
                        f"  Lastmode未通过对比项: {dump_value(failed_items)}\n"
                    )

            if detail.get("error"):
                log_lines.append(f"  错误信息: {detail.get('error')}\n")
            if detail.get("tolerance") is not None:
                log_lines.append(f"  容差: {detail.get('tolerance')}\n")
            log_lines.append("\n")
        
        with open(file_path, 'a', encoding='utf-8') as f:
            f.writelines(log_lines)
    
    def _run_loop(self, start_cycle=1):
        """
        核心执行循环
        :param start_cycle: 起始循环次数
        """
        self.log_signal.emit("=" * 50)
        if start_cycle > 1:
            self.log_signal.emit(f"🚀 继续执行测试，从第 {start_cycle} 次循环开始")
            self.log_signal.emit("ℹ️ 历史结果已加载到内存（断点续跑正常）")
            self.log_signal.emit("ℹ️ 界面仅显示本次新执行的结果，完整历史请查看 Excel")
        else:
            self.log_signal.emit("🚀 开始执行测试")
        self.log_signal.emit("=" * 50)
        
        # 🎯 重置循环计数（如果从头开始）
        if start_cycle == 1:
            self.test_executor.reset_cycle_count()
        
        for cycle in range(start_cycle, self.total_cycles + 1):
            if not self.is_running:
                break
            
            while self.is_paused and self.is_running:
                time.sleep(0.1)
            
            self.current_cycle = cycle
            current_wait = self.test_executor.set_current_wait_for_cycle(cycle)
            self.cycle_wait_time_updated.emit(current_wait)
            self.log_signal.emit(f"\n📍 第 {cycle}/{self.total_cycles} 次循环")
            
            cycle_result = [f"{cycle}"]
            command_results = []
            row_offset = cycle - self.start_cycle
            self.cell_update_signal.emit(row_offset, 0, f"{cycle}")
            
            for cmd_idx, (cmd_name, cmd_content, cmd_expect) in enumerate(self.commands):
                if not self.is_running:
                    break
                
                while self.is_paused and self.is_running:
                    time.sleep(0.1)
                
                col = cmd_idx + 1
                
                # 显示执行中
                self.cell_update_signal.emit(row_offset, col, "⏳执行中")
                cmd_start_time = time.time()
                self.log_signal.emit(f"▶️ 开始指令: 第{cycle}次 / {cmd_name}")
                
                # 🎯 判断是否是基准测试指令（有配置的内置指令）
                canonical_name = self.test_executor._canonical_instruction_name(cmd_name)
                if canonical_name in self.test_executor.instructions:
                    result = self.test_executor.execute_and_compare(
                        cmd_name, 
                        self.delay_time,
                        current_cycle=cycle,
                        save_folder=self.save_folder
                    )
                else:
                    result = self._execute_single_command(cmd_name, cmd_content, cmd_expect)
                elapsed = time.time() - cmd_start_time
                self.log_signal.emit(f"⏱️ 指令结束: {cmd_name}, 耗时 {elapsed:.1f}s, 结果: {result}")
                
                cycle_result.append(result)
                command_results.append({
                    "name": cmd_name,
                    "result": result,
                    "passed": not any(
                        marker in str(result) for marker in ("❌", "失败", "错误")
                    ),
                })
                
                # 回写结果
                self.cell_update_signal.emit(row_offset, col, result)
                
                if "❌" in result or "失败" in result:
                    self._write_fail_log(cycle, cmd_name, result)
                    self.instruction_failed_signal.emit(cmd_name)
                
                time.sleep(0.01)
            
            # 🎯 加锁追加结果（防止与 stop() 的 clear 竞态）
            with self._results_lock:
                self.results.append(cycle_result)
            
            # 🎯 加锁保存结果（与 stop() 避免竞态）
            with self._results_lock:
                self.save_result_to_excel()

            upload_payload = dict(self.upload_context)
            upload_payload.update({
                "cycleNo": cycle,
                "totalCycles": self.total_cycles,
                "commands": command_results,
                "finishedAt": datetime.now().isoformat(timespec="seconds"),
            })
            self.cycle_result_signal.emit(upload_payload)
        
        self.log_signal.emit("\n" + "=" * 50)
        self.log_signal.emit("✅ 测试执行完成")
        self.log_signal.emit("=" * 50)
        self.finished_signal.emit()
    
    def _execute_single_command(self, cmd_name, cmd_content, cmd_expect):
        """
        执行单条指令 - 新架构：从注册表找处理器
        """
        # ====================================================================
        # 🎯 先处理特殊指令（全局通用，不需要处理器）
        # ====================================================================
        cmd_name_lower = cmd_name.strip().lower()
        
        # 1. 音频探测指令
        if "音频" in cmd_name and "探测" in cmd_name or cmd_name_lower in ["音频探测"]:
            self.log_signal.emit(f"🎵 开始执行音频探测")
            
            # 从主程序配置中读取参数
            duration = 10  # 默认10秒
            threshold = 30  # 默认30%
            
            if hasattr(self, 'parent'):
                main_win = self.parent
                if 'voice_test' in main_win.config:
                    vt_config = main_win.config['voice_test']
                    duration = vt_config.get('detection_duration', 10)
                    threshold = vt_config.get('volume_threshold', 30)
                    self.log_signal.emit(f"  配置参数: 时长={duration}s, 阈值={threshold}%")
            
            # 调用音频探测
            try:
                from Subpy.audio_detection import AudioDetector
                
                def log_callback(msg):
                    self.log_signal.emit(f"  {msg}")
                
                detector = AudioDetector(log_callback)
                result = detector.detect(duration, self.save_folder, threshold)
                
                if result["success"]:
                    avg_vol = result["avg_volume"]
                    is_silent = result["is_silent"]
                    audio_file = result.get("audio_file", "")
                    
                    self.log_signal.emit(f"📊 平均音量: {avg_vol:.2f}%")
                    self.log_signal.emit(f"🔇 是否静音: {'是' if is_silent else '否'}")
                    if audio_file:
                        self.log_signal.emit(f"💾 音频文件: {audio_file}")
                    
                    if is_silent:
                        return f"✅探测成功|平均音量{avg_vol:.2f}%|静音"
                    else:
                        return f"✅探测成功|平均音量{avg_vol:.2f}%|有声音"
                else:
                    return f"❌探测失败|{result.get('error', '未知错误')}"
            except Exception as e:
                return f"❌探测异常|{str(e)}"
        
        # 2. 等待/延时指令（覆盖掉处理器的默认等待）
        if cmd_name_lower in ["等待", "延时", "sleep", "wait"]:
            try:
                seconds = float(cmd_content.strip())
                if not self.test_executor.interruptible_sleep(seconds):
                    return "❌执行失败: 测试已停止"
                return f"✅等待 {seconds} 秒"
            except:
                return f"❌参数错误: {cmd_content}"
        
        # 3. 记录日志/打标记
        if cmd_name_lower in ["日志", "标记", "log", "mark"]:
            self.log_signal.emit(f"📝 {cmd_content}")
            return f"✅已标记"
        
        # 4. 截图指令
        if cmd_name_lower in ["截图", "screenshot", "snap"]:
            return "✅已截图"
        
        # 5. 复位/重置
        if cmd_name_lower in ["复位", "重置", "reset", "restart"]:
            return "✅已复位"
        
        # ====================================================================
        # 🎯 正常指令：从注册表找对应处理器
        # ====================================================================
        # 1. 从注册表找处理器类
        handler_class = COMMAND_HANDLERS.get(cmd_name.strip())
        
        if handler_class:
            # 2. 找到专用处理器，走完整的 执行→等待→校验 三阶段
            handler = handler_class(self.context)
            success, result = handler.run(cmd_content, cmd_expect)
        else:
            # 3. 没找到，走默认通用处理器
            handler = DefaultCommandHandler(self.context)
            success, result = handler.run(cmd_content, cmd_expect)
        
        # ====================================================================
        # 🎯 视觉验证：如果是亮屏相关指令或纯视觉指令，执行视觉检测
        # ====================================================================
        is_visual_cmd = ("亮屏" in cmd_name) or ("屏幕" in cmd_name) or ("显示" in cmd_name)
        
        if is_visual_cmd:
            from Subpy.visual_detector import get_visual_detector
            detector = get_visual_detector()
            
            # 只有配置了ROI区域才执行视觉验证
            if len(detector.roi_list) > 0:
                self.log_signal.emit(f"📸 执行屏幕视觉检测: {cmd_name}")
                
                # 🎯 确保摄像头一定打开，不管之前是什么状态
                if detector.cap is None or not detector.cap.isOpened():
                    self.log_signal.emit(f"  正在打开摄像头 {detector.camera_port}...")
                    detector.open_camera(detector.camera_port)
                    if not self.test_executor.interruptible_sleep(0.5):  # 给足够时间让摄像头稳定
                        return "❌执行失败: 测试已停止"
                
                # 🎯 强制抓取一帧新图像（确保是最新的）
                for i in range(3):  # 尝试抓3帧，确保摄像头稳定
                    ret, frame = detector.cap.read()
                    if ret:
                        detector.current_frame = frame
                    if not self.test_executor.interruptible_sleep(0.1):
                        return "❌执行失败: 测试已停止"
                
                if detector.current_frame is None:
                    self.log_signal.emit(f"❌ 无法获取摄像头图像，跳过检测")
                else:
                    # 执行屏幕验证
                    current_cycle = getattr(self, 'current_cycle', 0)
                    visual_success, visual_result = detector.verify_screen(current_cycle)
                    
                    # 显示各区域亮度详细信息
                    brightness_text = ", ".join([f"区域{i+1}={b:.1f}" for i, b in enumerate(visual_result)])
                    self.log_signal.emit(f"  亮度检测: {brightness_text}, 阈值={detector.brightness_threshold}")
                    
                    if not visual_success:
                        self.log_signal.emit(f"❌ 屏幕检测失败: 检测到黑屏")
                        
                        # 🎯 强制保存截图 - 详细日志
                        import os
                        if not detector.save_folder:
                            detector.save_folder = "./visual_screenshots"
                            self.log_signal.emit(f"  截图路径使用默认: {detector.save_folder}")
                        else:
                            self.log_signal.emit(f"  截图保存路径: {detector.save_folder}")
                        
                        os.makedirs(detector.save_folder, exist_ok=True)
                        
                        # 确保有图像帧
                        if detector.current_frame is None:
                            self.log_signal.emit(f"  ⚠️ current_frame 为空，重新抓取...")
                            ret, frame = detector.cap.read()
                            if ret:
                                detector.current_frame = frame
                                self.log_signal.emit(f"  ✅ 重新抓取成功")
                            else:
                                self.log_signal.emit(f"  ❌ 无法抓取图像")
                        
                        self.log_signal.emit(f"  正在保存截图...")
                        screenshot_path = detector.save_screenshot(current_cycle, prefix="黑屏异常")
                        
                        if screenshot_path and os.path.exists(screenshot_path):
                            self.log_signal.emit(f"📸 截图已保存: {os.path.basename(screenshot_path)}")
                            self.log_signal.emit(f"   完整路径: {screenshot_path}")
                        else:
                            self.log_signal.emit(f"⚠️ 截图保存失败，请检查文件路径和权限")
                        
                        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        result = f"❌黑屏异常 ({now})"
                        success = False
                    else:
                        self.log_signal.emit(f"✅ 屏幕检测通过")
                
                # 测试时保持摄像头打开，避免频繁开关
            else:
                self.log_signal.emit(f"⚠️ 未配置ROI区域，跳过视觉检测，请先在视觉设置中框选检测区域")
        
        # 失败时加上时间戳
        if not success:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            result = f"{result} ({now})"
        
        return result
