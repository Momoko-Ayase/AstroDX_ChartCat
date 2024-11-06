# -*- coding: utf-8 -*-

import os
import json
import shutil
import requests

# 常量定义
DATA_URL = 'https://dp4p6x0xfi5o9.cloudfront.net/maimai/data.json'
DATA_FILE = 'data.json'
CHARTS_DIR = 'charts'
COLLECTIONS_DIR = 'collections'
LEVELS_DIR = 'levels'

# 步骤1：下载 data.json 文件
response = requests.get(DATA_URL)
with open(DATA_FILE, 'wb') as f:
    f.write(response.content)

# 读取 data.json
with open(DATA_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)
songs = data.get('songs', [])

# 定义分类列表
collections_list = [
    "POPS＆アニメ",
    "niconico＆ボーカロイド",
    "東方Project",
    "ゲーム＆バラエティ",
    "maimai",
    "オンゲキ＆CHUNITHM",
    "宴会場"
]

# 步骤2：扫描 "charts" 目录
version_list = []
if os.path.exists(CHARTS_DIR):
    for version_name in os.listdir(CHARTS_DIR):
        version_path = os.path.join(CHARTS_DIR, version_name)
        if os.path.isdir(version_path):
            version_list.append(version_name)
else:
    print(f'"{CHARTS_DIR}" 目录不存在。')
    exit()

# 步骤3：创建 "collections" 目录及其子目录
if not os.path.exists(COLLECTIONS_DIR):
    os.makedirs(COLLECTIONS_DIR)

# 创建分类子目录和 manifest.json
for collection in collections_list + version_list:
    collection_path = os.path.join(COLLECTIONS_DIR, collection)
    if not os.path.exists(collection_path):
        os.makedirs(collection_path)
    manifest_path = os.path.join(collection_path, 'manifest.json')
    if not os.path.exists(manifest_path):
        manifest_data = {
            "name": collection,
            "id": None,
            "serverUrl": None,
            "levelIds": []
        }
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest_data, f, ensure_ascii=False, indent=4)

# 步骤4：处理每个歌曲文件夹
if not os.path.exists(LEVELS_DIR):
    os.makedirs(LEVELS_DIR)

for version_name in version_list:
    version_path = os.path.join(CHARTS_DIR, version_name)
    collection_manifest_path = os.path.join(COLLECTIONS_DIR, version_name, 'manifest.json')

    # 读取版本的 manifest.json
    with open(collection_manifest_path, 'r', encoding='utf-8') as f:
        version_manifest = json.load(f)

    for song_name in os.listdir(version_path):
        song_src_path = os.path.join(version_path, song_name)
        song_dest_path = os.path.join(LEVELS_DIR, song_name)

        if os.path.isdir(song_src_path):
            # 如果歌曲已存在于 "levels" 目录中，替换旧的文件夹
            if os.path.exists(song_dest_path):
                shutil.rmtree(song_dest_path)
            shutil.copytree(song_src_path, song_dest_path)

            # 将歌曲名称添加到版本的 manifest.json
            if song_name not in version_manifest['levelIds']:
                version_manifest['levelIds'].append(song_name)

            # 在 data.json 中查找歌曲的分类
            song_collection = None
            special_prefixes = ["[光", "[星", "[傾", "[蔵", "[狂", "[辛", "[耐", "[蛸", "[角", "[宴", "[覺", "[協",
                                "[逆", "[片", "[即", "[撫"]
            if any(song_name.startswith(prefix) for prefix in special_prefixes):
                song_collection = "宴会場"
            else:
                for song in songs:
                    if song.get('songId') == song_name:
                        song_collection = song.get('category')
                        break

            # 将歌曲名称添加到对应分类的 manifest.json
            if song_collection and song_collection in collections_list:
                collection_manifest_path = os.path.join(COLLECTIONS_DIR, song_collection, 'manifest.json')
                with open(collection_manifest_path, 'r', encoding='utf-8') as f:
                    collection_manifest = json.load(f)
                if song_name not in collection_manifest['levelIds']:
                    collection_manifest['levelIds'].append(song_name)
                with open(collection_manifest_path, 'w', encoding='utf-8') as f:
                    json.dump(collection_manifest, f, ensure_ascii=False, indent=4)

    # 保存版本的 manifest.json
    with open(os.path.join(COLLECTIONS_DIR, version_name, 'manifest.json'), 'w', encoding='utf-8') as f:
        json.dump(version_manifest, f, ensure_ascii=False, indent=4)