# 作者：CSDN-笑脸惹桃花 https://blog.csdn.net/qq_67105081?type=blog
# github:peng-xiaobai https://github.com/peng-xiaobai/Dataset-Conversion
import os,shutil
from PIL import Image, ImageEnhance


def write_xml(folder_path,output_folder, new_suffix):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder_path):
        # 获取文件的扩展名
        file_base_name, file_extension = os.path.splitext(filename)
        # 构造新的文件名
        new_filename = f"{file_base_name}{new_suffix}{file_extension}"
        # 获取完整的原文件路径和新文件路径
        old_file_path = os.path.join(folder_path, filename)
        new_file_path = os.path.join(output_folder, new_filename)
        # 复制或重命名文件
        shutil.copy(old_file_path, new_file_path)

# 调整对比度
def adjust_contrast(image, factor):
    enhancer = ImageEnhance.Contrast(image)
    adjusted_image = enhancer.enhance(factor)
    return adjusted_image

# 调整锐度
def adjust_sharpness(image, factor):
    enhancer = ImageEnhance.Sharpness(image)
    adjusted_image = enhancer.enhance(factor)
    return adjusted_image

# 批量处理文件夹中的图片
def process_images(input_folder, output_folder, sharpness_factor, new_suffix):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tif')):
            image_path = os.path.join(input_folder, filename)
            image = Image.open(image_path)
            # 调整锐度
            image_with_adjusted_sharpness = adjust_sharpness(image, sharpness_factor)
            file_base_name, file_extension = os.path.splitext(filename)
            new_filename = f"{file_base_name}{new_suffix}{file_extension}"
            # 保存到输出文件夹
            output_path = os.path.join(output_folder, new_filename)
            image_with_adjusted_sharpness.save(output_path)
            print(f"Processed and saved: {output_path}")

# 输入文件夹和输出文件夹路径
input_folder_jpg = r'E:\peanut_data\jj'  #输入图片文件夹
input_folder_xml = r'E:\peanut_data\xx'  #输入标签文件夹
output_folder_jpg = r'E:\peanut_data\jj-'  #输出图片文件夹
output_folder_xml = r'E:\peanut_data\xx-'  #输出标签文件夹
new_suffix = '_r'
# 调整参数
sharpness_factor = 4.0  #锐度因子

# 执行批量处理
process_images(input_folder_jpg, output_folder_jpg, sharpness_factor,new_suffix)
write_xml(input_folder_xml,output_folder_xml, new_suffix)
