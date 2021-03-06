import sys
import os
from os import listdir
from os.path import isfile, isdir, join

blacklist = ['__pycache__', 'migrations', 'env', '.git', '.vscode', 'bootstrap', 'chartjs', 'feather.min.js']

def get_files(path, ext, files):
    for f in listdir(path):
        current_file = join(path, f)
        if isfile(current_file) and f.endswith(ext):
            files.append(current_file)
        elif isdir(current_file) and f not in blacklist:
            get_files(current_file, ext, files)

def filter_files(files, ext):
    return list(filter(lambda f: f.endswith('.' + ext), files))

def get_lines(path):
    with open(path) as f:
        i = 0
        for i, l in enumerate(f):
            pass
        return i + 1

def main():
    project_root = '/'.join(sys.path[0].split('/')[:-1])
    all_files = list()
    get_files(project_root, '', all_files)
    
    lines_count = {'py': 0, 'js': 0, 'html': 0}
    for ext in list(lines_count):
        for fname in filter_files(all_files, ext):
            lines_count[ext] += get_lines(fname)

    project_size = 0
    for fname in all_files:
        project_size = os.path.getsize(fname)

    print('Python: %d lines' % lines_count['py'])
    print('JavaScript: %d lines' % lines_count['js'])
    print('HTML: %d lines' % lines_count['html'])
    print('Size: %d KB' % (project_size / 1024))

if __name__ == '__main__':
    main()
