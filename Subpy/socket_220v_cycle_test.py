# -*- coding: utf-8 -*-
"""
220V 插座循环测试模块
支持打开/关闭配对循环测试，带状态验证和失败重试机制
"""
import subprocess
import time
from datetime import datetime


class Socket220VCycleTester:
    """220V 插座循环测试器"""
    
    def __init__(self, log_callback=None):
        """
        初始化测试器
        :param log_callback: 日志回调函数
        """
        self.log_callback = log_callback or print
        self.open_cmd = "adb -host shell vapisend -set ctrl.bms.inner_discharge_switch 1"
        self.close_cmd = "adb -host shell vapisend -set ctrl.bms.inner_discharge_switch 2"
        self.check_cmd = "adb -host shell vapisend -get ctrl.bms.inner_discharge_switch"
        self.expected_open = "1"
        self.expected_close = "2"
        
    def log(self, message):
        """输出日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        if self.log_callback:
            self.log_callback(log_msg)
        else:
            print(log_msg)
    
    def run_adb_cmd(self, cmd, timeout=10):
        """
        执行 ADB 命令
        :param cmd: 命令字符串
        :param timeout: 超时时间（秒）
        :return: (success, output)
        """
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding='utf-8'
            )
            output = result.stdout.strip()
            if result.returncode == 0:
                return True, output
            else:
                error_msg = result.stderr.strip() if result.stderr else f"返回码：{result.returncode}"
                return False, error_msg
        except subprocess.TimeoutExpired:
            return False, f"命令执行超时 ({timeout}s)"
        except Exception as e:
            return False, str(e)
    
    def check_socket_state(self, expected_state=None):
        """
        检查插座当前状态
        :param expected_state: 期望状态 (None 表示只读取不验证)
        :return: (success, current_state, message)
        """
        success, output = self.run_adb_cmd(self.check_cmd, timeout=5)
        
        if not success:
            return False, None, f"❌ 读取状态失败：{output}"
        
        current_state = output.strip()
        
        if expected_state is not None:
            if current_state == expected_state:
                return True, current_state, f"✅ 状态验证通过：{current_state}"
            else:
                return False, current_state, f"❌ 状态不匹配：期望={expected_state}, 实际={current_state}"
        else:
            return True, current_state, f"📊 当前状态：{current_state}"
    
    def execute_open(self, verify=True, retry_count=2):
        """
        执行打开操作
        :param verify: 是否验证结果
        :param retry_count: 失败重试次数
        :return: (success, message)
        """
        for attempt in range(1, retry_count + 2):
            self.log(f"🔌 执行打开操作 (第{attempt}次尝试)...")
            
            # 执行打开命令
            success, output = self.run_adb_cmd(self.open_cmd, timeout=5)
            if not success:
                self.log(f"⚠️ 打开命令执行失败：{output}")
                if attempt <= retry_count:
                    time.sleep(1)
                    continue
                return False, f"打开命令执行失败：{output}"
            
            # 等待执行
            time.sleep(2)
            
            # 验证状态
            if verify:
                success, state, msg = self.check_socket_state(self.expected_open)
                self.log(msg)
                if success:
                    return True, "打开成功"
                else:
                    if attempt <= retry_count:
                        self.log(f"⚠️ 验证失败，准备重试...")
                        time.sleep(1)
                        continue
                    return False, msg
            else:
                return True, "打开命令已执行"
        
        return False, "打开操作超过最大重试次数"
    
    def execute_close(self, verify=True, retry_count=2):
        """
        执行关闭操作
        :param verify: 是否验证结果
        :param retry_count: 失败重试次数
        :return: (success, message)
        """
        for attempt in range(1, retry_count + 2):
            self.log(f"🔌 执行关闭操作 (第{attempt}次尝试)...")
            
            # 执行关闭命令
            success, output = self.run_adb_cmd(self.close_cmd, timeout=5)
            if not success:
                self.log(f"⚠️ 关闭命令执行失败：{output}")
                if attempt <= retry_count:
                    time.sleep(1)
                    continue
                return False, f"关闭命令执行失败：{output}"
            
            # 等待执行
            time.sleep(2)
            
            # 验证状态
            if verify:
                success, state, msg = self.check_socket_state(self.expected_close)
                self.log(msg)
                if success:
                    return True, "关闭成功"
                else:
                    if attempt <= retry_count:
                        self.log(f"⚠️ 验证失败，准备重试...")
                        time.sleep(1)
                        continue
                    return False, msg
            else:
                return True, "关闭命令已执行"
        
        return False, "关闭操作超过最大重试次数"
    
    def run_single_cycle(self, cycle_num, verify=True, retry_count=2, wait_between=1):
        """
        执行单次完整循环（打开 -> 关闭）
        :param cycle_num: 循环次数编号
        :param verify: 是否验证每个步骤
        :param retry_count: 失败重试次数
        :param wait_between: 打开和关闭之间的等待时间
        :return: (success, log_summary)
        """
        self.log(f"\n{'='*60}")
        self.log(f"🔄 开始第 {cycle_num} 次循环测试")
        self.log(f"{'='*60}")
        
        cycle_log = {
            'cycle': cycle_num,
            'open_success': False,
            'close_success': False,
            'open_state': None,
            'close_state': None,
            'errors': []
        }
        
        # Step 1: 打开插座
        self.log(f"\n📍 Step 1/3: 打开 220V 插座")
        success, msg = self.execute_open(verify=verify, retry_count=retry_count)
        cycle_log['open_success'] = success
        
        if not success:
            cycle_log['errors'].append(f"打开失败：{msg}")
            self.log(f"❌ 第 {cycle_num} 次循环失败（打开步骤）")
            return False, cycle_log
        
        # 获取并记录状态
        _, state, _ = self.check_socket_state()
        cycle_log['open_state'] = state
        
        # 等待
        if wait_between > 0:
            self.log(f"⏱️ 等待 {wait_between} 秒...")
            time.sleep(wait_between)
        
        # Step 2: 关闭插座
        self.log(f"\n📍 Step 2/3: 关闭 220V 插座")
        success, msg = self.execute_close(verify=verify, retry_count=retry_count)
        cycle_log['close_success'] = success
        
        if not success:
            cycle_log['errors'].append(f"关闭失败：{msg}")
            self.log(f"❌ 第 {cycle_num} 次循环失败（关闭步骤）")
            return False, cycle_log
        
        # 获取并记录状态
        _, state, _ = self.check_socket_state()
        cycle_log['close_state'] = state
        
        # Step 3: 总结
        self.log(f"\n✅ 第 {cycle_num} 次循环测试完成")
        self.log(f"   打开：{'成功' if cycle_log['open_success'] else '失败'} (状态={cycle_log['open_state']})")
        self.log(f"   关闭：{'成功' if cycle_log['close_success'] else '失败'} (状态={cycle_log['close_state']})")
        
        return True, cycle_log
    
    def run_continuous_cycles(self, total_cycles, verify=True, retry_count=2, 
                              wait_between=1, wait_between_cycles=0):
        """
        执行连续循环测试
        :param total_cycles: 总循环次数
        :param verify: 是否验证每个步骤
        :param retry_count: 失败重试次数
        :param wait_between: 打开和关闭之间的等待时间
        :param wait_between_cycles: 循环之间的等待时间
        :return: (success_count, total_cycles, all_logs)
        """
        self.log(f"\n{'='*60}")
        self.log(f"🚀 开始 220V 插座循环测试")
        self.log(f"   总循环次数：{total_cycles}")
        self.log(f"   验证模式：{'开启' if verify else '关闭'}")
        self.log(f"   重试次数：{retry_count}")
        self.log(f"   步骤间隔：{wait_between}s")
        self.log(f"   循环间隔：{wait_between_cycles}s")
        self.log(f"{'='*60}\n")
        
        success_count = 0
        all_logs = []
        
        for cycle in range(1, total_cycles + 1):
            success, log_data = self.run_single_cycle(
                cycle_num=cycle,
                verify=verify,
                retry_count=retry_count,
                wait_between=wait_between
            )
            
            all_logs.append(log_data)
            
            if success:
                success_count += 1
            
            # 循环间隔等待
            if cycle < total_cycles and wait_between_cycles > 0:
                self.log(f"\n⏱️ 循环间隔等待 {wait_between_cycles} 秒...")
                time.sleep(wait_between_cycles)
        
        # 总结
        self.log(f"\n{'='*60}")
        self.log(f"📊 测试总结")
        self.log(f"{'='*60}")
        self.log(f"   总循环数：{total_cycles}")
        self.log(f"   成功数：{success_count}")
        self.log(f"   失败数：{total_cycles - success_count}")
        self.log(f"   成功率：{success_count/total_cycles*100:.1f}%")
        
        if success_count == total_cycles:
            self.log(f"\n🎉 所有循环测试通过！")
        else:
            self.log(f"\n⚠️ 有 {total_cycles - success_count} 次循环失败，请检查日志")
        
        self.log(f"{'='*60}\n")
        
        return success_count, total_cycles, all_logs


def run_socket_220v_test(total_cycles=10, verify=True, retry_count=2, 
                         wait_between=1, wait_between_cycles=0, 
                         log_callback=None):
    """
    快捷函数：执行 220V 插座循环测试
    :param total_cycles: 总循环次数
    :param verify: 是否验证
    :param retry_count: 重试次数
    :param wait_between: 步骤间隔
    :param wait_between_cycles: 循环间隔
    :param log_callback: 日志回调
    :return: (success_count, total_cycles, all_logs)
    """
    tester = Socket220VCycleTester(log_callback)
    return tester.run_continuous_cycles(
        total_cycles=total_cycles,
        verify=verify,
        retry_count=retry_count,
        wait_between=wait_between,
        wait_between_cycles=wait_between_cycles
    )


# 命令行测试入口
if __name__ == "__main__":
    print("="*60)
    print("220V 插座循环测试工具")
    print("="*60)
    
    # 简单测试：执行 3 次循环
    success, total, logs = run_socket_220v_test(
        total_cycles=3,
        verify=True,
        retry_count=2,
        wait_between=1,
        wait_between_cycles=2
    )
    
    print(f"\n测试结果：{success}/{total} 成功")
