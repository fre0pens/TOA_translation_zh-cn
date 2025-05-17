import os
import json
import re

translation_source_path = './translation_src/'
dictionary_path = './dictionary/'



def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def infer_type(value):
    if value.lower() in ('true', 'false'):
        return value.lower() == 'true'
    try:
        return int(value)
    except:
        try:
            return float(value)
        except:
            return value

def process_encounter():
    with open(os.path.join(translation_source_path, 'encounters.json'), 'r', encoding='utf-8') as f:
        data = json.load(f)
    for key, events in data.items():
        for event in events:
            event_keys = list(event.keys())
            for k in event_keys:
                if k != "text":
                    del event[k]
    os.makedirs(dictionary_path, exist_ok=True)  # Ensure the directory exists
    save_json(os.path.join(dictionary_path, 'encounters.json'), data)

def build_nested_dict(keys, value, data, delimiter='.', array_delimiter='[', type_infer=True):
    current = data
    for i, key in enumerate(keys[:-1]):
        # 处理数组语法 parent[0].child
        arr_match = re.match(r'(\w+)$$(\d+)$$$', key)
        if arr_match:
            arr_key, arr_idx = arr_match.groups()
            arr_idx = int(arr_idx)
            if arr_key not in current:
                current[arr_key] = []
            while len(current[arr_key]) <= arr_idx:
                current[arr_key].append({} if i < len(keys)-2 else None)
            current = current[arr_key][arr_idx]
        else:
            if key not in current or not isinstance(current[key], dict):
                current[key] = {}
            current = current[key]
    
    last_key = keys[-1]
    # 类型推断
    final_value = infer_type(value) if type_infer else value
    # 处理最终键的数组语法
    arr_match = re.match(r'(\w+)$$(\d+)$$$', last_key)
    if arr_match:
        arr_key, arr_idx = arr_match.groups()
        arr_idx = int(arr_idx)
        if arr_key not in current:
            current[arr_key] = []
        while len(current[arr_key]) <= arr_idx:
            current[arr_key].append(None)
        current[arr_key][arr_idx] = final_value
    else:
        current[last_key] = final_value
    return data

def properties_to_json(delimiter='.', indent=4):
    data = {}
    with open(os.path.join(translation_source_path, 'strings.properties'), 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith(('#', '!')):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().replace('\\=', '=')  # 处理转义等号
                # 分割嵌套键
                key_parts = []
                buffer = []
                escape = False
                for char in key:
                    if escape:
                        buffer.append(char)
                        escape = False
                    elif char == '\\':
                        escape = True
                    elif char == delimiter and not escape:
                        key_parts.append(''.join(buffer))
                        buffer = []
                    else:
                        buffer.append(char)
                if buffer:
                    key_parts.append(''.join(buffer))
                # 构建嵌套结构
                data = build_nested_dict(key_parts, value, data, delimiter)
    
    with open(os.path.join(dictionary_path, 'strings.properties.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)



# Example usage
if __name__ == '__main__':
    process_encounter()
    properties_to_json()