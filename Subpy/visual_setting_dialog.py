#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视觉设置对话框（简化版）
功能：摄像头选择、阈值设置、ROI区域框选
简化坐标转换，固定640x480显示
"""
import sys
import os
# import cv2  # 延迟导入，避免打包兼容性问题
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout,
    QPushButton, QComboBox, QLineEdit, QLabel, QMessageBox,
    QFileDialog
)
from PySide6.QtCore import Qt, QTimer, Signal, QPoint
from PySide6.QtGui import QImage, QPixmap, QPainter, QColor, QPen
# from Subpy.visual_detector import VisualDetector, get_visual_detector  # 延迟导入


class ImageLabel(QLabel):
    """支持鼠标框选ROI的图像标签（固定640x480，无缩放）"""
    
    roi_selected = Signal(int, int, int, int)  # 发送ROI坐标
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.start_pos = None
        self.end_pos = None
        self.is_selecting = False
        self.setFixedSize(640, 480)  # 固定大小，与摄像头分辨率一致
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("background-color: black;")
        self.setText("请打开摄像头")
    
    def mousePressEvent(self, event):
        """鼠标按下开始框选"""
        if event.button() == Qt.LeftButton:
            self.start_pos = event.pos()
            self.is_selecting = True
    
    def mouseMoveEvent(self, event):
        """鼠标移动更新框选区域"""
        if self.is_selecting and self.start_pos:
            self.end_pos = event.pos()
            self.update()  # 触发重绘
    
    def mouseReleaseEvent(self, event):
        """鼠标释放完成框选"""
        if event.button() == Qt.LeftButton and self.is_selecting:
            self.end_pos = event.pos()
            self.is_selecting = False
            
            # 直接使用鼠标坐标（标签固定640x480，与图像大小一致）
            if self.start_pos and self.end_pos:
                x1 = self.start_pos.x()
                y1 = self.start_pos.y()
                x2 = self.end_pos.x()
                y2 = self.end_pos.y()
                
                # 确保区域最小10x10像素
                if abs(x2 - x1) < 10 or abs(y2 - y1) < 10:
                    print(f"[ROI] 区域太小，忽略")
                    return
                
                print(f"[ROI] 选择区域: ({x1}, {y1}) -> ({x2}, {y2})")
                self.roi_selected.emit(x1, y1, x2, y2)
    
    def paintEvent(self, event):
        """绘制ROI框"""
        super().paintEvent(event)
        
        if self.start_pos and self.end_pos:
            painter = QPainter(self)
            pen = QPen(QColor(0, 255, 0), 2, Qt.SolidLine)
            painter.setPen(pen)
            
            x = min(self.start_pos.x(), self.end_pos.x())
            y = min(self.start_pos.y(), self.end_pos.y())
            w = abs(self.end_pos.x() - self.start_pos.x())
            h = abs(self.end_pos.y() - self.start_pos.y())
            
            painter.drawRect(x, y, w, h)
            painter.end()


class VisualSettingDialog(QDialog):
    """视觉设置对话框"""
    
    # 信号：配置更新
    settings_updated = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("视觉识别设置")
        self.setMinimumSize(700, 750)
        
        # 获取视觉检测器
        from Subpy.visual_detector import VisualDetector, get_visual_detector
        self.detector = get_visual_detector()
        
        # 定时器：更新摄像头画面
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        
        # 存储参考帧
        self.reference_frame = None
        
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """初始化UI"""
        main_layout = QVBoxLayout(self)
        
        # ========== 1. 设置区域 ==========
        setting_group = QGroupBox("摄像头与阈值设置")
        setting_layout = QFormLayout(setting_group)
        
        # 摄像头选择
        camera_layout = QHBoxLayout()
        self.camera_combo = QComboBox()
        self.camera_combo.setMinimumHeight(30)
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self.load_cameras)
        camera_layout.addWidget(self.camera_combo)
        camera_layout.addWidget(self.refresh_btn)
        setting_layout.addRow("摄像头端口:", camera_layout)
        
        # 亮度阈值
        threshold_layout = QHBoxLayout()
        self.threshold_input = QLineEdit("50")
        self.threshold_input.setPlaceholderText("亮度阈值(0-255)")
        self.threshold_input.setMinimumHeight(30)
        threshold_layout.addWidget(self.threshold_input)
        threshold_layout.addWidget(QLabel("低于此值认为是黑屏"))
        setting_layout.addRow("亮度阈值:", threshold_layout)
        
        # 保存路径提示（使用综合测试配置，不再手动设置）
        self.path_label = QLabel("截图将保存到: 综合测试配置的测试文件夹路径")
        self.path_label.setStyleSheet("color: #666; font-style: italic;")
        setting_layout.addRow("保存路径:", self.path_label)
        
        main_layout.addWidget(setting_group)
        
        # ========== 2. 控制按钮区域 ==========
        btn_layout = QHBoxLayout()
        
        self.open_btn = QPushButton("打开摄像头")
        self.open_btn.setMinimumHeight(40)
        self.open_btn.clicked.connect(self.open_camera)
        btn_layout.addWidget(self.open_btn)
        
        self.close_btn = QPushButton("关闭摄像头")
        self.close_btn.setMinimumHeight(40)
        self.close_btn.clicked.connect(self.close_camera)
        self.close_btn.setEnabled(False)
        btn_layout.addWidget(self.close_btn)
        
        self.clear_roi_btn = QPushButton("清除所有ROI")
        self.clear_roi_btn.setMinimumHeight(40)
        self.clear_roi_btn.clicked.connect(self.clear_rois)
        btn_layout.addWidget(self.clear_roi_btn)
        
        main_layout.addLayout(btn_layout)
        
        # ========== 3. 图像显示区域（居中）==========
        image_group = QGroupBox("摄像头画面（鼠标拖拽框选ROI区域）")
        image_layout = QVBoxLayout(image_group)
        image_layout.setAlignment(Qt.AlignCenter)  # 居中
        
        self.image_label = ImageLabel()
        self.image_label.roi_selected.connect(self.add_roi)
        image_layout.addWidget(self.image_label)
        
        main_layout.addWidget(image_group)
        
        # ========== 4. 状态显示区域 ==========
        self.status_label = QLabel("状态: 未打开摄像头 | ROI数量: 0")
        self.status_label.setMinimumHeight(30)
        main_layout.addWidget(self.status_label)
        
        # ========== 5. 底部按钮 ==========
        bottom_btn_layout = QHBoxLayout()
        
        self.ok_btn = QPushButton("确定")
        self.ok_btn.setMinimumHeight(40)
        self.ok_btn.clicked.connect(self.accept_settings)
        bottom_btn_layout.addWidget(self.ok_btn)
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setMinimumHeight(40)
        self.cancel_btn.clicked.connect(self.reject)
        bottom_btn_layout.addWidget(self.cancel_btn)
        
        main_layout.addLayout(bottom_btn_layout)
    
    def load_cameras(self):
        """加载可用摄像头"""
        self.camera_combo.clear()
        cameras = self.detector.get_available_cameras()
        
        if cameras:
            for port in cameras:
                self.camera_combo.addItem(f"摄像头 {port}", port)
            self.status_label.setText(f"状态: 检测到 {len(cameras)} 个摄像头 | ROI数量: {len(self.detector.roi_list)}")
        else:
            self.camera_combo.addItem("未检测到摄像头")
            self.status_label.setText("状态: 未检测到摄像头 | ROI数量: 0")
    
    def open_camera(self):
        """打开摄像头"""
        port = self.camera_combo.currentData()
        if port is None:
            QMessageBox.warning(self, "警告", "请选择有效的摄像头端口！")
            return
        
        if self.detector.open_camera(port):
            self.timer.start(33)  # 约30fps
            self.open_btn.setEnabled(False)
            self.close_btn.setEnabled(True)
            self.status_label.setText(f"状态: 摄像头 {port} 已打开 | ROI数量: {len(self.detector.roi_list)}")
            
            # 🎯 立即保存摄像头端口到配置
            self.detector.camera_port = port
            self.detector.save_config()
            print(f"[视觉设置] 摄像头端口 {port} 已保存到配置")
        else:
            QMessageBox.critical(self, "错误", f"无法打开摄像头 {port}！")
    
    def close_camera(self):
        """关闭摄像头"""
        self.timer.stop()
        self.detector.close_camera()
        self.open_btn.setEnabled(True)
        self.close_btn.setEnabled(False)
        self.image_label.clear()
        self.image_label.setText("请打开摄像头")
        self.status_label.setText(f"状态: 摄像头已关闭 | ROI数量: {len(self.detector.roi_list)}")
    
    def update_frame(self):
        """更新画面"""
        frame = self.detector.get_frame()
        if frame is not None:
            # 绘制ROI区域
            frame_with_roi = self.detector.draw_rois(frame.copy())
            
            # 转换为Qt显示格式
            height, width, channel = frame_with_roi.shape
            bytes_per_line = channel * width
            q_image = QImage(frame_with_roi.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
            
            # 直接显示，不缩放（标签已经是640x480）
            pixmap = QPixmap.fromImage(q_image)
            self.image_label.setPixmap(pixmap)
    
    def add_roi(self, x1, y1, x2, y2):
        """添加ROI区域"""
        if self.detector.add_roi(x1, y1, x2, y2):
            self.status_label.setText(f"状态: 摄像头已打开 | ROI数量: {len(self.detector.roi_list)}")
    
    def clear_rois(self):
        """清除所有ROI"""
        reply = QMessageBox.question(
            self, "确认", "确定要清除所有ROI区域吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.detector.clear_rois()
            # 🎯 立即持久化到 ITS_config.json，否则下次打开还会加载回来
            self.detector.save_config()
            # 🎯 同时删除基准帧文件
            import os
            if os.path.exists(self.detector.reference_image_path):
                try:
                    os.remove(self.detector.reference_image_path)
                    self.detector.reference_frame = None
                    print(f"[视觉] 已删除基准帧: {self.detector.reference_image_path}")
                except Exception as e:
                    print(f"[视觉] 删除基准帧失败: {e}")
            
            # 🎯 清除 ImageLabel 中残留的鼠标临时框选记录
            self.image_label.start_pos = None
            self.image_label.end_pos = None
            self.image_label.is_selecting = False
            self.image_label.update()  # 触发重绘移除临时框
            
            # 🎯 立即重绘当前画面（移除已显示的ROI绿框）
            if self.detector.current_frame is not None:
                from PySide6.QtGui import QImage, QPixmap
                frame = self.detector.current_frame.copy()  # 不调用 draw_rois
                height, width, channel = frame.shape
                bytes_per_line = channel * width
                q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
                pixmap = QPixmap.fromImage(q_image)
                self.image_label.setPixmap(pixmap)
            
            self.status_label.setText(f"状态: 摄像头已打开 | ROI数量: {len(self.detector.roi_list)}")
    
    def load_settings(self):
        """加载已有设置"""
        # 先从文件加载配置
        self.detector.load_config()
        
        # 加载阈值
        self.threshold_input.setText(str(self.detector.brightness_threshold))
        
        # 🎯 先保存一下要恢复的端口
        saved_port = self.detector.camera_port
        if saved_port is not None:
            try:
                saved_port = int(saved_port)
            except (ValueError, TypeError):
                saved_port = None
        
        # 🎯 先清空并重新加载摄像头列表
        self.camera_combo.clear()
        cameras = self.detector.get_available_cameras()
        if cameras:
            for port in cameras:
                self.camera_combo.addItem(f"摄像头 {port}", port)
        
        # 🎯 再恢复摄像头端口到下拉框
        if saved_port is not None:
            found = False
            for i in range(self.camera_combo.count()):
                item_data = self.camera_combo.itemData(i)
                if item_data is not None:
                    try:
                        item_data = int(item_data)
                        if item_data == saved_port:
                            self.camera_combo.setCurrentIndex(i)
                            found = True
                            print(f"[视觉设置] 已恢复摄像头端口: {saved_port}")
                            break
                    except (ValueError, TypeError):
                        continue
            
            if not found:
                print(f"[视觉设置] 未找到摄像头端口 {saved_port} 的选项，可用摄像头: {cameras}")
        
        # 更新状态显示
        roi_count = len(self.detector.roi_list)
        self.status_label.setText(f"状态: 已加载配置 | ROI数量: {roi_count}")
        
        # 🎯 如果已有ROI区域，在日志中显示
        if roi_count > 0:
            for i, roi in enumerate(self.detector.roi_list):
                print(f"[视觉设置] ROI{i+1}: {roi}")
        
        # 显示当前保存路径
        if self.detector.save_folder:
            self.path_label.setText(f"截图将保存到: {self.detector.save_folder}")
        
        # 🎯 如果已经有ROI配置，显示提示信息
        if roi_count > 0:
            self.path_label.setText(self.path_label.text() + f" | 已加载{roi_count}个检测区域")
    
    def accept_settings(self):
        """确认设置并关闭对话框"""
        # 保存阈值
        try:
            threshold = int(self.threshold_input.text())
            self.detector.brightness_threshold = threshold
        except ValueError:
            QMessageBox.warning(self, "警告", "亮度阈值必须是数字！")
            return
        
        # 🎯 同时保存当前下拉框选中的摄像头端口（即使未打开摄像头）
        port = self.camera_combo.currentData()
        if port is not None:
            self.detector.camera_port = port
        
        # 🎯 保存当前帧作为基准帧（用于循环测试中图像对比）
        if self.detector.current_frame is not None and len(self.detector.roi_list) > 0:
            self.detector.save_reference_frame()
        
        # 🎯 保存配置到文件（持久化）
        self.detector.save_config()
        
        # 发送配置更新信号
        settings = {
            "camera_port": self.detector.camera_port,
            "brightness_threshold": self.detector.brightness_threshold,
            "roi_count": len(self.detector.roi_list),
            "save_folder": self.detector.save_folder
        }
        self.settings_updated.emit(settings)
        
        # 🎯 关闭摄像头释放资源（accept 不会触发 closeEvent，必须手动释放）
        self.timer.stop()
        self.detector.close_camera()
        
        self.accept()
        
        # 显示保存成功提示 - 用相对路径显示
        display_path = os.path.join(".", "配置基准文件")
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle("成功")
        msg_box.setText(f"视觉设置已保存！\nROI数量: {len(self.detector.roi_list)}")
        msg_box.setInformativeText(f"保存路径: {display_path}")
        msg_box.setMinimumWidth(500)  # 设置最小宽度
        msg_box.exec()
    
    def closeEvent(self, event):
        """关闭对话框时自动保存配置 + 关闭摄像头"""
        # 🎯 自动保存阈值（点 X 关闭时也要持久化）
        try:
            threshold_text = self.threshold_input.text().strip()
            if threshold_text:
                threshold = int(threshold_text)
                self.detector.brightness_threshold = threshold
        except ValueError:
            print(f"[视觉] 阈值无效，跳过保存阈值")
        
        # 🎯 自动保存摄像头端口
        port = self.camera_combo.currentData()
        if port is not None:
            self.detector.camera_port = port
        
        # 🎯 如果有ROI且当前帧有图像，自动保存基准帧
        if self.detector.current_frame is not None and len(self.detector.roi_list) > 0:
            self.detector.save_reference_frame()
        
        # 🎯 自动持久化配置到 ITS_config.json
        self.detector.save_config()
        print(f"[视觉] 关闭窗口时自动保存配置完成")
        
        self.timer.stop()
        self.detector.close_camera()
        super().closeEvent(event)


# 测试用
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    dialog = VisualSettingDialog()
    dialog.exec()
    sys.exit(app.exec())
