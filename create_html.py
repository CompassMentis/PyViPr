# TODO: Can I use Markdown instead of own codes?

def convert_one_line_to_html(line):
    try:
        code, text = line.split(' ', 1)
    except ValueError:
        code, text = line, ''

    try:
        return {
            't_ol': '<ol>',
            't_ul': '<ul>',
            't_end_ol': '</ol>',
            't_end_ul': '</ul>'
        }[code]
    except KeyError:
        pass

    html_tag = {
        't': 'p',
        't_li': 'li',
        't_h1': 'h1',
        't_h2': 'h2'
    }[code]

    return f'<{html_tag}>{text}</{html_tag}>'


def slide_lines_to_html(lines):
    """
    Special characters

    t_ol, t_ul: <ol>, <ul>
    t_end_ol, t_end_ul: </ol>, </ul>
    t_li: <li>
    t_h1, t_h2: <h1>, <h2>
    t: <p>
    """

    html = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        html.append(
            convert_one_line_to_html(line)
        )

    return '\n'.join(html)
