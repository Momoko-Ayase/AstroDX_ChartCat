# -*- coding: utf-8 -*-

import os
import json
import shutil
import requests
import sys

# 常量定义
DATA_URL = 'https://dp4p6x0xfi5o9.cloudfront.net/maimai/data.json'
DATA_FILE = 'data.json'
CHARTS_DIR = 'charts'
COLLECTIONS_DIR = 'collections'
LEVELS_DIR = 'levels'

# 参数处理
remove_video = '-novideo' in sys.argv
restore_mode = '-restore' in sys.argv

if restore_mode:
    print("Running in RESTORE mode...")
    # 忽略的分类列表
    ignored_collections = [
        "POPS＆アニメ",
        "niconico＆ボーカロイド",
        "東方Project",
        "ゲーム＆バラエティ",
        "maimai",
        "オンゲキ＆CHUNITHM",
        "宴会場"    
    ]
    
    if not os.path.exists(COLLECTIONS_DIR):
        print(f"'{COLLECTIONS_DIR}' directory not found. Cannot restore.")
        exit()
        
    if not os.path.exists(CHARTS_DIR):
        os.makedirs(CHARTS_DIR)

    # 遍历 collections 目录
    for version_name in os.listdir(COLLECTIONS_DIR):
        if version_name in ignored_collections:
            continue
            
        version_manifest_path = os.path.join(COLLECTIONS_DIR, version_name, 'manifest.json')
        if not os.path.exists(version_manifest_path):
            continue
            
        # 读取版本 manifest
        try:
            with open(version_manifest_path, 'r', encoding='utf-8') as f:
                version_manifest = json.load(f)
        except Exception as e:
            print(f"Error reading manifest for {version_name}: {e}")
            continue
            
        level_ids = version_manifest.get('levelIds', [])
        if not level_ids:
            continue
            
        # 确保目标版本目录存在
        version_charts_dir = os.path.join(CHARTS_DIR, version_name)
        if not os.path.exists(version_charts_dir):
            os.makedirs(version_charts_dir)
            
        for song_name in level_ids:
            song_src_path = os.path.join(LEVELS_DIR, song_name)
            song_dest_path = os.path.join(version_charts_dir, song_name)
            
            if os.path.exists(song_src_path):
                try:
                    # 如果目标已存在，先删除
                    if os.path.exists(song_dest_path):
                        shutil.rmtree(song_dest_path)
                    
                    shutil.move(song_src_path, song_dest_path)
                    print(f"Restored {song_name} to {version_name}")
                except Exception as e:
                    print(f"Error restoring {song_name}: {e}")
            else:
                # 可能是已经被移动了，或者是 manifest 里有但 levels 里没有
                pass
    
    print("Restore operation completed.")
    exit()

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

    # 获取当前版本 manifest 中已有的 levelIds，用于快速查找
    existing_level_ids = set(version_manifest.get('levelIds', []))

    for song_name in os.listdir(version_path):
        song_src_path = os.path.join(version_path, song_name)
        song_dest_path = os.path.join(LEVELS_DIR, song_name)

        if os.path.isdir(song_src_path):
            # 2. 检查必要文件
            # maidata.txt 是必须的
            if not os.path.exists(os.path.join(song_src_path, 'maidata.txt')):
                print(f"Skipping {song_name}: Missing maidata.txt")
                continue
            
            # track.mp3 和 track.ogg 二者需要有一个
            has_mp3 = os.path.exists(os.path.join(song_src_path, 'track.mp3'))
            has_ogg = os.path.exists(os.path.join(song_src_path, 'track.ogg'))
            
            if not (has_mp3 or has_ogg):
                print(f"Skipping {song_name}: Missing audio file (track.mp3 or track.ogg)")
                continue

            # 3. 检测 manifest 中是否有对应谱面索引
            is_known_song = song_name in existing_level_ids

            # 1. 移动谱面到 levels (替换旧的)
            if os.path.exists(song_dest_path):
                try:
                    shutil.rmtree(song_dest_path)
                except Exception as e:
                    print(f"Error removing existing {song_dest_path}: {e}")
                    continue
            
            try:
                shutil.move(song_src_path, song_dest_path)
                print(f"Moved {song_name} to levels")
                
                # 如果启用了 -novideo 参数，移除视频文件
                if remove_video:
                    for file in os.listdir(song_dest_path):
                        if file.lower().endswith('.mp4'):
                            try:
                                os.remove(os.path.join(song_dest_path, file))
                                print(f"Removed video from {song_name}")
                            except Exception as e:
                                print(f"Error removing video from {song_name}: {e}")

            except Exception as e:
                print(f"Error moving {song_name}: {e}")
                continue

            # 如果 manifest 中已有索引，则跳过后续 manifest 更新步骤
            if is_known_song:
                continue

            # --- 以下是新谱面的处理逻辑 (Manifest 更新) ---

            # 将歌曲名称添加到版本的 manifest.json
            version_manifest['levelIds'].append(song_name)
            existing_level_ids.add(song_name) # 更新本地集合

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
                collection_manifest_path_cat = os.path.join(COLLECTIONS_DIR, song_collection, 'manifest.json')
                
                # 读取分类 manifest
                if os.path.exists(collection_manifest_path_cat):
                    with open(collection_manifest_path_cat, 'r', encoding='utf-8') as f:
                        collection_manifest = json.load(f)
                else:
                    # 理论上前面已经创建了，但为了安全
                    collection_manifest = {
                        "name": song_collection,
                        "id": None,
                        "serverUrl": None,
                        "levelIds": []
                    }

                if song_name not in collection_manifest['levelIds']:
                    collection_manifest['levelIds'].append(song_name)
                    with open(collection_manifest_path_cat, 'w', encoding='utf-8') as f:
                        json.dump(collection_manifest, f, ensure_ascii=False, indent=4)

    # 保存版本的 manifest.json (循环结束后保存一次即可)
    with open(collection_manifest_path, 'w', encoding='utf-8') as f:
        json.dump(version_manifest, f, ensure_ascii=False, indent=4)
    
    # 检查版本文件夹是否为空，如果为空则删除
    if not os.listdir(version_path):
        try:
            os.rmdir(version_path)
            print(f"Removed empty directory: {version_path}")
        except Exception as e:
            print(f"Error removing empty directory {version_path}: {e}")

# 4. 检查 collections 中的 manifests，确认所有谱面索引在 levels 里面都有对应的谱面
print("\nVerifying manifests against levels...")
all_manifests_files = []
for root, dirs, files in os.walk(COLLECTIONS_DIR):
    for file in files:
        if file == 'manifest.json':
            all_manifests_files.append(os.path.join(root, file))

missing_levels = []
for manifest_file in all_manifests_files:
    try:
        with open(manifest_file, 'r', encoding='utf-8') as f:
            manifest_data = json.load(f)
            level_ids = manifest_data.get('levelIds', [])
            collection_name = manifest_data.get('name', 'Unknown')
            
            for level_id in level_ids:
                level_path = os.path.join(LEVELS_DIR, level_id)
                if not os.path.exists(level_path):
                    missing_levels.append(f"[{collection_name}] {level_id}")
    except Exception as e:
        print(f"Error reading manifest {manifest_file}: {e}")

if missing_levels:
    print("WARNING: The following levels referenced in manifests are missing from the 'levels' directory:")
    for missing in missing_levels:
        print(f" - {missing}")
else:
    print("Verification successful: All manifest entries exist in 'levels'.")