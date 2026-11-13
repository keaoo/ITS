#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视觉检测核心模块
功能：摄像头操作、ROI区域亮度检测、图像对比、截图保存
"""
import cv2
import numpy as np
import os
import time
import json
from datetime import datetime


class VisualDetector:
    """视觉检测器"""
    
    def __init__(self):
        self.cap = None               # 摄像头对象
        self.current_frame = None     # 当前帧
        self.roi_list = []            # ROI区域列表 [(x1, y1, x2, y2), ...]
        self.brightness_threshold = 50  # 亮度阈值（低于此值认为是黑屏）
        self.camera_port = 0          # 摄像头端口
        self.save_folder = ""         # 截图保存路径
        # 配置基准文件夹（打包后在程序目录下）
        import sys
        if hasattr(sys, '_MEIPASS'):
            # 打包后：配置文件保存在程序所在目录
            base_path = os.path.dirname(os.path.abspath(sys.executable))
        else:
            # 开发模式：配置文件保存在脚本所在目录
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        config_dir = os.path.join(base_path, "配置基准文件")
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        self.config_file = os.path.join(config_dir, "ITS_config.json")  # 统一配置文件路径
        self.reference_image_path = os.path.join(config_dir, "visual_reference.jpg")  # 基准图保存路径
        self.reference_frame = None   # 基准帧（用于图像对比）
        self.image_diff_threshold = 30  # 图像差异阈值（差异均值大于此值认为不一致）
        
        # 初始化时加载已有配置
        self.load_config()
        # 加载基准帧
        self.load_reference_frame()
    
    def save_reference_frame(self, frame=None):
        """保存基准帧到磁盘"""
        if frame is None:
            frame = self.current_frame
        if frame is None:
            print(f"[视觉] 无法保存基准帧：当前帧为空")
            return False
        try:
            # 用 imencode 兼容中文路径
            ext = os.path.splitext(self.reference_image_path)[1] or ".jpg"
            result, nparray = cv2.imencode(ext, frame)
            if result:
                nparray.tofile(self.reference_image_path)
                self.reference_frame = frame.copy()
                print(f"[视觉] 基准帧已保存: {self.reference_image_path}")
                return True
        except Exception as e:
            print(f"[视觉] 保存基准帧失败: {e}")
        return False
    
    def load_reference_frame(self):
        """从磁盘加载基准帧"""
        if not os.path.exists(self.reference_image_path):
            return False
        try:
            # 兼容中文路径
            nparray = np.fromfile(self.reference_image_path, dtype=np.uint8)
            self.reference_frame = cv2.imdecode(nparray, cv2.IMREAD_COLOR)
            if self.reference_frame is not None:
                print(f"[视觉] 基准帧已加载: {self.reference_image_path}")
                return True
        except Exception as e:
            print(f"[视觉] 加载基准帧失败: {e}")
        return False
    
    def save_config(self):
        """保存视觉配置到统一配置文件（合并写入，不覆盖其他配置）"""
        # 先读取已有配置
        config = {}
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except Exception as e:
                print(f"[视觉] 读取已有配置失败: {e}")
        
        # 合并视觉相关配置
        config["camera_port"] = self.camera_port
        config["brightness_threshold"] = self.brightness_threshold
        config["roi_list"] = self.roi_list
        config["visual_save_folder"] = self.save_folder
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            print(f"[视觉] 配置已保存到: {self.config_file}")
            return True
        except Exception as e:
            print(f"[视觉] 保存配置失败: {e}")
            return False
    
    def load_config(self):
        """从统一配置文件加载视觉配置"""
        if not os.path.exists(self.config_file):
            print(f"[视觉] 配置文件不存在，使用默认配置")
            return False
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.camera_port = config.get("camera_port", 0)
            self.brightness_threshold = config.get("brightness_threshold", 50)
            # ROI 区域：兼容字符串/元组格式
            roi_list_raw = config.get("roi_list", [])
            self.roi_list = [tuple(roi) if isinstance(roi, list) else roi for roi in roi_list_raw]
            self.save_folder = config.get("visual_save_folder", "")
            
            print(f"[视觉] 配置已加载:")
            print(f"  - 摄像头端口: {self.camera_port}")
            print(f"  - 亮度阈值: {self.brightness_threshold}")
            print(f"  - ROI数量: {len(self.roi_list)}")
            return True
        except Exception as e:
            print(f"[视觉] 加载配置失败: {e}")
            return False
        
    def get_available_cameras(self):
        """获取所有可用摄像头端口"""
        available = []
        # 尝试检测前5个端口（减少不必要的检测）
        for i in range(5):
            # 使用CAP_DSHOW后端（Windows专用，减少警告）
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.isOpened():
                available.append(i)
                cap.release()
        return available
    
    def open_camera(self, port=0):
        """打开摄像头"""
        if self.cap is not None:
            self.cap.release()
        
        # 使用CAP_DSHOW后端（Windows专用，减少警告和打开时间）
        self.cap = cv2.VideoCapture(port, cv2.CAP_DSHOW)
        
        # 设置分辨率（提高性能）
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        self.camera_port = port
        
        if self.cap.isOpened():
            print(f"[视觉] 摄像头 {port} 打开成功 (640x480)")
            return True
        else:
            print(f"[视觉] 摄像头 {port} 打开失败")
            return False
    
    def close_camera(self):
        """关闭摄像头"""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            print("[视觉] 摄像头已关闭")
    
    def get_frame(self):
        """获取当前帧"""
        if self.cap is None or not self.cap.isOpened():
            return None
        
        ret, frame = self.cap.read()
        if ret:
            self.current_frame = frame.copy()
            return frame
        return None
    
    def add_roi(self, x1, y1, x2, y2):
        """添加ROI区域"""
        # 确保坐标是左上角和右下角
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)
        
        # 确保区域有效
        if x2 - x1 > 10 and y2 - y1 > 10:  # 至少10x10像素
            self.roi_list.append((x1, y1, x2, y2))
            print(f"[视觉] 添加ROI区域: ({x1}, {y1}, {x2}, {y2})")
            return True
        return False
    
    def clear_rois(self):
        """清除所有ROI区域"""
        self.roi_list = []
        print("[视觉] 已清除所有ROI区域")
    
    def calculate_brightness(self, frame, roi=None):
        """
        计算图像或ROI区域的平均亮度
        :param frame: 图像帧
        :param roi: ROI区域 (x1, y1, x2, y2)，None表示整图
        :return: 平均亮度值 (0-255)
        """
        if frame is None:
            return 0
        
        if roi is not None:
            x1, y1, x2, y2 = roi
            roi_frame = frame[y1:y2, x1:x2]
        else:
            roi_frame = frame
        
        # 转换为灰度图
        if len(roi_frame.shape) == 3:
            gray = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2GRAY)
        else:
            gray = roi_frame
        
        # 计算平均亮度
        if gray.size > 0:
            brightness = np.mean(gray)
            return brightness
        return 0
    
    def check_black_screen(self, frame=None):
        """
        检查是否黑屏
        :param frame: 图像帧，None表示使用当前帧
        :return: (是否黑屏, 各ROI亮度列表)
        """
        if frame is None:
            frame = self.current_frame
        
        if frame is None or len(self.roi_list) == 0:
            return False, []
        
        brightness_list = []
        is_black = False
        
        for roi in self.roi_list:
            brightness = self.calculate_brightness(frame, roi)
            brightness_list.append(brightness)
            
            # 只要有一个区域亮度低于阈值就认为是黑屏
            if brightness < self.brightness_threshold:
                is_black = True
        
        return is_black, brightness_list
    
    def compare_images(self, img1, img2, roi=None, threshold=30):
        """
        对比两张图像是否一致
        :param img1: 图像1
        :param img2: 图像2
        :param roi: ROI区域，None表示整图
        :param threshold: 差异阈值
        :return: (是否一致, 差异值)
        """
        if img1 is None or img2 is None:
            return False, 999
        
        if roi is not None:
            x1, y1, x2, y2 = roi
            img1_roi = img1[y1:y2, x1:x2]
            img2_roi = img2[y1:y2, x1:x2]
        else:
            img1_roi = img1
            img2_roi = img2
        
        # 转换为灰度图
        if len(img1_roi.shape) == 3:
            gray1 = cv2.cvtColor(img1_roi, cv2.COLOR_BGR2GRAY)
        else:
            gray1 = img1_roi
        
        if len(img2_roi.shape) == 3:
            gray2 = cv2.cvtColor(img2_roi, cv2.COLOR_BGR2GRAY)
        else:
            gray2 = img2_roi
        
        # 计算差异
        if gray1.shape != gray2.shape:
            return False, 999
        
        diff = cv2.absdiff(gray1, gray2)
        mean_diff = np.mean(diff)
        
        is_same = mean_diff <= threshold
        
        return is_same, mean_diff
    
    def save_screenshot(self, cycle_count, prefix="fail", folder=None):
        """
        保存截图
        :param cycle_count: 循环次数
        :param prefix: 文件名前缀
        :param folder: 保存文件夹，None使用默认
        :return: 保存的文件路径
        """
        print(f"[视觉] ========== 开始保存截图 ==========")
        
        # 确保有当前帧，如果没有就再抓一帧
        if self.current_frame is None:
            print(f"[视觉] current_frame 为空，尝试重新抓取...")
            if self.cap is not None and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    self.current_frame = frame
                    print(f"[视觉] 重新抓取成功，图像尺寸: {frame.shape}")
                else:
                    print(f"[视觉] 重新抓取失败")
            else:
                print(f"[视觉] 摄像头未打开，无法抓取")
        
        if self.current_frame is None:
            print(f"[视觉] 无法截图：没有有效的图像帧")
            return None
        
        print(f"[视觉] 当前图像尺寸: {self.current_frame.shape}")
        
        # 确定保存路径
        save_path = folder if folder else self.save_folder
        if not save_path:
            save_path = "./screenshots"
        
        # 🎯 路径规范化：统一用 os.path.normpath 处理 Windows 路径分隔符
        save_path = os.path.normpath(save_path)
        print(f"[视觉] 保存路径: {save_path}")
        
        try:
            os.makedirs(save_path, exist_ok=True)
            
            # 生成文件名：循环次数_年月日_时分秒.jpg
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{cycle_count:04d}_{prefix}_{timestamp}.jpg"
            full_path = os.path.join(save_path, filename)
            
            print(f"[视觉] 准备保存到: {full_path}")
            
            # 🎯 先尝试创建文件，检查路径是否可写
            test_file = os.path.join(save_path, "test_write.tmp")
            try:
                with open(test_file, "w") as f:
                    f.write("test")
                os.remove(test_file)
                print(f"[视觉] 路径写入测试通过")
            except Exception as e:
                print(f"[视觉] 路径写入测试失败: {e}")
            
            # 保存图片
            success = cv2.imwrite(full_path, self.current_frame)
            if success:
                file_size = os.path.getsize(full_path)
                print(f"[视觉] ✅ 截图保存成功！大小: {file_size} 字节")
                print(f"[视觉] ========== 截图完成 ==========")
                return full_path
            else:
                print(f"[视觉] cv2.imwrite 直接保存失败（可能是中文路径问题），尝试用 numpy 方案...")
                try:
                    # 🎯 解决中文路径问题：用 cv2.imencode + 文件写入
                    ext = os.path.splitext(full_path)[1]
                    result, nparray = cv2.imencode(ext, self.current_frame)
                    if result:
                        nparray.tofile(full_path)
                        if os.path.exists(full_path):
                            file_size = os.path.getsize(full_path)
                            print(f"[视觉] ✅ numpy 方案保存成功！大小: {file_size} 字节")
                            print(f"[视觉] ========== 截图完成 ==========")
                            return full_path
                except Exception as e2:
                    print(f"[视觉] numpy 方案也失败: {e2}")
                
                print(f"[视觉] ========== 截图失败 ==========")
                return None
        except Exception as e:
            print(f"[视觉] ❌ 截图保存异常: {e}")
            import traceback
            traceback.print_exc()
            print(f"[视觉] ========== 截图异常 ==========")
            return None
    
    def verify_screen(self, cycle_count, reference_frame=None):
        """
        执行屏幕验证（亮屏指令时调用）
        :param cycle_count: 当前循环次数
        :param reference_frame: 参考帧（用于图像对比，None表示只检测黑屏）
        :return: (是否通过, 验证信息)
        """
        # 1. 获取当前帧
        frame = self.get_frame()
        if frame is None:
            return False, "无法获取摄像头图像"
        
        # 2. 检查黑屏
        is_black, brightness_list = self.check_black_screen(frame)
        info = f"各ROI亮度: {[round(b, 1) for b in brightness_list]}, 阈值={self.brightness_threshold}"
        
        if is_black:
            # 黑屏，保存截图
            self.save_screenshot(cycle_count, prefix="black_screen")
            return False, f"检测到黑屏！{info}"
        
        # 3. 如果有参考帧，对比图像
        if reference_frame is not None:
            all_same = True
            diff_list = []
            
            for roi in self.roi_list:
                is_same, diff = self.compare_images(reference_frame, frame, roi)
                diff_list.append(round(diff, 1))
                if not is_same:
                    all_same = False
            
            info += f", 各ROI差异: {diff_list}"
            
            if not all_same:
                # 图像不一致，保存截图
                self.save_screenshot(cycle_count, prefix="diff")
                return False, f"检测到图像不一致！{info}"
        
        return True, f"屏幕正常。{info}"
    
    def draw_rois(self, frame):
        """在图像上绘制ROI区域"""
        if frame is None:
            return frame
        
        for i, roi in enumerate(self.roi_list):
            x1, y1, x2, y2 = roi
            # 绘制矩形框
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            # 绘制编号
            cv2.putText(frame, f"ROI{i+1}", (x1, y1-5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        return frame


# 单例模式
_detector_instance = None

def get_visual_detector():
    """获取视觉检测器单例"""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = VisualDetector()
    return _detector_instance
