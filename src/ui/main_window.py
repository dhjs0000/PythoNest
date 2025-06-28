from PyQt6.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
                         QLabel, QPushButton, QListWidget, QMessageBox,
                         QHBoxLayout, QLineEdit, QComboBox, QGroupBox, QFormLayout,
                         QMenuBar, QMenu, QDialog, QTextEdit, QTextBrowser, QSplitter, QApplication, QFileDialog,QCheckBox, QListWidgetItem, QProgressBar
                         )
from PyQt6.QtCore import Qt, QSize, QUrl, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon, QAction, QFont, QColor, QPalette, QDesktopServices

import sys
import os
from pathlib import Path
import subprocess
import re
import time
import logging

from src.core.python_manager import PythonManager
from src.core.venv_manager import VenvManager
from src.core.package_manager import PackageManager


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("关于 PythoNest")
        self.setFixedSize(500, 400)
        
        # 设置对话框背景色为白色
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel {
                color: black;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("PythoNest - Python版本管理工具")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #333333;")
        layout.addWidget(title_label)
        
        # 版本
        version_label = QLabel("版本: 1.1.5")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("color: #333333;")
        layout.addWidget(version_label)
        
        # 描述 - 使用QTextBrowser代替QTextEdit以支持链接点击
        description = QTextBrowser()
        description.setOpenExternalLinks(True)  # 这个设置使链接可以直接在浏览器中打开
        description.setStyleSheet("""
            QTextBrowser {
                background-color: white;
                color: #333333;
                border: none;
            }
        """)
        description.setHtml("""
        <div style='text-align:center;'>
            <p style='color:#333333;'>PythoNest是一个功能强大的Python版本管理工具，帮助用户轻松管理多个Python版本、虚拟环境和包。</p>
            
            <p style='color:#333333;'><b>主要功能：</b></p>
            <ul style='list-style-position: inside; color:#333333;'>
                <li>管理多个Python版本</li>
                <li>创建和管理虚拟环境</li>
                <li>搜索、安装和管理包</li>
            </ul>
            <p style='color:#333333;'><b>版本更新：</b></p>
            <p style='color:#333333;'>1.1.5版本：</p>
            <ul style='list-style-position: inside; color:#333333;'>
                <li>更新了软件布局</li>
            </ul>
            <p style='color:#333333;'><b>作者：</b> dhjs0000</p>
            <p style='color:#333333;'><b>GitHub：</b> <a href='https://github.com/dhjs0000/PythoNest'>https://github.com/dhjs0000/PythoNest</a></p>
            <p style='color:#333333;'><b>Bilibili：</b> <a href='https://space.bilibili.com/430218185'>https://space.bilibili.com/430218185</a></p>
            
            <p style='margin-top:20px; color:#333333;'><b>开源协议：</b></p>
            <p style='color:#333333;'>本软件基于GNU通用公共许可证第3版(GPL-3.0)发布</p>
            <p style='color:#333333;'>您可以自由使用、修改和分发本软件，但需要遵守GPL-3.0协议的条款。</p>
        </div>
        """)
        layout.addWidget(description)
        
        self.setLayout(layout)


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PythoNest 设置")
        self.setFixedSize(600, 400)
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel {
                color: #333333;
            }
            QGroupBox {
                color: #333333;
            }
            QCheckBox {
                color: #333333;
            }
        """)
        
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("PythoNest 设置")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 创建标签页控件
        tab_widget = QTabWidget()
        
        # Python搜索设置
        search_tab = QWidget()
        search_layout = QVBoxLayout(search_tab)
        
        search_group = QGroupBox("Python版本搜索方式")
        search_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #dddddd;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
            }
        """)
        
        search_options_layout = QVBoxLayout()
        
        self.registry_check = QCheckBox("使用注册表搜索 (仅Windows)")
        self.registry_check.setChecked(True)
        search_options_layout.addWidget(self.registry_check)
        
        self.py_launcher_check = QCheckBox("使用py启动器搜索 (仅Windows)")
        self.py_launcher_check.setChecked(True)
        search_options_layout.addWidget(self.py_launcher_check)
        
        self.path_check = QCheckBox("在PATH中搜索Python可执行文件")
        self.path_check.setChecked(True)
        search_options_layout.addWidget(self.path_check)
        
        self.custom_paths_check = QCheckBox("在自定义路径中搜索")
        search_options_layout.addWidget(self.custom_paths_check)
        
        self.custom_paths_input = QLineEdit()
        self.custom_paths_input.setPlaceholderText("自定义路径，多个路径使用;分隔")
        self.custom_paths_input.setStyleSheet("color: #333333;")
        search_options_layout.addWidget(self.custom_paths_input)
        
        search_group.setLayout(search_options_layout)
        search_layout.addWidget(search_group)
        
        # 添加一些垂直空间
        search_layout.addStretch()
        
        # Python源设置
        source_tab = QWidget()
        source_layout = QVBoxLayout(source_tab)
        
        source_group = QGroupBox("Python下载源")
        source_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #dddddd;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
            }
        """)
        
        source_options_layout = QVBoxLayout()
        
        # Python源选择
        source_label = QLabel("选择Python下载源:")
        source_label.setStyleSheet("margin-top: 10px;")
        source_options_layout.addWidget(source_label)
        
        self.source_combo = QComboBox()
        self.source_combo.addItem("Python官方源 (python.org)", "https://www.python.org/downloads/")
        self.source_combo.addItem("淘宝Python镜像", "https://npm.taobao.org/mirrors/python/")
        self.source_combo.addItem("华为云镜像", "https://mirrors.huaweicloud.com/python/")
        self.source_combo.addItem("清华大学镜像", "https://mirrors.tuna.tsinghua.edu.cn/anaconda/archive/")
        self.source_combo.addItem("北京外国语大学镜像", "https://mirrors.bfsu.edu.cn/anaconda/archive/")
        self.source_combo.currentIndexChanged.connect(self.on_source_changed)
        self.source_combo.setStyleSheet("""
            QComboBox {
                color: #333333;
                background-color: white;
                border: 1px solid #dddddd;
                border-radius: 4px;
                padding: 4px;
            }
            QComboBox QAbstractItemView {
                color: #333333;
                background-color: white;
                selection-background-color: #e6f0ff;
                selection-color: #333333;
            }
        """)
        source_options_layout.addWidget(self.source_combo)
        
        # 自定义源URL
        custom_source_layout = QHBoxLayout()
        self.custom_source_check = QCheckBox("使用自定义源:")
        self.custom_source_check.toggled.connect(self.on_custom_source_toggled)
        custom_source_layout.addWidget(self.custom_source_check)
        
        self.custom_source_input = QLineEdit()
        self.custom_source_input.setPlaceholderText("输入自定义Python下载源URL")
        self.custom_source_input.setEnabled(False)
        self.custom_source_input.setStyleSheet("color: #333333;")
        custom_source_layout.addWidget(self.custom_source_input)
        
        source_options_layout.addLayout(custom_source_layout)
        source_group.setLayout(source_options_layout)
        source_layout.addWidget(source_group)
        
        # 下载设置
        download_group = QGroupBox("下载设置")
        download_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #dddddd;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
            }
        """)
        
        download_layout = QVBoxLayout()
        
        # 下载目录
        download_dir_layout = QHBoxLayout()
        download_dir_label = QLabel("下载目录:")
        download_dir_layout.addWidget(download_dir_label)
        
        self.download_dir_input = QLineEdit()
        self.download_dir_input.setText(os.path.join(os.environ.get("TEMP", ""), "PythoNest"))
        self.download_dir_input.setStyleSheet("color: #333333;")
        download_dir_layout.addWidget(self.download_dir_input)
        
        download_dir_btn = QPushButton("浏览...")
        download_dir_btn.clicked.connect(self.select_download_dir)
        download_dir_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #4a86e8;
                border: 1px solid #4a86e8;
                padding: 4px 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e6f0ff;
            }
        """)
        download_dir_layout.addWidget(download_dir_btn)
        
        download_layout.addLayout(download_dir_layout)
        
        # 版本选择模式
        version_select_label = QLabel("版本选择模式:")
        download_layout.addWidget(version_select_label)
        
        self.version_select_mode = QComboBox()
        self.version_select_mode.addItem("直接选择完整版本", "direct")
        self.version_select_mode.addItem("先选择主版本，再选择次版本", "two_step")
        self.version_select_mode.setStyleSheet("""
            QComboBox {
                color: #333333;
                background-color: white;
                border: 1px solid #dddddd;
                border-radius: 4px;
                padding: 4px;
            }
            QComboBox QAbstractItemView {
                color: #333333;
                background-color: white;
                selection-background-color: #e6f0ff;
                selection-color: #333333;
            }
        """)
        download_layout.addWidget(self.version_select_mode)
        
        # 自动安装选项
        self.auto_install_check = QCheckBox("下载后自动安装")
        self.auto_install_check.setChecked(True)
        download_layout.addWidget(self.auto_install_check)
        
        # SSL验证选项
        self.verify_ssl_check = QCheckBox("验证SSL证书 (禁用可解决某些镜像源的证书问题)")
        self.verify_ssl_check.setChecked(True)
        download_layout.addWidget(self.verify_ssl_check)
        
        download_group.setLayout(download_layout)
        source_layout.addWidget(download_group)
        
        # 添加一些垂直空间
        source_layout.addStretch()
        
        # 将选项卡添加到标签页控件
        tab_widget.addTab(search_tab, "搜索设置")
        tab_widget.addTab(source_tab, "下载源")
        
        layout.addWidget(tab_widget)
        
        # 按钮区域
        buttons_layout = QHBoxLayout()
        
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save_settings)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a86e8;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #3a76d8;
            }
        """)
        buttons_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #333333;
                border: 1px solid #dddddd;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #f5f5f5;
            }
        """)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def on_custom_source_toggled(self, checked):
        self.custom_source_input.setEnabled(checked)
        self.source_combo.setEnabled(not checked)
    
    def on_source_changed(self, index):
        # 可以在这里添加根据选择的源更改UI的代码
        pass
    
    def select_download_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择下载目录", self.download_dir_input.text())
        if dir_path:
            self.download_dir_input.setText(dir_path)
    
    def load_settings(self):
        # 从配置文件或全局设置中加载设置
        settings = None
        
        # 通过父窗口获取PythonManager实例并加载设置
        if isinstance(self.parent(), MainWindow):
            settings = self.parent().python_manager.settings
        
        if settings:
            # 设置搜索选项
            search_settings = settings.get("search", {})
            self.registry_check.setChecked(search_settings.get("use_registry", True))
            self.py_launcher_check.setChecked(search_settings.get("use_py_launcher", True))
            self.path_check.setChecked(search_settings.get("use_path", True))
            self.custom_paths_check.setChecked(search_settings.get("use_custom_paths", False))
            self.custom_paths_input.setText(search_settings.get("custom_paths", ""))
            
            # 设置源选项
            source_settings = settings.get("source", {})
            use_custom = source_settings.get("use_custom_source", False)
            self.custom_source_check.setChecked(use_custom)
            self.custom_source_input.setText(source_settings.get("custom_source_url", ""))
            self.custom_source_input.setEnabled(use_custom)
            
            selected_index = source_settings.get("selected_source_index", 0)
            if 0 <= selected_index < self.source_combo.count():
                self.source_combo.setCurrentIndex(selected_index)
            self.source_combo.setEnabled(not use_custom)
            
            # 设置下载选项
            download_settings = settings.get("download", {})
            self.download_dir_input.setText(download_settings.get("download_dir", 
                                           os.path.join(os.environ.get("TEMP", ""), "PythoNest")))
            self.auto_install_check.setChecked(download_settings.get("auto_install", True))
            self.verify_ssl_check.setChecked(download_settings.get("verify_ssl", True))
            
            # 设置版本选择模式
            version_select_mode = download_settings.get("version_select_mode", "direct")
            index = 0
            for i in range(self.version_select_mode.count()):
                if self.version_select_mode.itemData(i) == version_select_mode:
                    index = i
                    break
            self.version_select_mode.setCurrentIndex(index)
    
    def save_settings(self):
        # 保存设置到配置文件或全局设置
        settings = {
            "search": {
                "use_registry": self.registry_check.isChecked(),
                "use_py_launcher": self.py_launcher_check.isChecked(),
                "use_path": self.path_check.isChecked(),
                "use_custom_paths": self.custom_paths_check.isChecked(),
                "custom_paths": self.custom_paths_input.text()
            },
            "source": {
                "use_custom_source": self.custom_source_check.isChecked(),
                "custom_source_url": self.custom_source_input.text(),
                "selected_source_index": self.source_combo.currentIndex(),
                "selected_source_url": self.source_combo.currentData()
            },
            "download": {
                "download_dir": self.download_dir_input.text(),
                "auto_install": self.auto_install_check.isChecked(),
                "verify_ssl": self.verify_ssl_check.isChecked(),
                "version_select_mode": self.version_select_mode.currentData()
            }
        }
        
        # 通过父窗口获取PythonManager实例并保存设置
        if isinstance(self.parent(), MainWindow):
            success = self.parent().python_manager.save_settings(settings)
            if success:
                QMessageBox.information(self, "成功", "设置已成功保存")
            else:
                QMessageBox.warning(self, "警告", "设置保存失败，请检查权限")
        
        self.settings = settings
        self.accept()


class VersionSelectDialog(QDialog):
    def __init__(self, versions, parent=None):
        super().__init__(parent)
        self.versions = versions
        self.selected_version = None
        
        self.setWindowTitle("选择Python版本")
        self.setFixedSize(400, 500)
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel {
                color: #333333;
            }
        """)
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("选择要安装的Python版本")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 描述
        desc_label = QLabel("以下是可安装的Python版本列表，请选择一个版本进行安装：")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # 版本列表
        self.version_list = QListWidget()
        self.version_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #dddddd;
                border-radius: 5px;
                background-color: white;
                color: #333333;
            }
            QListWidget::item {
                height: 30px;
                padding: 5px;
                border-bottom: 1px solid #eeeeee;
            }
            QListWidget::item:selected {
                background-color: #e6f0ff;
                color: #333333;
            }
        """)
        
        # 添加版本到列表
        for version in self.versions:
            item = QListWidgetItem(f"Python {version}")
            major, minor, patch = version.split('.')
            
            # 为不同主版本使用不同图标或样式
            if major == '3':
                if minor in ['9', '10', '11', '12']:
                    item.setIcon(QIcon("src/ui/images/python_new.svg"))  # 最新版本
                else:
                    item.setIcon(QIcon("src/ui/images/python_new.svg"))  # 较旧版本
            else:
                # Python 2.x版本
                item.setIcon(QIcon("src/ui/images/python_old.png"))
            
            self.version_list.addItem(item)
        
        # 如果有版本，选中第一个
        if self.versions:
            self.version_list.setCurrentRow(0)
            
        # 当没有可用版本时显示提示
        if not self.versions:
            empty_item = QListWidgetItem("没有可用的Python版本")
            empty_item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.version_list.addItem(empty_item)
        
        self.version_list.itemDoubleClicked.connect(self.accept)
        layout.addWidget(self.version_list)
        
        # 版本详情
        self.version_details = QTextBrowser()
        self.version_details.setStyleSheet("""
            QTextBrowser {
                border: 1px solid #dddddd;
                border-radius: 5px;
                background-color: white;
                color: #333333;
            }
        """)
        self.version_details.setHtml("""
            <h3 style="color: #333333;">版本详情</h3>
            <p style="color: #333333;">选择一个版本查看详情</p>
        """)
        self.version_details.setFixedHeight(120)
        layout.addWidget(self.version_details)
        
        self.version_list.currentItemChanged.connect(self.update_version_details)
        
        # 按钮区域
        buttons_layout = QHBoxLayout()
        
        install_btn = QPushButton("安装")
        install_btn.clicked.connect(self.accept)
        install_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a86e8;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #3a76d8;
            }
        """)
        buttons_layout.addWidget(install_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #333333;
                border: 1px solid #dddddd;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #f5f5f5;
            }
        """)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def update_version_details(self, current, previous):
        if not current or not self.versions:
            return
            
        row = self.version_list.currentRow()
        if row >= 0 and row < len(self.versions):
            version = self.versions[row]
            major, minor, patch = version.split('.')
            
            # 显示版本详情
            self.version_details.setHtml(f"""
                <h3 style="color: #333333;">Python {version}</h3>
                <p style="color: #333333;">
                    <b>发布日期:</b> 获取中...<br>
                    <b>稳定性:</b> {'稳定版' if int(major) >= 3 and int(minor) >= 8 else '维护版'}<br>
                    <b>主要特性:</b> {'新的语法特性和性能改进' if int(major) >= 3 and int(minor) >= 10 else '标准库更新和错误修复'}
                </p>
                <p style="color: #666666;">点击"安装"开始下载并安装此版本</p>
            """)
    
    def get_selected_version(self):
        row = self.version_list.currentRow()
        if row >= 0 and row < len(self.versions):
            return self.versions[row]
        return None


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.python_manager = PythonManager()
        self.venv_manager = VenvManager()
        self.package_manager = PackageManager()
        
        # 禁用系统颜色主题，强制使用浅色主题
        self.force_light_theme()
        
        self.init_ui()
        
    def force_light_theme(self):
        """强制使用浅色主题，解决系统深色主题导致的文字显示问题"""
        app = QApplication.instance()
        
        # 创建浅色调色板
        palette = QPalette()
        
        # 设置窗口和控件背景色
        palette.setColor(QPalette.ColorRole.Window, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(245, 245, 245))
        
        # 设置文本颜色
        palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
        
        # 设置按钮颜色
        palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
        
        # 设置高亮和选中颜色
        palette.setColor(QPalette.ColorRole.Highlight, QColor(74, 134, 232))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        
        # 设置链接颜色
        palette.setColor(QPalette.ColorRole.Link, QColor(74, 134, 232))
        palette.setColor(QPalette.ColorRole.LinkVisited, QColor(82, 102, 172))
        
        # 设置禁用状态颜色
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(150, 150, 150))
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(150, 150, 150))
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(150, 150, 150))
        
        # 应用调色板到应用程序
        app.setPalette(palette)
        
        # 确保特定UI元素不受系统主题影响
        app.setStyleSheet("""
            QMainWindow, QDialog, QWidget {
                background-color: white;
                color: black;
            }
            QLabel {
                color: black;
            }
            QGroupBox {
                color: black;
            }
            QTabWidget::pane {
                background-color: white;
                border: 1px solid #dddddd;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                color: black;
                padding: 8px 16px;
                border: 1px solid #dddddd;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 1px solid white;
            }
            QTableView, QListView, QTreeView {
                background-color: white;
                alternate-background-color: #f5f5f5;
                color: black;
            }
            QMenu {
                background-color: white;
                color: black;
            }
            QMenu::item:selected {
                background-color: #4a86e8;
                color: white;
            }
            QMenuBar {
                background-color: #f5f5f5;
                color: black;
            }
            QMenuBar::item:selected {
                background-color: #e0e0e0;
            }
        """)
        
    def init_ui(self):
        self.setWindowTitle("PythoNest - Python版本管理器")
        self.setMinimumSize(900, 700)
        
        # 设置应用图标
        # self.setWindowIcon(QIcon("icons/app_icon.png"))
        
        # 创建菜单栏 - 修改这部分确保菜单栏可见
        menu_bar = self.menuBar()
        menu_bar.setNativeMenuBar(False)  # 禁用原生菜单栏，确保在所有平台上显示
        self.create_menu_bar(menu_bar)
        
        # 创建选项卡部件
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.tabs.setDocumentMode(True)
        
        # 添加各个功能选项卡
        self.setup_version_tab()
        
        # 临时添加虚拟环境和包管理选项卡
        venv_tab = QWidget()
        venv_layout = QVBoxLayout()
        venv_label = QLabel("虚拟环境管理功能将在后续版本中实现")
        venv_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        venv_layout.addWidget(venv_label)
        venv_tab.setLayout(venv_layout)
        self.tabs.addTab(venv_tab, "虚拟环境")
        
        packages_tab = QWidget()
        packages_layout = QVBoxLayout()
        packages_label = QLabel("包管理功能将在后续版本中实现")
        packages_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        packages_layout.addWidget(packages_label)
        packages_tab.setLayout(packages_layout)
        self.tabs.addTab(packages_tab, "包管理")
        
        # 设置样式
        self.set_styles()
        
        self.setCentralWidget(self.tabs)
        
        # 设置状态栏
        self.statusBar().showMessage("准备就绪")
    
    def create_menu_bar(self, menu_bar):
        # 文件菜单
        file_menu = menu_bar.addMenu("文件")
        
        refresh_action = QAction("刷新", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.refresh_all)
        file_menu.addAction(refresh_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 编辑菜单
        edit_menu = menu_bar.addMenu("编辑")
        
        settings_action = QAction("设置", self)
        settings_action.triggered.connect(self.show_settings)
        edit_menu.addAction(settings_action)
        
        # 关于菜单
        help_menu = menu_bar.addMenu("关于")
        
        about_action = QAction("关于 PythoNest", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_version_tab(self):
        """设置Python版本管理选项卡"""
        self.version_tab = QWidget()
        version_layout = QVBoxLayout()
        version_layout.setSpacing(10)
        version_layout.setContentsMargins(15, 15, 15, 15)
        
        # 标题和描述
        title_label = QLabel("Python版本管理")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        title_label.setFont(title_font)
        version_layout.addWidget(title_label)
        
        desc_label = QLabel("管理您计算机上安装的Python版本，安装新版本或设置默认版本。")
        desc_label.setWordWrap(True)
        version_layout.addWidget(desc_label)
        
        # 已安装版本列表
        installed_group = QGroupBox("已安装的Python版本")
        installed_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #dddddd;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
            }
        """)
        
        installed_layout = QVBoxLayout()
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("刷新")
        refresh_btn.setIcon(QIcon("src/ui/images/EpRefresh.svg"))
        refresh_btn.clicked.connect(self.refresh_versions)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #4a86e8;
                border: 1px solid #4a86e8;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e6f0ff;
            }
        """)
        toolbar_layout.addWidget(refresh_btn)
        
        toolbar_layout.addStretch()
        
        install_btn = QPushButton("安装新的Python版本")
        install_btn.setIcon(QIcon("src/ui/images/EpDownload.svg"))
        install_btn.clicked.connect(self.install_new_version)
        install_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a86e8;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #3a76d8;
            }
        """)
        toolbar_layout.addWidget(install_btn)
        
        installed_layout.addLayout(toolbar_layout)
        
        # 版本列表
        self.version_list = QListWidget()
        self.version_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #dddddd;
                border-radius: 4px;
                background-color: white;
                color: #333333;
            }
            QListWidget::item {
                height: 30px;
                padding: 5px;
                border-bottom: 1px solid #eeeeee;
            }
            QListWidget::item:selected {
                background-color: #e6f0ff;
                color: #333333;
            }
        """)
        self.version_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        installed_layout.addWidget(self.version_list)
        
        # 版本操作按钮
        version_actions_layout = QHBoxLayout()
        
        set_default_btn = QPushButton("设为默认")
        set_default_btn.clicked.connect(self.set_default_version)
        set_default_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a86e8;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #3a76d8;
            }
        """)
        version_actions_layout.addWidget(set_default_btn)
        
        uninstall_btn = QPushButton("卸载")
        uninstall_btn.clicked.connect(self.uninstall_version)
        uninstall_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #e04a3f;
                border: 1px solid #e04a3f;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #ffeeee;
            }
        """)
        version_actions_layout.addWidget(uninstall_btn)
        
        installed_layout.addLayout(version_actions_layout)
        installed_group.setLayout(installed_layout)
        version_layout.addWidget(installed_group)
        
        # 版本详情区域
        details_group = QGroupBox("版本详情")
        details_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #dddddd;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
            }
        """)
        
        details_layout = QVBoxLayout()
        
        self.version_details = QTextBrowser()
        self.version_details.setStyleSheet("""
            QTextBrowser {
                border: 1px solid #dddddd;
                border-radius: 4px;
                background-color: white;
                color: #333333;
            }
        """)
        self.version_details.setHtml("""
            <h3 style="color: #333333;">版本详情</h3>
            <p style="color: #333333;">选择一个版本查看详情</p>
        """)
        details_layout.addWidget(self.version_details)
        
        details_group.setLayout(details_layout)
        version_layout.addWidget(details_group)
        
        # 版本信息更新
        self.version_list.currentItemChanged.connect(self.update_version_details)
        
        self.version_tab.setLayout(version_layout)
        self.tabs.addTab(self.version_tab, "版本管理")
        
        # 初始刷新版本列表
        QTimer.singleShot(100, self.refresh_versions)

    def refresh_versions(self):
        """刷新Python版本列表"""
        self.statusBar().showMessage("正在刷新Python版本列表...")
        self.version_list.clear()
        
        # 使用QThread运行耗时操作
        class VersionThread(QThread):
            versions_ready = pyqtSignal(list)
            
            def __init__(self, python_manager):
                super().__init__()
                self.python_manager = python_manager
            
            def run(self):
                versions = self.python_manager.get_installed_versions()
                self.versions_ready.emit(versions)
        
        self.version_thread = VersionThread(self.python_manager)
        self.version_thread.versions_ready.connect(self.on_versions_ready)
        self.version_thread.start()

    def on_versions_ready(self, versions):
        """当版本列表刷新完成时调用"""
        if not versions:
            self.version_list.addItem("未找到已安装的Python版本")
            empty_item = self.version_list.item(0)
            empty_item.setFlags(Qt.ItemFlag.NoItemFlags)
        else:
            # 获取当前系统默认Python版本
            default_version = self.get_default_python_version()
            
            for version in versions:
                item = QListWidgetItem(f"Python {version}")
                major, minor = version.split(".")[:2]
                
                # 为不同主版本使用不同图标或样式
                if major == '3':
                    if minor in ['9', '10', '11', '12']:
                        item.setIcon(QIcon("src/ui/images/python_new.svg"))  # 最新版本
                    else:
                        item.setIcon(QIcon("src/ui/images/python_new.svg"))  # 较旧版本
                else:
                    # Python 2.x版本
                    item.setIcon(QIcon("src/ui/images/python_old.png"))
                
                # 标记默认版本
                if version == default_version:
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                    item.setText(f"Python {version} (默认)")
                
                self.version_list.addItem(item)
        
        # 如果有版本，选中第一个
        if versions and self.version_list.count() > 0:
            self.version_list.setCurrentRow(0)
        
        self.statusBar().showMessage("Python版本刷新完成", 3000)

    def get_default_python_version(self):
        """获取系统默认Python版本"""
        try:
            # 运行python --version命令
            result = subprocess.run(["python", "--version"], 
                                   capture_output=True, text=True)
            if result.returncode == 0:
                version_output = result.stdout or result.stderr
                version_match = re.search(r"Python (\d+\.\d+\.\d+)", version_output)
                if version_match:
                    return version_match.group(1)
        except:
            pass
        
        return None

    def update_version_details(self, current, previous):
        """更新选中版本的详细信息"""
        if not current:
            return
        
        version_text = current.text()
        version_match = re.search(r"Python (\d+\.\d+\.\d+)", version_text)
        
        if version_match:
            version = version_match.group(1)
            major, minor, patch = version.split(".")
            
            # 获取安装路径
            install_path = self.python_manager._get_python_install_path(version)
            
            # 检查是否为默认版本
            is_default = "默认" in version_text
            default_status = "是" if is_default else "否"
            
            # 构建HTML内容
            html_content = f"""
            <h3 style="color: #333333;">Python {version}</h3>
            <p style="color: #333333;">
                <b>安装路径:</b> {install_path or "未知"}<br>
                <b>默认版本:</b> {default_status}<br>
                <b>版本类型:</b> {"稳定版" if int(major) >= 3 and int(minor) >= 8 else "维护版"}<br>
            </p>
            """
            
            # 添加版本特性信息
            if int(major) == 3:
                features = {
                    "12": "持续增强性能、内存和稳定性改进。增加了新的内置编辑器增强功能和格式化选项。",
                    "11": "新的字符串格式化模块、性能优化和垃圾回收改进。",
                    "10": "结构化模式匹配、精确的GIL实现和更好的错误消息。",
                    "9": "时区改进、更灵活的装饰器和字典合并操作符。",
                    "8": "赋值表达式、仅位置参数和f-string格式说明符。",
                    "7": "数据类、上下文变量和优化的dict实现。"
                }
                
                if minor in features:
                    html_content += f"""
                    <p style="color: #333333;"><b>主要特性:</b> {features[minor]}</p>
                    """
            
            self.version_details.setHtml(html_content)

    def install_new_version(self):
        """安装新的Python版本"""
        try:
            # 获取版本选择模式
            version_select_mode = self.python_manager.settings["download"].get("version_select_mode", "direct")
            
            if version_select_mode == "direct":
                # 直接选择完整版本模式
                self._install_direct_mode()
            else:
                # 两步选择模式（先选择主版本，再选择次版本）
                self._install_two_step_mode()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"安装新版本失败: {str(e)}")
            logging.error(f"安装新版本失败: {str(e)}")
    
    def _install_direct_mode(self):
        """直接选择完整版本模式"""
        # 获取可用版本
        versions = self.python_manager.get_available_versions()
        
        if not versions:
            QMessageBox.warning(self, "警告", "没有找到可用的Python版本")
            return
        
        # 创建并显示版本选择对话框
        version_dialog = VersionSelectDialog(versions, self)
        if version_dialog.exec():
            selected_version = version_dialog.get_selected_version()
            if selected_version:
                self._download_and_install_version(selected_version)
    
    def _install_two_step_mode(self):
        """两步选择模式（先选择主版本，再选择次版本）"""
        # 获取主版本列表
        major_versions = self.python_manager.get_major_versions()
        
        if not major_versions:
            QMessageBox.warning(self, "警告", "没有找到可用的Python版本")
            return
        
        # 创建并显示主版本选择对话框
        major_dialog = MajorVersionSelectDialog(major_versions, self)
        if major_dialog.exec():
            # 获取选中的主版本及其对应的次版本列表
            selected_major, minor_versions = major_dialog.get_selected_major_version()
            
            if selected_major and minor_versions:
                # 创建并显示次版本选择对话框
                minor_dialog = MinorVersionSelectDialog(selected_major, minor_versions, self)
                if minor_dialog.exec():
                    selected_version = minor_dialog.get_selected_version()
                    if selected_version:
                        self._download_and_install_version(selected_version)
    
    def _download_and_install_version(self, version):
        """下载并安装指定版本"""
        # 创建下载进度对话框
        progress_dialog = DownloadProgressDialog(self)
        progress_dialog.setWindowTitle(f"下载Python {version}")
        progress_dialog.show()
        
        # 定义进度回调函数
        def update_progress(progress):
            progress_dialog.update_progress(progress)
        
        # 在后台线程中下载
        download_thread = DownloadThread(self.python_manager, version, update_progress)
        download_thread.download_complete.connect(self._handle_download_complete)
        download_thread.download_error.connect(self._handle_download_error)
        download_thread.start()
        
        # 存储当前下载信息
        self.current_download = {
            "version": version,
            "thread": download_thread,
            "progress_dialog": progress_dialog
        }
    
    def _handle_download_complete(self, version, installer_path):
        """处理下载完成事件"""
        if hasattr(self, 'current_download') and self.current_download:
            self.current_download["progress_dialog"].close()
            
            # 检查是否自动安装
            auto_install = self.python_manager.settings["download"].get("auto_install", True)
            
            if auto_install:
                # 自动安装
                self.statusBar().showMessage(f"正在安装Python {version}...")
                
                try:
                    # 安装Python
                    success = self.python_manager.install_version(version, installer_path)
                    
                    if success:
                        QMessageBox.information(self, "安装成功", f"Python {version} 已成功安装")
                        self.refresh_versions()
                    else:
                        QMessageBox.warning(self, "安装失败", f"Python {version} 安装失败")
                except Exception as e:
                    QMessageBox.critical(self, "安装错误", f"安装Python {version}时发生错误: {str(e)}")
                    logging.error(f"安装Python {version}时发生错误: {str(e)}")
            else:
                # 提示用户手动安装
                result = QMessageBox.question(
                    self, 
                    "下载完成", 
                    f"Python {version} 已下载完成，是否立即安装？\n\n安装文件位置: {installer_path}",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if result == QMessageBox.StandardButton.Yes:
                    try:
                        # 安装Python
                        success = self.python_manager.install_version(version, installer_path)
                        
                        if success:
                            QMessageBox.information(self, "安装成功", f"Python {version} 已成功安装")
                            self.refresh_versions()
                        else:
                            QMessageBox.warning(self, "安装失败", f"Python {version} 安装失败")
                    except Exception as e:
                        QMessageBox.critical(self, "安装错误", f"安装Python {version}时发生错误: {str(e)}")
                        logging.error(f"安装Python {version}时发生错误: {str(e)}")
            
            # 清除当前下载信息
            self.current_download = None
    
    def _handle_download_error(self, version, error_msg):
        """处理下载错误事件"""
        if hasattr(self, 'current_download') and self.current_download:
            self.current_download["progress_dialog"].close()
            QMessageBox.critical(self, "下载错误", f"下载Python {version}失败: {error_msg}")
            self.current_download = None

    def set_default_version(self):
        """设置默认Python版本"""
        current_item = self.version_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "未选择版本", "请先选择一个Python版本")
            return
        
        version_text = current_item.text()
        version_match = re.search(r"Python (\d+\.\d+\.\d+)", version_text)
        
        if not version_match:
            return
        
        version = version_match.group(1)
        
        # 确认对话框
        reply = QMessageBox.question(
            self,
            "设置默认版本",
            f"确定要将Python {version} 设置为系统默认版本吗？\n\n这将修改系统环境变量。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.statusBar().showMessage(f"正在设置Python {version} 为默认版本...")
            
            # 使用QThread执行耗时操作
            class DefaultVersionThread(QThread):
                operation_complete = pyqtSignal(bool)
                
                def __init__(self, python_manager, version):
                    super().__init__()
                    self.python_manager = python_manager
                    self.version = version
                
                def run(self):
                    success = self.python_manager.activate_version(self.version)
                    self.operation_complete.emit(success)
            
            self.default_thread = DefaultVersionThread(self.python_manager, version)
            
            def on_operation_complete(success):
                if success:
                    self.statusBar().showMessage(f"Python {version} 已设为默认版本", 3000)
                    self.refresh_versions()
                else:
                    self.statusBar().showMessage("设置默认版本失败", 3000)
                    QMessageBox.warning(
                        self, 
                        "操作失败", 
                        "设置默认版本失败，可能需要管理员权限。"
                    )
            
            self.default_thread.operation_complete.connect(on_operation_complete)
            self.default_thread.start()

    def uninstall_version(self):
        """卸载Python版本"""
        current_item = self.version_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "未选择版本", "请先选择一个Python版本")
            return
        
        version_text = current_item.text()
        version_match = re.search(r"Python (\d+\.\d+\.\d+)", version_text)
        
        if not version_match:
            return
        
        version = version_match.group(1)
        
        # 检查是否为默认版本
        if "默认" in version_text:
            QMessageBox.warning(
                self,
                "无法卸载",
                "无法卸载当前默认的Python版本。请先设置其他版本为默认，然后再卸载此版本。"
            )
            return
        
        # 确认对话框
        reply = QMessageBox.question(
            self,
            "卸载确认",
            f"确定要卸载Python {version} 吗？\n\n这将从您的系统中移除此版本的Python。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.statusBar().showMessage(f"正在卸载Python {version}...")
            
            # 使用QThread执行耗时操作
            class UninstallThread(QThread):
                operation_complete = pyqtSignal(bool)
                
                def __init__(self, python_manager, version):
                    super().__init__()
                    self.python_manager = python_manager
                    self.version = version
                
                def run(self):
                    success = self.python_manager.uninstall_version(self.version)
                    self.operation_complete.emit(success)
            
            self.uninstall_thread = UninstallThread(self.python_manager, version)
            
            def on_operation_complete(success):
                if success:
                    self.statusBar().showMessage(f"Python {version} 已卸载", 3000)
                    self.refresh_versions()
                else:
                    self.statusBar().showMessage("卸载失败", 3000)
                    QMessageBox.warning(
                        self, 
                        "操作失败", 
                        "卸载Python版本失败，可能需要管理员权限或程序正在使用。"
                    )
            
            self.uninstall_thread.operation_complete.connect(on_operation_complete)
            self.uninstall_thread.start()

    def set_styles(self):
        # 为了保持程序正常运行，但不自定义UI颜色
        pass
    
    def refresh_all(self):
        """刷新所有数据"""
        self.refresh_versions()
        self.refresh_venvs()
        self.refresh_packages()
        self.statusBar().showMessage("所有数据已刷新", 3000)
    
    def show_settings(self):
        """显示设置对话框"""
        settings_dialog = SettingsDialog(self)
        settings_dialog.exec()
    
    def show_about(self):
        """显示关于对话框"""
        about_dialog = AboutDialog(self)
        about_dialog.exec()


class MajorVersionSelectDialog(QDialog):
    def __init__(self, major_versions, parent=None):
        super().__init__(parent)
        self.major_versions = major_versions  # 格式: [("3.12", ["3.12.0", ...]), ("3.11", ["3.11.5", ...])]
        self.selected_major = None
        
        self.setWindowTitle("选择Python主版本")
        self.setFixedSize(400, 450)
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel {
                color: #333333;
            }
        """)
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("选择Python主版本")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 描述
        desc_label = QLabel("请选择要安装的Python主版本（如3.12、3.11等）：")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # 版本列表
        self.version_list = QListWidget()
        self.version_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #dddddd;
                border-radius: 5px;
                background-color: white;
                color: #333333;
            }
            QListWidget::item {
                height: 30px;
                padding: 5px;
                border-bottom: 1px solid #eeeeee;
            }
            QListWidget::item:selected {
                background-color: #e6f0ff;
                color: #333333;
            }
        """)
        
        # 添加版本到列表
        for major_version, minor_versions in self.major_versions:
            item = QListWidgetItem(f"Python {major_version}")
            
            # 为不同主版本使用不同图标或样式
            major = major_version.split('.')[0]
            if major == '3':
                minor = major_version.split('.')[1]
                if int(minor) >= 9:
                    item.setIcon(QIcon("website/images/version-tab.svg"))  # 最新版本
                else:
                    item.setIcon(QIcon("website/images/version-tab.png"))  # 较旧版本
            else:
                # Python 2.x版本
                item.setIcon(QIcon("website/images/logo.png"))
            
            # 添加次版本数量信息
            item.setData(Qt.ItemDataRole.UserRole, major_version)
            item.setText(f"Python {major_version} ({len(minor_versions)} 个可用版本)")
            
            self.version_list.addItem(item)
        
        # 如果有版本，选中第一个
        if self.major_versions:
            self.version_list.setCurrentRow(0)
            
        # 当没有可用版本时显示提示
        if not self.major_versions:
            empty_item = QListWidgetItem("没有可用的Python版本")
            empty_item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.version_list.addItem(empty_item)
        
        self.version_list.itemDoubleClicked.connect(self.accept)
        layout.addWidget(self.version_list)
        
        # 版本详情
        self.version_details = QTextBrowser()
        self.version_details.setStyleSheet("""
            QTextBrowser {
                border: 1px solid #dddddd;
                border-radius: 5px;
                background-color: white;
                color: #333333;
            }
        """)
        self.version_details.setHtml("""
            <h3 style="color: #333333;">版本详情</h3>
            <p style="color: #333333;">选择一个主版本查看详情</p>
        """)
        self.version_details.setFixedHeight(120)
        layout.addWidget(self.version_details)
        
        self.version_list.currentItemChanged.connect(self.update_version_details)
        
        # 按钮区域
        buttons_layout = QHBoxLayout()
        
        select_btn = QPushButton("选择")
        select_btn.clicked.connect(self.accept)
        select_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a86e8;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #3a76d8;
            }
        """)
        buttons_layout.addWidget(select_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #333333;
                border: 1px solid #dddddd;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #f5f5f5;
            }
        """)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def update_version_details(self, current, previous):
        if not current or not self.major_versions:
            return
            
        major_version = current.data(Qt.ItemDataRole.UserRole)
        if not major_version:
            return
            
        # 找到对应的主版本信息
        minor_versions = []
        for mv, versions in self.major_versions:
            if mv == major_version:
                minor_versions = versions
                break
        
        # 显示版本详情
        major, minor = major_version.split('.')
        
        # 构建版本特性信息
        features = ""
        if major == '3':
            if minor == '12':
                features = "Python 3.12引入了更快的启动时间、更好的错误消息和f-string改进。"
            elif minor == '11':
                features = "Python 3.11提供了更快的执行速度、更好的错误消息和异常处理。"
            elif minor == '10':
                features = "Python 3.10引入了结构化模式匹配、更好的类型提示和更精确的错误位置。"
            elif minor == '9':
                features = "Python 3.9添加了字典合并操作符、灵活的装饰器和类型提示泛型。"
            elif minor == '8':
                features = "Python 3.8引入了赋值表达式、仅位置参数和f-string调试支持。"
        
        self.version_details.setHtml(f"""
            <h3 style="color: #333333;">Python {major_version}</h3>
            <p style="color: #333333;">
                <b>可用版本数量:</b> {len(minor_versions)}<br>
                <b>最新版本:</b> {minor_versions[0] if minor_versions else '无'}<br>
                <b>主要特性:</b> {features}
            </p>
            <p style="color: #666666;">点击"选择"进入次版本选择</p>
        """)
    
    def get_selected_major_version(self):
        """获取选中的主版本及其对应的次版本列表"""
        current_item = self.version_list.currentItem()
        if current_item:
            major_version = current_item.data(Qt.ItemDataRole.UserRole)
            for mv, versions in self.major_versions:
                if mv == major_version:
                    return mv, versions
        return None, []


