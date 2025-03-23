#!/bin/bash

# Tạo môi trường ảo
python -m venv .venv

# Kích hoạt môi trường ảo
source .venv/Scripts/activate

# Cài đặt uv nếu chưa có
pip install uv

# Cài đặt dependencies sử dụng uv
uv pip install -r requirements.txt

echo "Môi trường đã được thiết lập thành công!"
echo "Để kích hoạt môi trường, chạy: source .venv/Scripts/activate" 