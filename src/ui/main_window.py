from PyQt6.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
                         QLabel, QPushButton, QListWidget, QMessageBox,
                         QHBoxLayout, QLineEdit, QComboBox, QGroupBox, QFormLayout,
                         QMenuBar, QMenu, QDialog, QTextEdit, QTextBrowser, QSplitter, QApplication)
from PyQt6.QtCore import Qt, QSize, QUrl
from PyQt6.QtGui import QIcon, QAction, QFont, QColor, QPalette, QDesktopServices

import sys
import os
from pathlib import Path

from src.core.python_manager import PythonManager
from src.core.venv_manager import VenvManager
from src.core.package_manager import PackageManager


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("关于 PythoNest")
        self.setFixedSize(500, 400)
        
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
        layout.addWidget(title_label)
        
        # 版本
        version_label = QLabel("版本: 1.0.0")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)
        
        # 描述 - 使用QTextBrowser代替QTextEdit以支持链接点击
        description = QTextBrowser()
        description.setOpenExternalLinks(True)  # 这个设置使链接可以直接在浏览器中打开
        description.setHtml("""
        <div style='text-align:center;'>
            <p>PythoNest是一个功能强大的Python版本管理工具，帮助用户轻松管理多个Python版本、虚拟环境和包。</p>
            
            <p><b>主要功能：</b></p>
            <ul style='list-style-position: inside;'>
                <li>管理多个Python版本</li>
                <li>创建和管理虚拟环境</li>
                <li>搜索、安装和管理包</li>
            </ul>
            
            <p><b>作者：</b> dhjs0000</p>
            <p><b>GitHub：</b> <a href='https://github.com/dhjs0000/PythoNest'>https://github.com/dhjs0000/PythoNest</a></p>
            <p><b>Bilibili：</b> <a href='https://space.bilibili.com/430218185'>https://space.bilibili.com/430218185</a></p>
            
            <p style='margin-top:20px;'><b>开源协议：</b></p>
            <p>本软件基于GNU通用公共许可证第3版(GPL-3.0)发布</p>
            <p>您可以自由使用、修改和分发本软件，但需要遵守GPL-3.0协议的条款。</p>
        </div>
        """)
        layout.addWidget(description)
        
        self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.python_manager = PythonManager()
        self.venv_manager = VenvManager()
        self.package_manager = PackageManager()
        self.init_ui()
        
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
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setDocumentMode(True)
        
        # 添加各个功能选项卡
        self.tab_widget.addTab(self.create_versions_tab(), "版本管理")
        self.tab_widget.addTab(self.create_venv_tab(), "虚拟环境")
        self.tab_widget.addTab(self.create_packages_tab(), "包管理")
        
        # 设置样式
        self.set_styles()
        
        self.setCentralWidget(self.tab_widget)
        
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
    
    def create_versions_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # 已安装版本列表
        installed_group_label = QLabel("已安装的Python版本:")
        layout.addWidget(installed_group_label)
        
        self.installed_list = QListWidget()
        layout.addWidget(self.installed_list)
        
        # 刷新按钮
        refresh_btn = QPushButton("刷新列表")
        refresh_btn.clicked.connect(self.refresh_versions)
        layout.addWidget(refresh_btn)
        
        # 可安装版本列表
        available_group_label = QLabel("可安装的Python版本:")
        layout.addWidget(available_group_label)
        
        self.available_list = QListWidget()
        layout.addWidget(self.available_list)
        
        # 操作按钮
        install_btn = QPushButton("安装选中版本")
        install_btn.clicked.connect(self.install_version)
        layout.addWidget(install_btn)
        
        uninstall_btn = QPushButton("卸载选中版本")
        uninstall_btn.clicked.connect(self.uninstall_version)
        layout.addWidget(uninstall_btn)
        
        activate_btn = QPushButton("激活选中版本")
        activate_btn.clicked.connect(self.activate_version)
        layout.addWidget(activate_btn)
        
        tab.setLayout(layout)
        return tab
    
    def create_venv_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # 创建虚拟环境区域
        create_group = QGroupBox("创建虚拟环境")
        create_layout = QFormLayout()
        
        self.venv_name_input = QLineEdit()
        create_layout.addRow("名称:", self.venv_name_input)
        
        self.venv_python_combo = QComboBox()
        create_layout.addRow("Python版本:", self.venv_python_combo)
        
        create_btn = QPushButton("创建")
        create_btn.clicked.connect(self.create_venv)
        create_layout.addRow("", create_btn)
        
        create_group.setLayout(create_layout)
        layout.addWidget(create_group)
        
        # 已有虚拟环境列表
        venvs_group = QGroupBox("已有虚拟环境")
        venvs_layout = QVBoxLayout()
        
        self.venvs_list = QListWidget()
        venvs_layout.addWidget(self.venvs_list)
        
        venvs_btn_layout = QHBoxLayout()
        
        refresh_venvs_btn = QPushButton("刷新")
        refresh_venvs_btn.clicked.connect(self.refresh_venvs)
        venvs_btn_layout.addWidget(refresh_venvs_btn)
        
        delete_venv_btn = QPushButton("删除")
        delete_venv_btn.clicked.connect(self.delete_venv)
        venvs_btn_layout.addWidget(delete_venv_btn)
        
        open_venv_btn = QPushButton("管理包")
        open_venv_btn.clicked.connect(self.manage_venv_packages)
        venvs_btn_layout.addWidget(open_venv_btn)
        
        venvs_layout.addLayout(venvs_btn_layout)
        venvs_group.setLayout(venvs_layout)
        layout.addWidget(venvs_group)
        
        tab.setLayout(layout)
        return tab
    
    def create_packages_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # 搜索包区域
        search_group = QGroupBox("搜索包")
        search_layout = QHBoxLayout()
        
        self.package_search_input = QLineEdit()
        search_layout.addWidget(self.package_search_input)
        
        search_btn = QPushButton("搜索")
        search_btn.clicked.connect(self.search_packages)
        search_layout.addWidget(search_btn)
        
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)
        
        # 搜索结果列表
        results_group = QGroupBox("搜索结果")
        results_layout = QVBoxLayout()
        
        self.packages_results_list = QListWidget()
        results_layout.addWidget(self.packages_results_list)
        
        install_package_btn = QPushButton("安装选中包")
        install_package_btn.clicked.connect(self.install_package)
        results_layout.addWidget(install_package_btn)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        # 已安装包列表
        installed_group = QGroupBox("已安装的包")
        installed_layout = QVBoxLayout()
        
        self.installed_packages_list = QListWidget()
        installed_layout.addWidget(self.installed_packages_list)
        
        installed_btn_layout = QHBoxLayout()
        
        refresh_packages_btn = QPushButton("刷新")
        refresh_packages_btn.clicked.connect(self.refresh_packages)
        installed_btn_layout.addWidget(refresh_packages_btn)
        
        uninstall_package_btn = QPushButton("卸载选中包")
        uninstall_package_btn.clicked.connect(self.uninstall_package)
        installed_btn_layout.addWidget(uninstall_package_btn)
        
        upgrade_package_btn = QPushButton("升级选中包")
        upgrade_package_btn.clicked.connect(self.upgrade_package)
        installed_btn_layout.addWidget(upgrade_package_btn)
        
        installed_layout.addLayout(installed_btn_layout)
        installed_group.setLayout(installed_layout)
        layout.addWidget(installed_group)
        
        tab.setLayout(layout)
        return tab
    
    def refresh_versions(self):
        self.installed_list.clear()
        installed_versions = self.python_manager.get_installed_versions()
        for version in installed_versions:
            self.installed_list.addItem(version)
        
        self.available_list.clear()
        available_versions = self.python_manager.get_available_versions()
        for version in available_versions:
            self.available_list.addItem(version)
            
        # 更新虚拟环境选项卡中的Python版本下拉列表
        self.venv_python_combo.clear()
        self.venv_python_combo.addItem("当前版本")
        for version in installed_versions:
            self.venv_python_combo.addItem(version)
    
    def install_version(self):
        selected_items = self.available_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请先选择要安装的Python版本")
            return
        
        version = selected_items[0].text()
        success = self.python_manager.install_version(version)
        
        if success:
            QMessageBox.information(self, "成功", f"Python {version} 安装成功")
            self.refresh_versions()
        else:
            QMessageBox.critical(self, "错误", f"Python {version} 安装失败")
    
    def uninstall_version(self):
        selected_items = self.installed_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请先选择要卸载的Python版本")
            return
        
        version = selected_items[0].text()
        success = self.python_manager.uninstall_version(version)
        
        if success:
            QMessageBox.information(self, "成功", f"Python {version} 卸载成功")
            self.refresh_versions()
        else:
            QMessageBox.critical(self, "错误", f"Python {version} 卸载失败")
    
    def activate_version(self):
        selected_items = self.installed_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请先选择要激活的Python版本")
            return
        
        version = selected_items[0].text()
        success = self.python_manager.activate_version(version)
        
        if success:
            QMessageBox.information(self, "成功", f"Python {version} 已设为默认版本")
        else:
            QMessageBox.critical(self, "错误", f"无法将 Python {version} 设为默认版本")
    
    def refresh_venvs(self):
        self.venvs_list.clear()
        venvs = self.venv_manager.get_venvs()
        for venv in venvs:
            self.venvs_list.addItem(venv)
    
    def create_venv(self):
        name = self.venv_name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "警告", "请输入虚拟环境名称")
            return
        
        python_version = None
        if self.venv_python_combo.currentIndex() > 0:
            python_version = self.venv_python_combo.currentText()
        
        success = self.venv_manager.create_venv(name, python_version)
        
        if success:
            QMessageBox.information(self, "成功", f"虚拟环境 '{name}' 创建成功")
            self.venv_name_input.clear()
            self.refresh_venvs()
        else:
            QMessageBox.critical(self, "错误", f"虚拟环境 '{name}' 创建失败")
    
    def delete_venv(self):
        selected_items = self.venvs_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请先选择要删除的虚拟环境")
            return
        
        venv_name = selected_items[0].text()
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除虚拟环境 '{venv_name}' 吗？此操作不可撤销。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success = self.venv_manager.delete_venv(venv_name)
            
            if success:
                QMessageBox.information(self, "成功", f"虚拟环境 '{venv_name}' 删除成功")
                self.refresh_venvs()
            else:
                QMessageBox.critical(self, "错误", f"虚拟环境 '{venv_name}' 删除失败")
    
    def manage_venv_packages(self):
        selected_items = self.venvs_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请先选择要管理的虚拟环境")
            return
        
        venv_name = selected_items[0].text()
        # 切换到包管理选项卡
        self.tab_widget.setCurrentIndex(2)
        # 加载虚拟环境中的包
        self.load_venv_packages(venv_name)
    
    def load_venv_packages(self, venv_name):
        python_path = self.venv_manager.get_venv_python(venv_name)
        if not python_path:
            QMessageBox.warning(self, "警告", f"无法获取虚拟环境 '{venv_name}' 的Python解释器")
            return
        
        # 更新已安装包列表
        self.installed_packages_list.clear()
        packages = self.package_manager.list_installed_packages(python_path)
        for package in packages:
            self.installed_packages_list.addItem(f"{package['name']} ({package['version']})")
    
    def search_packages(self):
        query = self.package_search_input.text().strip()
        if not query:
            QMessageBox.warning(self, "警告", "请输入搜索关键词")
            return
        
        # 清空搜索结果列表
        self.packages_results_list.clear()
        
        # 搜索包
        packages = self.package_manager.search_packages(query)
        
        # 显示搜索结果
        for package in packages:
            self.packages_results_list.addItem(
                f"{package['name']} ({package['version']}) - {package['description']}"
            )
    
    def install_package(self):
        selected_items = self.packages_results_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请先选择要安装的包")
            return
        
        # 提取包名
        package_text = selected_items[0].text()
        package_name = package_text.split(" ")[0]
        
        # 确定Python解释器
        python_path = None
        selected_venvs = self.venvs_list.selectedItems()
        if selected_venvs:
            venv_name = selected_venvs[0].text()
            python_path = self.venv_manager.get_venv_python(venv_name)
        
        # 安装包
        success = self.package_manager.install_package(package_name, python_path)
        
        if success:
            QMessageBox.information(self, "成功", f"包 '{package_name}' 安装成功")
            if python_path:
                # 刷新已安装包列表
                self.load_venv_packages(venv_name)
        else:
            QMessageBox.critical(self, "错误", f"包 '{package_name}' 安装失败")
    
    def refresh_packages(self):
        # 清空已安装包列表
        self.installed_packages_list.clear()
        
        # 确定Python解释器
        python_path = None
        selected_venvs = self.venvs_list.selectedItems()
        if selected_venvs:
            venv_name = selected_venvs[0].text()
            python_path = self.venv_manager.get_venv_python(venv_name)
        
        # 获取已安装包列表
        packages = self.package_manager.list_installed_packages(python_path)
        
        # 显示已安装包
        for package in packages:
            self.installed_packages_list.addItem(f"{package['name']} ({package['version']})")
    
    def uninstall_package(self):
        selected_items = self.installed_packages_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请先选择要卸载的包")
            return
        
        # 提取包名
        package_text = selected_items[0].text()
        package_name = package_text.split(" ")[0]
        
        # 确定Python解释器
        python_path = None
        selected_venvs = self.venvs_list.selectedItems()
        if selected_venvs:
            venv_name = selected_venvs[0].text()
            python_path = self.venv_manager.get_venv_python(venv_name)
        
        # 确认卸载
        reply = QMessageBox.question(
            self, "确认卸载", 
            f"确定要卸载包 '{package_name}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 卸载包
            success = self.package_manager.uninstall_package(package_name, python_path)
            
            if success:
                QMessageBox.information(self, "成功", f"包 '{package_name}' 卸载成功")
                # 刷新已安装包列表
                self.refresh_packages()
            else:
                QMessageBox.critical(self, "错误", f"包 '{package_name}' 卸载失败")
    
    def upgrade_package(self):
        selected_items = self.installed_packages_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请先选择要升级的包")
            return
        
        # 提取包名
        package_text = selected_items[0].text()
        package_name = package_text.split(" ")[0]
        
        # 确定Python解释器
        python_path = None
        selected_venvs = self.venvs_list.selectedItems()
        if selected_venvs:
            venv_name = selected_venvs[0].text()
            python_path = self.venv_manager.get_venv_python(venv_name)
        
        # 升级包
        success = self.package_manager.upgrade_package(package_name, python_path)
        
        if success:
            QMessageBox.information(self, "成功", f"包 '{package_name}' 升级成功")
            # 刷新已安装包列表
            self.refresh_packages()
        else:
            QMessageBox.critical(self, "错误", f"包 '{package_name}' 升级失败")
    
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
        QMessageBox.information(self, "设置", "设置功能即将推出...")
    
    def show_about(self):
        """显示关于对话框"""
        about_dialog = AboutDialog(self)
        about_dialog.exec() 