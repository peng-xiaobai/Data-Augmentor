import torch
import os
import numpy as np
import cv2 as cv


def GetFileList(dir):
	l = []
	files = os.listdir(dir)
	for file in files:
		if file.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tif')):
			l.append(os.path.join(dir, file))
	return l


def xywhn2xyxy(x, w, h):
	# Convert nx4 boxes from [x, y, w, h] normalized to [x1, y1, x2, y2] where xy1=top-left, xy2=bottom-right
	y = x.clone() if isinstance(x, torch.Tensor) else np.copy(x)
	# print(f'y={y}')
	y[0] = w * (x[0] - 0.5 * x[2])
	y[1] = h * (x[1] - 0.5 * x[3])
	y[2] = w * (x[0] + 0.5 * x[2])
	y[3] = h * (x[1] + 0.5 * x[3])
	return y


def xyxy2xywhn(size, box):
	# 转换为中心点坐标和宽高
	x_center = (box[0] + box[2]) / 2.0
	y_center = (box[1] + box[3]) / 2.0
	w = box[2] - box[0]
	h = box[3] - box[1]
	# 归一化
	x = x_center / size[0]
	y = y_center / size[1]
	w = w / size[0]
	h = h / size[1]
	return x, y, w, h


def crop_image(image, save_dir, name, suf, boxes):
	"""
	根据标注框 box 划分图像，并保存分割后的图像和对应的 box 标注。
	"""
	H, W, _ = image.shape  # 获取图像的高度和宽度

	# 创建保存目录
	if not os.path.exists(save_dir):
		os.makedirs(save_dir)

	# Left top region
	if boxes[0] == 1:
		img_top_left = image[0:H // 2, 0:W // 2]
		save_path = os.path.join(save_dir, f"{name}_1{suf}")
		cv.imwrite(save_path, img_top_left)
	# Right top region
	if boxes[1] == 1:
		img_top_right = image[0:H // 2, W // 2:W]
		save_path = os.path.join(save_dir, f"{name}_2{suf}")
		cv.imwrite(save_path, img_top_right)
	# Left bottom region
	if boxes[2] == 1:
		img_bottom_left = image[H // 2:H, 0:W // 2]
		save_path = os.path.join(save_dir, f"{name}_3{suf}")
		cv.imwrite(save_path, img_bottom_left)
	# Right bottom region
	if boxes[3] == 1:
		img_bottom_right = image[H // 2:H, W // 2:W]
		save_path = os.path.join(save_dir, f"{name}_4{suf}")
		cv.imwrite(save_path, img_bottom_right)

def split_box(box, shape):
	W, H = shape[1], shape[0]
	n, xmin, ymin, xmax, ymax = box
	regions = []
	# 左上区域
	if xmin < W / 2 and ymin < H / 2:
		xmin_new = max(0, xmin)
		ymin_new = max(0, ymin)
		xmax_new = min(W / 2, xmax)
		ymax_new = min(H / 2, ymax)
		regions.append((n, xmin_new, ymin_new, xmax_new, ymax_new, 'left_top'))
	# 右上区域
	if xmax > W / 2 and ymin < H / 2:
		xmin_new = max(W / 2, xmin) - W / 2
		ymin_new = max(0, ymin)
		xmax_new = min(W, xmax) - W / 2
		ymax_new = min(H / 2, ymax)
		regions.append((n, xmin_new, ymin_new, xmax_new, ymax_new, 'right_top'))
	# 左下区域
	if xmin < W / 2 and ymax > H / 2:
		xmin_new = max(0, xmin)
		ymin_new = max(H / 2, ymin) - H / 2
		xmax_new = min(W / 2, xmax)
		ymax_new = min(H, ymax) - H / 2
		regions.append((n, xmin_new, ymin_new, xmax_new, ymax_new, 'left_bottom'))
	# 右下区域
	if xmax > W / 2 and ymax > H / 2:
		xmin_new = max(W / 2, xmin) - W / 2
		ymin_new = max(H / 2, ymin) - H / 2
		xmax_new = min(W, xmax) - W / 2
		ymax_new = min(H, ymax) - H / 2
		regions.append((n, xmin_new, ymin_new, xmax_new, ymax_new, 'right_bottom'))
	normalized_regions = []
	for region in regions:
		box = region[1:5]  # 获取 (xmin, ymin, xmax, ymax)
		normalized_box = xyxy2xywhn((W/2, H/2), box)  # 归一化
		normalized_regions.append((region[0], *normalized_box, region[5]))  # 保留标签
	return normalized_regions

def save_boxes(label_path, boxes):
	# 先获取标注文件的基本路径和扩展名
	base_label_path, ext = os.path.splitext(label_path)

	for box in boxes:
		# 获取区域标识（左上、右上、左下、右下）
		region = box[5]  # 假设 box[5] 是区域标识
		if region == 'left_top':
			suffix = '_1'
		elif region == 'right_top':
			suffix = '_2'
		elif region == 'left_bottom':
			suffix = '_3'
		elif region == 'right_bottom':
			suffix = '_4'
		else:
			continue  # 如果区域标识不在预期范围内，跳过
		# 构建保存路径
		specific_label_path = f"{base_label_path}{suffix}{ext}"
		# 写入对应区域的标注框
		with open(specific_label_path, 'a') as f:
			f.write(f"{int(box[0])} " + " ".join(map(str, box[1:5])) + '\n')


fileDir = r"E:\peanut_data\j"  # 原图片路径
label_path = r"E:\peanut_data\txt"  # 原label的路径
list1 = GetFileList(fileDir)

image_save_path_head = r"E:\peanut_data\j1"  # 分割后有标注图片储存路径
label_save_path_head = r"E:\peanut_data\txt1"  # 标签储存路径


if not os.path.exists(image_save_path_head):
	os.makedirs(image_save_path_head)
if not os.path.exists(label_save_path_head):
	os.makedirs(label_save_path_head)

for i in list1:
	l = [0, 0, 0, 0]
	img = cv.imread(i)
	shape = img.shape
	seq = 1
	name, suf = os.path.splitext(os.path.basename(i))
	labelname = os.path.join(label_path, name) + '.txt'  # 找到对应图片的label
	pos = []
	with open(labelname, 'r') as f1:
		#print(labelname)
		while True:
			lines = f1.readline()
			if lines == '\n':
				lines = None
			if not lines:
				break
			p_tmp = [float(i) for i in lines.split()]
			pos.append(p_tmp)
		pos = np.array(pos)
		for k in pos:
			k[1:] = xywhn2xyxy(k[1:], shape[1], shape[0])
			regions = split_box(k, shape)
			labelname_new = os.path.join(label_save_path_head, name) + '.txt'
			#print(regions[:5])
			save_boxes(labelname_new, regions)
			for region in regions:
				region_name = region[-1]  # 取元组的最后一个元素
				# 进行判断
				if region_name == 'left_top':
					l[0] = 1
					print("The region is 'left_top'.")
				elif region_name == 'right_top':
					l[1] = 1
					print("The region is 'right_top'.")
				elif region_name == 'left_bottom':
					l[2] = 1
					print("The region is 'left_bottom'.")
				elif region_name == 'right_bottom':
					l[3] = 1
					print("The region is 'right_bottom'.")
		f1.close()
	crop_image(img, image_save_path_head, name, suf, l)
