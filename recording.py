import queue
import sys
import datetime
import os
import functools

import sounddevice as sd
import soundfile as sf
import numpy  # Make sure NumPy is loaded before it is used in the callback
assert numpy  # avoid "imported but unused" message (W0611)

from settings import Settings
import file_operations


@functools.lru_cache(maxsize=500)
def get_audio_recording_duration(full_file_name):
    data, samplerate = sf.read(full_file_name)
    seconds = int(len(data) / samplerate)
    return f'{seconds // 60}:{seconds % 60:02}'


# TODO: Put source folder somewhere central
class AudioRecorder:
    def __init__(self):
        self.source_folder = Settings.root_path
        self.channels = 2
        self.sample_rate = 44100  # Sample rate
        self.recording = False
        self.seconds = 60  # Maximum 60 second sound recording

    def target_path(self, part_name):
        result = f'{self.source_folder}{part_name}/recordings/'
        file_operations.ensure_path(result)
        return result

    def start_recording(self, part_name, vo_line_id):
        now = datetime.datetime.now()

        # voice_over_<step.line_number>_<start time, yyyy-mm-dd_hh:mm:ss>_tbd.wav
        filename = f'{self.target_path(part_name)}voice_over_{vo_line_id}_{now:%Y-%m-%d_%H:%M:%S_tbd.wav}'

        self.recording = True

        with sf.SoundFile(filename, mode='x', samplerate=self.sample_rate,
                          channels=self.channels) as file:
            with sd.InputStream(samplerate=self.sample_rate,
                                channels=self.channels, callback=callback):
                while self.recording:
                    file.write(q.get())

    def stop_recording(self):
        self.recording = False

    # @staticmethod
    def list_recordings(self, part_name, vo_line_id):
        folder = self.target_path(part_name)
        result = []
        names = sorted(
            (name for name in os.listdir(folder) if name.startswith('voice_over') and name.endswith('.wav')),
            key=lambda name: ('_yes' not in name, name)
        )

        for name in names:
            _, _, line_number, date, time, status = name.split('_')
            duration = get_audio_recording_duration(folder + name)
            status = status.split('.')[0]
            if int(line_number) == vo_line_id:
                result.append((name, date, time, status, duration))
        return result

    def start_play(self, part_name, file_name):
        print('Start playing', part_name, file_name)
        full_file_name = f'{self.target_path(part_name)}/{file_name}'
        data, fs = sf.read(full_file_name, dtype='float32')
        sd.play(data, fs)
        print('Started')

    @staticmethod
    def stop_play():
        print('Stop playing')
        sd.stop()
        print('Stopped')

    def change_status(self, part_name, file_name, new_status):
        old_status = file_name.split('_')[-1].split('.')[0]
        old_file_name = f'{self.target_path(part_name)}/{file_name}'
        new_file_name = old_file_name.replace(old_status, new_status)
        print('Changing file name')
        print('From', old_file_name)
        print('To', new_file_name)
        os.rename(old_file_name, new_file_name)


q = queue.Queue()


def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(indata.copy())
