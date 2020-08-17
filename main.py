import os
import collections

from flask import Flask, render_template, request

from recording import AudioRecorder
from settings import Settings
from part import Part

app = Flask(
    __name__,
    static_folder=Settings.static_path
)

audio_recorder = AudioRecorder()


def part_list():
    result = []
    for name in sorted(os.listdir(Settings.root_path)):
        if not os.path.isdir(Settings.root_path + name):
            continue
        if not os.path.isfile(Settings.root_path + name + '/contents.txt'):
            continue
        result.append(name)
    return result


@app.route('/')
def section_list():
    Section = collections.namedtuple('Section', 'name, has_contents')
    sections = []
    for name in sorted(os.listdir(Settings.root_path)):
        if not os.path.isdir(Settings.root_path + name):
            continue

        has_contents = os.path.isfile(Settings.root_path + name + '/contents.txt')

        sections.append(Section(name=name, has_contents=has_contents))

    return render_template(
        'section_list.html',
        sections=sections
    )


@app.route('/<string:part_name>/<int:slide_id>/<int:step_id>/<int:vo_line_id>')
def parts_list(part_name, slide_id, step_id, vo_line_id):
    parts = sorted(part_list())

    if not part_name in parts:
        part_name = parts[0]

    part = Part.from_file(part_name)

    try:
        slide = next(slide for slide in part.slides if slide.id == slide_id)
    except StopIteration:
        slide = part.slides[0]
        print('Slide not found:', slide_id)

    try:
        step = next(step for step in slide.steps if step.id == step_id)
    except StopIteration:
        step = slide.steps[0]
        print('Step not found:', step_id)

    try:
        vo_line = next(vo_line for vo_line in step.vo_lines if vo_line.id == vo_line_id)
    except StopIteration:
        vo_line = slide.first_vo_line
        print('vo line not found:', vo_line_id)

    return render_template(
        'main.html',
        parts=parts,
        part=part,
        slide=slide,
        step=step,
        vo_line=vo_line,
    )


@app.route('/api/audio/start_recording', methods=['POST'])
def start_recording():
    data = request.form
    audio_recorder.start_recording(data['part_name'], data['vo_line_id'])
    return ''


@app.route('/api/audio/stop_recording')
def stop_recording():
    audio_recorder.stop_recording()
    return ''


@app.route('/api/audio/start_play', methods=['POST'])
def start_audio_play():
    audio_recorder.start_play(request.form['part_name'], request.form['file_name'])
    return ''


@app.route('/api/audio/stop_play')
def stop_audio_play():
    audio_recorder.stop_play()
    return ''


@app.route('/api/audio/change_status', methods=['POST'])
def change_audio_recording_status():
    audio_recorder.change_status(request.form['part_name'], request.form['file_name'], request.form['new_status'])
    return ''


# TODO: Switch go GET request?
@app.route('/api/audio/list_recordings/', methods=['POST'])
def get_audio_recordings_list():
    audio_recordings = audio_recorder.list_recordings(request.form['part_name'], int(request.form['vo_line_id']))
    return render_template(
        'audio_recordings_list.html',
        audio_recordings=audio_recordings
    )
