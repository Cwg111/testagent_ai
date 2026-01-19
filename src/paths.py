# @FileName  :paths.py
# @Time      :2026/1/19 9:55
# @Author    :ChenWenGang
import os

src_path = os.path.dirname(os.path.abspath(__file__))
base_path = os.path.dirname(src_path)

if __name__ == "__main__":
    print(base_path)