class MinorVersionSelectDialog(QDialog):
    def __init__(self, major_version, minor_versions, parent=None):
        super().__init__(parent)
        self.major_version = major_version  # 例如 "3.12"
        self.minor_versions = minor_versions  # 例如 ["3.12.0", "3.12.1", ...]
        self.selected_version = None
        
        self.setWindowTitle(f"选择Python {major_version}版本")
        self.setFixedSize(400, 500)
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel {
                color: #333333;
            }
        """)
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel(f"选择Python {self.major_version}版本")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 描述
        desc_label = QLabel(f"以下是Python {self.major_version}的可用版本，请选择一个进行安装：")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # 版本列表
        self.version_list = QListWidget()
        self.version_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #dddddd;
                border-radius: 5px;
                background-color: white;
                color: #333333;
            }
            QListWidget::item {
                height: 30px;
                padding: 5px;
                border-bottom: 1px solid #eeeeee;
            }
            QListWidget::item:selected {
                background-color: #e6f0ff;
                color: #333333;
            }
        """)
        
        # 添加版本到列表
        for version in self.minor_versions:
            item = QListWidgetItem(f"Python {version}")
            
            # 使用相同的图标
            major, minor = self.major_version.split('.')
            if major == '3' and int(minor) >= 9:
                item.setIcon(QIcon("website/images/version-tab.svg"))
            else:
                item.setIcon(QIcon("website/images/version-tab.png"))
            
            self.version_list.addItem(item)
        
        # 如果有版本，选中第一个
        if self.minor_versions:
            self.version_list.setCurrentRow(0)
            
        # 当没有可用版本时显示提示
        if not self.minor_versions:
            empty_item = QListWidgetItem(f"没有可用的Python {self.major_version}版本")
            empty_item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.version_list.addItem(empty_item)
        
        self.version_list.itemDoubleClicked.connect(self.accept)
        layout.addWidget(self.version_list)
        
        # 版本详情
        self.version_details = QTextBrowser()
        self.version_details.setStyleSheet("""
            QTextBrowser {
                border: 1px solid #dddddd;
                border-radius: 5px;
                background-color: white;
                color: #333333;
            }
        """)
        self.version_details.setHtml("""
            <h3 style="color: #333333;">版本详情</h3>
            <p style="color: #333333;">选择一个版本查看详情</p>
        """)
        self.version_details.setFixedHeight(120)
        layout.addWidget(self.version_details)
        
        self.version_list.currentItemChanged.connect(self.update_version_details)
        
        # 按钮区域
        buttons_layout = QHBoxLayout()
        
        install_btn = QPushButton("安装")
        install_btn.clicked.connect(self.accept)
        install_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a86e8;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #3a76d8;
            }
        """)
        buttons_layout.addWidget(install_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #333333;
                border: 1px solid #dddddd;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #f5f5f5;
            }
        """)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def update_version_details(self, current, previous):
        if not current or not self.minor_versions:
            return
            
        row = self.version_list.currentRow()
        if row >= 0 and row < len(self.minor_versions):
            version = self.minor_versions[row]
            major, minor, patch = version.split('.')
            
            # 显示版本详情
            self.version_details.setHtml(f"""
                <h3 style="color: #333333;">Python {version}</h3>
                <p style="color: #333333;">
                    <b>发布日期:</b> 获取中...<br>
                    <b>稳定性:</b> {'稳定版' if int(major) >= 3 and int(minor) >= 8 else '维护版'}<br>
                    <b>主要特性:</b> {'新的语法特性和性能改进' if int(major) >= 3 and int(minor) >= 10 else '标准库更新和错误修复'}
                </p>
                <p style="color: #666666;">点击"安装"开始下载并安装此版本</p>
            """)
    
    def get_selected_version(self):
        row = self.version_list.currentRow()
        if row >= 0 and row < len(self.minor_versions):
            return self.minor_versions[row]
        return None


