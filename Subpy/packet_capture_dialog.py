#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抓包工具对话框
用于SOME/IP协议抓包、监控和分析
"""

import sys
import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QSplitter, QTextEdit, QMessageBox, QFileDialog,
    QCheckBox, QLineEdit
)
from PySide6.QtCore import Qt, QTimer, Signal, QThread
from PySide6.QtGui import QIcon

from Subpy.packet_capture import PacketCapture, PacketInfo


class PacketCaptureDialog(QDialog):
    """抓包工具对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.capture = PacketCapture()
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_ui)
        
        self.init_ui()
        self._load_interfaces()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("SOME/IP抓包工具")
        self.setMinimumSize(1200, 800)
        
        # 设置窗口图标
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "image", "Car.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        main_layout = QVBoxLayout(self)
        
        # ========== 控制区 ==========
        control_group = QGroupBox("抓包控制")
        control_layout = QHBoxLayout()
        
        # 网络接口选择
        control_layout.addWidget(QLabel("网络接口:"))
        self.interface_combo = QComboBox()
        self.interface_combo.setMinimumWidth(200)
        control_layout.addWidget(self.interface_combo)
        
        # 过滤器
        control_layout.addWidget(QLabel("过滤器:"))
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("BPF过滤规则 (如: udp port 30490)")
        control_layout.addWidget(self.filter_edit)
        
        # 只显示SOME/IP
        self.someip_only_check = QCheckBox("只显示SOME/IP")
        self.someip_only_check.setChecked(True)
        control_layout.addWidget(self.someip_only_check)
        
        control_layout.addStretch()
        
        # 按钮
        self.start_btn = QPushButton("▶ 开始抓包")
        self.start_btn.clicked.connect(self.start_capture)
        control_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("⏹ 停止抓包")
        self.stop_btn.clicked.connect(self.stop_capture)
        self.stop_btn.setEnabled(False)
        control_layout.addWidget(self.stop_btn)
        
        self.clear_btn = QPushButton("🗑️ 清空")
        self.clear_btn.clicked.connect(self.clear_packets)
        control_layout.addWidget(self.clear_btn)
        
        self.save_btn = QPushButton("💾 保存")
        self.save_btn.clicked.connect(self.save_packets)
        control_layout.addWidget(self.save_btn)
        
        control_group.setLayout(control_layout)
        main_layout.addWidget(control_group)
        
        # ========== 状态区 ==========
        status_layout = QHBoxLayout()
        self.status_label = QLabel("就绪")
        self.packet_count_label = QLabel("包数: 0")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.packet_count_label)
        main_layout.addLayout(status_layout)
        
        # ========== 包列表 ==========
        packet_group = QGroupBox("数据包列表")
        packet_layout = QVBoxLayout()
        
        self.packet_table = QTableWidget()
        self.packet_table.setColumnCount(7)
        self.packet_table.setHorizontalHeaderLabels([
            "时间", "源地址", "目标地址", "协议", "长度", "是否SOME/IP", "摘要"
        ])
        self.packet_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.packet_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.packet_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.packet_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.packet_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.packet_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.packet_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Stretch)
        self.packet_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.packet_table.setAlternatingRowColors(True)
        self.packet_table.itemSelectionChanged.connect(self._on_packet_selected)
        packet_layout.addWidget(self.packet_table)
        
        packet_group.setLayout(packet_layout)
        
        # ========== 详情区 ==========
        detail_group = QGroupBox("数据包详情")
        detail_layout = QVBoxLayout()
        
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setMaximumHeight(300)
        detail_layout.addWidget(self.detail_text)
        
        detail_group.setLayout(detail_layout)
        
        # ========== 分割器 ==========
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(packet_group)
        splitter.addWidget(detail_group)
        splitter.setStretchFactor(0, 7)
        splitter.setStretchFactor(1, 3)
        
        main_layout.addWidget(splitter)
    
    def _load_interfaces(self):
        """加载网络接口列表"""
        interfaces = self.capture.get_interfaces()
        self.interface_combo.clear()
        
        if interfaces:
            self.interface_combo.addItems(interfaces)
        else:
            self.interface_combo.addItem("未找到网络接口")
            self.start_btn.setEnabled(False)
    
    def start_capture(self):
        """开始抓包"""
        interface = self.interface_combo.currentText()
        if not interface or interface == "未找到网络接口":
            QMessageBox.warning(self, "提示", "请选择有效的网络接口")
            return
        
        filter_str = self.filter_edit.text().strip()
        success = self.capture.start_capture(interface, filter_str)
        
        if success:
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.interface_combo.setEnabled(False)
            self.filter_edit.setEnabled(False)
            self.status_label.setText("正在抓包...")
            
            # 开始UI更新定时器
            self.update_timer.start(100)  # 100ms更新一次
    
    def stop_capture(self):
        """停止抓包"""
        self.capture.stop_capture()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.interface_combo.setEnabled(True)
        self.filter_edit.setEnabled(True)
        self.status_label.setText("已停止")
        self.update_timer.stop()
    
    def clear_packets(self):
        """清空数据包"""
        self.capture.clear_packets()
        self.packet_table.setRowCount(0)
        self.detail_text.clear()
        self.packet_count_label.setText("包数: 0")
        self.status_label.setText("已清空")
    
    def save_packets(self):
        """保存数据包（TODO）"""
        # TODO: 实现保存为pcap格式
        QMessageBox.information(self, "提示", "保存功能开发中...")
    
    def _update_ui(self):
        """更新UI（定时器调用）"""
        packets = self.capture.get_packets()
        someip_only = self.someip_only_check.isChecked()
        
        # 过滤SOME/IP包
        if someip_only:
            packets = [p for p in packets if p.is_someip]
        
        # 更新包数显示
        self.packet_count_label.setText(f"包数: {len(packets)}")
        
        # 更新表格（只在数量变化时）
        current_rows = self.packet_table.rowCount()
        if len(packets) > current_rows:
            # 添加新包
            for i in range(current_rows, len(packets)):
                self._add_packet_to_table(packets[i], i)
    
    def _add_packet_to_table(self, packet: PacketInfo, row: int):
        """添加数据包到表格"""
        self.packet_table.insertRow(row)
        
        info = packet.to_dict()
        
        # 设置单元格
        self.packet_table.setItem(row, 0, QTableWidgetItem(info['timestamp']))
        self.packet_table.setItem(row, 1, QTableWidgetItem(f"{info['source_ip']}:{info['source_port']}"))
        self.packet_table.setItem(row, 2, QTableWidgetItem(f"{info['dest_ip']}:{info['dest_port']}"))
        self.packet_table.setItem(row, 3, QTableWidgetItem(info['protocol']))
        self.packet_table.setItem(row, 4, QTableWidgetItem(str(info['length'])))
        self.packet_table.setItem(row, 5, QTableWidgetItem("✅" if info['is_someip'] else "❌"))
        self.packet_table.setItem(row, 6, QTableWidgetItem(info['summary']))
        
        # 设置背景色
        if info['is_someip']:
            for col in range(7):
                item = self.packet_table.item(row, col)
                if item:
                    item.setBackground(Qt.lightGray)
        
        # 滚动到最新
        self.packet_table.scrollToBottom()
    
    def _on_packet_selected(self):
        """选中数据包时显示详情"""
        selected_rows = self.packet_table.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        packets = self.capture.get_packets()
        someip_only = self.someip_only_check.isChecked()
        
        if someip_only:
            packets = self.capture.get_someip_packets()
        
        if row < len(packets):
            packet = packets[row]
            self._show_packet_detail(packet)
    
    def _show_packet_detail(self, packet: PacketInfo):
        """显示数据包详情"""
        info = packet.to_dict()
        
        detail = f"数据包详情\n{'='*60}\n"
        detail += f"时间: {info['timestamp']}\n"
        detail += f"源: {info['source_ip']}:{info['source_port']}\n"
        detail += f"目标: {info['dest_ip']}:{info['dest_port']}\n"
        detail += f"协议: {info['protocol']}\n"
        detail += f"长度: {info['length']} 字节\n"
        
        if info['is_someip'] and info['someip_info']:
            detail += f"\n{'='*60}\n"
            detail += "SOME/IP信息\n"
            detail += f"{'='*60}\n"
            detail += f"有Payload: {'是' if info['someip_info'].get('has_payload', False) else '否'}\n"
            detail += f"Payload长度: {info['someip_info'].get('payload_length', 0)} 字节\n"
        
        detail += f"\n{'='*60}\n"
        detail += "原始数据 (HEX)\n"
        detail += f"{'='*60}\n"
        detail += self._format_hex(packet.raw_data)
        
        self.detail_text.setText(detail)
    
    def _format_hex(self, data: bytes) -> str:
        """格式化HEX显示"""
        lines = []
        for i in range(0, len(data), 16):
            chunk = data[i:i+16]
            hex_part = ' '.join(f'{b:02X}' for b in chunk)
            ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
            lines.append(f"{i:04X}  {hex_part:<48}  {ascii_part}")
        return '\n'.join(lines)
    
    def closeEvent(self, event):
        """关闭窗口时停止抓包"""
        self.stop_capture()
        self.update_timer.stop()
        super().closeEvent(event)
