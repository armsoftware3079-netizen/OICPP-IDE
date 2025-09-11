import sys
import configparser
import os
import sys
import shutil
import tempfile
import subprocess
import time
from PyQt6.QtWidgets import QApplication, QMainWindow, QMenu, QDialog, QVBoxLayout, QTextEdit, QPushButton, QFontDialog, QHBoxLayout, QLabel, QGroupBox, QComboBox, QScrollArea, QGridLayout, QCheckBox, QSpinBox, QLineEdit, QMessageBox, QWidget, QSplitter, QTreeWidget, QTreeWidgetItem, QFileDialog, QTabWidget, QSizePolicy
from PyQt6.QtGui import QScreen, QFont, QPainter, QColor, QBrush, QPen, QPixmap, QIcon
from PyQt6.QtCore import Qt, QRectF, QProcess, QTimer
from PyQt6.Qsci import QsciScintilla, QsciLexerCPP, QsciStyle
try:
    from PyQt6.QtGui import QAction
except ImportError:
    from PyQt6.QtWidgets import QAction
current_font = None
class CppCodeEditor(QsciScintilla):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setUtf8(True)
        self.setAutoIndent(True)
        self.setTabWidth(4)
        self.setIndentationsUseTabs(False)
        self.setIndentationWidth(4)
        font = QFont("Consolas")
        font.setPointSize(12)
        self.setFont(font)
        self.lexer = QsciLexerCPP()
        self.lexer.setFont(font)
        self.setLexer(self.lexer)
        self.setPaper(QColor("#1e1e1e"))
        self.setColor(QColor("#d4d4d4"))
        self._init_line_numbers()
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Backspace:
            line, pos = self.getCursorPosition()
            line_text = self.text(line)
            if pos >= 4:
                prev_chars = line_text[pos-4:pos]
                if prev_chars == '    ':
                    self.setSelection(line, pos-4, line, pos)
                    self.removeSelectedText()
                    self.setCursorPosition(line, pos-4)
                    return
        super().keyPressEvent(event)
    def _init_line_numbers(self):
        preferences = font_manager.load_preferences()
        show_line_numbers = preferences.get("display", {}).get("show_line_numbers", "true").lower() == "true"
        self.set_line_numbers_visibility(show_line_numbers)
    def set_line_numbers_visibility(self, visible):
        if visible:
            self.setMarginType(0, QsciScintilla.MarginType.NumberMargin)
            self.setMarginWidth(0, "000")
        else:
            self.setMarginWidth(0, 0)
    def apply_theme(self, theme_mode):
        if theme_mode == "light":
            self.setPaper(QColor("#ffffff"))
            self.setColor(QColor("#000000"))
            self.lexer.setColor(QColor("#0000ff"), 1)
            self.lexer.setColor(QColor("#2b91af"), 2)
            self.lexer.setColor(QColor("#a31515"), 3)
            self.lexer.setColor(QColor("#0451a5"), 4)
            self.lexer.setColor(QColor("#098658"), 5)
            self.SendScintilla(self.SCI_STYLESETBACK, 32, 0xffffff)
            self.setMarginsBackgroundColor(QColor("#f0f0f0"))
            self.setMarginsForegroundColor(QColor("#000000"))
        else:
            self.setPaper(QColor("#1e1e1e"))
            self.setColor(QColor("#d4d4d4"))
            self.lexer.setColor(QColor("#569cd6"), 1)
            self.lexer.setColor(QColor("#4ec9b0"), 2)
            self.lexer.setColor(QColor("#ce9178"), 3)
            self.lexer.setColor(QColor("#6a9955"), 4)
            self.lexer.setColor(QColor("#b5cea8"), 5)
            self.SendScintilla(self.SCI_STYLESETBACK, 32, 0x1e1e1e)
            self.setMarginsBackgroundColor(QColor("#2d2d2d"))
            self.setMarginsForegroundColor(QColor("#cccccc"))
        self.setLexer(self.lexer)
        self.repaint()
class FontConfigManager:
    def __init__(self):
        self.ini_path = os.path.join("userdata", "config", "prop.ini")
        self.config = configparser.ConfigParser()
        os.makedirs(os.path.dirname(self.ini_path), exist_ok=True)
    def load_font(self):
        try:
            self.config.read(self.ini_path)
            if "Font" in self.config and "family" in self.config["Font"]:
                font = QFont()
                font.setFamily(self.config["Font"]["family"])
                if "size" in self.config["Font"]:
                    font.setPointSize(int(self.config["Font"]["size"]))
                if "weight" in self.config["Font"]:
                    font.setWeight(int(self.config["Font"]["weight"]))
                if "italic" in self.config["Font"]:
                    font.setItalic(self.config["Font"]["italic"].lower() == "true")
                return font
            else:
                return QFont()
        except Exception as e:
            print(f"加载字体配置失败: {e}")
            return QFont()
    def save_font(self, font):
        try:
            self.config.read(self.ini_path)
            if "Font" not in self.config:
                self.config["Font"] = {}
            self.config["Font"]["family"] = font.family()
            self.config["Font"]["size"] = str(font.pointSize())
            self.config["Font"]["weight"] = str(font.weight())
            self.config["Font"]["italic"] = str(font.italic())
            with open(self.ini_path, 'w') as config_file:
                self.config.write(config_file)
            return True
        except Exception as e:
            print(f"保存字体配置失败: {e}")
            return False
    def load_theme(self):
        try:
            self.config.read(self.ini_path)
            if "Theme" in self.config and "mode" in self.config["Theme"]:
                return self.config["Theme"]["mode"]
            else:
                return "light"
        except Exception as e:
            print(f"加载主题配置失败: {e}")
            return "light"
    def save_theme(self, theme_mode):
        try:
            self.config.read(self.ini_path)
            if "Theme" not in self.config:
                self.config["Theme"] = {}
            self.config["Theme"]["mode"] = theme_mode
            with open(self.ini_path, 'w') as f:
                self.config.write(f)
            return True
        except Exception as e:
            print(f"保存主题配置失败: {e}")
            return False
    def load_preferences(self):
        try:
            self.config.read(self.ini_path)
            preferences = {}
            for section in self.config.sections():
                preferences[section] = {}
                for key, value in self.config[section].items():
                    preferences[section][key] = value
            return preferences
        except Exception as e:
            print(f"加载偏好设置失败: {e}")
            return {}
    def save_preferences(self, preferences):
        try:
            os.makedirs(os.path.dirname(self.ini_path), exist_ok=True)
            self.config.read(self.ini_path)
            for section, settings in preferences.items():
                if section not in self.config:
                    self.config[section] = {}
                for key, value in settings.items():
                    self.config[section][key] = value
            with open(self.ini_path, 'w') as f:
                self.config.write(f)
            print(f"成功保存偏好设置到 {self.ini_path}")
            return True
        except Exception as e:
            print(f"保存偏好设置失败: {e}")
            return False
            if "Theme" not in self.config:
                self.config["Theme"] = {}
            self.config["Theme"]["mode"] = theme_mode
            with open(self.ini_path, 'w') as config_file:
                self.config.write(config_file)
        except Exception:
            pass
    def save_preferences(self, preferences):
        try:
            self.config.read(self.ini_path)
            for section, options in preferences.items():
                if section not in self.config:
                    self.config[section] = {}
                for key, value in options.items():
                    self.config[section][key] = str(value)
            with open(self.ini_path, 'w') as config_file:
                self.config.write(config_file)
        except Exception:
            pass
