import os
import sys
import subprocess
import requests
import re
import json
from urllib.parse import urljoin

class PackageManager:
    def __init__(self):
        self.pypi_url = "https://pypi.org/pypi/"
        self.pypi_search_url = "https://pypi.org/search/"
    
    def search_packages(self, query, max_results=20):
        """搜索PyPI上的包
        
        参数:
            query: 搜索关键词
            max_results: 最大结果数量
        
        返回:
            包含包信息的字典列表
        """
        packages = []
        
        try:
            # 构建搜索URL
            params = {"q": query}
            response = requests.get(self.pypi_search_url, params=params)
            
            if response.status_code == 200:
                # 使用正则表达式从HTML中提取包信息
                # 注意：这是一个简化的实现，真实应用中应该使用官方API或HTML解析库
                package_pattern = r'<span class="package-snippet__name">(.+?)</span>.*?<span class="package-snippet__version">(.+?)</span>.*?<p class="package-snippet__description">(.+?)</p>'
                matches = re.findall(package_pattern, response.text, re.DOTALL)
                
                for match in matches[:max_results]:
                    name, version, description = match
                    packages.append({
                        "name": name.strip(),
                        "version": version.strip(),
                        "description": description.strip()
                    })
        except:
            # 如果出现异常，返回空列表
            pass
        
        return packages
    
    def get_package_info(self, package_name):
        """获取指定包的详细信息
        
        参数:
            package_name: 包名称
        
        返回:
            包含包详细信息的字典，失败返回None
        """
        try:
            # 构建API URL
            url = urljoin(self.pypi_url, f"{package_name}/json")
            response = requests.get(url)
            
            if response.status_code == 200:
                # 解析JSON响应
                data = response.json()
                info = data.get("info", {})
                
                # 提取关键信息
                return {
                    "name": info.get("name"),
                    "version": info.get("version"),
                    "summary": info.get("summary"),
                    "description": info.get("description"),
                    "author": info.get("author"),
                    "author_email": info.get("author_email"),
                    "license": info.get("license"),
                    "project_url": info.get("project_url"),
                    "requires_python": info.get("requires_python"),
                    "classifiers": info.get("classifiers", []),
                    "releases": list(data.get("releases", {}).keys())
                }
            else:
                return None
        except:
            return None
    
    def install_package(self, package_name, python_path=None):
        """安装指定的包
        
        参数:
            package_name: 包名称
            python_path: Python解释器路径（可选，默认使用当前解释器）
        
        返回:
            成功返回True，失败返回False
        """
        try:
            # 确定Python解释器
            python = python_path if python_path else sys.executable
            
            # 执行pip install命令
            cmd = [python, "-m", "pip", "install", package_name]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # 检查结果
            return result.returncode == 0
        except:
            return False
    
    def uninstall_package(self, package_name, python_path=None):
        """卸载指定的包
        
        参数:
            package_name: 包名称
            python_path: Python解释器路径（可选，默认使用当前解释器）
        
        返回:
            成功返回True，失败返回False
        """
        try:
            # 确定Python解释器
            python = python_path if python_path else sys.executable
            
            # 执行pip uninstall命令
            cmd = [python, "-m", "pip", "uninstall", "-y", package_name]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # 检查结果
            return result.returncode == 0
        except:
            return False
    
    def list_installed_packages(self, python_path=None):
        """列出已安装的包
        
        参数:
            python_path: Python解释器路径（可选，默认使用当前解释器）
        
        返回:
            包含包信息的字典列表
        """
        packages = []
        
        try:
            # 确定Python解释器
            python = python_path if python_path else sys.executable
            
            # 执行pip list命令
            cmd = [python, "-m", "pip", "list", "--format=json"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # 解析JSON输出
                packages_data = json.loads(result.stdout)
                for package in packages_data:
                    packages.append({
                        "name": package["name"],
                        "version": package["version"]
                    })
        except:
            pass
        
        return packages
    
    def check_outdated_packages(self, python_path=None):
        """检查过时的包
        
        参数:
            python_path: Python解释器路径（可选，默认使用当前解释器）
        
        返回:
            包含过时包信息的字典列表
        """
        outdated = []
        
        try:
            # 确定Python解释器
            python = python_path if python_path else sys.executable
            
            # 执行pip list --outdated命令
            cmd = [python, "-m", "pip", "list", "--outdated", "--format=json"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # 解析JSON输出
                packages_data = json.loads(result.stdout)
                for package in packages_data:
                    outdated.append({
                        "name": package["name"],
                        "version": package["version"],
                        "latest_version": package.get("latest_version", "未知")
                    })
        except:
            pass
        
        return outdated
    
    def upgrade_package(self, package_name, python_path=None):
        """升级指定的包
        
        参数:
            package_name: 包名称
            python_path: Python解释器路径（可选，默认使用当前解释器）
        
        返回:
            成功返回True，失败返回False
        """
        try:
            # 确定Python解释器
            python = python_path if python_path else sys.executable
            
            # 执行pip install --upgrade命令
            cmd = [python, "-m", "pip", "install", "--upgrade", package_name]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # 检查结果
            return result.returncode == 0
        except:
            return False 