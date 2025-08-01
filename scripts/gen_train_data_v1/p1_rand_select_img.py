import os
import shutil
import random
from argparse import ArgumentParser

def copy_images(src_dir, dst_dir, n, mode='random', extensions=('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
    """
    从源文件夹复制n张图片到目标文件夹，支持随机和顺序两种模式
    
    :param src_dir: 源文件夹路径
    :param dst_dir: 目标文件夹路径
    :param n: 要复制的图片数量
    :param mode: 选取模式，'random'为随机选取，'sequential'为顺序选取
    :param extensions: 支持的图片扩展名
    """
    # 确保目标文件夹存在
    os.makedirs(dst_dir, exist_ok=True)
    
    # 获取当前目录名作为前缀（DIV2K_train_HR）
    dir_name = os.path.basename(src_dir.rstrip('/'))
    print(f"将使用目录名作为前缀: {dir_name}")
    
    selected_images = []
    total_images = 0
    
    if mode == 'sequential':
        # 顺序模式：获取排序后的前n个文件，达到数量后停止
        files = sorted(os.listdir(src_dir))  # 先排序所有文件名
        for filename in files:
            file_path = os.path.join(src_dir, filename)
            # if os.path.isfile(file_path) and filename.lower().endswith(extensions):
            total_images += 1
            selected_images.append(filename)
            # 收集到足够数量则停止
            if len(selected_images) >= n:
                break
    else:
        # 随机模式：需要先获取所有图片
        all_images = [
            f for f in os.listdir(src_dir) 
            if os.path.isfile(os.path.join(src_dir, f)) 
            and f.lower().endswith(extensions)
        ]
        total_images = len(all_images)
        if total_images > 0:
            # 随机选择n张图片
            selected_images = random.sample(all_images, min(n, total_images))
    
    if total_images == 0:
        print(f"源文件夹中没有找到支持的图片文件: {src_dir}")
        return
    
    # 确定实际要复制的数量
    actual_n = min(n, total_images)
    if actual_n < n:
        print(f"警告: 请求数量({n})超过可用图片数量({total_images}), 将复制所有可用图片")
        selected_images = selected_images[:actual_n]
    
    # 复制选中的图片
    for i, filename in enumerate(selected_images, 1):
        src_path = os.path.join(src_dir, filename)
        
        # 使用当前目录名作为前缀
        name, ext = os.path.splitext(filename)
        new_filename = f"{dir_name}_{name}{ext}"
        dst_path = os.path.join(dst_dir, new_filename)
        
        # 处理文件名冲突
        counter = 1
        while os.path.exists(dst_path):
            dst_path = os.path.join(dst_dir, f"{dir_name}_{name}_copy{counter}{ext}")
            counter += 1
        
        shutil.copy2(src_path, dst_path)
        print(f"[{i}/{actual_n}] 已复制: {filename} -> {os.path.basename(dst_path)}")
    
    print(f"\n完成! 已从 {src_dir} {'随机' if mode == 'random' else '顺序'}复制 {actual_n} 张图片到 {dst_dir}")

if __name__ == "__main__":
    parser = ArgumentParser(description="图片复制工具，支持随机和顺序两种模式")
    parser.add_argument("src_dir", help="源文件夹路径")
    parser.add_argument("dst_dir", help="目标文件夹路径")
    parser.add_argument("-n", "--number", type=int, required=True, help="要复制的图片数量")
    parser.add_argument("--mode", choices=['random', 'sequential'], default='random',
                      help="选取模式: random(随机选取) 或 sequential(顺序选取) (默认: random)")
    parser.add_argument("--extensions", nargs="+", default=['.png', '.jpg', '.jpeg', '.bmp', '.gif'],
                      help="支持的图片扩展名 (默认: .png .jpg .jpeg .bmp .gif)")
    
    args = parser.parse_args()
    
    copy_images(
        src_dir=args.src_dir,
        dst_dir=args.dst_dir,
        n=args.number,
        mode=args.mode,
        extensions=tuple(ext.lower() for ext in args.extensions)
    )