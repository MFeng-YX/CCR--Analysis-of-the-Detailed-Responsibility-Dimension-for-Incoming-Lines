import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import os
import sys
import importlib.util
from PIL import Image, ImageTk
import io
import threading

# 获取资源文件的绝对路径，适用于 PyInstaller 打包后的程序
def resource_path(relative_path):
    """获取资源文件的绝对路径，适用于 PyInstaller 打包后的程序"""
    try:
        # PyInstaller 创建的临时文件夹
        base_path = sys._MEIPASS
    except Exception:
        # 脚本运行的当前路径
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class DataAnalysisApp:
    def __init__(self):
        # 初始化主窗口
        self.root = tb.Window(title="CCR-进线明细责任维度分析", themename="darkly", size=(1000, 800))
        self.root.minsize(800, 600)
        
        # 获取程序根目录
        self.root_dir = os.path.dirname(os.path.abspath(__file__))
        print(self.root_dir)
        
        # 设置窗口图标
        icon_path = resource_path('favicon.ico')
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)
        else:
            print(f"图标文件未找到：{icon_path}")
        
        # 设置主窗口背景颜色为黑色
        self.root.configure(bg="#000000")
        
        # 加载模块信息
        self.modules = self.load_modules()
        
        # 创建UI元素
        self.create_widgets()
        
    def load_modules(self):
        """加载所有功能模块"""
        # 获取当前文件的绝对路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 计算 modules 目录的路径
        modules_dir = os.path.join(os.path.dirname(current_dir), 'modules')
        
        # 确保 modules 目录在系统路径中
        if modules_dir not in sys.path:
            sys.path.append(modules_dir)
        
        modules = []
        # 遍历 modules 目录下的所有文件
        for file_name in os.listdir(modules_dir):
            if file_name.endswith('.py') and not file_name.startswith('__'):
                module_name = file_name[:-3]  # 去掉 .py 扩展名
                module_path = os.path.join(modules_dir, file_name)
                
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # 检查模块中是否定义了 main 函数
                if hasattr(module, 'main'):
                    # 获取参数中文提示映射
                    param_prompts = getattr(module, 'PARAM_PROMPTS', {})
                    
                    modules.append({
                        "name": f"{module.__doc__.strip() if module.__doc__ else module_name}",
                        "module": module,
                        "params": self.get_function_params(module.main),
                        "prompts": param_prompts  # 存储参数提示映射
                    })
                else:
                    print(f"模块 {module_name} 没有定义 main 函数，已跳过。")
        
        return modules

    def get_function_params(self, func):
        """获取函数参数信息"""
        import inspect
        sig = inspect.signature(func)
        return list(sig.parameters.values())

    def create_widgets(self):
        """创建所有UI元素"""
        # 主框架
        self.main_frame = tb.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        title_label = tb.Label(
            self.main_frame, 
            text="CCR-进线明细责任维度分析", 
            font=("Arial", 20, "bold"),
            bootstyle="light"
        )
        title_label.pack(pady=(0, 20))
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("执行状态：就绪")
        status_bar = tb.Label(
            self.main_frame, 
            textvariable=self.status_var, 
            bootstyle="light",
            font=("Arial", 12)
        )
        status_bar.pack(fill=tk.X, pady=(0, 20))

        # 功能选择框架
        func_frame = tb.Frame(self.main_frame)
        func_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 功能选择标签
        tb.Label(
            func_frame, 
            text="选择功能模块:", 
            font=("Arial", 12),
            bootstyle="light"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        # 功能选择下拉框
        self.func_var = tk.StringVar()
        self.func_combobox = tb.Combobox(
            func_frame, 
            textvariable=self.func_var, 
            width=50,
            bootstyle="light"
        )
        self.func_combobox['values'] = [module['name'] for module in self.modules]
        self.func_combobox.current(0)
        self.func_combobox.pack(side=tk.LEFT, padx=5, pady=5)
        self.func_combobox.bind("<<ComboboxSelected>>", self.on_module_select)
        
        # 参数输入区域
        self.params_frame = tb.LabelFrame(self.main_frame, text="参数输入", bootstyle="light")
        self.params_frame.pack(fill=tk.X, pady=10, padx=10)

    def on_module_select(self, event):
        """当选择功能模块时更新参数输入框"""
        selected_index = self.func_combobox.current()
        module = self.modules[selected_index]
        
        # 清除现有的参数输入框
        for widget in self.params_frame.winfo_children():
            if widget.winfo_class() != "Labelframe":
                widget.destroy()
        
        # 创建新的参数输入框
        self.param_entries = {}
        param_info = module['params']
        param_prompts = module.get('prompts', {})
        
        for param in param_info:
            if param.name == 'self':
                continue
                
            param_frame = tb.Frame(self.params_frame)
            param_frame.pack(fill=tk.X, pady=8)
            
            # 获取参数的中文提示，如果没有则使用参数名称
            prompt = param_prompts.get(param.name, param.name)
            
            tb.Label(
                param_frame, 
                text=f"{prompt}:", 
                font=("Arial", 10),
                bootstyle="light"
            ).pack(side=tk.LEFT, padx=(0, 10))
            
            if param.annotation == 'file_path':
                entry_frame = tb.Frame(param_frame)
                entry_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                entry = tb.Entry(entry_frame, width=50)
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                btn = tb.Button(
                    entry_frame, 
                    text="浏览", 
                    command=lambda e=entry, p=param.name: self.browse_file(e, p),
                    bootstyle="light"
                )
                btn.pack(side=tk.LEFT, padx=5)
            elif param.annotation == 'dir_path':
                entry_frame = tb.Frame(param_frame)
                entry_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                entry = tb.Entry(entry_frame, width=50)
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                btn = tb.Button(
                    entry_frame, 
                    text="浏览", 
                    command=lambda e=entry, p=param.name: self.browse_folder(e, p),
                    bootstyle="light"
                )
                btn.pack(side=tk.LEFT, padx=5)
            else:
                # 判断是否是功能6的 file_paths 参数
                if module['name'].startswith("_6") and param.name == 'file_paths':
                    # 创建一个多行文本框
                    text = tk.Text(param_frame, width=80, height=15, wrap=tk.WORD)
                    text.pack(side=tk.LEFT, fill=tk.X, expand=True)
                    self.param_entries[param.name] = text    
                elif module['name'].startswith("_2") and param.name == 'extra_conditions':
                    text = tk.Text(param_frame, width=80, height=5, wrap=tk.WORD)
                    text.pack(side=tk.LEFT, fill=tk.X, expand=True)
                    self.param_entries[param.name] = text   
                else:
                    entry = tb.Entry(param_frame, width=60)
                    entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
                    self.param_entries[param.name] = entry
            
            # 设置默认值
            if param.default != param.empty:
                if param.name in self.param_entries and isinstance(self.param_entries[param.name], tk.Text):
                    self.param_entries[param.name].insert(tk.END, str(param.default))
                elif param.name in self.param_entries:
                    self.param_entries[param.name].insert(0, str(param.default))
        
        # 添加执行按钮
        execute_btn = tb.Button(
            self.params_frame,
            text="执行",
            command=lambda m=module: self.execute_module(m),
            bootstyle="danger",
            width=10
        )
        execute_btn.pack(pady=20)

    def browse_file(self, entry, param_name):
        """浏览文件对话框"""
        file_path = filedialog.askopenfilename()
        if file_path:
            entry.delete(0, tk.END)
            entry.insert(0, file_path.strip('"'))

    def browse_folder(self, entry, param_name):
        """浏览文件夹对话框"""
        folder_path = filedialog.askdirectory()
        if folder_path:
            entry.delete(0, tk.END)
            entry.insert(0, folder_path.strip('"'))

    def execute_module(self, module):
        """执行选中的功能模块"""
        self.status_var.set("执行状态：执行中...")
        self.root.update()
        
        try:
            # 获取所有参数值
            param_values = {}
            for name, entry in self.param_entries.items():
                if isinstance(entry, tk.Text):
                    param_values[name] = entry.get("1.0", tk.END).strip()
                else:
                    param_values[name] = entry.get()
            
            # 在后台线程中运行模块
            thread = threading.Thread(
                target=self.run_module_in_thread,
                args=(module, param_values)
            )
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            messagebox.showerror("错误", f"执行过程中发生错误：{str(e)}")
            self.status_var.set("执行状态：就绪")

    def run_module_in_thread(self, module, param_values):
        """在后台线程中运行模块"""
        try:
            # 调用模块的main函数
            result = module['module'].main(**param_values)
            
            # 检查模块是否返回成功状态
            if result is not None and result.get('success', False):
                self.root.after(0, lambda: messagebox.showinfo("完成", result.get('message', "操作成功完成！")))
            else:
                self.root.after(0, lambda: messagebox.showwarning("警告", result.get('message', "操作完成但可能有错误，请检查输出。")))
            
            self.root.after(0, lambda: self.status_var.set("执行状态：就绪"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("错误", f"执行过程中发生错误：{str(e)}"))
            self.root.after(0, lambda: self.status_var.set("执行状态：就绪"))

    def run(self):
        """运行主循环"""
        self.root.mainloop()

if __name__ == "__main__":
    app = DataAnalysisApp()
    app.run()