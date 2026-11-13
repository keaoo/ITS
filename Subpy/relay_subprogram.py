#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
继电器控制子程序 - 可独立调用，也可集成到主程序
提供简单易用的继电器控制接口

使用示例：
    # 直接调用
    from Subpy.relay_subprogram import brake_control
    brake_control(port="COM4", channel=1, duration=2.0)
    
    # 或使用快捷函数
    press_start_button()  # 按启动键
    press_brake()         # 踩刹车
"""
import serial
import time
import subprocess


# ==================== 基础继电器控制函数 ====================

def control_relay(port, baudrate, channel, action):
    """
    控制继电器通道
    :param port: 串口号 (如 "COM4")
    :param baudrate: 波特率 (如 9600)
    :param channel: 通道号 (1-8)
    :param action: 'on' 或 'off'
    """
    try:
        channel = int(channel)
    except ValueError:
        print(f"❌ 无效的通道号: {channel}")
        return False
    
    # 构造指令
    if action == 'on':
        # 打开指令: A0 XX 01 YY
        checksum = 0xA0 + channel + 0x01
        cmd = bytes([0xA0, channel, 0x01, checksum])
    else:
        # 关闭指令: A0 XX 00 YY
        checksum = 0xA0 + channel + 0x00
        cmd = bytes([0xA0, channel, 0x00, checksum])
    
    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        print(f"📤 发送指令: {' '.join(f'{b:02X}' for b in cmd)}")
        ser.write(cmd)
        time.sleep(0.1)
        ser.close()
        return True
    except Exception as e:
        print(f"❌ 继电器控制失败: {e}")
        return False


def press_relay(port, baudrate, channel, duration=2.0):
    """
    模拟按下动作：打开 -> 等待 -> 关闭
    :param port: 串口号
    :param baudrate: 波特率
    :param channel: 通道号
    :param duration: 按下持续时间（秒）
    """
    print(f"\n🔘 按下通道 {channel}，持续 {duration} 秒 (串口: {port})")
    
    if not control_relay(port, baudrate, channel, 'on'):
        print(f"❌ 打开通道 {channel} 失败")
        return False
    
    time.sleep(duration)
    
    if not control_relay(port, baudrate, channel, 'off'):
        print(f"❌ 关闭通道 {channel} 失败")
        return False
    
    print(f"✅ 通道 {channel} 已释放")
    return True


# ==================== 读取状态验证函数 ====================

def get_power_mode():
    """
    读取电源模式状态
    :return: sigVal 值 (int) 或 None
    """
    cmd = "adb -host shell vapisend -get ctrl.sys.power_mode"
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        output = result.stdout.strip()
        
        # 提取 sigVal
        import re
        match = re.search(r'sigVal[^0-9]*(\d+)', output)
        if match:
            value = int(match.group(1))
            print(f"📊 电源模式状态: {value}")
            return value
        else:
            print(f"⚠️  无法解析状态: {output}")
            return None
    except Exception as e:
        print(f"❌ 读取状态失败: {e}")
        return None


def get_signal_value(signal_path):
    """
    读取任意信号值
    :param signal_path: 信号路径 (如 "ctrl.sys.power_mode")
    :return: sigVal 值 (int) 或 None
    """
    cmd = f"adb -host shell vapisend -get {signal_path}"
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        output = result.stdout.strip()
        
        import re
        match = re.search(r'sigVal[^0-9]*(\d+)', output)
        if match:
            return int(match.group(1))
        return None
    except Exception as e:
        print(f"❌ 读取信号失败: {e}")
        return None


# ==================== 快捷操作函数（按业务场景） ====================

def brake_control(port="COM4", channel=1, duration=2.0, verify=True):
    """
    踩刹车控制子程序
    :param port: 串口号 (在综合测试面板中选择)
    :param channel: 通道号 (踩刹车的通道)
    :param duration: 按下持续时间
    :param verify: 是否验证结果
    """
    print("="*60)
    print("🚗 踩刹车控制子程序")
    print("="*60)
    
    # 执行动作
    success = press_relay(port, 9600, channel, duration)
    
    if not success:
        print("❌ 踩刹车动作执行失败")
        return False
    
    # 等待系统响应
    time.sleep(1)
    
    # 验证结果
    if verify:
        print("\n📋 验证结果...")
        power_mode = get_power_mode()
        if power_mode is not None:
            print(f"✅ 验证完成，电源模式 = {power_mode}")
        else:
            print("⚠️  无法验证，请手动检查")
    
    print("\n✅ 踩刹车控制完成")
    print("="*60)
    return True


def start_button_control(port="COM4", channel=2, duration=2.0, verify=True):
    """
    按启动键控制子程序
    """
    print("="*60)
    print("🔑 按启动键控制子程序")
    print("="*60)
    
    success = press_relay(port, 9600, channel, duration)
    
    if not success:
        print("❌ 按启动键动作执行失败")
        return False
    
    time.sleep(1)
    
    if verify:
        print("\n📋 验证结果...")
        power_mode = get_power_mode()
        if power_mode is not None:
            print(f"✅ 验证完成，电源模式 = {power_mode}")
    
    print("\n✅ 按启动键控制完成")
    print("="*60)
    return True


def door_control(port="COM4", channel=3, action="open", duration=2.0, verify=True):
    """
    车门控制子程序
    :param action: 'open' 开门, 'close' 关门
    """
    action_name = "开门" if action == "open" else "关门"
    print("="*60)
    print(f"🚪 车门{action_name}控制子程序")
    print("="*60)
    
    success = press_relay(port, 9600, channel, duration)
    
    if not success:
        print(f"❌ {action_name}动作执行失败")
        return False
    
    time.sleep(1)
    
    if verify:
        print("\n📋 验证结果...")
        door_status = get_signal_value("ctrl.door.driver_door_status")
        if door_status is not None:
            print(f"✅ 验证完成，车门状态 = {door_status}")
    
    print(f"\n✅ 车门{action_name}控制完成")
    print("="*60)
    return True


def seat_occupy_control(port="COM4", channel=3, duration=3.0, verify=True):
    """
    座椅占座控制子程序
    """
    print("="*60)
    print("🪑 座椅占座控制子程序")
    print("="*60)
    
    success = press_relay(port, 9600, channel, duration)
    
    if not success:
        print("❌ 占座动作执行失败")
        return False
    
    time.sleep(1)
    
    if verify:
        print("\n📋 验证结果...")
        seat_status = get_signal_value("ctrl.seat.driver_occupied")
        if seat_status is not None:
            print(f"✅ 验证完成，座椅占用状态 = {seat_status}")
    
    print("\n✅ 座椅占座控制完成")
    print("="*60)
    return True


# ==================== 快捷别名（更直观） ====================

def press_brake(**kwargs):
    """快捷：踩刹车"""
    return brake_control(**kwargs)


def press_start_button(**kwargs):
    """快捷：按启动键"""
    return start_button_control(**kwargs)


def open_door(**kwargs):
    """快捷：开门"""
    kwargs['action'] = 'open'
    return door_control(**kwargs)


def close_door(**kwargs):
    """快捷：关门"""
    kwargs['action'] = 'close'
    return door_control(**kwargs)


def occupy_seat(**kwargs):
    """快捷：占座"""
    return seat_occupy_control(**kwargs)


# ==================== 命令行直接调用支持 ====================

if __name__ == "__main__":
    import sys
    
    # 默认参数
    port = "COM4"
    channel = 1
    duration = 2.0
    
    # 解析命令行参数
    if len(sys.argv) >= 2:
        port = sys.argv[1]
    if len(sys.argv) >= 3:
        channel = int(sys.argv[2])
    if len(sys.argv) >= 4:
        duration = float(sys.argv[3])
    
    print(f"\n🚀 命令行模式")
    print(f"   串口: {port}")
    print(f"   通道: {channel}")
    print(f"   持续: {duration}秒")
    
    # 执行踩刹车（默认动作）
    brake_control(port=port, channel=channel, duration=duration)
