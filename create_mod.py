import json
import os.path
import shutil
from pydub import AudioSegment

mod_path_sound = './soundsense2mod_sfx/'
mod_path_music = './soundsense2mod_music/'

with open('log_patterns.json', 'r', encoding='utf-8') as f:
    log_patterns2raw = json.load(f)

with open('soundsense_data.json', 'r', encoding='utf-8') as f:
    soundsense_data = json.load(f)

with open('file2patterns.json', 'r', encoding='utf-8') as f:
    files2patterns = json.load(f)


def copy_file(file_data, type):
    file_name: str = file_data['fileName']
    src = file_data['filePath']
    name_wo_ext, sep, ext = file_name.rpartition('.')
    dest = "{0}sound/{1}.ogg".format(mod_path_sound if type == 'sound' else mod_path_music, name_wo_ext)
    file_dfid = ""
    letter = False
    for i, x in enumerate(name_wo_ext, 0):
        if x.isalpha():
            file_dfid += x
            letter = True
        elif x.isspace() or x == '_':
            file_dfid += '_'
        elif x.isnumeric() and letter:
            file_dfid += x
    file_dfid = file_dfid.strip('_').upper()
    if not os.path.isfile(dest):
        if ext == 'ogg':
            print(f"Copying {file_name}")
            try:
                shutil.copy(src, dest)
            except shutil.SameFileError:
                pass
        else:
            print(f"Converting {file_name} from {ext} to ogg")
            sound = AudioSegment.from_file(src, format=ext)
            sound.export(dest, format='ogg')

    return f"{name_wo_ext}.ogg", name_wo_ext, file_dfid


def get_announcements(file):
    result = set()
    patterns = files2patterns[file['fileName']]
    for pattern in log_patterns2raw:
        if pattern in patterns and log_patterns2raw[pattern] != ['']:
            for a in log_patterns2raw[pattern]:
                result.add(a)
    return list(result)


added_ids = []
counter_s = 1
counter_m = 1
sound_pack_file_name = f"soundsense2mod_sound_file"
sound_pack_file = f"{sound_pack_file_name}\n\n[OBJECT:SOUND_FILE]\n"
music_pack_file_name = f"soundsense2mod_music_file"
music_pack_file = f"{music_pack_file_name}\n\n[OBJECT:MUSIC_FILE]\n"
object_sound_pack_file_name = f"soundsense2mod_sound"
object_sound_pack_file_content = f"{object_sound_pack_file_name}\n\n[OBJECT:SOUND]\n"
object_music_pack_file_name = f"soundsense2mod_music"
object_music_pack_file_content = f"{object_music_pack_file_name}\n\n[OBJECT:MUSIC]\n"
for pack_name in soundsense_data:
    print(pack_name)
    if soundsense_data[pack_name]['music']:
        added = False
        for pattern, files in soundsense_data[pack_name]['music'].items():
            for music_file_data in files:
                name, title, file_id = copy_file(music_file_data, 'music')
                if file_id not in added_ids:
                    added = True
                    added_ids.append(file_id)
                    # TODO: add authors from xml comments
                    music_pack_file += f"\n[MUSIC_FILE:{file_id}]\n" \
                                       f"    [FILE:{name}]\n" \
                                       f"    [TITLE:{title}]\n"
                    object_music_pack_file_content += f"\n[MUSIC:SOUND2MOD_MUSIC_{counter_m}]\n" \
                                                      f"	[FILE:{file_id}]\n" \
                                                      f"    [CARD:{file_id}]\n"
                    counter_m += 1

    if soundsense_data[pack_name]['sound']:
        added = False
        for pattern, files in soundsense_data[pack_name]['sound'].items():
            for file in files:
                name, title, file_id = copy_file(file, 'sound')
                if file_id not in added_ids:
                    added = True
                    added_ids.append(file_id)
                    sound_pack_file += f"\n[SOUND_FILE:{file_id}]\n" \
                                       f"    [FILE:{name}]\n" \
                                       f"    [TITLE:{title}]\n"

                    object_sound_pack_file_content += f"\n[SOUND:SOUND2MOD_SOUND_{counter_s}]\n" \
                                                      f"	[FILE:{file_id}]\n"
                    counter_s += 1
                    announcements = get_announcements(file)
                    for announcement in announcements:
                        object_sound_pack_file_content += f"	[ANNOUNCEMENT:{announcement}]\n"

with open(mod_path_sound + f"sound/{sound_pack_file_name}.txt", 'w', encoding='utf-8') as f:
    f.write(sound_pack_file)

with open(mod_path_music + f"sound/{music_pack_file_name}.txt", 'w', encoding='utf-8') as f:
    f.write(music_pack_file)

with open(mod_path_sound + f"objects/{object_sound_pack_file_name}.txt", 'w', encoding='utf-8') as f:
    f.write(object_sound_pack_file_content)

with open(mod_path_music + f"objects/{object_music_pack_file_name}.txt", "w", encoding='utf-8') as f:
    f.write(object_music_pack_file_content)
