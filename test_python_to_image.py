import create_source_code_image



python_code = """
for x in list(range(10)):
    if x % 2:
        print(f'{x} * 10 = {x * 10}')
"""

source = '/home/coen/demos/semaphores.py'
target = '/tmp/python_code_image.png'

create_source_code_image.create_source_code_image(source, target, highlighted=[10, 11, 12])
