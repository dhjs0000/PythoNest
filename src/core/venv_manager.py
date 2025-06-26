import os
import sys
import subprocess
import platform
import re
from pathlib import Path

class VenvManager:
    def __init__(self):
        self.system = platform.system()
        self.venv_base_dir = self._get_venv_base_dir()
    
    def _get_venv_base_dir(self):
        """获取存储虚拟环境的基础目录"""
        if self.system == "Windows":
            return os.path.join(os.path.expanduser("~"), ".pythonest", "venvs")
        else:
            return os.path.join(os.path.expanduser("~"), ".pythonest", "venvs")
    
    def get_venvs(self):
        """获取已创建的虚拟环境列表"""
        venvs = []
        
        try:
            # 确保基础目录存在
            os.makedirs(self.venv_base_dir, exist_ok=True)
            
            # 列出基础目录下的所有子目录
            for entry in os.listdir(self.venv_base_dir):
                venv_path = os.path.join(self.venv_base_dir, entry)
                if os.path.isdir(venv_path):
                    # 检查是否是虚拟环境
                    if self._is_valid_venv(venv_path):
                        venvs.append(entry)
        except:
            pass
        
        return sorted(venvs)
    
    def _is_valid_venv(self, path):
        """检查指定路径是否是有效的虚拟环境"""
        if self.system == "Windows":
            return os.path.isfile(os.path.join(path, "Scripts", "python.exe"))
        else:
            return os.path.isfile(os.path.join(path, "bin", "python"))
    
    def create_venv(self, name, python_version=None):
        """创建新的虚拟环境
        
        参数:
            name: 虚拟环境名称
            python_version: 要使用的Python版本（可选）
        
        返回:
            成功返回True，失败返回False
        """
        try:
            # 构建虚拟环境路径
            venv_path = os.path.join(self.venv_base_dir, name)
            
            # 确保基础目录存在
            os.makedirs(self.venv_base_dir, exist_ok=True)
            
            # 检查名称是否已存在
            if os.path.exists(venv_path):
                return False
            
            # 构建创建虚拟环境的命令
            cmd = []
            
            if python_version:
                # 如果指定了Python版本，使用该版本的Python解释器
                if self.system == "Windows":
                    cmd = [f"py -{python_version}", "-m", "venv", venv_path]
                else:
                    cmd = [f"python{python_version}", "-m", "venv", venv_path]
            else:
                # 否则使用当前Python解释器
                cmd = [sys.executable, "-m", "venv", venv_path]
            
            # 执行命令
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # 检查结果
            return result.returncode == 0
        except:
            return False
    
    def delete_venv(self, name):
        """删除指定的虚拟环境
        
        参数:
            name: 虚拟环境名称
        
        返回:
            成功返回True，失败返回False
        """
        try:
            # 构建虚拟环境路径
            venv_path = os.path.join(self.venv_base_dir, name)
            
            # 检查虚拟环境是否存在
            if not os.path.exists(venv_path):
                return False
            
            # 递归删除目录
            import shutil
            shutil.rmtree(venv_path)
            
            return True
        except:
            return False
    
    def get_venv_python(self, name):
        """获取虚拟环境中Python解释器的路径
        
        参数:
            name: 虚拟环境名称
        
        返回:
            成功返回Python解释器路径，失败返回None
        """
        try:
            # 构建虚拟环境路径
            venv_path = os.path.join(self.venv_base_dir, name)
            
            # 检查虚拟环境是否存在
            if not os.path.exists(venv_path):
                return None
            
            # 根据操作系统构建Python解释器路径
            if self.system == "Windows":
                python_path = os.path.join(venv_path, "Scripts", "python.exe")
            else:
                python_path = os.path.join(venv_path, "bin", "python")
            
            # 检查Python解释器是否存在
            if os.path.isfile(python_path):
                return python_path
            else:
                return None
        except:
            return None
    
    def get_venv_packages(self, name):
        """获取虚拟环境中已安装的包列表
        
        参数:
            name: 虚拟环境名称
        
        返回:
            成功返回包列表，失败返回空列表
        """
        packages = []
        
        try:
            # 获取虚拟环境Python解释器路径
            python_path = self.get_venv_python(name)
            
            if python_path:
                # 执行pip list命令
                cmd = [python_path, "-m", "pip", "list", "--format=json"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    # 解析JSON输出
                    import json
                    packages_data = json.loads(result.stdout)
                    for package in packages_data:
                        packages.append(f"{package['name']}=={package['version']}")
        except:
            pass
        
        return sorted(packages)
    
    def install_package(self, venv_name, package_name):
        """在指定虚拟环境中安装包
        
        参数:
            venv_name: 虚拟环境名称
            package_name: 包名称
        
        返回:
            成功返回True，失败返回False
        """
        try:
            # 获取虚拟环境Python解释器路径
            python_path = self.get_venv_python(venv_name)
            
            if python_path:
                # 执行pip install命令
                cmd = [python_path, "-m", "pip", "install", package_name]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                # 检查结果
                return result.returncode == 0
            else:
                return False
        except:
            return False
    
    def uninstall_package(self, venv_name, package_name):
        """在指定虚拟环境中卸载包
        
        参数:
            venv_name: 虚拟环境名称
            package_name: 包名称
        
        返回:
            成功返回True，失败返回False
        """
        try:
            # 获取虚拟环境Python解释器路径
            python_path = self.get_venv_python(venv_name)
            
            if python_path:
                # 执行pip uninstall命令
                cmd = [python_path, "-m", "pip", "uninstall", "-y", package_name]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                # 检查结果
                return result.returncode == 0
            else:
                return False
        except:
            return False