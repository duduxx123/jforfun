import paramiko
import os
import sys
import warnings
from cryptography.utils import CryptographyDeprecationWarning

# 忽略加密库警告
warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)


def progress_bar(transferred, total):
    """
    进度条回调函数
    transferred: 已传输字节数
    total: 总字节数
    """
    if total <= 0: return

    # 计算百分比和进度条长度
    percentage = (transferred / total) * 100
    bar_length = 30
    filled_length = int(bar_length * transferred // total)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)

    # \r 使光标回到行首，实现动画效果
    # 使用 .2f 保留两位小数，单位转换为 MB 提高可读性
    mbytes_transferred = transferred / (1024 * 1024)
    mbytes_total = total / (1024 * 1024)

    sys.stdout.write(f"\r正在上传: |{bar}| {percentage:.1f}% ({mbytes_transferred:.2f}/{mbytes_total:.2f} MB)")
    sys.stdout.flush()

def upload_file(local_path, remote_path, host, username, key_path):
    # 1. 检查本地文件是否存在
    if not os.path.exists(local_path):
        print(f"❌ 错误：本地文件 {local_path} 不存在！")
        return

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # 2. 加载私钥并连接
        key = paramiko.RSAKey.from_private_key_file(key_path)
        print(f"正在连接服务器 {host}...")
        ssh.connect(hostname=host, username=username, pkey=key, timeout=15)

        sftp = ssh.open_sftp()
        print(f"✅ 连接成功！准备上传: {os.path.basename(local_path)}")

        # 3. 开始上传，并绑定进度条
        # put 方法会根据文件大小自动分块调用 callback
        sftp.put(local_path, remote_path, callback=progress_bar)

        print(f"\n✨ 上传完成！远程路径: {remote_path}")

        sftp.close()
    except Exception as e:
        print(f"\n❌ 上传过程中出错: {e}")
    finally:
        ssh.close()


if __name__ == "__main__":
    # 本地文件路径 (建议使用正斜杠 / 或原始字符串 r"")
    local_file = r"D:\Photos\lab_data.zip"
    # 远程保存路径
    remote_file = "C:/Users/403_lab/Desktop"

    # --- 配置区 ---
    CONFIG = {
        "host": "192.168.0.101",  # 服务器域名
        "username": "403_lab",  # 服务器用户名
        "key_path": "test_rsa.key",  # 私钥路径

        "local_file": local_file,

        "remote_file": os.path.join(remote_file, os.path.basename(local_file)),
    }

    upload_file(
        CONFIG["local_file"],
        CONFIG["remote_file"],
        CONFIG["host"],
        CONFIG["username"],
        CONFIG["key_path"]
    )
