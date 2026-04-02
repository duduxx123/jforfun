import cv2
import numpy as np
import math

# 基于DCT的水印嵌入
def embed_dct_watermark(carrier_image_path, watermark_text, output_image_path):
    # 1. 读图 → YUV
    img_YUV = cv2.cvtColor(cv2.imread(carrier_image_path), cv2.COLOR_BGR2YUV)

    # 2. 文字 → 二进制
    binary_watermark = ''.join(format(ord(char), '08b') for char in watermark_text)
    watermark_length = len(binary_watermark)
    print(f"DCT Watermark length: {watermark_length} bits")

    # 3. 只处理 Y 通道，8×8 块
    y_channel   = img_YUV[:, :, 0]
    height, width = y_channel.shape
    block_size  = 8
    block_index = 0

    for i in range(0, height, block_size):
        for j in range(0, width, block_size):
            if block_index >= watermark_length:
                break

            block     = y_channel[i:i+block_size, j:j+block_size]
            dct_block = cv2.dct(np.float32(block) / 255.0)

            # 4. 埋 bit：保证「硬币数」奇偶 = bit
            bit = int(binary_watermark[block_index])
            # 先量化到 0.1 的整数倍
            quant = int(abs(dct_block[3, 3]) / 0.1)
            # 强制奇偶
            if bit == 0:
                quant &= ~1          # 清最低位 → 偶数
            else:
                quant |= 1           # 置最低位 → 奇数
            dct_block[3, 3] = quant * 0.1

            # 5. 逆 DCT → 放回 Y 通道
            idct_block = cv2.idct(dct_block) * 255.0
            y_channel[i:i+block_size, j:j+block_size] = idct_block
            block_index += 1

    # 6. 重组图像并保存
    img_YUV[:, :, 0] = y_channel
    watermarked_img = cv2.cvtColor(img_YUV, cv2.COLOR_YUV2BGR)
    cv2.imwrite(output_image_path, watermarked_img)
    print(f"DCT 水印嵌入完成，保存为 {output_image_path}")
    return watermark_length

# 水印提取
def extract_dct_watermark(watermarked_image_path, watermark_length):
    watermarked_YUV = cv2.cvtColor(cv2.imread(watermarked_image_path), cv2.COLOR_BGR2YUV)
    y_channel = watermarked_YUV[:, :, 0]
    height, width = y_channel.shape
    block_size = 8
    extracted_bits = []

    block_index = 0
    for i in range(0, height, block_size):
        for j in range(0, width, block_size):
            if block_index >= watermark_length:
                break
            block = y_channel[i:i+block_size, j:j+block_size]
            dct_block = cv2.dct(np.float32(block) / 255.0)

            # 回读：最低位奇偶 → bit
            coin_count = round(abs(dct_block[3, 3]) / 0.1)
            bit = coin_count & 1
            extracted_bits.append(str(bit))
            block_index += 1

    # 二进制 → 文本
    binary_watermark = ''.join(extracted_bits)
    # 确保二进制字符串长度是8的倍数
    binary_watermark = binary_watermark[: (watermark_length // 8) * 8]
    extracted_text = ''
    for i in range(0, len(binary_watermark), 8):
        byte = binary_watermark[i:i+8]
        if len(byte) == 8:
            extracted_text += chr(int(byte, 2))
    return extracted_text

# 示例用法
if __name__ == "__main__":
    carrier_image_path = 'imgs/135518788_p0.png'  # 载体图像路径
    watermark_text = 'Hello,DCT'  # 水印文本
    compressed_output_path = 'imgs/watermarked_image_DCT_yasuo.jpg'  # 压缩后的图片路径
    # compressed_output_path = 'imgs/QQ20251115154332.jpg'  # 经过qq压缩的图片
    dct_output_path = 'imgs/watermarked_image_DCT.png'  # DCT嵌入水印后的图像路径

    binary_watermark = ''.join(format(ord(char), '08b') for char in watermark_text)
    dct_watermark_length = len(binary_watermark)
    print(dct_watermark_length)

    # DCT水印嵌入和提取
    try:
        #水印嵌入
        dct_watermark_length = embed_dct_watermark(carrier_image_path, watermark_text, dct_output_path)

        # 水印提取(无损)
        dct_extracted_text0 = extract_dct_watermark(dct_output_path, dct_watermark_length)
        print("无损图片提取的DCT水印:", dct_extracted_text0)

        # 将嵌入水印后的图像压缩为JPG
        # 读取嵌入水印后的图像
        watermarked_img = cv2.imread(dct_output_path)
        # 压缩为JPG
        cv2.imwrite(compressed_output_path, watermarked_img, [cv2.IMWRITE_JPEG_QUALITY, 60])  # 调整压缩质量(0-100)
        print(f"嵌入水印后的图像已压缩为JPG，保存为 {compressed_output_path}")

        # 水印提取(压缩)
        dct_extracted_text = extract_dct_watermark(compressed_output_path, dct_watermark_length)
        print("DCT提取的水印:", dct_extracted_text)
    except Exception as e:
        print(f"DCT错误：{str(e)}")
