import parse

from recording import AudioRecorder


class VOLine:
    def __init__(self, step, text, id):
        self.step = step
        self.text = text
        self.id = id
        self._recordings = None
        self._final_audio_recording_name = None

    @staticmethod
    def from_text(step, text):
        search_result = parse.search('({:d}) {}', text)
        if search_result:
            return VOLine(step, text=text.split(' ', 1)[1], id=search_result[0])

        return VOLine(step, text=text, id=None)

    def __str__(self):
        return f'({self.id}) {self.text}'

    def to_text(self):
        return f'vo ({self.id}) {self.text}'

    @property
    def recordings(self):
        if self._recordings is None:
            audio_recorder = AudioRecorder()
            self._recordings = audio_recorder.list_recordings(self.step.slide.part.name, self.id)
        return self._recordings

    @property
    def confirmed_recording(self):
        for name, date, time, status, duration in self.recordings:
            # TODO: Tidy this up, e.g. make a Recording class
            if status == 'yes':
                return name

    def create_final_audio_recording(self):
        print('Step, create_final_audio_recording')

        names = []
        s = self
        while s is not None:
            names.append(self.path + 'recordings/' + s.confirmed_recording)
            s = s.next_sub_step
        target_name = names[0].replace('voice_over', 'combined_voice_over')
        utils.combine_audio_sequentially(names, target_name)
        return target_name.split('/')[-1]

    @property
    def final_audio_recording_name(self):
        if self._final_audio_recording_name is None:
            self._final_audio_recording_name = self.confirmed_recording

        return self._final_audio_recording_name

    @property
    def confirmed_recording_duration(self):
        for name, date, time, status, duration in self.recordings:
            # TODO: Tidy this up, e.g. make a Recording class
            # TODO: Remove duplication with confirmed_recordings()
            if status == 'yes':
                return duration
