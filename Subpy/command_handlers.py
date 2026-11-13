#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
指令处理器架构 - 每个指令一个处理器，自己负责执行+等待+校验
"""
import os
import time
import subprocess
from abc import ABC, abstractmethod
from datetime import datetime


# ============================================================================
# 1. 全局上下文 Context - 所有处理器都能访问的全局配置
# ============================================================================

class TestContext:
    """测试上下文 - 存放所有全局配置和公共对象"""
    
    def __init__(self):
        # 基础配置
        self.delay_time = 1.0       # 主界面的基础延迟时间
        self.test_mode = "CMD"      # 测试模式
        self.test_cycle = 1         # 当前循环次数
        
        # 设备配置
        self.adb_device = ""        # ADB设备ID
        self.serial_port = None     # 串口对象
        self.robot_ip = ""          # 机器人IP
        
        # 公共工具方法可以挂在这里
        self.log_callback = None    # 日志回调函数
        self.stop_check = None      # 停止检查回调
    
    def log(self, msg):
        """输出日志"""
        if self.log_callback:
            self.log_callback(msg)
        else:
            print(msg)

    def should_stop(self):
        if not self.stop_check:
            return False
        try:
            return bool(self.stop_check())
        except Exception:
            return False

    def interruptible_sleep(self, seconds, interval=0.2):
        try:
            seconds = float(seconds)
        except (TypeError, ValueError):
            seconds = 0
        if seconds <= 0:
            return not self.should_stop()

        deadline = time.time() + seconds
        while time.time() < deadline:
            if self.should_stop():
                return False
            remaining = deadline - time.time()
            if remaining <= 0:
                break
            time.sleep(min(interval, remaining))
        return not self.should_stop()
    
    def run_adb(self, cmd, timeout=10):
        """公共方法：执行 ADB 命令"""
        full_cmd = f"adb {cmd}" if not self.adb_device else f"adb -s {self.adb_device} {cmd}"
        try:
            result = subprocess.run(
                full_cmd,
                shell=True,
                capture_output=True,
                text=True,
                encoding='gbk',
                timeout=timeout
            )
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            return -1, "", str(e)


# ============================================================================
# 2. 指令处理器基类 - 所有具体处理器都继承这个
# ============================================================================

class BaseCommandHandler(ABC):
    """
    指令处理器基类
    
    每个子类需要实现：
    1. cmd_name = 指令名称（和 Excel 第一列对应）
    2. execute() - 执行逻辑
    3. verify() - 校验逻辑
    （可选）wait() - 自定义等待时间，不重写就用默认的
    """
    
    # 子类必须填写指令名称（和 Excel 第一列完全一致）
    cmd_name = ""
    
    def __init__(self, context: TestContext):
        self.context = context
        self.cmd_content = ""     # Excel第二列的内容
        self.expect_result = ""   # Excel第三列的期望结果
    
    def execute(self, cmd_content):
        """
        执行阶段：发送指令给车机
        :param cmd_content: Excel第二列的指令内容
        :return: (是否成功, 附加信息)
        """
        # 默认实现：直接执行 CMD
        returncode, stdout, stderr = self.context.run_adb(cmd_content)
        return returncode == 0, stdout
    
    def wait(self):
        """
        等待阶段：指令执行后等待多久再校验
        默认：基础延迟时间 + 1秒
        子类可以重写这个方法，自己定义等待时间
        """
        wait_time = self.context.delay_time + 1.0
        self.context.interruptible_sleep(wait_time)
        return wait_time
    
    def verify(self, target_value=None):
        """
        校验阶段：读取车机状态判断是否执行成功
        :param target_value: 目标值（Excel第三列）
        :return: (是否成功, 失败原因/成功信息)
        """
        # 默认实现：不校验，直接返回成功
        # 子类必须重写这个方法做自己的校验逻辑
        return True, "（无校验）"
    
    def run(self, cmd_content, expect_result=None):
        """
        统一执行入口：执行 → 等待 → 校验
        :return: (是否成功, 结果字符串)
        """
        self.cmd_content = cmd_content
        self.expect_result = expect_result
        
        result_msg = ""
        
        # ====================================================================
        # 阶段1：执行指令
        # ====================================================================
        self.context.log(f"  🚀 执行: {self.cmd_name}")
        exec_ok, exec_msg = self.execute(cmd_content)
        
        if not exec_ok:
            now = datetime.now().strftime("%H:%M:%S")
            return False, f"❌执行失败 ({now}): {exec_msg}"
        
        if exec_msg:
            result_msg += f"执行: {exec_msg}; "
        
        # ====================================================================
        # 阶段2：等待
        # ====================================================================
        wait_time = self.wait()
        if self.context.should_stop():
            return False, "执行已停止"
        self.context.log(f"  ⏱️  等待: {wait_time:.1f} 秒")
        
        # ====================================================================
        # 阶段3：校验结果
        # ====================================================================
        self.context.log(f"  🔍 校验中...")
        verify_ok, verify_msg = self.verify(expect_result)
        
        if not verify_ok:
            now = datetime.now().strftime("%H:%M:%S")
            return False, f"❌校验失败 ({now}): {verify_msg}"
        
        if verify_msg and verify_msg != "（无校验）":
            result_msg += f"校验: {verify_msg}"
        
        return True, f"✅成功" if not result_msg else f"✅成功 ({result_msg})"


# ============================================================================
# 3. 具体处理器示例 - 可以参考这个写其他指令
# ============================================================================

class WindowFullOpenHandler(BaseCommandHandler):
    """车窗全开处理器"""
    cmd_name = "车窗全开"
    
    def execute(self, cmd_content):
        """执行车窗全开指令"""
        # 示例：adb -host shell vapisend -set ctrl.custom.536872231 2
        returncode, stdout, stderr = self.context.run_adb(cmd_content)
        return returncode == 0, stdout
    
    def wait(self):
        """车窗动作慢，多等2秒"""
        wait_time = self.context.delay_time + 3.0  # 基础延迟 + 3秒
        self.context.interruptible_sleep(wait_time)
        return wait_time
    
    def verify(self, target_value=None):
        """校验四个车窗位置是否都在全开位置"""
        # 示例：读取四个车窗位置
        returncode, stdout, stderr = self.context.run_adb("shell vapiget window_position")
        
        if returncode != 0:
            return False, f"读车窗状态失败: {stderr}"
        
        # 解析返回值（这里根据你实际的返回格式改）
        # 假设返回格式: "FL=100, FR=100, RL=99, RR=98"
        try:
            # 示例解析逻辑，按你的实际格式改
            parts = stdout.strip().split(',')
            positions = []
            for p in parts:
                if '=' in p:
                    val = int(p.split('=')[1].strip())
                    positions.append(val)
            
            if len(positions) != 4:
                return False, f"返回格式异常: {stdout}"
            
            fl, fr, rl, rr = positions
            
            # 判断四个车窗位置是否都在目标值附近（误差<3）
            target = 100  # 全开是100
            if abs(fl - target) < 3 and abs(fr - target) < 3 and \
               abs(rl - target) < 3 and abs(rr - target) < 3:
                return True, f"位置: {fl},{fr},{rl},{rr}"
            else:
                return False, f"位置不符: {fl},{fr},{rl},{rr}, 目标: {target}"
                
        except Exception as e:
            return False, f"解析失败: {str(e)}, 原始输出: {stdout}"


# ============================================================================
# 4. 指令注册表 - 把所有处理器注册到这里
# ============================================================================

# ==================== 继电器指令处理器 ====================

class BrakeHandler(BaseCommandHandler):
    """踩刹车处理器"""
    cmd_name = "踩刹车"
    
    def execute(self, cmd_content):
        """执行踩刹车动作"""
        from Subpy.relay_subprogram import press_relay
        
        # 从context获取继电器配置
        port = getattr(self.context, 'relay_port', "COM4")
        channel = getattr(self.context, 'relay_channel_brake', 1)
        
        try:
            duration = float(cmd_content.strip()) if cmd_content.strip() else 2.0
        except:
            duration = 2.0
        
        self.context.log(f"  🚗 踩刹车: 串口={port}, 通道={channel}, 持续={duration}秒")
        success = press_relay(port, 9600, int(channel), duration)
        return success, ""
    
    def verify(self, target_value=None):
        """校验：读取电源模式"""
        from Subpy.relay_subprogram import get_power_mode
        power_mode = get_power_mode()
        if power_mode is not None:
            return True, f"电源模式={power_mode}"
        return False, "无法读取电源模式"


class StartButtonHandler(BaseCommandHandler):
    """按启动键处理器"""
    cmd_name = "按启动键"
    
    def execute(self, cmd_content):
        """执行按启动键动作"""
        from Subpy.relay_subprogram import press_relay
        
        port = getattr(self.context, 'relay_port', "COM4")
        channel = getattr(self.context, 'relay_channel_start', 2)
        
        try:
            duration = float(cmd_content.strip()) if cmd_content.strip() else 2.0
        except:
            duration = 2.0
        
        self.context.log(f"  🔑 按启动键: 串口={port}, 通道={channel}, 持续={duration}秒")
        success = press_relay(port, 9600, int(channel), duration)
        return success, ""
    
    def verify(self, target_value=None):
        """校验：读取电源模式"""
        from Subpy.relay_subprogram import get_power_mode
        power_mode = get_power_mode()
        if power_mode is not None:
            return True, f"电源模式={power_mode}"
        return False, "无法读取电源模式"


class SeatOccupyHandler(BaseCommandHandler):
    """座椅占座处理器"""
    cmd_name = "占座"
    
    def execute(self, cmd_content):
        """执行占座动作"""
        from Subpy.relay_subprogram import press_relay
        
        port = getattr(self.context, 'relay_port', "COM4")
        channel = getattr(self.context, 'relay_channel_seat', 3)
        
        try:
            duration = float(cmd_content.strip()) if cmd_content.strip() else 3.0
        except:
            duration = 3.0
        
        self.context.log(f"  🪑 座椅占座: 串口={port}, 通道={channel}, 持续={duration}秒")
        success = press_relay(port, 9600, int(channel), duration)
        return success, ""
    
    def wait(self):
        """占座后等待时间稍长"""
        wait_time = self.context.delay_time + 2.0
        self.context.interruptible_sleep(wait_time)
        return wait_time


# 📌 新增指令只要在这里加一行就行！
COMMAND_HANDLERS = {
    # 指令名称（和Excel第一列完全一致）: 处理器类
    "车窗全开": WindowFullOpenHandler,
    
    # 继电器控制指令
    "踩刹车": BrakeHandler,
    "按启动键": StartButtonHandler,
    "占座": SeatOccupyHandler,
    
    # 在这里继续加其他指令...
    # "空调26度": Aircon26Handler,
    # "座椅通风": SeatVentHandler,
}


# ============================================================================
# 5. 默认处理器 - 没注册的通用指令走这个
# ============================================================================

class DefaultCommandHandler(BaseCommandHandler):
    """默认处理器 - 通用指令走这个，只执行不校验"""
    
    def verify(self, target_value=None):
        """通用指令：可以根据返回码判断是否成功"""
        # 如果有期望结果，就判断返回结果是否包含期望字符串
        if target_value and str(target_value).strip():
            # 这里可以加通用的字符串匹配逻辑
            pass
        return True, "（通用指令，无特殊校验）"
