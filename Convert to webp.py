"""
图片转 WebP + 更新HTML引用 一键脚本
WebP 格式比 PNG 小 60-70%，微信浏览器完全支持
预计：116MB → 30-40MB，加载速度提升 3-4 倍

使用方法：
1. pip install Pillow
2. 把脚本放到项目根目录
3. python convert_to_webp.py
4. 输入 y 确认
"""

import os
import re
from PIL import Image

# ============ 配置 ============
PROJECT_DIR = "."
MAX_WIDTH = 1440        # 手机屏幕够用
MAX_HEIGHT = 1440
WEBP_QUALITY = 72       # WebP 质量 (60-80 推荐)
# ==============================

def main():
    print("=" * 60)
    print("  图片转 WebP + HTML引用更新 一键工具")
    print("=" * 60)

    # ===== 第1步：扫描所有图片 =====
    image_extensions = {'.png', '.jpg', '.jpeg', '.bmp'}
    image_files = []
    
    for dirpath, dirnames, filenames in os.walk(PROJECT_DIR):
        dirnames[:] = [d for d in dirnames if d != '.git' and d != 'node_modules']
        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            if ext in image_extensions:
                image_files.append(os.path.join(dirpath, filename))

    total_size = sum(os.path.getsize(f) for f in image_files)
    print(f"\n找到 {len(image_files)} 张图片，总大小: {total_size / (1024*1024):.1f}MB")
    print(f"配置: 最大 {MAX_WIDTH}x{MAX_HEIGHT}, WebP质量 {WEBP_QUALITY}")
    print(f"预计压缩后: {total_size / (1024*1024) * 0.3:.1f}MB ~ {total_size / (1024*1024) * 0.4:.1f}MB")

    # ===== 第2步：扫描所有代码文件 =====
    code_files = []
    for dirpath, dirnames, filenames in os.walk(PROJECT_DIR):
        dirnames[:] = [d for d in dirnames if d != '.git' and d != 'node_modules']
        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            if ext in ('.html', '.htm', '.js', '.css'):
                code_files.append(os.path.join(dirpath, filename))

    print(f"找到 {len(code_files)} 个代码文件需要更新引用")

    confirm = input(f"\n⚠ 将把所有图片转为 WebP 并更新引用，请确保已备份！继续？(y/n): ")
    if confirm.lower() != 'y':
        print("已取消")
        return

    # ===== 第3步：转换图片 =====
    print("\n===== 开始转换图片 =====\n")
    
    rename_map = {}  # 旧文件名 → 新文件名
    converted = 0
    failed = 0
    saved_bytes = 0

    for i, filepath in enumerate(image_files):
        old_size = os.path.getsize(filepath)
        old_filename = os.path.basename(filepath)
        name_without_ext = os.path.splitext(old_filename)[0]
        new_filename = name_without_ext + ".webp"
        new_filepath = os.path.join(os.path.dirname(filepath), new_filename)

        # 如果同名 webp 已存在，跳过
        if os.path.exists(new_filepath):
            rename_map[old_filename] = new_filename
            try:
                os.remove(filepath)
            except:
                pass
            converted += 1
            continue

        try:
            img = Image.open(filepath)

            # 处理透明通道：RGBA 转为白底 RGB
            if img.mode == 'RGBA':
                background = Image.new('RGB', img.size, (0, 0, 0))  # 黑底（配合你的黑色背景）
                background.paste(img, mask=img.split()[3])
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')

            # 缩小尺寸
            width, height = img.size
            if width > MAX_WIDTH or height > MAX_HEIGHT:
                img.thumbnail((MAX_WIDTH, MAX_HEIGHT), Image.LANCZOS)

            # 保存为 WebP
            img.save(new_filepath, 'WEBP', quality=WEBP_QUALITY, method=4)
            new_size = os.path.getsize(new_filepath)

            # 删除原文件
            os.remove(filepath)

            rename_map[old_filename] = new_filename
            saved_bytes += (old_size - new_size)
            converted += 1

            if converted <= 20 or converted % 50 == 0:
                print(f"  ✅ {old_filename} ({old_size//1024}KB → {new_size//1024}KB)")

        except Exception as e:
            print(f"  ⚠ 失败 {old_filename}: {e}")
            failed += 1

        # 进度
        if (i + 1) % 100 == 0:
            print(f"  ... 已处理 {i+1}/{len(image_files)}")

    print(f"\n转换完成: 成功 {converted}, 失败 {failed}")
    print(f"节省空间: {saved_bytes / (1024*1024):.1f}MB")

    # ===== 第4步：更新代码文件引用 =====
    print("\n===== 更新 HTML/JS 引用 =====\n")

    fixed_files = 0
    total_replacements = 0

    for code_file in code_files:
        try:
            with open(code_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            try:
                with open(code_file, 'r', encoding='gbk') as f:
                    content = f.read()
            except:
                print(f"  ⚠ 无法读取: {code_file}")
                continue

        original = content
        file_fixes = 0

        for old_name, new_name in rename_map.items():
            if old_name in content:
                count = content.count(old_name)
                content = content.replace(old_name, new_name)
                file_fixes += count

        if content != original:
            with open(code_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ {code_file} ({file_fixes} 处)")
            fixed_files += 1
            total_replacements += file_fixes

    # ===== 第5步：验证 =====
    print("\n===== 最终验证 =====\n")

    # 检查残留的旧格式引用
    remaining_old_refs = 0
    for code_file in code_files:
        try:
            with open(code_file, 'r', encoding='utf-8') as f:
                content = f.read()
            matches = re.findall(r'["\'][^"\']*\.(png|jpg|jpeg|bmp)["\']', content, re.IGNORECASE)
            if matches:
                remaining_old_refs += len(matches)
                print(f"  ⚠ {code_file} 仍有 {len(matches)} 处旧引用")
        except:
            pass

    if remaining_old_refs == 0:
        print("  ✅ 所有引用已更新为 .webp！")

    # 检查残留的旧格式文件
    remaining_old_files = 0
    for dirpath, dirnames, filenames in os.walk(PROJECT_DIR):
        dirnames[:] = [d for d in dirnames if d != '.git' and d != 'node_modules']
        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            if ext in image_extensions:
                remaining_old_files += 1

    if remaining_old_files == 0:
        print("  ✅ 所有图片已转为 WebP！")
    else:
        print(f"  ⚠ 还有 {remaining_old_files} 个旧格式图片")

    # 计算最终大小
    final_size = 0
    for dirpath, dirnames, filenames in os.walk(PROJECT_DIR):
        dirnames[:] = [d for d in dirnames if d != '.git' and d != 'node_modules']
        for filename in filenames:
            if filename.endswith('.webp'):
                final_size += os.path.getsize(os.path.join(dirpath, filename))

    # ===== 汇总 =====
    print(f"\n{'=' * 60}")
    print(f"  🎉 全部完成！")
    print(f"  图片转换: {converted} 张 → WebP")
    print(f"  代码修复: {fixed_files} 个文件, {total_replacements} 处引用")
    print(f"  原始大小: {total_size / (1024*1024):.1f}MB")
    print(f"  现在大小: {final_size / (1024*1024):.1f}MB")
    print(f"  压缩比:   {(1 - final_size/total_size)*100:.0f}%")
    print(f"{'=' * 60}")
    print(f"\n下一步:")
    print(f"  1. 本地双击 index.html 测试图片是否正常")
    print(f"  2. git add . && git commit -m '转WebP加速' && git push")
    print(f"  3. 等 Cloudflare 部署完，用手机测试速度")

if __name__ == "__main__":
    main()