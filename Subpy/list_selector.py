import sys
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QLabel,
    QLineEdit,
)
from PySide6.QtCore import Qt


class ListSelector(QWidget):
    """左右列表选择器。"""

    def __init__(self, left_items=None, insert_after_selected_right=False):
        super().__init__()
        self.all_items = []
        self.numbered_repeat_items = set()
        self.insert_after_selected_right = insert_after_selected_right
        self.init_ui()

        if left_items:
            self.all_items = left_items.copy()
            self.left_list.addItems(left_items)
            self.update_labels()

    def update_labels(self):
        """更新左右列表数量标签。"""
        left_count = self.left_list.count()
        right_count = self.right_list.count()
        platform = getattr(self, "vehicle_platform", "")
        label_prefix = f"{platform}可选指令" if platform else "可选项指令"
        self.left_label.setText(f"{label_prefix} (共{left_count}项)")
        self.right_label.setText(f"已选项指令 (共{right_count}项)")

    def _make_right_widget(self, text, keep_scene=False):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(4, 1, 4, 1)
        layout.setSpacing(6)

        label = QLabel(str(text))
        # 让标签区域的单击交给列表处理，保证整行都能正常选中。
        label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        checkbox = QCheckBox()
        checkbox.setChecked(bool(keep_scene))

        layout.addWidget(label, 1)
        layout.addWidget(checkbox, 0, Qt.AlignRight)
        return widget

    def _insert_right_item(self, row, text, keep_scene=False):
        item = QListWidgetItem()
        item.setData(Qt.UserRole, str(text))
        widget = self._make_right_widget(text, keep_scene)
        item.setSizeHint(widget.sizeHint())
        if row is None or row < 0 or row >= self.right_list.count():
            self.right_list.addItem(item)
        else:
            self.right_list.insertItem(row, item)
        self.right_list.setItemWidget(item, widget)
        return item

    def _right_item_text(self, row_or_item):
        item = row_or_item
        if isinstance(row_or_item, int):
            item = self.right_list.item(row_or_item)
        if item is None:
            return ""
        return str(item.data(Qt.UserRole) or "")

    def _right_item_keep_scene(self, row_or_item):
        item = row_or_item
        if isinstance(row_or_item, int):
            item = self.right_list.item(row_or_item)
        if item is None:
            return False
        widget = self.right_list.itemWidget(item)
        checkbox = widget.findChild(QCheckBox) if widget else None
        return bool(checkbox and checkbox.isChecked())

    def set_numbered_repeat_items(self, items):
        """设置需要在右侧按出现顺序自动编号的可重复指令。"""
        self.numbered_repeat_items = {
            str(item).strip() for item in (items or []) if str(item).strip()
        }
        self._renumber_repeat_items()

    def _numbered_repeat_base(self, text):
        text = str(text or "").strip()
        for base in self.numbered_repeat_items:
            if text == base:
                return base
            if text.startswith(f"{base} "):
                suffix = text[len(base):].strip()
                if suffix.isdigit() and int(suffix) > 0:
                    return base
        return ""

    def _set_right_item_text(self, row, text):
        item = self.right_list.item(row)
        if item is None:
            return
        item.setData(Qt.UserRole, str(text))
        widget = self.right_list.itemWidget(item)
        label = widget.findChild(QLabel) if widget else None
        if label:
            label.setText(str(text))
            item.setSizeHint(widget.sizeHint())

    def _renumber_repeat_items(self):
        counters = {base: 0 for base in self.numbered_repeat_items}
        for row in range(self.right_list.count()):
            base = self._numbered_repeat_base(self._right_item_text(row))
            if not base:
                continue
            counters[base] += 1
            self._set_right_item_text(row, f"{base} {counters[base]}")

    def _numbered_right_text(self, text):
        base = self._numbered_repeat_base(text)
        if not base:
            return str(text)
        count = sum(
            1
            for row in range(self.right_list.count())
            if self._numbered_repeat_base(self._right_item_text(row)) == base
        )
        return f"{base} {count + 1}"

    def set_vehicle_platform(self, platform):
        """设置左侧可选指令的平台显示名称。"""
        platform = str(platform or "").strip()
        self.vehicle_platform = platform if platform in ("8295", "8797") else ""
        self.update_labels()

    def add_left_items(self, items):
        """动态刷新左侧列表。"""
        if isinstance(items, list):
            self.all_items = items.copy()
            self.left_list.clear()
            self.left_list.addItems(items)
            self.update_labels()

    def init_ui(self):
        self.setWindowTitle("选项选择器")
        self.setGeometry(100, 100, 500, 300)

        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        left_layout = QVBoxLayout()
        self.left_label = QLabel("可选项指令")
        left_layout.addWidget(self.left_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入关键字筛选...")
        self.search_input.textChanged.connect(self.filter_items)
        left_layout.addWidget(self.search_input)

        self.left_list = QListWidget()
        self.left_list.setMinimumSize(80, 200)
        self.left_list.setSelectionMode(QListWidget.ExtendedSelection)
        left_layout.addWidget(self.left_list)
        main_layout.addLayout(left_layout)

        btn_layout = QVBoxLayout()
        btn_layout.addStretch()

        btn_width = 80
        btn_height = 25

        self.btn_add = QPushButton("添加 →")
        self.btn_add.setMinimumSize(btn_width, btn_height)
        self.btn_add.clicked.connect(self.add_selected)
        btn_layout.addWidget(self.btn_add)

        self.btn_add_all = QPushButton("全部添加 →")
        self.btn_add_all.setMinimumSize(btn_width, btn_height)
        self.btn_add_all.clicked.connect(self.add_all)
        btn_layout.addWidget(self.btn_add_all)

        btn_layout.addSpacing(20)

        self.btn_remove = QPushButton("← 删除")
        self.btn_remove.setMinimumSize(btn_width, btn_height)
        self.btn_remove.clicked.connect(self.remove_selected)
        btn_layout.addWidget(self.btn_remove)

        self.btn_remove_all = QPushButton("← 全部删除")
        self.btn_remove_all.setMinimumSize(btn_width, btn_height)
        self.btn_remove_all.clicked.connect(self.remove_all)
        btn_layout.addWidget(self.btn_remove_all)

        btn_layout.addSpacing(20)

        self.btn_up = QPushButton("↑ 上移")
        self.btn_up.setMinimumSize(btn_width, btn_height)
        self.btn_up.clicked.connect(self.move_up)
        btn_layout.addWidget(self.btn_up)

        self.btn_down = QPushButton("↓ 下移")
        self.btn_down.setMinimumSize(btn_width, btn_height)
        self.btn_down.clicked.connect(self.move_down)
        btn_layout.addWidget(self.btn_down)

        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        right_layout = QVBoxLayout()
        self.right_label = QLabel("已选项指令")
        right_layout.addWidget(self.right_label)

        self.right_list = QListWidget()
        self.right_list.setMinimumSize(80, 200)
        self.right_list.setSelectionMode(QListWidget.ExtendedSelection)
        right_layout.addWidget(self.right_list)
        main_layout.addLayout(right_layout)

        self.update_labels()

    def set_insert_after_selected_right(self, enabled=True):
        self.insert_after_selected_right = enabled

    def _get_right_insert_row(self):
        """返回插入位置对应的右侧行号。"""
        current_row = self.right_list.currentRow()
        if current_row >= 0:
            return current_row

        selected_right_items = self.right_list.selectedItems()
        if selected_right_items:
            return self.right_list.row(selected_right_items[0])

        return -1

    def add_selected(self):
        """把左侧选中项加入右侧。"""
        items = self.left_list.selectedItems()
        if not items:
            self.update_labels()
            return

        insert_row = self._get_right_insert_row() if self.insert_after_selected_right else -1
        last_row = -1

        for item in items:
            right_text = self._numbered_right_text(item.text())
            if insert_row >= 0:
                insert_row += 1
                self._insert_right_item(insert_row, right_text)
                last_row = insert_row
            else:
                self._insert_right_item(-1, right_text)
                last_row = self.right_list.count() - 1

        self._renumber_repeat_items()

        if last_row >= 0:
            self.right_list.setCurrentRow(last_row)

        self.update_labels()

    def add_all(self):
        """把左侧全部项加入右侧。"""
        for i in range(self.left_list.count()):
            item = self.left_list.item(i)
            self._insert_right_item(-1, self._numbered_right_text(item.text()))
        self._renumber_repeat_items()
        self.update_labels()

    def remove_selected(self):
        """删除右侧选中项。"""
        rows = sorted({self.right_list.row(item) for item in self.right_list.selectedItems()}, reverse=True)
        for row in rows:
            self.right_list.takeItem(row)
        self._renumber_repeat_items()
        self.update_labels()

    def remove_all(self):
        """清空右侧全部项。"""
        self.right_list.clear()
        self.update_labels()

    def move_up(self):
        """选中项上移。"""
        current_row = self.right_list.currentRow()
        if current_row > 0:
            text = self._right_item_text(current_row)
            keep_scene = self._right_item_keep_scene(current_row)
            self.right_list.takeItem(current_row)
            self._insert_right_item(current_row - 1, text, keep_scene)
            self._renumber_repeat_items()
            self.right_list.setCurrentRow(current_row - 1)
        self.update_labels()

    def move_down(self):
        """选中项下移。"""
        current_row = self.right_list.currentRow()
        if current_row >= 0 and current_row < self.right_list.count() - 1:
            text = self._right_item_text(current_row)
            keep_scene = self._right_item_keep_scene(current_row)
            self.right_list.takeItem(current_row)
            self._insert_right_item(current_row + 1, text, keep_scene)
            self._renumber_repeat_items()
            self.right_list.setCurrentRow(current_row + 1)
        self.update_labels()

    def get_selected_items(self):
        """获取右侧所有已选项列表。"""
        return [self._right_item_text(i) for i in range(self.right_list.count())]

    def get_keep_scene_items(self):
        """获取已勾选失败暂停的指令名称。"""
        return [
            self._right_item_text(i)
            for i in range(self.right_list.count())
            if self._right_item_keep_scene(i)
        ]

    def set_keep_scene_items(self, items):
        """设置已勾选失败暂停的指令名称。"""
        keep_scene_items = {str(item) for item in (items or [])}
        for i in range(self.right_list.count()):
            item = self.right_list.item(i)
            widget = self.right_list.itemWidget(item)
            checkbox = widget.findChild(QCheckBox) if widget else None
            if checkbox:
                checkbox.setChecked(self._right_item_text(i) in keep_scene_items)

    def set_selected_items(self, items):
        """设置右侧已选项，用于恢复保存的内容。"""
        self.right_list.clear()
        if isinstance(items, list) and items:
            available_items = set(self.all_items)
            for item in items:
                text = str(item).strip()
                base = self._numbered_repeat_base(text)
                if text in available_items or base in available_items:
                    self._insert_right_item(-1, self._numbered_right_text(text))
            self._renumber_repeat_items()
        self.update_labels()

    def filter_items(self):
        """根据输入的关键字筛选左侧列表。"""
        search_text = self.search_input.text().strip().lower()

        self.left_list.clear()
        if not search_text:
            self.left_list.addItems(self.all_items)
        else:
            for item in self.all_items:
                if search_text in item.lower():
                    self.left_list.addItem(item)
        self.update_labels()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    items = ["功能1", "功能2", "功能3", "功能4", "功能5", "功能6"]
    selector = ListSelector(left_items=items)
    selector.show()
    sys.exit(app.exec())