font_manager = FontConfigManager()
class OutputWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("程序运行输出")
        self.setGeometry(100, 100, 800, 600)
        self.run_process = None
        self.timer_id = None
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        self.output_group = QGroupBox("Output")
        self.output_group.setMinimumHeight(400)
        self.output_panel = QTextEdit()
        self.output_panel.setReadOnly(True)
        self.output_panel.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        output_group_layout = QVBoxLayout()
        output_group_layout.addWidget(self.output_panel)
        self.output_group.setLayout(output_group_layout)
        main_layout.addWidget(self.output_group)
        self.input_group = QGroupBox("Input")
        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("输入内容并按Enter发送...")
        self.input_line.setEnabled(False)
        self.input_line.returnPressed.connect(self._send_input)
        input_group_layout = QVBoxLayout()
        input_group_layout.addWidget(self.input_line)
        self.input_group.setLayout(input_group_layout)
        main_layout.addWidget(self.input_group)
        self.apply_theme()
    def apply_theme(self, theme_mode=None):
        if theme_mode is None:
            theme = font_manager.load_theme()
        else:
            theme = theme_mode
        if theme == "dark":
            self.setStyleSheet("background-color: #2d2d2d;")
            self.output_group.setStyleSheet(
                "QGroupBox { color: #ffffff; border: 1px solid #555555; border-radius: 4px; margin-top: 10px; }"
                "QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px; }"
            )
            self.input_group.setStyleSheet(
                "QGroupBox { color: #ffffff; border: 1px solid #555555; border-radius: 4px; margin-top: 10px; }"
                "QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px; }"
            )
            self.output_panel.setStyleSheet("background-color: #1e1e1e; color: #ffffff; border: 1px solid #555555;")
            self.input_line.setStyleSheet("background-color: #3c3c3c; color: #ffffff; border: 1px solid #555555;")
        else:
            self.setStyleSheet("background-color: #f0f0f0;")
            self.output_group.setStyleSheet(
                "QGroupBox { color: #000000; border: 1px solid #cccccc; border-radius: 4px; margin-top: 10px; }"
                "QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px; }"
            )
            self.input_group.setStyleSheet(
                "QGroupBox { color: #000000; border: 1px solid #cccccc; border-radius: 4px; margin-top: 10px; }"
                "QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px; }"
            )
            self.output_panel.setStyleSheet("background-color: #ffffff; color: #000000; border: 1px solid #cccccc;")
            self.input_line.setStyleSheet("background-color: #ffffff; color: #000000; border: 1px solid #cccccc;")
    def append_output(self, text):
        self.output_panel.append(text)
        self.output_panel.verticalScrollBar().setValue(self.output_panel.verticalScrollBar().maximum())
    def _send_input(self):
        if self.run_process and self.run_process.state() == QProcess.ProcessState.Running:
            input_text = self.input_line.text() + '\n'
            self.output_panel.append(f'> {input_text.rstrip()}')
            self.run_process.write(input_text.encode())
            self.input_line.clear()
            self.output_panel.verticalScrollBar().setValue(self.output_panel.verticalScrollBar().maximum())
    def timerEvent(self, event):
        if hasattr(self, 'timer_id') and event.timerId() == self.timer_id:
            if self.run_process and self.run_process.state() == QProcess.ProcessState.Running:
                self.output_panel.append("\n[运行超时] 程序运行时间超过10秒，已终止。")
                self.run_process.kill()
                self.input_line.setEnabled(False)
                if self.parent:
                    self.parent._cleanup_temp_files()
            delattr(self, 'timer_id')
        super().timerEvent(event)
class RoundedButton(QPushButton):
    def __init__(self, text, parent=None, gradient=False):
        super().__init__(text, parent)
        self.setMinimumHeight(30)
        current_theme = font_manager.load_theme()
        self.apply_theme(current_theme, gradient)
    def apply_theme(self, theme_mode, gradient=False):
        if gradient:
            if theme_mode == "dark":
                self.setStyleSheet(
                )
            else:
                self.setStyleSheet(
                )
        else:
            if theme_mode == "dark":
                self.setStyleSheet(
                )
            else:
                self.setStyleSheet(
                )
