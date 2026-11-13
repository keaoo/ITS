#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音频探测辅助模块 - 用于在测试执行器中进行音频探测
"""
import os
import time
import threading
import numpy as np
import wave
from datetime import datetime

try:
    import pyaudio
    HAS_AUDIO = True
except ImportError:
    HAS_AUDIO = False


class AudioDetector:
    """音频探测器"""
    
    def __init__(self, log_callback=None):
        self.log_callback = log_callback
        self.is_running = False
        self.audio_frames = []
        self.volume_samples = []
        self.audio = None
        self.stream = None
        
    def log(self, message):
        """记录日志"""
        if self.log_callback:
            self.log_callback(message)
        print(message)
    
    def detect(self, duration_seconds, save_folder, threshold_percent=30, current_cycle=0):
        """
        执行音频探测
        
        Args:
            duration_seconds: 采集时长（秒）
            save_folder: 保存文件夹
            threshold_percent: 音量下限（百分比）
            current_cycle: 当前循环次数（用于文件名）
            
        Returns:
            dict: {
                "success": bool,
                "avg_volume": float,
                "is_silent": bool,
                "audio_file": str,
                "error": str
            }
        """
        if not HAS_AUDIO:
            return {
                "success": False,
                "avg_volume": 0,
                "is_silent": False,
                "audio_file": "",
                "error": "缺少音频库，请安装: pip install pyaudio numpy"
            }
        
        result = {
            "success": False,
            "avg_volume": 0,
            "is_silent": False,
            "audio_file": "",
            "error": ""
        }
        
        try:
            self.log(f"🎵 开始音频探测，时长: {duration_seconds} 秒")
            self.log(f"🎯 音量下限: {threshold_percent} %")
            
            # 确保保存文件夹存在
            audio_folder = os.path.join(save_folder, "音频")
            if not os.path.exists(audio_folder):
                os.makedirs(audio_folder)
                self.log(f"📁 创建文件夹: {audio_folder}")
            
            self.is_running = True
            self.audio_frames = []
            self.volume_samples = []
            
            # 初始化音频
            self.audio = pyaudio.PyAudio()
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=44100,
                input=True,
                frames_per_buffer=1024
            )
            
            # 启动采集线程
            self.collect_thread = threading.Thread(target=self._collect_loop, daemon=True)
            self.collect_thread.start()
            
            # 等待采集完成
            start_time = time.time()
            while self.is_running and (time.time() - start_time) < duration_seconds:
                time.sleep(0.1)
            
            # 停止采集
            self.is_running = False
            if self.collect_thread:
                self.collect_thread.join(timeout=2)
            
            # 停止音频流
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
            
            # 计算平均音量
            if self.volume_samples:
                avg_volume = float(np.mean(self.volume_samples))
                result["avg_volume"] = avg_volume
                self.log(f"📊 平均音量: {avg_volume:.2f} %")
                
                # 判断是否静音
                result["is_silent"] = avg_volume < threshold_percent
                if result["is_silent"]:
                    self.log(f"🔇 判断结果: 环境静音 (平均音量 {avg_volume:.2f}% < 阈值 {threshold_percent}%)")
                else:
                    self.log(f"🔊 判断结果: 环境有声音 (平均音量 {avg_volume:.2f}% >= 阈值 {threshold_percent}%)")
            else:
                avg_volume = 0
                result["avg_volume"] = 0
                result["is_silent"] = False
                self.log(f"⚠️ 未采集到音量数据")
            
            # 保存音频文件
            if self.audio_frames:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                if current_cycle > 0:
                    audio_filename = f"音频探测_第{current_cycle}次循环_{timestamp}.wav"
                else:
                    audio_filename = f"音频探测_{timestamp}.wav"
                audio_filepath = os.path.join(audio_folder, audio_filename)
                
                self._save_wav(audio_filepath, self.audio_frames)
                result["audio_file"] = audio_filepath
                self.log(f"💾 音频已保存: {audio_filepath}")
            else:
                self.log(f"⚠️ 未采集到音频数据")
            
            result["success"] = True
            self.log(f"✅ 音频探测完成")
            
        except Exception as e:
            error_msg = f"音频探测失败: {str(e)}"
            self.log(f"❌ {error_msg}")
            result["error"] = error_msg
            result["success"] = False
            
            # 确保资源清理
            try:
                if self.stream:
                    self.stream.stop_stream()
                    self.stream.close()
                if self.audio:
                    self.audio.terminate()
            except:
                pass
        
        return result
    
    def _collect_loop(self):
        """采集循环"""
        while self.is_running:
            try:
                data = self.stream.read(1024, exception_on_overflow=False)
                self.audio_frames.append(data)
                
                # 计算音量
                audio_data = np.frombuffer(data, dtype=np.int16)
                rms = np.sqrt(np.mean(audio_data.astype(np.float32) ** 2))
                volume = min(100, rms / 327.68)
                
                self.volume_samples.append(volume)
                
            except Exception as e:
                print(f"采集错误: {e}")
                break
    
    def _save_wav(self, filepath, frames):
        """保存WAV文件"""
        try:
            wf = wave.open(filepath, 'wb')
            wf.setnchannels(1)
            wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b''.join(frames))
            wf.close()
            return True
        except Exception as e:
            self.log(f"❌ 保存WAV文件失败: {e}")
            return False


def run_audio_detection(duration_seconds, save_folder, threshold_percent=30, log_callback=None):
    """
    运行音频探测（便捷函数）
    
    Args:
        duration_seconds: 采集时长（秒）
        save_folder: 保存文件夹
        threshold_percent: 音量下限（百分比）
        log_callback: 日志回调函数
        
    Returns:
        dict: 探测结果
    """
    detector = AudioDetector(log_callback)
    return detector.detect(duration_seconds, save_folder, threshold_percent)


if __name__ == "__main__":
    # 测试
    def test_log(msg):
        print(msg)
    
    result = run_audio_detection(5, ".", 30, test_log)
    print(f"\n探测结果: {result}")
