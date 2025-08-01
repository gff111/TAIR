import json
import os
import argparse
'''
用于补充数据 从生成的单json中合并出最终json
'''
def interpolate(poly):
    """4点转16点插值"""
    return [
        [p1[0] * (1 - r) + p2[0] * r, p1[1] * (1 - r) + p2[1] * r]
        for i in range(4)
        for p1, p2 in [(poly[i], poly[(i+1)%4])]
        for r in [j/4 for j in range(4)]
    ] if len(poly) == 4 else poly

def process_file(in_path):
    """处理单个文件并返回结果数据"""
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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', required=True, help='输入目录')     # 输入单json文件
    parser.add_argument('-o', '--output', required=True, help='输出文件路径')
    args = parser.parse_args()

    # 创建输出目录（如果不存在）
    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    combined_data = {}
    processed_count = 0  # 新增计数器
    
    for f in os.listdir(args.input):
        if f.endswith('.json'):
            try:
                file_path = os.path.join(args.input, f)
                result = process_file(file_path)
                combined_data.update(result)
                processed_count += 1  # 成功处理一个文件就增加计数
                print(f"处理成功: {f}")
            except Exception as e:
                print(f"处理失败 {f}: {e}")
    
    # 将合并后的数据写入单个文件
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(combined_data, f, indent=2, ensure_ascii=False)
    print(f"所有结果已保存到: {args.output}")
    print(f"共处理了 {processed_count} 个图片对应的JSON文件")  # 新增输出统计信息

if __name__ == "__main__":
    main()