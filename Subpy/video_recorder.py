import cv2
import os
import time
from datetime import datetime
import threading
import queue

class VideoRecorder:
    def __init__(self, test_folder_path, camera_index=0):
        self.test_folder_path = test_folder_path
        self.camera_index = camera_index
        self.video_folder = os.path.join(test_folder_path, "视频记录")
        
        self.cap = None
        self.writer = None
        self.is_recording = False
        self.record_thread = None
        self.current_file_path = None
        
        # 视频参数
        self.fps = 30.0
        self.frame_size = (640, 480)
        self.max_file_size = 50 * 1024 * 1024  # 50MB
        
        # 线程安全
        self.frame_queue = queue.Queue(maxsize=30)  # 帧队列，避免内存溢出
        self.lock = threading.Lock()  # 锁，保护共享资源
        
        # 确保视频文件夹存在
        os.makedirs(self.video_folder, exist_ok=True)
        
    def open_camera(self):
        """打开摄像头"""
        with self.lock:
            if self.cap and self.cap.isOpened():
                return True
                
            # 尝试多个索引
            for idx in [self.camera_index, 1, 0, 2, 3]:
                self.cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
                if self.cap.isOpened():
                    self.camera_index = idx
                    # 设置分辨率
                    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_size[0])
                    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_size[1])
                    # 设置缓冲区大小，减少延迟
                    self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)
                    print(f"[VideoRecorder] Camera opened: index={idx}")
                    return True
            
            print(f"[VideoRecorder] Cannot open camera")
            return False
    
    def close_camera(self):
        """关闭摄像头"""
        with self.lock:
            if self.cap:
                self.cap.release()
                self.cap = None
                print("[VideoRecorder] Camera closed")
    
    def start_recording(self):
        """开始录制视频"""
        with self.lock:
            if self.is_recording:
                print("[VideoRecorder] Already recording")
                return False
                
        if not self.open_camera():
            return False
            
        # 生成文件名：年月日时分秒.mp4
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.current_file_path = os.path.join(self.video_folder, f"{timestamp}.mp4")
        
        # 创建视频写入器 - 使用MP4格式，尝试更兼容的编码器
        # 先尝试 mp4v，如果不行就用 avc1 或 XVID
        fourcc_options = [
            cv2.VideoWriter_fourcc(*'mp4v'),
            cv2.VideoWriter_fourcc(*'avc1'),
            cv2.VideoWriter_fourcc(*'XVID'),
            cv2.VideoWriter_fourcc(*'MJPG')
        ]
        
        writer_opened = False
        for fourcc in fourcc_options:
            self.writer = cv2.VideoWriter(
                self.current_file_path,
                fourcc,
                self.fps,
                self.frame_size
            )
            if self.writer.isOpened():
                print(f"[VideoRecorder] Video writer opened with fourcc: {fourcc}")
                writer_opened = True
                break
            else:
                print(f"[VideoRecorder] Failed to open writer with fourcc: {fourcc}")
        
        if not writer_opened:
            print(f"[VideoRecorder] Cannot create video file: {self.current_file_path}")
            self.close_camera()
            return False
            
        self.is_recording = True
        
        # 清空队列
        while not self.frame_queue.empty():
            try:
                self.frame_queue.get_nowait()
            except:
                pass
        
        # 启动录制线程
        self.record_thread = threading.Thread(target=self._record_loop, daemon=True)
        self.record_thread.start()
        
        print(f"[VideoRecorder] Started recording: {self.current_file_path}")
        return True
    
    def _record_loop(self):
        """录制循环（在后台线程运行）"""
        current_file_size = 0
        current_writer = self.writer
        current_file_path = self.current_file_path
        
        # 最后成功写入的时间，用于检测写入失败
        last_successful_write = time.time()
        
        while self.is_recording:
            # 先检查是否应该退出
            if not self.is_recording:
                break
                
            # 捕获帧（加锁保护）
            with self.lock:
                if not self.cap or not self.cap.isOpened():
                    time.sleep(0.1)
                    continue
                    
                ret, frame = self.cap.read()
            
            if not ret:
                time.sleep(0.03)  # 30fps
                continue
                
            # 调整帧大小（确保与预期一致）
            try:
                if frame.shape[0] != self.frame_size[1] or frame.shape[1] != self.frame_size[0]:
                    frame = cv2.resize(frame, self.frame_size)
            except Exception as e:
                print(f"[VideoRecorder] Frame resize error: {e}")
                continue
                
            # 在视频帧上添加时间戳
            try:
                frame_with_timestamp = self._add_timestamp_to_frame(frame)
            except Exception as e:
                print(f"[VideoRecorder] Timestamp error: {e}")
                frame_with_timestamp = frame
            
            # 写入帧（捕获异常）
            try:
                if current_writer and current_writer.isOpened():
                    current_writer.write(frame_with_timestamp)
                    last_successful_write = time.time()
            except Exception as e:
                print(f"[VideoRecorder] Write frame error: {e}")
                # 如果写入失败超过2秒，尝试重新创建写入器
                if time.time() - last_successful_write > 2.0:
                    print(f"[VideoRecorder] Attempting to recover video writer...")
                    try:
                        if current_writer:
                            current_writer.release()
                    except:
                        pass
                    
                    # 尝试重新创建
                    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    new_file_path = os.path.join(self.video_folder, f"recovery_{timestamp}.mp4")
                    
                    for fourcc in [cv2.VideoWriter_fourcc(*'mp4v'), cv2.VideoWriter_fourcc(*'XVID')]:
                        new_writer = cv2.VideoWriter(
                            new_file_path,
                            fourcc,
                            self.fps,
                            self.frame_size
                        )
                        if new_writer.isOpened():
                            current_writer = new_writer
                            current_file_path = new_file_path
                            self.writer = current_writer
                            self.current_file_path = current_file_path
                            last_successful_write = time.time()
                            print(f"[VideoRecorder] Recovered to: {new_file_path}")
                            break
            
            # 检查文件大小
            try:
                if os.path.exists(current_file_path):
                    current_file_size = os.path.getsize(current_file_path)
                    
                    # 如果超过50MB，创建新文件
                    if current_file_size >= self.max_file_size:
                        print(f"[VideoRecorder] File reached 50MB, creating new file")
                        
                        # 关闭当前写入器
                        try:
                            current_writer.release()
                        except:
                            pass
                        
                        # 创建新文件
                        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                        current_file_path = os.path.join(self.video_folder, f"{timestamp}.mp4")
                        
                        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                        current_writer = cv2.VideoWriter(
                            current_file_path,
                            fourcc,
                            self.fps,
                            self.frame_size
                        )
                        
                        if current_writer.isOpened():
                            self.writer = current_writer
                            self.current_file_path = current_file_path
                            print(f"[VideoRecorder] Continue recording to: {current_file_path}")
                        else:
                            print(f"[VideoRecorder] Cannot create new video file")
                            break
            except Exception as e:
                print(f"[VideoRecorder] File size check error: {e}")
            
            # 控制帧率（约30fps）
            time.sleep(0.03)
    
    def _add_timestamp_to_frame(self, frame):
        """在视频帧上添加时间戳
        
        Args:
            frame: 原始视频帧
            
        Returns:
            添加了时间戳的视频帧
        """
        try:
            # 获取当前时间
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            
            # 设置字体和样式
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.7
            font_color = (0, 255, 0)  # 绿色
            thickness = 2
            line_type = cv2.LINE_AA
            
            # 获取文本大小
            text_size, _ = cv2.getTextSize(current_time, font, font_scale, thickness)
            
            # 计算位置（右下角，留出边距）
            margin = 10
            x = frame.shape[1] - text_size[0] - margin
            y = frame.shape[0] - margin
            
            # 添加黑色背景框，让文字更清晰
            background_x1 = x - 5
            background_y1 = y - text_size[1] - 5
            background_x2 = x + text_size[0] + 5
            background_y2 = y + 5
            cv2.rectangle(frame, (background_x1, background_y1), (background_x2, background_y2), (0, 0, 0), -1)
            
            # 添加时间戳文字
            cv2.putText(frame, current_time, (x, y), font, font_scale, font_color, thickness, line_type)
        except Exception as e:
            print(f"[VideoRecorder] Timestamp overlay error: {e}")
        
        return frame
    
    def stop_recording(self):
        """停止录制视频（不阻塞调用线程）"""
        print("[VideoRecorder] Stopping recording...")
        
        # 先标记停止，让录制线程退出
        with self.lock:
            if not self.is_recording:
                print("[VideoRecorder] Not recording")
                return False
            self.is_recording = False
            
            # 在锁内释放写入器（录制线程已标记停止，不会再用 writer）
            if self.writer:
                try:
                    self.writer.release()
                    print("[VideoRecorder] Video writer released")
                except Exception as e:
                    print(f"[VideoRecorder] Error releasing writer: {e}")
                self.writer = None
        
        # 录制线程是 daemon 的，设 is_recording=False 后会在下一帧检测到并退出
        if self.record_thread and self.record_thread.is_alive():
            print("[VideoRecorder] Record thread will exit on next iteration")
        
        # 关闭摄像头（在锁外执行，避免与 close_camera 自身锁冲突）
        self.close_camera()
        
        print(f"[VideoRecorder] Recording stopped")
        return True
    
    def is_active(self):
        """检查是否正在录制"""
        with self.lock:
            return self.is_recording
    
    def get_video_folder(self):
        """获取视频保存文件夹"""
        return self.video_folder


# 测试代码
if __name__ == "__main__":
    print("=== Video Recorder Test ===")
    print("1. Test simple recording")
    
    recorder = VideoRecorder(os.getcwd(), camera_index=1)
    
    print("Start recording 5 seconds...")
    recorder.start_recording()
    time.sleep(5)
    recorder.stop_recording()
    
    print(f"Video saved in: {recorder.get_video_folder()}")
    print("Test completed!")
