import os


def ensure_path(path):
    parts_sofar = []
    for part in path.split('/'):
        if not part:
            continue
        parts_sofar.append(part)
        path_sofar = '/' + '/'.join(parts_sofar)
        if not os.path.isdir(path_sofar):
            os.mkdir(path_sofar)


def backup_file(file_path):
    folder, file_name = file_path.rsplit('/', 1)
    backup_folder = folder + '/backup/'
    ensure_path(backup_folder)

    backup_file_path = backup_folder + file_name
    n = 1
    while os.path.isfile(f'{backup_file_path}.{n:04}'):
        n += 1

    if n > 1:
        # At least one backup file found - is it the same as the current one?
        last_backup = f'{backup_file_path}.{(n - 1):04}'
        if os.path.getmtime(file_path) <= os.path.getmtime(last_backup):
            # Backup up to date - done
            return

    os.system(f'cp "{file_path}" "{backup_file_path}.{n:04}"')


def already_up_to_date(source, target_file):
    """
    source is either single string (file path + name) or an iterable of strings

    <target_file> is derived from <source_file(s)>

    We need to (re-)create target file only if
        Either target file doesn't exist, or
        Target file older than source file
    """
    if not os.path.isfile(target_file):
        return False

    if isinstance(source, str):
        source_files = [source]
    else:
        source_files = source

    for source_file in source_files:
        if os.path.getmtime(source_file) > os.path.getmtime(target_file):
            return False

    return True