class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        if current_font:
            self.setFont(current_font)
        self.setWindowTitle("Help")
        icon_path = os.path.join("res", "img", "icon", "icon2.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.resize(600, 500)
        self.setSizeGripEnabled(True)
        layout = QVBoxLayout(self)
        from PyQt6.QtWidgets import QTabWidget
        self.tab_widget = QTabWidget()
        start_tab = QWidget()
        start_layout = QVBoxLayout(start_tab)
        start_text_edit = QTextEdit()
        start_text_edit.setReadOnly(True)
        start_text_edit.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        start_text_edit.setStyleSheet("background-color: #333333; color: #FFFFFF; border: none;")
        if current_font:
            start_text_edit.setFont(current_font)
        start_text_edit.setText()
        start_layout.addWidget(start_text_edit)
        self.tab_widget.addTab(start_tab, "Start")
        help_tab = QWidget()
        help_layout = QVBoxLayout(help_tab)
        help_text_edit = QTextEdit()
        help_text_edit.setReadOnly(True)
        help_text_edit.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        help_text_edit.setStyleSheet("background-color: #333333; color: #FFFFFF; border: none;")
        if current_font:
            help_text_edit.setFont(current_font)
        help_text_edit.setText()
        help_layout.addWidget(help_text_edit)
        self.tab_widget.addTab(help_tab, "Help")
        advance_tab = QWidget()
        advance_layout = QVBoxLayout(advance_tab)
        advance_text_edit = QTextEdit()
        advance_text_edit.setReadOnly(True)
        advance_text_edit.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        advance_text_edit.setStyleSheet("background-color: #333333; color: #FFFFFF; border: none;")
        if current_font:
            advance_text_edit.setFont(current_font)
        advance_text_edit.setText()
        advance_layout.addWidget(advance_text_edit)
        self.tab_widget.addTab(advance_tab, "Advance")
        layout.addWidget(self.tab_widget)
    def resizeEvent(self, event):
        super().resizeEvent(event)
        current_theme = font_manager.load_theme()
        self.apply_theme(current_theme)
    def apply_theme(self, theme_mode):
        if theme_mode == "light":
            self.setStyleSheet("background-color: #f0f0f0; color: #000000;")
            for text_edit in self.findChildren(QTextEdit):
                text_edit.setStyleSheet("background-color: #e0e0e0; color: #000000; border: none;")
            self.tab_widget.setStyleSheet(
                "QTabWidget::pane { background-color: #f0f0f0; border: 1px solid #cccccc; }"
                "QTabBar::tab { background-color: #e0e0e0; color: #000000; padding: 8px; }"
                "QTabBar::tab:selected { background-color: #f0f0f0; border-bottom: 2px solid #818CF8; }"
            )
        else:
            self.setStyleSheet("background-color: #2d2d2d; color: #ffffff;")
            for text_edit in self.findChildren(QTextEdit):
                text_edit.setStyleSheet("background-color: #333333; color: #ffffff; border: none;")
            self.tab_widget.setStyleSheet(
                "QTabWidget::pane { background-color: #2d2d2d; border: 1px solid #444444; }"
                "QTabBar::tab { background-color: #333333; color: #ffffff; padding: 8px; }"
                "QTabBar::tab:selected { background-color: #2d2d2d; border-bottom: 2px solid #60A5FA; }"
            )
class InfoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        if current_font:
            self.setFont(current_font)
        self.setWindowTitle("Info")
        icon_path = os.path.join("res", "img", "icon", "icon2.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.resize(400, 400)
        layout = QVBoxLayout(self)
        info_group_box = QGroupBox("Info")
        group_box_layout = QVBoxLayout()
        self.image_label = QLabel()
        image_path = os.path.join("res", "img", "icon", "icon.png")
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            scaled_pixmap = pixmap.scaled(140, 140, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)
            self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        group_box_layout.addWidget(self.image_label)
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.text_edit.setStyleSheet("background-color: #333333; color: #FFFFFF; border: none;")
        if current_font:
            self.text_edit.setFont(current_font)
        self.text_edit.setText()
        group_box_layout.addWidget(self.text_edit)
        info_group_box.setLayout(group_box_layout)
        layout.addWidget(info_group_box)
        self.setLayout(layout)
        current_theme = font_manager.load_theme()
        self.apply_theme(current_theme)
    def closeEvent(self, event):
        if self.parent():
            if hasattr(self.parent(), 'update_editor_settings'):
                self.parent().update_editor_settings()
            if hasattr(self.parent(), '_load_saved_font'):
                self.parent()._load_saved_font()
            if hasattr(self.parent(), 'apply_theme'):
                current_theme = font_manager.load_theme()
                self.parent().apply_theme(current_theme)
        super().closeEvent(event)
    def update_editor_settings(self):
        if hasattr(self, 'code_editor'):
            preferences = font_manager.load_preferences()
            show_line_numbers = preferences.get("display", {}).get("show_line_numbers", "true").lower() == "true"
            self.code_editor.set_line_numbers_visibility(show_line_numbers)
    def resizeEvent(self, event):
        super().resizeEvent(event)
    def apply_theme(self, theme_mode):
        if theme_mode == "light":
            self.setStyleSheet("background-color: #f0f0f0; color: #000000;")
            if hasattr(self, 'findChild'):
                info_group_box = self.findChild(QGroupBox, "")
                if info_group_box:
                    info_group_box.setStyleSheet("QGroupBox { color: #000000; }")
            if hasattr(self, 'text_edit'):
                self.text_edit.setStyleSheet("background-color: #e0e0e0; color: #000000; border: none;")
        else:
            self.setStyleSheet("background-color: #2d2d2d; color: #ffffff;")
            if hasattr(self, 'findChild'):
                info_group_box = self.findChild(QGroupBox, "")
                if info_group_box:
                    info_group_box.setStyleSheet("QGroupBox { color: #ffffff; }")
            if hasattr(self, 'text_edit'):
                self.text_edit.setStyleSheet("background-color: #333333; color: #ffffff; border: none;")
class UIConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        if current_font:
            self.setFont(current_font)
        self.setWindowTitle("UI Config")
        icon_path = os.path.join("res", "img", "icon", "icon2.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.setFixedSize(500, 300)
        main_layout = QVBoxLayout(self)
        font_group_box = QGroupBox("Font")
        group_box_layout = QVBoxLayout()
        ide_group_box = QGroupBox("IDE")
        ide_group_box.setMinimumHeight(60)
        ide_group_box.setMaximumHeight(90)
        button_layout = QHBoxLayout()
        self.font_button = RoundedButton("更改编辑器字体", self, gradient=True)
        self.font_button.clicked.connect(self._change_font)
        if current_font:
            self.font_button.setFont(current_font)
        button_layout.addWidget(self.font_button)
        self.preferences_button = RoundedButton("编辑偏好项", self, gradient=True)
        self.preferences_button.clicked.connect(self._show_preferences_dialog)
        if current_font:
            self.preferences_button.setFont(current_font)
        button_layout.addWidget(self.preferences_button)
        button_layout.addStretch()
        ide_group_box.setLayout(button_layout)
        group_box_layout.addWidget(ide_group_box)
        theme_group_box = QGroupBox("Theme")
        theme_group_box.setMinimumHeight(60)
        theme_group_box.setMaximumHeight(90)
        theme_layout = QHBoxLayout()
        theme_label = QLabel("选择主题:")
        if current_font:
            theme_label.setFont(current_font)
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("浅色（渐变）")
        self.theme_combo.addItem("深色（渐变）")
        if current_font:
            self.theme_combo.setFont(current_font)
        current_theme = font_manager.load_theme()
        if current_theme == "light":
            self.theme_combo.setCurrentIndex(0)
        else:
            self.theme_combo.setCurrentIndex(1)
        self.theme_combo.currentIndexChanged.connect(self._change_theme)
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        theme_info_label = QLabel("当前主题信息:")
        if current_font:
            theme_info_label.setFont(current_font)
        self.theme_info_edit = QLineEdit()
        self.theme_info_edit.setReadOnly(True)
        if current_font:
            self.theme_info_edit.setFont(current_font)
        self._update_theme_info(current_theme)
        theme_info_layout = QHBoxLayout()
        theme_info_layout.addWidget(theme_info_label)
        theme_info_layout.addWidget(self.theme_info_edit)
        theme_vlayout = QVBoxLayout()
        theme_vlayout.addLayout(theme_layout)
        theme_vlayout.addLayout(theme_info_layout)
        theme_group_box.setLayout(theme_vlayout)
        theme_group_box.setMinimumHeight(100)
        theme_group_box.setMaximumHeight(130)
        group_box_layout.addWidget(theme_group_box)
        group_box_layout.addStretch()
        font_group_box.setLayout(group_box_layout)
        main_layout.addWidget(font_group_box)
        self.setLayout(main_layout)
        self.apply_theme(current_theme)
    def _setup_background(self):
        self.background_label = QLabel(self)
        self.background_label.setObjectName("backgroundLabel")
        self.background_label.setScaledContents(True)
        self.background_label.lower()
        pixmap = QPixmap(r"res\img\background\dark\darkspace.PNG")
        self.background_label.setPixmap(pixmap)
        self.background_label.setGeometry(0, 0, self.width(), self.height())
    def _change_font(self):
        global current_font
        initial_font = QFont()
        font, ok = QFontDialog.getFont(initial_font, self, "选择字体")
        if ok:
            self.font_button.setFont(font)
            font_manager.save_font(font)
            current_font = font
            if self.parent():
                self.parent().update_fonts(font)
    def _change_theme(self, index):
        theme_mode = "light" if index == 0 else "dark"
        font_manager.save_theme(theme_mode)
        self._update_theme_info(theme_mode)
        self.apply_theme(theme_mode)
        if self.parent():
            self.parent().apply_theme(theme_mode)
    def _update_theme_info(self, theme_mode):
        if hasattr(self, 'theme_info_edit'):
            if theme_mode == "light":
                self.theme_info_edit.setText("浅色主题 - 渐变效果")
            else:
                self.theme_info_edit.setText("深色主题 - 渐变效果")
    def _show_preferences_dialog(self):
        preferences_dialog = PreferencesDialog(self)
        preferences_dialog.exec()
        if self.parent():
            if hasattr(self.parent(), 'update_editor_settings'):
                self.parent().update_editor_settings()
            if hasattr(self.parent(), '_load_saved_font'):
                self.parent()._load_saved_font()
            if hasattr(self.parent(), 'apply_theme'):
                current_theme = font_manager.load_theme()
                self.parent().apply_theme(current_theme)
    def closeEvent(self, event):
        if self.parent():
            if hasattr(self.parent(), 'update_editor_settings'):
                self.parent().update_editor_settings()
            if hasattr(self.parent(), '_load_saved_font'):
                self.parent()._load_saved_font()
            if hasattr(self.parent(), 'apply_theme'):
                current_theme = font_manager.load_theme()
                self.parent().apply_theme(current_theme)
        super().closeEvent(event)
    def apply_theme(self, theme_mode):
        if theme_mode == "light":
            self.setStyleSheet("background-color: #f0f0f0; color: #000000;")
            self.findChild(QGroupBox, "").setStyleSheet("QGroupBox { color: #000000; }")
            for group_box in self.findChildren(QGroupBox):
                group_box.setStyleSheet("QGroupBox { color: #000000; } QGroupBox::title { padding: 0 3px; }")
        else:
            self.setStyleSheet("background-color: #2d2d2d; color: #ffffff;")
            self.findChild(QGroupBox, "").setStyleSheet("QGroupBox { color: #ffffff; }")
            for group_box in self.findChildren(QGroupBox):
                group_box.setStyleSheet("QGroupBox { color: #ffffff; } QGroupBox::title { padding: 0 3px; }")
        if hasattr(self, 'font_button'):
            self.font_button.apply_theme(theme_mode, gradient=True)
        if hasattr(self, 'preferences_button'):
            self.preferences_button.apply_theme(theme_mode, gradient=True)
class CompileConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        if current_font:
            self.setFont(current_font)
        self.setWindowTitle("Compile Config")
        icon_path = os.path.join("res", "img", "icon", "icon2.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.setFixedSize(600, 400)
        main_layout = QVBoxLayout(self)
        compile_group_box = QGroupBox("Compile")
        group_box_layout = QVBoxLayout()
        compiler_dir_layout = QHBoxLayout()
        compiler_dir_layout.addWidget(QLabel("编译器目录:"))
        self.compiler_dir_edit = QLineEdit()
        if current_font:
            self.compiler_dir_edit.setFont(current_font)
        self.browse_button = RoundedButton("浏览", self, gradient=True)
        self.browse_button.clicked.connect(self._browse_compiler_dir)
        if current_font:
            self.browse_button.setFont(current_font)
        self.browse_button.setFixedWidth(80)
        compiler_dir_layout.addWidget(self.compiler_dir_edit)
        compiler_dir_layout.addWidget(self.browse_button)
        group_box_layout.addLayout(compiler_dir_layout)
        checkbox_layout = QHBoxLayout()
        self.enable_compile_opts = QCheckBox("启用编译选项（编译时加入选项）")
        if current_font:
            self.enable_compile_opts.setFont(current_font)
        checkbox_layout.addWidget(self.enable_compile_opts)
        checkbox_layout.addStretch()
        group_box_layout.addLayout(checkbox_layout)
        edit_layout = QHBoxLayout()
        edit_layout.addWidget(QLabel("编译选项:"))
        self.compile_opts_edit = QLineEdit()
        if current_font:
            self.compile_opts_edit.setFont(current_font)
        edit_layout.addWidget(self.compile_opts_edit)
        group_box_layout.addLayout(edit_layout)
        compile_group_box.setLayout(group_box_layout)
        main_layout.addWidget(compile_group_box)
        link_group_box = QGroupBox("Link")
        link_group_box_layout = QVBoxLayout()
        link_checkbox_layout = QHBoxLayout()
        self.enable_link_opts = QCheckBox("启用链接选项（链接时加入选项）")
        if current_font:
            self.enable_link_opts.setFont(current_font)
        link_checkbox_layout.addWidget(self.enable_link_opts)
        link_checkbox_layout.addStretch()
        link_group_box_layout.addLayout(link_checkbox_layout)
        link_edit_layout = QHBoxLayout()
        link_edit_layout.addWidget(QLabel("链接选项:"))
        self.link_opts_edit = QLineEdit()
        if current_font:
            self.link_opts_edit.setFont(current_font)
        link_edit_layout.addWidget(self.link_opts_edit)
        link_group_box_layout.addLayout(link_edit_layout)
        link_group_box.setLayout(link_group_box_layout)
        main_layout.addWidget(link_group_box)
        button_layout = QHBoxLayout()
        self.refresh_button = RoundedButton("刷新", self, gradient=True)
        self.refresh_button.clicked.connect(self._refresh_settings)
        if current_font:
            self.refresh_button.setFont(current_font)
        self.refresh_button.setFixedWidth(100)
        button_layout.addWidget(self.refresh_button)
        button_layout.addStretch()
        self.ok_button = RoundedButton("确定", self, gradient=True)
        self.ok_button.clicked.connect(self._save_settings)
        if current_font:
            self.ok_button.setFont(current_font)
        button_layout.addWidget(self.ok_button)
        self.cancel_button = RoundedButton("取消", self, gradient=True)
        self.cancel_button.clicked.connect(self.reject)
        if current_font:
            self.cancel_button.setFont(current_font)
        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)
        main_layout.addSpacing(10)
        self.info_edit = QLineEdit()
        self.info_edit.setReadOnly(True)
        self.info_edit.setText("更改编译设置启动项后，需要点击按钮刷新配置文件")
        self.info_edit.setStyleSheet("background-color: #f0f0f0; color: #666666;")
        if current_font:
            self.info_edit.setFont(current_font)
        main_layout.addWidget(self.info_edit)
        self.enable_compile_opts.stateChanged.connect(self._on_checkbox_state_changed)
        self.enable_link_opts.stateChanged.connect(self._on_link_checkbox_state_changed)
        self._load_settings()
        current_theme = font_manager.load_theme()
        self.apply_theme(current_theme)
    def _browse_compiler_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "选择编译器目录", "",
                                                    QFileDialog.Option.ShowDirsOnly |
                                                    QFileDialog.Option.DontResolveSymlinks)
        if directory:
            self.compiler_dir_edit.setText(directory)
    def _refresh_settings(self):
        preferences = font_manager.load_preferences()
        if "compile" not in preferences:
            preferences["compile"] = {}
        preferences["compile"]["enable_opts"] = "true" if self.enable_compile_opts.isChecked() else "false"
        preferences["compile"]["enable_link_opts"] = "true" if self.enable_link_opts.isChecked() else "false"
        font_manager.save_preferences(preferences)
        self._load_settings()
        original_text = self.info_edit.text()
        self.info_edit.setText("配置已刷新！")
        self.info_edit.setStyleSheet("background-color: #d4edda; color: #155724;")
        QTimer.singleShot(2000, lambda: self._restore_info_text(original_text))
    def _restore_info_text(self, original_text):
        self.info_edit.setText(original_text)
        self.info_edit.setStyleSheet("background-color: #f0f0f0; color: #666666;")
    def _on_checkbox_state_changed(self, state):
        enabled = state == Qt.CheckState.Checked
        self.compile_opts_edit.setEnabled(enabled)
        self.compile_opts_edit.repaint()
        if enabled and not self.compile_opts_edit.text():
            self.compile_opts_edit.setText("-std=c++11")
    def _on_link_checkbox_state_changed(self, state):
        enabled = state == Qt.CheckState.Checked
        self.link_opts_edit.setEnabled(enabled)
        self.link_opts_edit.repaint()
        if enabled and not self.link_opts_edit.text():
            self.link_opts_edit.setText("-static-libstdc++ -static-libgcc")
    def _load_settings(self):
        preferences = font_manager.load_preferences()
        compiler_dir = preferences.get("compile", {}).get("compiler_dir", "")
        self.compiler_dir_edit.setText(compiler_dir)
        enabled = preferences.get("compile", {}).get("enable_opts", "false").lower() == "true"
        self.enable_compile_opts.setChecked(enabled)
        compile_opts = preferences.get("compile", {}).get("options", "")
        self.compile_opts_edit.setText(compile_opts)
        self.compile_opts_edit.setEnabled(enabled)
        link_enabled = preferences.get("compile", {}).get("enable_link_opts", "false").lower() == "true"
        self.enable_link_opts.setChecked(link_enabled)
        link_opts = preferences.get("compile", {}).get("link_options", "")
        self.link_opts_edit.setText(link_opts)
        self.link_opts_edit.setEnabled(link_enabled)
    def _save_settings(self):
        preferences = font_manager.load_preferences()
        if "compile" not in preferences:
            preferences["compile"] = {}
        preferences["compile"]["compiler_dir"] = self.compiler_dir_edit.text()
        preferences["compile"]["enable_opts"] = "true" if self.enable_compile_opts.isChecked() else "false"
        preferences["compile"]["options"] = self.compile_opts_edit.text()
        preferences["compile"]["enable_link_opts"] = "true" if self.enable_link_opts.isChecked() else "false"
        preferences["compile"]["link_options"] = self.link_opts_edit.text()
        font_manager.save_preferences(preferences)
        self.accept()
    def apply_theme(self, theme_mode):
        if theme_mode == "light":
            self.setStyleSheet("background-color: #f0f0f0; color: #000000;")
            for group_box in self.findChildren(QGroupBox):
                group_box.setStyleSheet("QGroupBox { color: #000000; } QGroupBox::title { padding: 0 3px; }")
            for label in self.findChildren(QLabel):
                label.setStyleSheet("color: #000000;")
        else:
            self.setStyleSheet("background-color: #2d2d2d; color: #ffffff;")
            for group_box in self.findChildren(QGroupBox):
                group_box.setStyleSheet("QGroupBox { color: #ffffff; } QGroupBox::title { padding: 0 3px; }")
            for label in self.findChildren(QLabel):
                label.setStyleSheet("color: #ffffff;")
            if hasattr(self, 'ok_button'):
                self.ok_button.apply_theme(theme_mode, gradient=True)
            if hasattr(self, 'cancel_button'):
                self.cancel_button.apply_theme(theme_mode, gradient=True)
class PreferencesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        if current_font:
            self.setFont(current_font)
        self.setWindowTitle("批量编辑偏好项")
        icon_path = os.path.join("res", "img", "icon", "icon2.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.resize(600, 500)
        main_layout = QVBoxLayout(self)
        self.preferences = font_manager.load_preferences()
        config_text = QTextEdit()
        config_text.setReadOnly(True)
        config_text.setMaximumHeight(150)
        config_str = "当前配置内容:\n"
        for section, settings in self.preferences.items():
            config_str += f"[{section}]\n"
            for key, value in settings.items():
                config_str += f"{key} = {value}\n"
            config_str += "\n"
        config_text.setPlainText(config_str)
        main_layout.addWidget(config_text)
        editor_group = QGroupBox("编辑器设置")
        editor_layout = QVBoxLayout()
        font_size_layout = QHBoxLayout()
        font_size_layout.addWidget(QLabel("字体大小:"))
        self.font_size = QLineEdit(self.preferences.get("editor", {}).get("font_size", "12"))
        font_size_layout.addWidget(self.font_size)
        editor_layout.addLayout(font_size_layout)
        auto_indent_layout = QHBoxLayout()
        auto_indent_layout.addWidget(QLabel("自动缩进:"))
        self.auto_indent = QCheckBox()
        self.auto_indent.setChecked(self.preferences.get("editor", {}).get("auto_indent", "true").lower() == "true")
        auto_indent_layout.addWidget(self.auto_indent)
        editor_layout.addLayout(auto_indent_layout)
        editor_group.setLayout(editor_layout)
        main_layout.addWidget(editor_group)
        display_group = QGroupBox("显示设置")
        display_layout = QVBoxLayout()
        show_line_numbers_layout = QHBoxLayout()
        show_line_numbers_layout.addWidget(QLabel("显示行号:"))
        self.show_line_numbers = QCheckBox()
        self.show_line_numbers.setChecked(self.preferences.get("display", {}).get("show_line_numbers", "true").lower() == "true")
        show_line_numbers_layout.addWidget(self.show_line_numbers)
        display_layout.addLayout(show_line_numbers_layout)
        display_group.setLayout(display_layout)
        main_layout.addWidget(display_group)
        button_layout = QHBoxLayout()
        self.close_button = QPushButton("关闭")
        self.close_button.clicked.connect(self.reject)
        self.apply_button = QPushButton("应用")
        self.apply_button.clicked.connect(self._apply_preferences)
        if current_font:
            self.close_button.setFont(current_font)
            self.apply_button.setFont(current_font)
        button_layout.addStretch()
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.close_button)
        main_layout.addLayout(button_layout)
        current_theme = font_manager.load_theme()
        self.apply_theme(current_theme)
    def _apply_preferences(self):
        if "editor" not in self.preferences:
            self.preferences["editor"] = {}
        self.preferences["editor"]["font_size"] = self.font_size.text()
        self.preferences["editor"]["auto_indent"] = "true" if self.auto_indent.isChecked() else "false"
        if "display" not in self.preferences:
            self.preferences["display"] = {}
        self.preferences["display"]["show_line_numbers"] = "true" if self.show_line_numbers.isChecked() else "false"
        font_manager.save_preferences(self.preferences)
        QMessageBox.information(self, "成功", "偏好设置已保存！")
    def closeEvent(self, event):
        if self.parent():
            if hasattr(self.parent(), 'update_editor_settings'):
                self.parent().update_editor_settings()
            if hasattr(self.parent(), '_load_saved_font'):
                self.parent()._load_saved_font()
            if hasattr(self.parent(), 'apply_theme'):
                current_theme = font_manager.load_theme()
                self.parent().apply_theme(current_theme)
        super().closeEvent(event)
    def apply_theme(self, theme_mode):
        if theme_mode == "light":
            self.setStyleSheet("background-color: #f0f0f0; color: #000000;")
            for group_box in self.findChildren(QGroupBox):
                group_box.setStyleSheet("QGroupBox { color: #000000; } QGroupBox::title { padding: 0 3px; }")
        else:
            self.setStyleSheet("background-color: #2d2d2d; color: #ffffff;")
            for group_box in self.findChildren(QGroupBox):
                group_box.setStyleSheet("QGroupBox { color: #ffffff; } QGroupBox::title { padding: 0 3px; }")
class MainWindow(QMainWindow):
    def __init__(self, screen_resolution):
        super().__init__()
        self.setWindowTitle("Srumble-Cpp")
        icon_path = os.path.join("res", "img", "icon", "icon2.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self._create_tool_bar()
        self._create_main_layout()
        self.current_folder = None
        self.current_file = None
        self.compile_process = None
        self.run_process = None
        self.temp_cpp_file = None
        self.temp_exe_file = None
        self._load_saved_font()
        current_theme = font_manager.load_theme()
        self.apply_theme(current_theme)
        self.showMaximized()
        self._check_gcc_installation()
        test_file_path = os.path.join(os.getcwd(), "test_output.cpp")
        if os.path.exists(test_file_path):
            try:
                with open(test_file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                self.code_editor.setText(content)
                self.output_panel.append(f"已自动加载测试文件: {test_file_path}")
                self.output_panel.append("请使用编译并运行按钮(F5)测试输出功能")
            except Exception as e:
                self.output_panel.append(f"无法加载测试文件: {str(e)}")
    def _load_saved_font(self):
        global current_font
        font = font_manager.load_font()
        if font:
            current_font = font
            self.update_fonts(font)
    def update_editor_settings(self):
        preferences = font_manager.load_preferences()
        show_line_numbers = preferences.get("display", {}).get("show_line_numbers", "true").lower() == "true"
        if hasattr(self, 'code_editor') and hasattr(self.code_editor, 'set_line_numbers_visibility'):
            self.code_editor.set_line_numbers_visibility(show_line_numbers)
    def update_fonts(self, font):
        if hasattr(self, 'code_editor'):
            self.code_editor.setFont(font)
            if hasattr(self.code_editor, 'lexer'):
                self.code_editor.lexer.setFont(font)
                self.code_editor.setLexer(self.code_editor.lexer)
        if hasattr(self, 'compile_report_panel'):
            self.compile_report_panel.setFont(font)
        if hasattr(self, 'output_panel'):
            self.output_panel.setFont(font)
        for group_box in self.findChildren(QGroupBox):
            title_font = group_box.font()
            title_font.setFamily(font.family())
            title_font.setPointSize(font.pointSize())
            group_box.setFont(title_font)
    def resizeEvent(self, event):
        super().resizeEvent(event)
    def _create_tool_bar(self):
        self.tool_bar = self.addToolBar("Main Tools")
        open_folder_action = QAction(QIcon(os.path.join("res", "img", "icon", "open_folder.png")), "Open Folder", self)
        open_folder_action.triggered.connect(self._open_folder)
        self.tool_bar.addAction(open_folder_action)
        open_file_action = QAction(QIcon(os.path.join("res", "img", "icon", "open_file.png")), "Open File", self)
        open_file_action.triggered.connect(self._open_file)
        self.tool_bar.addAction(open_file_action)
        save_file_action = QAction(QIcon(os.path.join("res", "img", "icon", "save_file.png")), "Save File", self)
        save_file_action.triggered.connect(self._save_file)
        save_file_action.setShortcut("Ctrl+S")
        self.tool_bar.addAction(save_file_action)
        self.tool_bar.addSeparator()
        compile_action = QAction(QIcon(os.path.join("res", "img", "icon", "compile.png")), "编译", self)
        compile_action.triggered.connect(self._compile_code)
        compile_action.setShortcut("Ctrl+B")
        self.tool_bar.addAction(compile_action)
        run_action = QAction(QIcon(os.path.join("res", "img", "icon", "run.png")), "运行", self)
        run_action.triggered.connect(self._run_program_only)
        self.tool_bar.addAction(run_action)
        compile_and_run_action = QAction(QIcon(os.path.join("res", "img", "icon", "compile_and_run.png")), "编译并运行", self)
        compile_and_run_action.triggered.connect(self._compile_and_run)
        compile_and_run_action.setShortcut("F5")
        self.tool_bar.addAction(compile_and_run_action)
        self.tool_bar.addSeparator()
        ui_config_action = QAction(QIcon(os.path.join("res", "img", "icon", "ui_config.png")), "UI Config", self)
        ui_config_action.triggered.connect(self._show_ide_config_dialog)
        self.tool_bar.addAction(ui_config_action)
        compile_config_action = QAction(QIcon(os.path.join("res", "img", "icon", "compile_config.png")), "Compile Config", self)
        compile_config_action.triggered.connect(self._show_compile_config_dialog)
        self.tool_bar.addAction(compile_config_action)
        self.tool_bar.addSeparator()
        help_action = QAction(QIcon(os.path.join("res", "img", "icon", "help.png")), "Help", self)
        help_action.triggered.connect(self._show_help_dialog)
        self.tool_bar.addAction(help_action)
        info_action = QAction(QIcon(os.path.join("res", "img", "icon", "info.png")), "Info", self)
        info_action.triggered.connect(self._show_info_dialog)
        self.tool_bar.addAction(info_action)
        current_theme = font_manager.load_theme()
        self._apply_tool_bar_theme(current_theme)
    def _open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开文件", ".",
            "C++ Files (*.cpp *.h *.hpp);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                self.code_editor.setText(content)
                self.current_file = file_path
                self.setWindowTitle(f"Srumble-Cpp - {os.path.basename(file_path)}")
                self.current_folder = os.path.dirname(file_path)
                self._refresh_directory_tree()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法打开文件: {str(e)}")
    def _save_file(self):
        if not self.current_file:
            return self._save_file_as()
        try:
            with open(self.current_file, 'w', encoding='utf-8') as file:
                file.write(self.code_editor.text())
            QMessageBox.information(self, "成功", "文件已保存!")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法保存文件: {str(e)}")
    def _save_file_as(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "另存为", ".",
            "C++ Files (*.cpp *.h *.hpp);;All Files (*)"
        )
        if file_path:
            self.current_file = file_path
            self.setWindowTitle(f"Srumble-Cpp - {os.path.basename(file_path)}")
            return self._save_file()
        return False
    def _refresh_directory_tree(self):
        if self.current_folder:
            self.directory_view.clear()
            root_item = QTreeWidgetItem([os.path.basename(self.current_folder)])
            self.directory_view.addTopLevelItem(root_item)
            self._add_directory_to_tree(root_item, self.current_folder)
            root_item.setExpanded(True)
    def _on_directory_item_double_clicked(self, item, column):
        path_parts = []
        current_item = item
        while current_item:
            path_parts.append(current_item.text(0))
            current_item = current_item.parent()
        path_parts.reverse()
        if self.current_folder:
            full_path = os.path.join(self.current_folder, *path_parts[1:])
        else:
            return
        if os.path.isfile(full_path):
            try:
                with open(full_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                self.code_editor.setText(content)
                self.current_file = full_path
                self.setWindowTitle(f"Srumble-Cpp - {os.path.basename(full_path)}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法打开文件: {str(e)}")
    def _show_help_dialog(self):
        help_dialog = HelpDialog(self)
        current_theme = font_manager.load_theme()
        help_dialog.apply_theme(current_theme)
        help_dialog.exec()
    def _show_info_dialog(self):
        info_dialog = InfoDialog(self)
        current_theme = font_manager.load_theme()
        info_dialog.apply_theme(current_theme)
        info_dialog.exec()
    def _create_main_layout(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_vertical_layout = QVBoxLayout(central_widget)
        horizontal_splitter = QSplitter()
        horizontal_splitter.setOrientation(Qt.Orientation.Horizontal)
        horizontal_splitter.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        directory_widget = QWidget()
        directory_layout = QVBoxLayout(directory_widget)
        directory_layout.setContentsMargins(5, 5, 5, 5)
        directory_layout.setSpacing(5)
        self.directory_group = QGroupBox("项目文件")
        self.directory_group.setMinimumWidth(200)
        self.directory_group.setMaximumWidth(400)
        self.directory_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.directory_view = QTreeWidget()
        self.directory_view.setHeaderLabel("文件")
        self.directory_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.directory_view.itemDoubleClicked.connect(self._on_directory_item_double_clicked)
        directory_group_layout = QVBoxLayout()
        directory_group_layout.setContentsMargins(5, 5, 5, 5)
        directory_group_layout.addWidget(self.directory_view)
        self.directory_group.setLayout(directory_group_layout)
        directory_layout.addWidget(self.directory_group)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(5, 5, 5, 5)
        right_layout.setSpacing(5)
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        self.editor_group = QGroupBox("代码编辑")
        self.code_editor = CppCodeEditor()
        editor_group_layout = QVBoxLayout()
        editor_group_layout.setContentsMargins(5, 5, 5, 5)
        editor_group_layout.addWidget(self.code_editor)
        self.editor_group.setLayout(editor_group_layout)
        editor_layout.addWidget(self.editor_group)
        compile_report_widget = QWidget()
        compile_report_layout = QVBoxLayout(compile_report_widget)
        compile_report_layout.setContentsMargins(0, 0, 0, 0)
        self.compile_report_group = QGroupBox("编译报告")
        self.compile_report_group.setMinimumHeight(150)
        self.compile_report_panel = QTextEdit()
        self.compile_report_panel.setReadOnly(True)
        self.compile_report_panel.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        compile_report_group_layout = QVBoxLayout()
        compile_report_group_layout.setContentsMargins(5, 5, 5, 5)
        compile_report_group_layout.addWidget(self.compile_report_panel)
        self.compile_report_group.setLayout(compile_report_group_layout)
        compile_report_layout.addWidget(self.compile_report_group)
        output_widget = QWidget()
        output_layout = QVBoxLayout(output_widget)
        output_layout.setContentsMargins(0, 0, 0, 0)
        self.output_group = QGroupBox("Output")
        self.output_group.setMinimumHeight(150)
        self.output_panel = QTextEdit()
        self.output_panel.setReadOnly(True)
        self.output_panel.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        output_group_layout = QVBoxLayout()
        output_group_layout.setContentsMargins(5, 5, 5, 5)
        output_group_layout.addWidget(self.output_panel)
        self.output_group.setLayout(output_group_layout)
        self.input_group = QGroupBox("Input")
        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("输入内容并按Enter发送...")
        self.input_line.setEnabled(False)
        self.input_line.returnPressed.connect(self._send_input)
        input_group_layout = QVBoxLayout()
        input_group_layout.setContentsMargins(5, 5, 5, 5)
        input_group_layout.addWidget(self.input_line)
        self.input_group.setLayout(input_group_layout)
        output_layout.addWidget(self.input_group)
        self.output_group.setVisible(False)
        self.input_group.setVisible(False)
        right_layout.addWidget(editor_widget)
        right_layout.addWidget(compile_report_widget)
        right_layout.addWidget(output_widget)
        right_layout.setStretch(0, 3)
        right_layout.setStretch(1, 1)
        right_layout.setStretch(2, 0)
        horizontal_splitter.addWidget(directory_widget)
        horizontal_splitter.addWidget(right_widget)
        horizontal_splitter.setSizes([200, 800])
        horizontal_splitter.setStyleSheet("QSplitter::handle:horizontal { width: 4px; background-color: rgba(255, 255, 255, 0.1); }")
        main_vertical_layout.addWidget(horizontal_splitter)
        central_widget.setLayout(main_vertical_layout)
    def _open_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹", ".")
        if folder_path:
            self.current_folder = folder_path
            self.setWindowTitle(f"Srumble-Cpp - {folder_path}")
            self.directory_view.clear()
            root_item = QTreeWidgetItem([os.path.basename(folder_path)])
            self.directory_view.addTopLevelItem(root_item)
            self._add_directory_to_tree(root_item, folder_path)
            root_item.setExpanded(True)
    def _add_directory_to_tree(self, parent_item, directory_path):
        try:
            items = os.listdir(directory_path)
            for item in sorted(items):
                item_path = os.path.join(directory_path, item)
                item_name = os.path.basename(item_path)
                if item_name.startswith('.'):
                    continue
                tree_item = QTreeWidgetItem([item_name])
                parent_item.addChild(tree_item)
                if os.path.isdir(item_path):
                    self._add_directory_to_tree(tree_item, item_path)
        except Exception as e:
            print(f"无法访问目录 {directory_path}: {e}")
    def _run_program_only(self):
        if not self.temp_exe_file or not os.path.exists(self.temp_exe_file):
            self.compile_report_panel.append("\n错误：未找到可执行文件")
            self.compile_report_panel.append("请先成功编译代码再运行程序。")
            QMessageBox.warning(self, "运行错误", "未找到可执行文件。请先成功编译代码再运行程序。")
            return
        self._run_program()
    def _apply_tool_bar_theme(self, theme_mode):
        if theme_mode == "light":
            self.tool_bar.setStyleSheet(
                "QToolBar { background-color: #f0f0f0; border: none; spacing: 2px; }"
                "QToolButton { padding: 5px; border-radius: 5px; }"
                "QToolButton:hover { background-color: #e0e0e0; }"
                "QToolButton:pressed { background-color: #d0d0d0; }"
            )
            for action in self.tool_bar.actions():
                if action.iconText() == "打开文件夹":
                    action.setIcon(QIcon(os.path.join("res", "img", "icon", "open_folder.png")))
                elif action.iconText() == "打开文件":
                    action.setIcon(QIcon(os.path.join("res", "img", "icon", "open_file.png")))
                elif action.iconText() == "保存文件":
                    action.setIcon(QIcon(os.path.join("res", "img", "icon", "save_file.png")))
                elif action.iconText() == "编译":
                    action.setIcon(QIcon(os.path.join("res", "img", "icon", "compile.png")))
                elif action.iconText() == "运行":
                    action.setIcon(QIcon(os.path.join("res", "img", "icon", "run.png")))
                elif action.iconText() == "编译并运行":
                    action.setIcon(QIcon(os.path.join("res", "img", "icon", "compile_and_run.png")))
                elif action.iconText() == "UI 设置":
                    action.setIcon(QIcon(os.path.join("res", "img", "icon", "ui_config.png")))
                elif action.iconText() == "编译设置":
                    action.setIcon(QIcon(os.path.join("res", "img", "icon", "compile_config.png")))
                elif action.iconText() == "获取帮助":
                    action.setIcon(QIcon(os.path.join("res", "img", "icon", "help.png")))
                elif action.iconText() == "信息":
                    action.setIcon(QIcon(os.path.join("res", "img", "icon", "info.png")))
        else:
            self.tool_bar.setStyleSheet(
                "QToolBar { background-color: #2d2d2d; border: none; spacing: 2px; }"
                "QToolButton { padding: 5px; border-radius: 5px; }"
                "QToolButton:hover { background-color: #3d3d3d; }"
                "QToolButton:pressed { background-color: #4d4d4d; }"
            )
            for action in self.tool_bar.actions():
                if action.iconText() == "打开文件夹":
                    action.setIcon(QIcon(os.path.join("res", "img", "icon", "open_folder_dark.png")))
                elif action.iconText() == "打开文件":
                    action.setIcon(QIcon(os.path.join("res", "img", "icon", "open_file_dark.png")))
                elif action.iconText() == "保存文件":
                    action.setIcon(QIcon(os.path.join("res", "img", "icon", "save_file_dark.png")))
                elif action.iconText() == "编译":
                    action.setIcon(QIcon(os.path.join("res", "img", "icon", "compile_dark.png")))
                elif action.iconText() == "运行":
                    action.setIcon(QIcon(os.path.join("res", "img", "icon", "run_dark.png")))
                elif action.iconText() == "编译并运行":
                    action.setIcon(QIcon(os.path.join("res", "img", "icon", "compile_and_run_dark.png")))
                elif action.iconText() == "UI 设置":
                    action.setIcon(QIcon(os.path.join("res", "img", "icon", "ui_config_dark.png")))
                elif action.iconText() == "编译设置":
                    action.setIcon(QIcon(os.path.join("res", "img", "icon", "compile_config_dark.png")))
                elif action.iconText() == "获取帮助":
                    action.setIcon(QIcon(os.path.join("res", "img", "icon", "help_dark.png")))
                elif action.iconText() == "信息":
                    action.setIcon(QIcon(os.path.join("res", "img", "icon", "info_dark.png")))
        self.tool_bar.update()
    def apply_theme(self, theme_mode):
        if theme_mode == "light":
            self.setStyleSheet("background-color: #f0f0f0; color: #000000;")
            if hasattr(self, 'menuBar'):
                menu_bar = self.menuBar()
                menu_bar.setStyleSheet("background-color: #f0f0f0; color: #000000;")
            if hasattr(self, 'directory_group'):
                self.directory_group.setStyleSheet("QGroupBox { color: #000000; } QGroupBox::title { padding: 0 3px; }")
            if hasattr(self, 'directory_view'):
                self.directory_view.setStyleSheet("background-color: #ffffff; color: #000000; border: 1px solid #cccccc;")
            if hasattr(self, 'editor_group'):
                self.editor_group.setStyleSheet("QGroupBox { color: #000000; } QGroupBox::title { padding: 0 3px; }")
            if hasattr(self, 'compile_report_group'):
                self.compile_report_group.setStyleSheet("QGroupBox { color: #000000; } QGroupBox::title { padding: 0 3px; }")
            if hasattr(self, 'compile_report_panel'):
                self.compile_report_panel.setStyleSheet("background-color: #ffffff; color: #000000; border: 1px solid #cccccc;")
            if hasattr(self, 'output_group'):
                self.output_group.setStyleSheet("QGroupBox { color: #000000; } QGroupBox::title { padding: 0 3px; }")
            if hasattr(self, 'output_panel'):
                self.output_panel.setStyleSheet("background-color: #ffffff; color: #000000; border: 1px solid #cccccc;")
            if hasattr(self, 'input_group'):
                self.input_group.setStyleSheet("QGroupBox { color: #000000; } QGroupBox::title { padding: 0 3px; }")
            if hasattr(self, 'input_line'):
                self.input_line.setStyleSheet("background-color: #ffffff; color: #000000; border: 1px solid #cccccc;")
            if hasattr(self, 'code_editor'):
                if isinstance(self.code_editor, CppCodeEditor):
                    self.code_editor.apply_theme("light")
            if hasattr(self, 'tool_bar'):
                self._apply_tool_bar_theme(theme_mode)
        else:
            self.setStyleSheet("background-color: #2d2d2d; color: #ffffff;")
            if hasattr(self, 'menuBar'):
                menu_bar = self.menuBar()
                menu_bar.setStyleSheet("background-color: #2d2d2d; color: #ffffff;")
            if hasattr(self, 'directory_group'):
                self.directory_group.setStyleSheet("QGroupBox { color: #ffffff; } QGroupBox::title { padding: 0 3px; }")
            if hasattr(self, 'directory_view'):
                self.directory_view.setStyleSheet("background-color: #1e1e1e; color: #ffffff; border: 1px solid #444444;")
            if hasattr(self, 'editor_group'):
                self.editor_group.setStyleSheet("QGroupBox { color: #ffffff; } QGroupBox::title { padding: 0 3px; }")
            if hasattr(self, 'compile_report_group'):
                self.compile_report_group.setStyleSheet("QGroupBox { color: #ffffff; } QGroupBox::title { padding: 0 3px; }")
            if hasattr(self, 'compile_report_panel'):
                self.compile_report_panel.setStyleSheet("background-color: #1e1e1e; color: #ffffff; border: 1px solid #444444;")
            if hasattr(self, 'output_group'):
                self.output_group.setStyleSheet("QGroupBox { color: #ffffff; } QGroupBox::title { padding: 0 3px; }")
            if hasattr(self, 'output_panel'):
                self.output_panel.setStyleSheet("background-color: #1e1e1e; color: #ffffff; border: 1px solid #444444;")
            if hasattr(self, 'input_group'):
                self.input_group.setStyleSheet("QGroupBox { color: #ffffff; } QGroupBox::title { padding: 0 3px; }")
            if hasattr(self, 'input_line'):
                self.input_line.setStyleSheet("background-color: #1e1e1e; color: #ffffff; border: 1px solid #444444;")
            if hasattr(self, 'code_editor'):
                if isinstance(self.code_editor, CppCodeEditor):
                    self.code_editor.apply_theme("dark")
            if hasattr(self, 'tool_bar'):
                self._apply_tool_bar_theme(theme_mode)
    def _show_ide_config_dialog(self):
        ui_config_dialog = UIConfigDialog(self)
        ui_config_dialog.exec()
        if current_font:
            self.update_fonts(current_font)
    def _show_compile_config_dialog(self):
        compile_config_dialog = CompileConfigDialog(self)
        compile_config_dialog.exec()
    def _check_gcc_installation(self):
        gcc_path = shutil.which('g++')
        if gcc_path:
            try:
                result = subprocess.run(['g++', '--version'], capture_output=True, text=True, check=True)
                version_info = result.stdout.split('\n')[0]
                self.compile_report_panel.append(f"找到编译器: {gcc_path}")
                self.compile_report_panel.append(f"版本信息: {version_info}")
            except Exception as e:
                self.compile_report_panel.append(f"找到g++，但无法获取版本信息: {str(e)}")
        else:
            self.compile_report_panel.append("未找到g++编译器。")
            self.compile_report_panel.append("请安装MinGW-w64或TDM-GCC以启用编译功能。")
            QMessageBox.warning(self, "编译器未找到",
                               "未找到g++编译器。请安装MinGW-w64或TDM-GCC以启用编译功能。\n\n" \
                               "推荐安装方式：\n" \
                               "1. 访问 https://winlibs.com/ 下载MinGW-w64\n" \
                               "2. 安装时确保添加到系统PATH\n" \
                               "3. 重启IDE后即可使用编译功能")
    def _cleanup_temp_files(self):
        if self.temp_cpp_file and os.path.exists(self.temp_cpp_file):
            try:
                os.remove(self.temp_cpp_file)
            except:
                pass
            self.temp_cpp_file = None
        if self.temp_exe_file and os.path.exists(self.temp_exe_file):
            try:
                os.remove(self.temp_exe_file)
            except:
                pass
            self.temp_exe_file = None
    def _compile_code(self):
        if not shutil.which('g++'):
            QMessageBox.critical(self, "编译器错误", "未找到g++编译器。请先安装MinGW-w64或TDM-GCC。")
            return
        self.compile_report_panel.clear()
        self.compile_report_panel.append("开始编译...")
        try:
            fd, self.temp_cpp_file = tempfile.mkstemp(suffix='.cpp', text=True)
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(self.code_editor.text())
            self.temp_exe_file = tempfile.mktemp(suffix='.exe')
            if self.compile_process and self.compile_process.state() == QProcess.ProcessState.Running:
                self.compile_process.kill()
            self.compile_process = QProcess(self)
            compile_args = [self.temp_cpp_file, '-o', self.temp_exe_file]
            preferences = font_manager.load_preferences()
            enable_opts = preferences.get("compile", {}).get("enable_opts", "false").lower() == "true"
            if enable_opts:
                compile_opts = preferences.get("compile", {}).get("options", "")
                if compile_opts:
                    compile_args.extend(compile_opts.split())
                    self.compile_report_panel.append(f"使用编译选项: {compile_opts}")
            self.compile_process.setProgram('g++')
            self.compile_process.setArguments(compile_args)
            self.compile_process.readyReadStandardOutput.connect(self._handle_compile_output)
            self.compile_process.readyReadStandardError.connect(self._handle_compile_error)
            self.compile_process.finished.connect(self._on_compile_finished)
            self.compile_process.start()
        except Exception as e:
            self.compile_report_panel.append(f"编译准备失败: {str(e)}")
            self._cleanup_temp_files()
            if hasattr(self, '_compile_for_run'):
                delattr(self, '_compile_for_run')
    def _compile_and_run(self):
        self._compile_for_run = True
        self._compile_code()
    def _handle_compile_output(self):
        if self.compile_process:
            data = self.compile_process.readAllStandardOutput().data().decode()
            self.compile_report_panel.append(data)
    def _handle_compile_error(self):
        if self.compile_process:
            data = self.compile_process.readAllStandardError().data().decode()
            self.compile_report_panel.append(f"[编译错误] {data}")
    def _on_compile_finished(self, exitCode, exitStatus):
        if exitCode == 0:
            self.compile_report_panel.append("\n编译成功！")
            if hasattr(self, '_compile_for_run') and self._compile_for_run:
                self._run_program()
                delattr(self, '_compile_for_run')
        else:
            self.compile_report_panel.append(f"\n编译失败，退出码: {exitCode}")
            self.compile_report_panel.append("请检查代码中的错误并重新编译。")
            if hasattr(self, '_compile_for_run'):
                delattr(self, '_compile_for_run')
    def _run_program(self):
        if not self.temp_exe_file or not os.path.exists(self.temp_exe_file):
            self.output_panel.append("没有可运行的程序。请先成功编译代码。")
            return
        self.output_window = OutputWindow(self)
        self.output_window.append_output("编译成功！\n")
        self.output_window.append_output("开始运行程序...")
        self.output_window.append_output("提示：程序正在运行，可在下方输入框中输入数据...")
        self.output_window.show()
        if hasattr(self, 'run_process') and self.run_process and self.run_process.state() == QProcess.ProcessState.Running:
            self.run_process.kill()
        self.run_process = QProcess(self)
        self.output_window.run_process = self.run_process
        self.run_process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.run_process.setProgram(self.temp_exe_file)
        self.run_process.readyReadStandardOutput.connect(self._handle_run_output)
        self.run_process.readyReadStandardError.connect(self._handle_run_error)
        self.run_process.finished.connect(self._on_run_finished)
        self.timer_id = self.output_window.startTimer(10000)
        self.output_window.timer_id = self.timer_id
        self.run_process.start(QProcess.OpenModeFlag.ReadWrite | QProcess.OpenModeFlag.Unbuffered)
        self.output_window.input_line.setEnabled(True)
        self.output_window.input_line.setFocus()
    def _send_input(self):
        if self.run_process and self.run_process.state() == QProcess.ProcessState.Running:
            input_text = self.input_line.text() + '\n'
            self.output_panel.append(f'> {input_text.rstrip()}')
            self.run_process.write(input_text.encode())
            self.input_line.clear()
            self.output_panel.verticalScrollBar().setValue(self.output_panel.verticalScrollBar().maximum())
    def _handle_run_output(self):
        if hasattr(self, 'output_window') and self.output_window and self.run_process:
            data = self.run_process.readAllStandardOutput().data().decode()
            self.output_window.append_output(data)
    def _handle_run_error(self):
        if hasattr(self, 'output_window') and self.output_window and self.run_process:
            data = self.run_process.readAllStandardError().data().decode()
            self.output_window.append_output(f"[运行错误] {data}")
    def _on_run_finished(self, exitCode, exitStatus):
        if hasattr(self, 'output_window') and self.output_window:
            self.output_window.append_output(f"\n程序运行完成，退出码: {exitCode}")
            self.output_window.input_line.setEnabled(False)
            self._cleanup_temp_files()
    def timerEvent(self, event):
        super().timerEvent(event)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    icon_path = os.path.join("res", "img", "icon", "icon2.png")
    if os.path.exists(icon_path):
        app_icon = QIcon(icon_path)
        app.setWindowIcon(app_icon)
    primary_screen = app.primaryScreen()
    screen_geometry = primary_screen.geometry()
    screen_resolution = (screen_geometry.width(), screen_geometry.height())
    window = MainWindow(screen_resolution)
    sys.exit(app.exec())