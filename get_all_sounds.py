import json
import os
import lxml.etree as ET


packs_dir = '.\\soundsense_packs\\packs'
extensions = ('.xml',)
exclude_files = ('autoUpdater.xml',)
exclude_dirs = ('default')
data = {}
for path, dirc, files in os.walk(packs_dir):
    if not path.split('\\')[-1] in exclude_dirs:
        for name in files:
            if name.endswith(extensions) and not name in exclude_files:
                name_wo_ext = name.split('.')[0]
                if not name_wo_ext in data:
                    data[name_wo_ext] = {
                        'music': {},
                        'sound': {},
                    }
                print(name)
                with open(f'{path}\\{name}', 'r') as f:
                    next(f)
                    root = ET.fromstring(f.read().replace('&', '&amp;'))
                    for sound in root.findall('.//sound'):
                        log_pattern = sound.attrib.get('logPattern', None)
                        sound_type = 'music' if sound.attrib.get('channel', '') == 'music' else 'sound'
                        if not log_pattern in data[name_wo_ext]:
                            data[name_wo_ext][sound_type][log_pattern] = []
                        for soundfile in sound.findall('.//soundFile'):
                            filename: str = soundfile.get('fileName', None)
                            if filename:
                                ext = filename.rpartition('.')[-1]
                                if ext == 'm3u':
                                    continue
                                filepath = f"{path}\\{filename}"
                                soundfile_dict = dict(soundfile.attrib)
                                soundfile_dict['filePath'] = filepath.replace('\\', '/')
                                soundfile_dict['fileName'] = soundfile_dict['filePath'].rpartition('/')[-1]
                                data[name_wo_ext][sound_type][log_pattern].append(soundfile_dict)
with open('soundsense_data.json', 'w', encoding='utf-8') as output:
    json.dump(data, output, indent='\t')

patterns = {}
patterns_set = set()
for pack_name, pack in data.items():
    for type, patterns in pack.items():
        for pattern in patterns:
            patterns_set.add(pattern)
for l in patterns_set:
    patterns[l] = [""]
with open('log_patterns_empty.json', 'w', encoding='utf-8') as output:
    json.dump(patterns, output, sort_keys=True, indent='\t')

filenames_dict = {}
for pack_name, pack in data.items():
    for type, patterns in pack.items():
        for pattern, files in patterns.items():
            for file in files:
                if not file:
                    continue
                filename: str = file['fileName']
                if filename not in filenames_dict:
                    filenames_dict[filename] = []
                filenames_dict[filename].append(pattern)
with open('file2patterns.json', 'w', encoding='utf-8') as output:
    json.dump(filenames_dict, output, sort_keys=True, indent='\t')
