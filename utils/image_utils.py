from PIL import Image, ImageTk
import io

def image_to_tkinter(image_data):
    """将图片字节数据转换为Tkinter可显示的格式"""
    try:
        image = Image.open(io.BytesIO(image_data))
        return ImageTk.PhotoImage(image)
    except Exception as e:
        print(f"图片转换错误：{e}")
        return None

def resize_image(image_data, width, height):
    """调整图片大小"""
    try:
        image = Image.open(io.BytesIO(image_data))
        image = image.resize((width, height), Image.LANCZOS)
        return ImageTk.PhotoImage(image)
    except Exception as e:
        print(f"图片调整大小错误：{e}")
        return None

def load_image_from_path(image_path):
    """从文件路径加载图片"""
    try:
        with open(image_path, "rb") as file:
            image_data = file.read()
            return image_to_tkinter(image_data)
    except Exception as e:
        print(f"加载图片错误：{e}")
        return None