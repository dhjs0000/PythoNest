# PythoNest - Python版本管理工具

PythoNest是一个基于PyQt6开发的图形化Python版本管理工具，旨在帮助用户方便地管理多个Python版本、虚拟环境和包。

## 主要功能

### Python版本管理
- 查看已安装的Python版本
- 安装新的Python版本
- 卸载不需要的Python版本
- 设置默认Python版本

### 虚拟环境管理
- 创建新的虚拟环境
- 使用指定的Python版本创建虚拟环境
- 删除不需要的虚拟环境
- 管理虚拟环境中的包

### 包管理
- 搜索PyPI上的包
- 安装/卸载/升级包
- 查看已安装的包
- 检查过时的包

## 安装说明

1. 确保已安装Python 3.6或更高版本
2. 安装依赖项：
   ```
   pip install -r requirements.txt
   ```
3. 运行主程序：
   ```
   python main.py
   ```

## 生成可执行文件

如果您想将PythoNest打包成Windows可执行文件（.exe），可以按照以下步骤操作：

1. 安装必要的依赖：
   ```
   pip install pyinstaller
   ```

2. 使用提供的打包脚本：
   ```
   python build_exe.py
   ```
   或直接双击运行`build_exe.bat`批处理文件

3. 打包完成后，可执行文件将保存在`build/YYYYMMDD/PythoNest`文件夹中（YYYYMMDD为打包日期）

4. 运行`PythoNest.exe`或`启动PythoNest.bat`来启动应用程序

## 系统要求

- Windows 10或更高版本（目前主要支持Windows平台）
- Python 3.6+
- PyQt6

## 开发说明

本项目使用以下目录结构：
- `src/core/`: 核心功能模块
- `src/ui/`: 用户界面相关代码
- `src/utils/`: 实用工具函数

## 作者

- 作者: dhjs0000
- GitHub: [https://github.com/dhjs0000/PythoNest](https://github.com/dhjs0000/PythoNest)

## 许可证

本项目基于GNU通用公共许可证第3版(GPL-3.0)开源。

您可以自由使用、修改和分发本软件，但需要遵守GPL-3.0协议的条款。详情请参阅[LICENSE](LICENSE)文件。

## 注意事项

- 某些功能（如安装/卸载Python版本）可能需要管理员权限
- 在Windows上，修改系统PATH环境变量需要重启应用程序或系统才能生效
- 本工具目前主要为Windows平台设计，其他平台支持有限 