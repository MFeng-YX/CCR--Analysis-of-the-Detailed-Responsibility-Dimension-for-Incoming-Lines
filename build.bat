@echo off
chcp 65001

setlocal enabledelayedexpansion

set "ROOT_DIR=%~dp0"
set "ICON_PATH=%ROOT_DIR%favicon.ico"

if not exist "%ICON_PATH%" (
    echo 图标文件未找到，请将图标文件放置在程序根目录下，并命名为 my_icon.ico
    echo 打包中止...
    pause
    exit /b
)

pyinstaller ^
    --onefile ^
    --windowed ^
    --add-data "modules/*.py;modules" ^
    --add-data "ui/*.py;ui" ^
    --add-data "utils/*.py;utils" ^
    --name "CCR-进线明细责任维度分析" ^
    --icon "%ICON_PATH%" ^
    --hidden-import "pandas" ^
    --hidden-import "matplotlib" ^
    --hidden-import "numpy" ^
    --hidden-import "openpyxl" ^
    --hidden-import "pillow" ^
    --hidden-import "ttkbootstrap" ^
    --hidden-import "xlrd" ^
    main.py

endlocal
echo 打包完成！可执行文件位于 dist 文件夹中。
pause