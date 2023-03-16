import file_operations

with open('projects/live_project.txt') as input_file:
    lines = input_file.readlines()

lines = [line.strip() for line in lines if line.strip()]
*parts, prefix, root_folder = lines
assert ':' in prefix

for part in parts:
    part = part.replace('*', '')
    full_path = root_folder + part
    file_operations.ensure_path(full_path)
