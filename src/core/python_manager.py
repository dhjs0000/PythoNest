import os
import sys
import subprocess
import platform
import re
import requests
import json
import logging
import warnings
from pathlib import Path

# 禁用SSL不安全警告
warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

class PythonManager:
    def __init__(self):
        self.system = platform.system()
        self.python_releases_url = "https://www.python.org/downloads/"
        self.settings = self._load_settings()
        
    def _load_settings(self):
        """从配置文件加载设置"""
        default_settings = {
            "search": {
                "use_registry": True,
                "use_py_launcher": True,
                "use_path": True,
                "use_custom_paths": False,
                "custom_paths": ""
            },
            "source": {
                "use_custom_source": False,
                "custom_source_url": "",
                "selected_source_index": 0,
                "selected_source_url": "https://www.python.org/downloads/"
            },
            "download": {
                "download_dir": os.path.join(os.environ.get("TEMP", ""), "PythoNest"),
                "auto_install": True,
                "verify_ssl": True,
                "version_select_mode": "direct"  # direct 或 two_step
            }
        }
        
        try:
            config_dir = os.path.join(os.path.expanduser("~"), ".pythonest")
            os.makedirs(config_dir, exist_ok=True)
            
            config_file = os.path.join(config_dir, "config.json")
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    return json.load(f)
            else:
                # 创建默认配置文件
                with open(config_file, 'w') as f:
                    json.dump(default_settings, f, indent=4)
                return default_settings
        except Exception as e:
            logging.error(f"加载设置失败: {str(e)}")
            return default_settings
    
    def save_settings(self, settings):
        """保存设置到配置文件"""
        try:
            config_dir = os.path.join(os.path.expanduser("~"), ".pythonest")
            os.makedirs(config_dir, exist_ok=True)
            
            config_file = os.path.join(config_dir, "config.json")
            with open(config_file, 'w') as f:
                json.dump(settings, f, indent=4)
            self.settings = settings
            return True
        except Exception as e:
            logging.error(f"保存设置失败: {str(e)}")
            return False
        
    def get_installed_versions(self):
        """获取已安装的Python版本列表"""
        installed_versions = []
        search_settings = self.settings["search"]
        
        if self.system == "Windows":
            # 使用注册表查询
            if search_settings["use_registry"]:
                try:
                    import winreg
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Python\PythonCore") as key:
                        i = 0
                        while True:
                            try:
                                version = winreg.EnumKey(key, i)
                                # 验证是否是有效版本号
                                if re.match(r"^\d+\.\d+$", version):
                                    # 检查InstallPath键是否存在
                                    try:
                                        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, f"SOFTWARE\\Python\\PythonCore\\{version}\\InstallPath") as install_key:
                                            install_path = winreg.QueryValue(install_key, "")
                                            if os.path.exists(install_path):
                                                # 尝试获取精确版本号
                                                try:
                                                    exe_path = os.path.join(install_path, "python.exe")
                                                    if os.path.exists(exe_path):
                                                        result = subprocess.run([exe_path, "--version"], 
                                                                           capture_output=True, text=True)
                                                        if result.returncode == 0:
                                                            version_match = re.search(r"Python (\d+\.\d+\.\d+)", 
                                                                                  result.stdout or result.stderr)
                                                            if version_match:
                                                                version = version_match.group(1)
                                                except:
                                                    pass  # 使用注册表中的版本号
                                                
                                                if version not in installed_versions:
                                                    installed_versions.append(version)
                                    except:
                                        pass  # 安装路径不存在或无法访问
                                i += 1
                            except OSError:
                                break
                except Exception as e:
                    logging.warning(f"通过注册表获取Python版本失败: {str(e)}")
            
            # 使用py启动器
            if search_settings["use_py_launcher"]:
                try:
                    result = subprocess.run(["py", "-0"], capture_output=True, text=True)
                    if result.returncode == 0:
                        for line in result.stdout.splitlines():
                            if "-" in line:
                                version_info = line.strip().split("-")[1].strip()
                                if "." in version_info:
                                    # 提取版本号
                                    version_match = re.search(r"(\d+\.\d+\.\d+)", version_info)
                                    if version_match:
                                        version = version_match.group(1)
                                    else:
                                        version_match = re.search(r"(\d+\.\d+)", version_info)
                                        if version_match:
                                            version = version_match.group(1) + ".0"
                                        else:
                                            continue
                                            
                                    if version and version not in installed_versions:
                                        installed_versions.append(version)
                except Exception as e:
                    logging.warning(f"通过py启动器获取Python版本失败: {str(e)}")
        
        # 在PATH中搜索
        if search_settings["use_path"]:
            paths = os.environ["PATH"].split(os.pathsep)
            for prefix in ["python", "python3", "python2"]:
                for path in paths:
                    python_path = os.path.join(path, prefix)
                    if self.system == "Windows":
                        python_path += ".exe"
                        
                    if os.path.isfile(python_path) and os.access(python_path, os.X_OK):
                        try:
                            result = subprocess.run([python_path, "--version"], 
                                                   capture_output=True, text=True)
                            if result.returncode == 0:
                                version_output = result.stdout or result.stderr
                                version_match = re.search(r"Python (\d+\.\d+\.\d+)", version_output)
                                if version_match:
                                    version = version_match.group(1)
                                    if version not in installed_versions:
                                        installed_versions.append(version)
                        except Exception as e:
                            logging.warning(f"通过PATH获取Python版本失败: {str(e)}")
        
        # 在自定义路径中搜索
        if search_settings["use_custom_paths"] and search_settings["custom_paths"]:
            custom_paths = search_settings["custom_paths"].split(";")
            for base_path in custom_paths:
                if not os.path.exists(base_path):
                    continue
                    
                # 搜索目录中的Python可执行文件
                for root, dirs, files in os.walk(base_path):
                    python_exe = "python.exe" if self.system == "Windows" else "python"
                    if python_exe in files:
                        python_path = os.path.join(root, python_exe)
                        try:
                            result = subprocess.run([python_path, "--version"], 
                                                   capture_output=True, text=True)
                            if result.returncode == 0:
                                version_output = result.stdout or result.stderr
                                version_match = re.search(r"Python (\d+\.\d+\.\d+)", version_output)
                                if version_match:
                                    version = version_match.group(1)
                                    if version not in installed_versions:
                                        installed_versions.append(version)
                        except:
                            pass
        
        # 排序版本号
        def version_key(v):
            parts = v.split('.')
            return [int(p) if p.isdigit() else p for p in parts]
            
        return sorted(installed_versions, key=version_key)
    
    def get_major_versions(self):
        """获取所有可用的主要版本（例如3.12, 3.11等）及其对应的次版本列表"""
        all_versions = self.get_available_versions()
        
        # 按主版本分组
        major_versions = {}
        for version in all_versions:
            # 获取主版本号 (例如 "3.12.0" -> "3.12")
            parts = version.split('.')
            if len(parts) >= 2:
                major_ver = f"{parts[0]}.{parts[1]}"
                if major_ver not in major_versions:
                    major_versions[major_ver] = []
                major_versions[major_ver].append(version)
        
        # 将字典转换为列表，并按版本号降序排序
        result = []
        for major_ver, versions in sorted(major_versions.items(), 
                                         key=lambda x: [int(p) for p in x[0].split('.')], 
                                         reverse=True):
            # 对每个主版本内的次版本也按降序排序
            sorted_versions = sorted(versions, 
                                   key=lambda x: [int(p) for p in x.split('.')], 
                                   reverse=True)
            result.append((major_ver, sorted_versions))
        
        return result
        
    def get_available_versions(self):
        """获取可用的Python版本列表"""
        versions = []
        
        # 根据选择的源获取版本列表
        source = self.get_current_source()
        source_url = source.get("url", "")
        
        try:
            # 根据不同的源使用不同的获取策略
            if "python.org" in source_url:
                versions = self._get_versions_from_python_org()
            elif "huaweicloud.com" in source_url:
                versions = self._get_versions_from_huaweicloud()
            elif "npmmirror.com" in source_url or "taobao" in source_url:
                versions = self._get_versions_from_taobao()
            elif "tuna.tsinghua.edu.cn" in source_url:
                versions = self._get_versions_from_tsinghua()
            elif "bfsu.edu.cn" in source_url:
                versions = self._get_versions_from_bfsu()
            else:
                # 尝试通用方法
                versions = self._get_versions_generic(source_url)
            
            # 如果没有获取到版本，使用预定义的版本列表
            if not versions:
                logging.warning(f"从 {source_url} 获取版本列表失败，使用预定义版本列表")
                versions = self._get_predefined_versions()
                
        except Exception as e:
            logging.error(f"获取Python版本列表失败: {str(e)}")
            # 使用预定义的版本列表作为备选
            versions = self._get_predefined_versions()
        
        # 过滤掉alpha, beta, rc版本（除非特别设置）
        if not self.settings.get("include_dev_versions", False):
            versions = [v for v in versions if not any(x in v for x in ['a', 'b', 'rc'])]
        
        return versions
    
    def _get_predefined_versions(self):
        """返回预定义的Python版本列表，确保即使在线获取失败也有可用选项"""
        return [
            "3.12.0", "3.11.8", "3.11.7", "3.11.6", "3.11.5", "3.11.4", "3.11.3", "3.11.2", "3.11.1", "3.11.0",
            "3.10.13", "3.10.12", "3.10.11", "3.10.10", "3.10.9", "3.10.8", "3.10.7", "3.10.6", "3.10.5", "3.10.4", "3.10.3", "3.10.2", "3.10.1", "3.10.0",
            "3.9.18", "3.9.17", "3.9.16", "3.9.15", "3.9.14", "3.9.13", "3.9.12", "3.9.11", "3.9.10", "3.9.9", "3.9.8", "3.9.7", "3.9.6", "3.9.5", "3.9.4", "3.9.3", "3.9.2", "3.9.1", "3.9.0",
            "3.8.18", "3.8.17", "3.8.16", "3.8.15", "3.8.14", "3.8.13", "3.8.12", "3.8.11", "3.8.10", "3.8.9", "3.8.8", "3.8.7", "3.8.6", "3.8.5", "3.8.4", "3.8.3", "3.8.2", "3.8.1", "3.8.0",
            "3.7.17", "3.7.16", "3.7.15", "3.7.14", "3.7.13", "3.7.12", "3.7.11", "3.7.10", "3.7.9", "3.7.8", "3.7.7", "3.7.6", "3.7.5", "3.7.4", "3.7.3", "3.7.2", "3.7.1", "3.7.0"
        ]
    
    def download_version(self, version, progress_callback=None):
        """下载指定版本的Python安装包
        
        Args:
            version: 要下载的Python版本号，如"3.11.5"
            progress_callback: 进度回调函数，接收一个字典参数，包含downloaded, total, percentage键
            
        Returns:
            安装包的本地路径
        """
        # 获取下载目录
        download_dir = self.settings["download"]["download_dir"]
        os.makedirs(download_dir, exist_ok=True)
        
        # 获取SSL验证设置
        verify_ssl = self.settings["download"].get("verify_ssl", True)
        
        # 构建安装包名称
        if sys.platform == "win32":
            installer_name = f"python-{version}-amd64.exe"
        elif sys.platform == "darwin":
            installer_name = f"python-{version}-macos11.pkg"
        else:
            # Linux平台通常使用包管理器安装
            installer_name = f"Python-{version}.tgz"
        
        # 本地安装包路径
        local_path = os.path.join(download_dir, installer_name)
        
        # 如果已经下载，直接返回
        if os.path.exists(local_path):
            logging.info(f"Python {version} 安装包已存在，跳过下载")
            return local_path
        
        # 获取下载URL
        source = self.get_current_source()
        source_url = source.get("url", "")
        download_url = self._get_download_url(source_url, version)
        
        if not download_url:
            logging.error(f"无法获取Python {version}的下载链接")
            return None
        
        logging.info(f"开始下载Python {version} 从 {download_url}")
        
        try:
            # 创建临时文件
            temp_path = local_path + ".tmp"
            
            # 根据源设置特定的请求头和参数
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            # 对于淘宝镜像，禁用SSL验证
            if "npmmirror.com" in source_url or "taobao" in source_url:
                verify_ssl = False
            
            # 使用requests下载文件，支持进度回调
            with requests.get(download_url, stream=True, verify=verify_ssl, headers=headers, timeout=30) as response:
                response.raise_for_status()
                
                # 获取文件大小
                total_size = int(response.headers.get('content-length', 0))
                downloaded_size = 0
                
                # 写入文件
                with open(temp_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded_size += len(chunk)
                            
                            # 计算进度百分比
                            percentage = int(downloaded_size * 100 / total_size) if total_size > 0 else 0
                            
                            # 调用进度回调
                            if progress_callback:
                                progress_info = {
                                    'downloaded': downloaded_size,
                                    'total': total_size,
                                    'percentage': percentage
                                }
                                progress_callback(progress_info)
            
            # 下载完成后重命名文件
            os.rename(temp_path, local_path)
            logging.info(f"Python {version} 下载完成: {local_path}")
            return local_path
            
        except Exception as e:
            logging.error(f"下载Python {version}失败: {str(e)}")
            # 清理临时文件
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
                    
            # 如果是淘宝镜像失败，尝试使用Python官网
            if "npmmirror.com" in source_url or "taobao" in source_url:
                logging.info("尝试从Python官网下载")
                try:
                    # 使用Python官网URL
                    download_url = f"https://www.python.org/ftp/python/{version}/python-{version}-amd64.exe"
                    
                    # 使用requests下载文件
                    with requests.get(download_url, stream=True, verify=True, headers=headers, timeout=30) as response:
                        response.raise_for_status()
                        
                        # 获取文件大小
                        total_size = int(response.headers.get('content-length', 0))
                        downloaded_size = 0
                        
                        # 写入文件
                        with open(temp_path, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                                    downloaded_size += len(chunk)
                                    
                                    # 计算进度百分比
                                    percentage = int(downloaded_size * 100 / total_size) if total_size > 0 else 0
                                    
                                    # 调用进度回调
                                    if progress_callback:
                                        progress_info = {
                                            'downloaded': downloaded_size,
                                            'total': total_size,
                                            'percentage': percentage
                                        }
                                        progress_callback(progress_info)
                        
                        # 下载完成后重命名文件
                        os.rename(temp_path, local_path)
                        logging.info(f"Python {version} 从官网下载完成: {local_path}")
                        return local_path
                        
                except Exception as e2:
                    logging.error(f"从Python官网下载失败: {str(e2)}")
                    # 清理临时文件
                    if os.path.exists(temp_path):
                        try:
                            os.remove(temp_path)
                        except:
                            pass
            
            return None
    
    def _get_download_url(self, source_url, version):
        """根据源URL和版本号构建下载URL"""
        if "python.org" in source_url:
            # Python官网格式
            major, minor, patch = version.split('.')
            return f"https://www.python.org/ftp/python/{version}/python-{version}-amd64.exe"
        
        elif "huaweicloud.com" in source_url:
            # 华为云镜像格式
            return f"https://repo.huaweicloud.com/python/{version}/python-{version}-amd64.exe"
        
        elif "npmmirror.com" in source_url or "taobao" in source_url:
            # 淘宝镜像格式 - 修正为正确的下载URL
            return f"https://npmmirror.com/mirrors/python/{version}/python-{version}-amd64.exe"
        
        elif "tuna.tsinghua.edu.cn" in source_url:
            # 清华镜像格式 (使用Anaconda)
            major, minor, _ = version.split('.')
            return f"https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda3-py{major}{minor}_23.5.2-0-Windows-x86_64.exe"
        
        elif "bfsu.edu.cn" in source_url:
            # 北外镜像格式 (使用Anaconda)
            major, minor, _ = version.split('.')
            return f"https://mirrors.bfsu.edu.cn/anaconda/miniconda/Miniconda3-py{major}{minor}_23.5.2-0-Windows-x86_64.exe"
        
        else:
            # 通用格式，尝试构建URL
            base_url = source_url.rstrip('/')
            return f"{base_url}/{version}/python-{version}-amd64.exe"
    
    def install_version(self, version, installer_path=None, silent=False):
        """安装指定版本的Python
        
        Args:
            version: 要安装的Python版本号
            installer_path: 安装包路径，如果为None，则自动下载
            silent: 是否静默安装
            
        Returns:
            安装是否成功
        """
        # 如果未提供安装包路径，则下载
        if not installer_path:
            installer_path = self.download_version(version)
        
        if not installer_path:
            return False
            
        try:
            if self.system == "Windows":
                # 构建安装参数
                if silent:
                    # 静默安装
                    install_args = [
                        installer_path,
                        "/quiet",
                        "InstallAllUsers=1",
                        "PrependPath=1",
                        "Include_test=0"
                    ]
                else:
                    # 交互式安装
                    install_args = [installer_path]
                
                # 执行安装
                subprocess.Popen(install_args)
                return True
            else:
                # 其他操作系统的安装逻辑
                return False
        except Exception as e:
            logging.error(f"安装Python版本失败: {str(e)}")
            return False
    
    def uninstall_version(self, version):
        """卸载指定版本的Python"""
        try:
            if self.system == "Windows":
                # 在Windows上使用控制面板卸载程序
                uninstall_cmd = f"wmic product where \"name like 'Python {version}%'\" call uninstall /nointeractive"
                subprocess.run(uninstall_cmd, shell=True)
                return True
            else:
                # 其他操作系统的卸载逻辑
                return False
        except Exception as e:
            logging.error(f"卸载Python版本失败: {str(e)}")
            return False
    
    def activate_version(self, version):
        """设置默认Python版本"""
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
                    
                    # 使用SetEnvironmentVariable API永久修改系统环境变量
                    try:
                        import win32con
                        import win32gui
                        from win32gui import SendMessage
                        
                        # 更新系统环境变量
                        win32gui.SendMessage(
                            win32con.HWND_BROADCAST,
                            win32con.WM_SETTINGCHANGE,
                            0,
                            "Environment"
                        )
                    except:
                        # 如果无法导入win32api，使用subprocess调用setx
                        subprocess.run(f'setx PATH "{new_path}"', shell=True)
                    
                    return True
            else:
                # 其他操作系统的激活逻辑
                return False
        except Exception as e:
            logging.error(f"设置默认Python版本失败: {str(e)}")
            return False
    
    def _get_python_install_path(self, version):
        """获取指定版本Python的安装路径"""
        if self.system == "Windows":
            try:
                import winreg
                # 提取主要版本号 (3.9.1 -> 3.9)
                version_parts = version.split(".")
                major_minor = ".".join(version_parts[:2])
                
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                  f"SOFTWARE\\Python\\PythonCore\\{major_minor}\\InstallPath") as key:
                    return winreg.QueryValue(key, "")
            except:
                pass
        return None
    
    def _version_sort_key(self, version):
        """版本排序键函数"""
        parts = version.split('.')
        return [int(p) if p.isdigit() else p for p in parts]
    
    def get_current_source(self):
        """获取当前选择的源信息"""
        source_settings = self.settings["source"]
        
        if source_settings["use_custom_source"] and source_settings["custom_source_url"]:
            return {
                "name": "自定义源",
                "url": source_settings["custom_source_url"]
            }
        else:
            # 预定义源列表
            sources = [
                {"name": "Python官网", "url": "https://www.python.org/downloads/"},
                {"name": "华为云镜像", "url": "https://repo.huaweicloud.com/python/"},
                {"name": "淘宝镜像", "url": "https://registry.npmmirror.com/binary.html?path=python/"},
                {"name": "清华大学镜像", "url": "https://mirrors.tuna.tsinghua.edu.cn/anaconda/archive/"},
                {"name": "北京外国语大学镜像", "url": "https://mirrors.bfsu.edu.cn/anaconda/archive/"}
            ]
            
            index = source_settings.get("selected_source_index", 0)
            if 0 <= index < len(sources):
                return sources[index]
            return sources[0]  # 默认使用Python官网

    def _get_versions_from_python_org(self):
        """从Python官网获取版本列表"""
        url = "https://www.python.org/downloads/"
        verify_ssl = self.settings["download"].get("verify_ssl", True)
        
        try:
            response = requests.get(url, timeout=15, verify=verify_ssl)
            if response.status_code == 200:
                # 使用正则表达式提取版本号
                version_pattern = r"Python (\d+\.\d+\.\d+)"
                versions = re.findall(version_pattern, response.text)
                versions = sorted(set(versions), key=lambda v: [int(x) for x in v.split('.')])
                
                # 移除已安装的版本
                installed = self.get_installed_versions()
                versions = [v for v in versions if v not in installed]
                
                logging.info(f"从Python官网找到 {len(versions)} 个版本")
                return versions
            else:
                logging.warning(f"从Python官网获取版本列表失败，HTTP状态码: {response.status_code}")
        except Exception as e:
            logging.error(f"从Python官网获取版本列表失败: {str(e)}")
        
        # 如果获取失败，使用预定义版本列表
        logging.info("使用预定义的Python版本列表作为备选")
        versions = self._get_predefined_versions()
        
        # 移除已安装的版本
        installed = self.get_installed_versions()
        versions = [v for v in versions if v not in installed]
        
        return versions
    
    def _get_versions_from_huaweicloud(self):
        """从华为云镜像获取版本列表"""
        url = "https://repo.huaweicloud.com/python/"
        verify_ssl = self.settings["download"].get("verify_ssl", True)
        versions = []
        
        try:
            response = requests.get(url, timeout=15, verify=verify_ssl)
            if response.status_code == 200:
                # 使用正则表达式提取版本号
                version_pattern = r'href="(\d+\.\d+\.\d+)/'
                versions = re.findall(version_pattern, response.text)
                versions = sorted(set(versions), key=lambda v: [int(x) for x in v.split('.')])
                
                # 移除已安装的版本
                installed = self.get_installed_versions()
                versions = [v for v in versions if v not in installed]
                
                logging.info(f"从华为云镜像找到 {len(versions)} 个版本")
                return versions
            else:
                logging.warning(f"从华为云镜像获取版本列表失败，HTTP状态码: {response.status_code}")
        except Exception as e:
            logging.error(f"从华为云镜像获取版本列表失败: {str(e)}")
        
        # 如果获取失败，使用预定义版本列表
        logging.info("使用预定义的Python版本列表作为备选")
        versions = self._get_predefined_versions()
        
        # 移除已安装的版本
        installed = self.get_installed_versions()
        versions = [v for v in versions if v not in installed]
        
        return versions
    
    def _get_versions_from_taobao(self):
        """从淘宝镜像获取版本列表"""
        # 淘宝镜像经常有SSL证书问题，所以默认不验证
        verify_ssl = False
        versions = []
        
        # 直接使用预定义的版本列表，因为淘宝镜像API不稳定
        logging.info("使用预定义的Python版本列表")
        versions = self._get_predefined_versions()
        
        # 移除已安装的版本
        installed = self.get_installed_versions()
        versions = [v for v in versions if v not in installed]
        
        logging.info(f"为淘宝镜像预设了 {len(versions)} 个Python版本")
        return versions
    
    def _get_versions_from_tsinghua(self):
        """从清华大学镜像获取版本列表"""
        # 清华镜像主要提供Anaconda，不是纯Python
        # 我们返回预定义版本列表
        versions = self._get_predefined_versions()
        
        # 移除已安装的版本
        installed = self.get_installed_versions()
        versions = [v for v in versions if v not in installed]
        
        logging.info(f"为清华大学镜像预设了 {len(versions)} 个Python版本")
        return versions
    
    def _get_versions_from_bfsu(self):
        """从北京外国语大学镜像获取版本列表"""
        # 北外镜像主要提供Anaconda，不是纯Python
        # 我们返回预定义版本列表
        versions = self._get_predefined_versions()
        
        # 移除已安装的版本
        installed = self.get_installed_versions()
        versions = [v for v in versions if v not in installed]
        
        logging.info(f"为北京外国语大学镜像预设了 {len(versions)} 个Python版本")
        return versions
    
    def _get_versions_generic(self, url):
        """从通用镜像源获取版本列表"""
        verify_ssl = self.settings["download"].get("verify_ssl", True)
        versions = []
        
        try:
            base_url = url.rstrip('/')
            response = requests.get(base_url, timeout=15, verify=verify_ssl)
            
            if response.status_code == 200:
                # 从HTML中提取版本目录
                dir_pattern = r'href="(\d+\.\d+\.\d+)/?"|href="\./(\d+\.\d+\.\d+)/?"|href="\.\./(\d+\.\d+\.\d+)/?"|href="python-(\d+\.\d+\.\d+)'
                matches = re.findall(dir_pattern, response.text)
                
                # 处理匹配结果
                for match in matches:
                    # 找到第一个非空的组
                    for group in match:
                        if group:
                            versions.append(group)
                            break
                
                # 如果没有找到版本号，尝试其他格式
                if not versions:
                    # 尝试获取所有链接并分析
                    link_pattern = r'href="([^"]+)"'
                    links = re.findall(link_pattern, response.text)
                    
                    for link in links:
                        version_match = re.search(r'(\d+\.\d+\.\d+)', link)
                        if version_match:
                            versions.append(version_match.group(1))
                
                versions = sorted(set(versions), key=lambda v: [int(x) for x in v.split('.')])
                
                # 移除已安装的版本
                installed = self.get_installed_versions()
                versions = [v for v in versions if v not in installed]
                
                logging.info(f"从通用镜像找到 {len(versions)} 个版本")
                return versions
            else:
                logging.warning(f"从通用镜像获取版本列表失败，HTTP状态码: {response.status_code}")
        except Exception as e:
            logging.error(f"从通用镜像获取版本列表失败: {str(e)}")
        
        # 如果获取失败，使用预定义版本列表
        logging.info("使用预定义的Python版本列表作为备选")
        versions = self._get_predefined_versions()
        
        # 移除已安装的版本
        installed = self.get_installed_versions()
        versions = [v for v in versions if v not in installed]
        
        return versions 