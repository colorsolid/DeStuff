import json
import os
import re
import sys
import time

from filecmp import cmp
from shutil import copyfile


class DirCheckException(Exception):
    pass


BASE_DIR = os.path.dirname(sys.argv[0])


def config_grids(widget, rows=None, columns=None):
    if not rows:
        rows = [1]
    if not columns:
        columns = [1]
    [widget.rowconfigure(i, weight=w) for i, w in enumerate(rows)]
    [widget.columnconfigure(i, weight=w) for i, w in enumerate(columns)]


def time_this(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        dur_str = '{:.2f}'.format(duration)
        print(f'function: {func.__name__}() executed in {dur_str} seconds')
        return result
    return wrapper


def load_settings():
    filepath = os.path.join(BASE_DIR, 'destuff.json')
    if os.path.isfile(filepath):
        with open(filepath, 'r') as settings_file:
            settings = json.load(settings_file)
    else:
        settings = {
            'font': 'Consolas 11',
            'colors': {
                'light': '#dcdcdc',
                'dark': '#0c0c0c'
            },
            'window': {
                'width': 780,
                'height': 570
            },
            'script-directory': '',
            'search-terms': [],
            'desbndbuild': ''
        }
        save_settings(settings)
    return settings


def save_settings(settings):
    # raise DirCheckException(BASE_DIR)
    filepath = os.path.join(BASE_DIR, 'destuff.json')
    with open(filepath, 'w+') as settings_file:
        json.dump(settings, settings_file)


def get_geometry(settings):
    if all([(key in settings['window']) for key in ['x', 'y']]):
        geometry = '{}x{}+{}+{}'.format(
            settings['window']['width'], settings['window']['height'],
            settings['window']['x'], settings['window']['y']
        )
    else:
        geometry = '{}x{}'.format(
            settings['window']['width'],
            settings['window']['height']
        )
    return geometry


def close_window(root):
    w = root.winfo_width()
    h = root.winfo_height()
    x = root.winfo_x()
    y = root.winfo_y()
    root.settings['window'].update({
        'width': w,
        'height': h,
        'x': x,
        'y': y
    })
    save_settings(root.settings)
    root.destroy()


def update_global(dir):
    nums = [1, 2, 3, 4, 5, 6, 8]
    for num in nums:
        extract_dir = os.path.join(
            dir, fr'm0{num}.luabnd.extract\DemonsSoul\data\DVDROOT\script'
        )
        if os.path.isdir(extract_dir):
            files = os.listdir(extract_dir)
            lua_files = [f for f in files if os.path.splitext(f)[1] == '.lua']
            for file in lua_files:
                main_path = os.path.join(dir, file)
                if os.path.isfile(main_path):
                    extract_path = os.path.join(extract_dir, file)
                    if not os.path.isfile(extract_path) \
                            or not cmp(main_path, extract_path, shallow=False):
                        copyfile(main_path, extract_path)


def update_sdat(dir):
    files = os.listdir(dir)
    dcx_files = [f for f in files if os.path.splitext(f)[1] == '.dcx']
    for file in dcx_files:
        dcx_path = os.path.join(dir, file)
        sdat_path = dcx_path + '.sdat'
        if not os.path.isfile(sdat_path) \
                or not cmp(dcx_path, sdat_path, shallow=False):
            copyfile(dcx_path, sdat_path)


def reset_permanently(dir):
    files = os.listdir(dir)
    files = [os.path.join(dir, f) for f in files]
    [os.remove(f) for f in files if os.path.splitext(f)[1] == '.sdat']
    for filepath in files:
        _, ext = os.path.splitext(filepath)
        if ext == '.bak':
            restored = filepath.replace('.bak', '')
            if os.path.isfile(restored):
                os.remove(filepath)
            else:
                os.rename(filepath, restored)


# @time_this
def find(dir, search_term, case_sensitive=False, regex=False):
    # ['m02_00_00_00.lua', ['line1', 'line2']]
    found = []
    files = []
    for f in os.listdir(dir):
        if os.path.isfile(os.path.join(dir, f)) \
                and os.path.splitext(f)[1] == '.lua':
            files.append(os.path.join(dir, f))
    for file in files:
        lines_found = []
        filename = os.path.split(file)[1]
        text = open(
            file, 'r', encoding='shift_jis', errors='replace'
        ).readlines()
        for i, line in enumerate(text):
            if regex:
                if case_sensitive:
                    results = re.findall(search_term, line)
                else:
                    results = re.findall(search_term, line, re.IGNORECASE)
                if results:
                    lines_found.append((i + 1, line))
            else:
                temp_line = line
                if not case_sensitive:
                    temp_line = line.lower()
                    search_term = search_term.lower()
                if search_term in temp_line:
                    lines_found.append((i + 1, line))
        if lines_found:
            lines_found.reverse()
            found.append((filename, lines_found))
    return found


def remove_search(listframe, settings):
    try:
        click_index = listframe.listbox.curselection()[0]
        search_term = listframe.listbox.get(click_index)
        listframe.listbox.delete(click_index)
        settings['search-terms'].remove(search_term)
        save_settings(settings)
    except IndexError:
        pass


def open_file(dir_, text):
    print(dir_)
    path = os.path.join(dir_, text.split()[1])
    if os.path.isfile(path):
        os.startfile(path)
