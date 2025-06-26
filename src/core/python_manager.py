import os
import sys
import subprocess
import platform
import re
import requests
from pathlib import Path

class PythonManager:
    def __init__(self):
        self.system = platform.system()
        self.python_releases_url = "https://www.python.org/downloads/"
        
    def get_installed_versions(self):
        """获取已安装的Python版本列表"""
        installed_versions = []
        
        if self.system == "Windows":
            # 在Windows上使用注册表查询已安装的Python版本
            try:
                import winreg
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Python\PythonCore") as key:
                    i = 0
                    while True:
                        try:
                            version = winreg.EnumKey(key, i)
                            installed_versions.append(version)
                            i += 1
                        except OSError:
                            break
            except:
                # 回退方案：使用py -0命令
                try:
                    result = subprocess.run(["py", "-0"], capture_output=True, text=True)
                    if result.returncode == 0:
                        for line in result.stdout.splitlines():
                            if "-" in line:
                                version = line.strip().split("-")[1]
                                if version and version not in installed_versions:
                                    installed_versions.append(version)
                except:
                    pass
        else:
            # 在Unix系统上搜索可能的Python安装
            paths = os.environ["PATH"].split(os.pathsep)
            for prefix in ["python", "python3"]:
                for path in paths:
                    python_path = os.path.join(path, prefix)
                    if os.path.isfile(python_path) and os.access(python_path, os.X_OK):
                        try:
                            result = subprocess.run([python_path, "--version"], 
                                                   capture_output=True, text=True)
                            if result.returncode == 0:
                                version_match = re.search(r"Python (\d+\.\d+\.\d+)", result.stdout)
                                if version_match:
                                    version = version_match.group(1)
                                    if version not in installed_versions:
                                        installed_versions.append(version)
                        except:
                            pass
        
        return sorted(installed_versions, key=lambda v: [int(x) for x in v.split('.')])
    
    def get_available_versions(self):
        """获取可安装的Python版本列表"""
        available_versions = []
        
        try:
            # 从Python官网获取可用版本
            response = requests.get(self.python_releases_url)
            if response.status_code == 200:
                # 使用正则表达式提取版本号
                version_pattern = r"Python (\d+\.\d+\.\d+)"
                versions = re.findall(version_pattern, response.text)
                
                # 过滤并排序版本
                available_versions = sorted(set(versions), 
                                          key=lambda v: [int(x) for x in v.split('.')])
                
                # 移除已安装的版本
                installed = self.get_installed_versions()
                available_versions = [v for v in available_versions if v not in installed]
        except:
            # 如果无法获取在线版本，返回一些最近的主要版本
            for major in [3, 2]:
                for minor in range(12, 5, -1):
                    version = f"{major}.{minor}.0"
                    if version not in available_versions:
                        available_versions.append(version)
        
        return available_versions[-10:]  # 返回最新的10个版本
    
    def install_version(self, version):
        """安装指定版本的Python"""
        # 这里只是演示，实际实现需要根据不同操作系统调用不同的安装方法
        try:
            if self.system == "Windows":
                # 在Windows上下载安装程序并执行
                url = f"https://www.python.org/ftp/python/{version}/python-{version}"
                if platform.architecture()[0] == "64bit":
                    url += "-amd64.exe"
                else:
                    url += ".exe"
                
                # 下载安装程序
                installer_path = os.path.join(os.environ["TEMP"], f"python-{version}.exe")
                self._download_file(url, installer_path)
                
                # 执行安装程序
                # 注意：这是一个简化的示例，实际实现可能需要更复杂的逻辑
                subprocess.run([installer_path, "/quiet", "InstallAllUsers=1", "PrependPath=1"])
                return True
            else:
                # 其他操作系统的安装逻辑
                return False
        except:
            return False
    
    def uninstall_version(self, version):
        """卸载指定版本的Python"""
        # 实际实现需要根据不同操作系统调用不同的卸载方法
        try:
            if self.system == "Windows":
                # 在Windows上使用控制面板卸载程序
                uninstall_cmd = f"wmic product where \"name like 'Python {version}%'\" call uninstall /nointeractive"
                subprocess.run(uninstall_cmd, shell=True)
                return True
            else:
                # 其他操作系统的卸载逻辑
                return False
        except:
            return False
    
    def activate_version(self, version):
        """设置默认Python版本"""
        # 实际实现需要根据不同操作系统修改环境变量或创建符号链接
        try:
            if self.system == "Windows":
                # 在Windows上修改PATH环境变量
                python_path = self._get_python_install_path(version)
                if python_path:
                    # 将该版本Python的路径添加到PATH的最前面
                    path = os.environ["PATH"]
                    paths = path.split(os.pathsep)
                    
                    # 移除其他Python路径
                    new_paths = [p for p in paths if not re.search(r"\\Python\d+", p)]
                    
                    # 添加新路径
                    new_paths.insert(0, python_path)
                    new_paths.insert(0, os.path.join(python_path, "Scripts"))
                    
                    # 更新环境变量
                    new_path = os.pathsep.join(new_paths)
                    # 注意：这只会更新当前进程的环境变量，不会永久更改系统环境变量
                    os.environ["PATH"] = new_path
                    
                    # 真实实现中，应该使用Windows API永久修改系统环境变量
                    return True
            else:
                # 其他操作系统的激活逻辑
                return False
        except:
            return False
    
    def _get_python_install_path(self, version):
        """获取指定版本Python的安装路径"""
        if self.system == "Windows":
            try:
                import winreg
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                  f"SOFTWARE\\Python\\PythonCore\\{version}\\InstallPath") as key:
                    return winreg.QueryValue(key, "")
            except:
                pass
        return None
    
    def _download_file(self, url, dest):
        """下载文件到指定位置"""
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(dest, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk) 