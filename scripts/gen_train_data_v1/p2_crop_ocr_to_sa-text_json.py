import os
import json
import argparse
from glob import glob
from PIL import Image
from paddleocr import PaddleOCR


class ImageProcessor:
    def __init__(self):
        self.ocr = PaddleOCR(
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False
        )

    def split_image(self, input_path, output_dir, tile_size=512):
        """将图像切分为 tile_size x tile_size 的小块"""
        os.makedirs(output_dir, exist_ok=True)
        files = []

        if os.path.isdir(input_path):
            for root, _, filenames in os.walk(input_path):
                for f in filenames:
                    if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                        files.append(os.path.join(root, f))
        elif os.path.isfile(input_path):
            files = [input_path]

        for file_path in files:
            img = Image.open(file_path)
            width, height = img.size
            basename = os.path.splitext(os.path.basename(file_path))[0]
            cols, rows = width // tile_size, height // tile_size

            for i in range(rows):
                for j in range(cols):
                    left, upper = j * tile_size, i * tile_size
                    right, lower = left + tile_size, upper + tile_size
                    tile = img.crop((left, upper, right, lower))
                    output_path = os.path.join(output_dir, f"{basename}_{i}_{j}.png")
                    tile.save(output_path)

            print(f"切分完成: {file_path} -> {cols * rows} 块")

    def run_ocr(self, input_path, output_dir):
        """运行 OCR 并保存识别结果为图像和 JSON"""
        os.makedirs(output_dir, exist_ok=True)
        files = []

        if os.path.isdir(input_path):
            for root, _, filenames in os.walk(input_path):
                for f in filenames:
                    if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                        files.append(os.path.join(root, f))
        elif os.path.isfile(input_path):
            files = [input_path]
        print(f"总图片文件数量: {len(files)}")
        for file_path in files:
            result = self.ocr.predict(input=file_path)
            print(f"OCR识别: {file_path} -> {len(result)} 条结果")
            for res in result:
                # res.save_to_img(output_dir)
                res.save_to_json(output_dir)

    def merge_jsons(self, input_dir, output_file):
        """合并 OCR 输出目录下的所有 JSON 文件为一个"""
        def interpolate(poly):
            return [
                [p1[0] * (1 - r) + p2[0] * r, p1[1] * (1 - r) + p2[1] * r]
                for i in range(4)
                for p1, p2 in [(poly[i], poly[(i + 1) % 4])]
                for r in [j / 4 for j in range(4)]
            ] if len(poly) == 4 else poly

        def process_file(in_path):
            with open(in_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            name = os.path.splitext(os.path.basename(data["input_path"]))[0]
            return {
                name: {
                    "0": {
                        "text_instances": [
                            {
                                "bbox": box,
                                "text": text,
                                "polygon": interpolate(poly)
                            }
                            for text, poly, box in zip(
                                data["rec_texts"],
                                data["rec_polys"],
                                data["rec_boxes"]
                            )
                        ]
                    }
                }
            }

        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        combined_data = {}
        processed_count = 0

        for f in os.listdir(input_dir):
            if f.endswith('.json'):
                try:
                    file_path = os.path.join(input_dir, f)
                    result = process_file(file_path)
                    combined_data.update(result)
                    processed_count += 1
                    print(f"合并成功: {f}")
                except Exception as e:
                    print(f"合并失败 {f}: {e}")

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, indent=2, ensure_ascii=False)
        print(f"\n✅ 合并完成: {output_file}")
        print(f"共合并了 {processed_count} 个 JSON 文件")


def main():
    parser = argparse.ArgumentParser(description='图像切分 + OCR + JSON 合并工具')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # split
    split_parser = subparsers.add_parser('split', help='图像切分')
    split_parser.add_argument('input_path', help='输入图像或目录')
    split_parser.add_argument('output_dir', help='输出图像切块目录')
    split_parser.add_argument('--tile_size', type=int, default=512, help='切块大小，默认512')

    # ocr
    ocr_parser = subparsers.add_parser('ocr', help='OCR识别 + 自动合并JSON')
    ocr_parser.add_argument('input', help='图像输入路径或目录')
    ocr_parser.add_argument('output', help='OCR输出文件目录')
    ocr_parser.add_argument('output_json', help='合并后的JSON路径')

    # full
    full_parser = subparsers.add_parser('full', help='完整流程：切分 + OCR + 合并')
    full_parser.add_argument('input_path', help='输入图像或目录')
    full_parser.add_argument('output_json', help='最终合并输出JSON路径')
    full_parser.add_argument('--tile_size', type=int, default=512, help='切块大小')
    full_parser.add_argument('--temp_dir', default='temp', help='中间过程目录')

    args = parser.parse_args()
    processor = ImageProcessor()

    if args.command == 'split':
        processor.split_image(args.input_path, args.output_dir, args.tile_size)

    elif args.command == 'ocr':
        processor.run_ocr(args.input, args.output)
        processor.merge_jsons(args.output, args.output_json)

    elif args.command == 'full':
        split_dir = os.path.join(args.temp_dir, 'split')
        ocr_dir = os.path.join(args.temp_dir, 'ocr')
        print("开始切分...")
        processor.split_image(args.input_path, split_dir, args.tile_size)

        print("开始OCR...")
        processor.run_ocr(split_dir, ocr_dir)

        print("开始合并...")
        processor.merge_jsons(ocr_dir, args.output_json)


if __name__ == '__main__':
    main()
