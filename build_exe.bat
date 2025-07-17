@echo off
title PythoNest打包工具

echo [*] 检查Python环境...
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [!] 错误: 未找到Python环境，请确保已安装Python并添加到PATH中
    pause
    exit /b 1
)

:: 设置颜色
color 0A

echo [*] 开始打包PythoNest应用程序...
echo [*] 时间: %date% %time%
echo [*] 这可能需要几分钟时间，请耐心等待...
echo.

python build_exe.py
if %errorlevel% neq 0 (
    color 0C
    echo.
    echo [!] 打包失败! 请检查logs文件夹中的日志了解详情
    pause
    exit /b 1
)

echo.
echo [*] 操作完成！请在build文件夹中查看结果
echo [*] 感谢使用PythoNest打包工具
pause 