class DownloadThread(QThread):
    download_complete = pyqtSignal(str, str)  # version, installer_path
    download_error = pyqtSignal(str, str)     # version, error_message
    
    def __init__(self, python_manager, version, progress_callback=None):
        super().__init__()
        self.python_manager = python_manager
        self.version = version
        self.progress_callback = progress_callback
        self.cancelled = False
    
    def run(self):
        try:
            installer_path = self.python_manager.download_version(
                self.version, 
                progress_callback=self.progress_callback
            )
            
            if installer_path and not self.cancelled:
                self.download_complete.emit(self.version, installer_path)
            elif self.cancelled:
                self.download_error.emit(self.version, "下载已取消")
            else:
                self.download_error.emit(self.version, "下载失败，未获取到安装文件路径")
        except Exception as e:
            self.download_error.emit(self.version, str(e))
    
    def cancel(self):
        self.cancelled = True


class DownloadProgressDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(400, 180)
        self.setStyleSheet("background-color: white;")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        
        self.last_downloaded = 0
        self.last_time = 0
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # 状态标签
        self.status_label = QLabel("正在准备下载...")
        self.status_label.setStyleSheet("color: #333333;")
        layout.addWidget(self.status_label)
        
        # 下载大小标签
        self.size_label = QLabel("已下载: 0 MB / 0 MB")
        self.size_label.setStyleSheet("color: #666666;")
        self.size_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.size_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #dddddd;
                border-radius: 4px;
                background-color: #f5f5f5;
                color: #333333;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4a86e8;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # 速度标签
        self.speed_label = QLabel("下载速度: 0 KB/s")
        self.speed_label.setStyleSheet("color: #666666;")
        self.speed_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.speed_label)
        
        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #333333;
                border: 1px solid #dddddd;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #f5f5f5;
            }
        """)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def update_progress(self, progress):
        """更新下载进度
        
        参数:
            progress: 字典，包含以下键:
                - downloaded: 已下载的字节数
                - total: 总字节数
                - percentage: 下载进度百分比
        """
        downloaded = progress.get('downloaded', 0)
        total = progress.get('total', 0)
        percentage = progress.get('percentage', 0)
        
        # 更新进度条
        self.progress_bar.setValue(percentage)
        
        # 更新大小标签
        downloaded_mb = downloaded / (1024 * 1024)
        total_mb = total / (1024 * 1024)
        self.size_label.setText(f"已下载: {downloaded_mb:.1f} MB / {total_mb:.1f} MB")
        
        # 更新窗口标题
        self.setWindowTitle(f"下载Python - {percentage}%")
        
        # 计算下载速度
        current_time = time.time()
        if self.last_time > 0:
            time_diff = current_time - self.last_time
            if time_diff >= 1.0:  # 每秒更新一次速度
                bytes_diff = downloaded - self.last_downloaded
                speed = bytes_diff / time_diff / 1024  # KB/s
                
                if speed >= 1024:
                    self.speed_label.setText(f"下载速度: {speed/1024:.2f} MB/s")
                else:
                    self.speed_label.setText(f"下载速度: {speed:.1f} KB/s")
                
                self.last_downloaded = downloaded
                self.last_time = current_time
        else:
            self.last_downloaded = downloaded
            self.last_time = current_time 