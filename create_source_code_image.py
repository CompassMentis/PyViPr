import imgkit
import pygments
import pygments.lexers
import pygments.formatters

source_file_name = '/home/coen/DevRoot/Clients/APress/video_003_optimisation/fibonacci.py'
target_file_name = '/home/coen/Documents/Work/Clients/APress/Commissioned videos/003 - Benchmarking profiling and optimising/PyVipr Production Data/temp/fibonacci_code.jpg'


def python_to_html(code, highlighted, file_name):
    options = {
        'linenos': True,
        'full': True,
        'title': file_name
    }
    if highlighted:
        options['hl_lines'] = highlighted

    return pygments.highlight(code, pygments.lexers.PythonLexer(), pygments.formatters.HtmlFormatter(**options))


def create_source_code_image(source_file_name, target_file_name, highlighted=None):
    with open(source_file_name) as input_file:
        source_code = input_file.read()

    file_name = source_file_name.rsplit('/', 1)[1]
    html = python_to_html(source_code, highlighted, file_name)
    stylesheet = pygments.formatters.HtmlFormatter().get_style_defs()

    html = f"""
    <head>
        <style>
            { stylesheet }
        </style>
    </head>

    <body>
        {html}
    </body>
    """

    imgkit.from_string(html, target_file_name)


if __name__ == '__main__':
    create_source_code_image(source_file_name, target_file_name)
