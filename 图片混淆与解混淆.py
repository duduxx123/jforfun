import math
from PIL import Image


def gilbert2d(width, height):
    """生成铺满宽高区域的空间填充曲线路径坐标"""
    coordinates = []
    if width >= height:
        generate2d(0, 0, width, 0, 0, height, coordinates)
    else:
        generate2d(0, 0, 0, height, width, 0, coordinates)
    return coordinates


def generate2d(x, y, ax, ay, bx, by, coordinates):
    w = abs(ax + ay)
    h = abs(bx + by)

    dax = 1 if ax > 0 else (-1 if ax < 0 else 0)
    day = 1 if ay > 0 else (-1 if ay < 0 else 0)
    dbx = 1 if bx > 0 else (-1 if bx < 0 else 0)
    dby = 1 if by > 0 else (-1 if by < 0 else 0)

    if h == 1:
        for _ in range(w):
            coordinates.append((x, y))
            x += dax
            y += day
        return

    if w == 1:
        for _ in range(h):
            coordinates.append((x, y))
            x += dbx
            y += dby
        return

    ax2, ay2 = ax // 2, ay // 2
    bx2, by2 = bx // 2, by // 2

    w2 = abs(ax2 + ay2)
    h2 = abs(bx2 + by2)

    if 2 * w > 3 * h:
        if (w2 % 2) and (w > 2):
            ax2 += dax
            ay2 += day
        generate2d(x, y, ax2, ay2, bx, by, coordinates)
        generate2d(x + ax2, y + ay2, ax - ax2, ay - ay2, bx, by, coordinates)
    else:
        if (h2 % 2) and (h > 2):
            bx2 += dbx
            by2 += dby
        generate2d(x, y, bx2, by2, ax2, ay2, coordinates)
        generate2d(x + bx2, y + by2, ax, ay, bx - bx2, by - by2, coordinates)
        generate2d(x + (ax - dax) + (bx2 - dbx), y + (ay - day) + (by2 - dby),
                   -bx2, -by2, -(ax - ax2), -(ay - ay2), coordinates)


class PixelObfuscator:
    def process(self, input_path, output_path, mode="encrypt", iterations=1):
        """
        :param input_path: 输入图片路径
        :param output_path: 输出图片路径
        :param mode: "encrypt" (混淆) 或 "decrypt" (解混淆)
        :param iterations: 混淆/解混淆的次数
        """
        try:
            img = Image.open(input_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
        except Exception as e:
            print(f"图片读取失败: {e}")
            return

        width, height = img.size
        pixels = img.load()

        action_name = "混淆" if mode == "encrypt" else "解混淆"
        print(f"正在生成曲线路径，准备执行 {iterations} 次{action_name}...")

        curve = gilbert2d(width, height)
        total_pixels = width * height

        # 基础偏移量（黄金分割）
        base_offset = round((math.sqrt(5) - 1) / 2 * total_pixels)

        # 核心优化：利用模运算特性，直接计算出多次迭代后的最终绝对偏移量
        # 这样可以避免多重循环，将 O(N * Pixels) 的时间复杂度降为 O(Pixels)
        actual_offset = (base_offset * iterations) % total_pixels

        new_img = Image.new(img.mode, (width, height))
        new_pixels = new_img.load()

        print("正在进行像素级重排...")
        for i in range(total_pixels):
            old_pos = curve[i]
            new_index = (i + actual_offset) % total_pixels
            new_pos = curve[new_index]

            if mode == "encrypt":
                # 加密：旧位置的像素放入新位置
                new_pixels[new_pos[0], new_pos[1]] = pixels[old_pos[0], old_pos[1]]
            elif mode == "decrypt":
                # 解密：新位置的像素放回旧位置
                new_pixels[old_pos[0], old_pos[1]] = pixels[new_pos[0], new_pos[1]]
            else:
                raise ValueError("仅支持 'encrypt' 或 'decrypt'")

        new_img.save(output_path, format="PNG")
        print(f"处理完成！文件已保存为: {output_path}")


if __name__ == "__main__":
    obfuscator = PixelObfuscator()

    # 测试：图片混淆  iterations为混淆次数
    obfuscator.process("imgs/135518788_p0.png", "imgs/encrypted.png", mode="encrypt", iterations=3)

    # 测试：解混淆(必须与混淆次数保持一致才能正确还原)
    obfuscator.process("imgs/encrypted.png", "imgs/decrypted.png", mode="decrypt", iterations=3)
