from step import Step
import terminal
from settings import Settings


def break_lines_into_steps(lines):
    """
    Steps are separate by blank lines

    returns a list of list of lines, where each list of lines defines one step
    """
    result = []
    step_lines = []
    for line in lines:
        if not line:
            if step_lines:
                result.append(step_lines)
            step_lines = []
        elif line.startswith('[step'):
            if step_lines:
                result.append(step_lines)
            step_lines = [line]
        else:
            step_lines.append(line)

    if step_lines and any(line for line in step_lines):
        result.append(step_lines)

    return result


class Slide:
    def __init__(self, part, lines):
        self.part = part
        self.raw_lines = lines
        self.type = None
        self.steps = []
        self.text_so_far = []

    @property
    def id(self):
        return self.steps[0].id

    @property
    def name(self):
        for step in self.steps:
            for line in step.text_lines:
                if line.startswith('t_h1'):
                    return line.split(' ', 1)[1]
        return '(no name)'

    @staticmethod
    def from_text(parent, lines):
        result = Slide(parent, lines)
        result.type = lines[0].split(':')[1].replace(']', '')

        result.steps = []
        for step_lines in break_lines_into_steps(lines[1:]):
            result.steps.append(Step.from_lines(result, step_lines))

        return result

    def to_save(self):
        result = f'[slide:{self.type}]\n\n'
        for step in self.steps:
            result += step.to_save()
        return result

    def build_slides(self):
        self.text_so_far = []
        needs_building = False
        for step in self.steps:
            self.text_so_far += step.text_lines

            # Once a step is changed, build this step plus all subsequent ones
            if needs_building or step.build_slide_needed():
                needs_building = True
                step.build_slide()

    def build_demos_needed(self):
        for step in self.steps:
            if step.build_demo_needed():
                return True

        return False

    @property
    def slide_columns(self):
        """
        if no demo: always 1 column

        If any of this slide's steps either contains text (other than the page header) or shows python source code,
        demo needs to fit in two column layout
        Otherwise, use full width
        """
        if not any(step.demo_lines for step in self.steps):
            return 1

        for step in self.steps:
            if any(line for line in step.text_lines if not line.startswith('t_h1')) or \
                    any(command.startswith('c_show_code') for command in step.command_lines):
                return 2
        return 1

    def set_terminal_size(self):
        """
        Called before any demo starts, i.e. in terminal mode
        """
        if self.slide_columns == 2:
            width, height = Settings.TwoColumnSlide.terminal_window
        else:
            width, height = Settings.OneColumnSlide.terminal_window

        terminal.set_size(width=width, height=height)

    def start_python(self):
        terminal.execute_line('python')

    def exit_python(self):
        terminal.execute_line('exit()')

    def clear_python_demo(self):
        terminal.execute_line(r'print("\033[2J\033[H")')

    def clear_terminal_demo(self):
        terminal.execute_line('clear')

    def build_demos(self):
        """
        Code from one step needed on subsequent steps.
        So if any step has changed, all demos need to be created

        Keep track of demo state, and check special commands

        If include_derived_artifacts, also create
            cropped demo
            last frame image
        """

        # No missing or out of date demos for any of the steps - done
        if not self.build_demos_needed():
            return

        demo_mode = None
        needs_clearing = False
        for step in self.steps:
            if step.contains_clear_demo_command():
                needs_clearing = True

            # No demo lines for this step - ignore
            if not step.demo_lines:
                continue

            # First demo for this slide - set the window to the correct size
            if demo_mode is None:
                self.set_terminal_size()

            if step.python_lines:
                if demo_mode in [None, 'terminal']:
                    # Going from none or terminal to Python - start python, clear
                    self.start_python()
                    needs_clearing = True
                else:
                    # Continuing demo - do nothing
                    pass

            elif step.terminal_lines:
                if demo_mode == 'python':
                    # Going from Python to terminal - close Python, clear
                    self.exit_python()
                    needs_clearing = True
                elif demo_mode is None:
                    # First demo - clear terminal
                    needs_clearing = True
                else:
                    # Continuing demo - do nothing
                    pass

            if needs_clearing:
                # If clean requested but not done yet
                if step.python_lines:
                    self.clear_python_demo()
                else:
                    self.clear_terminal_demo()

                # Clean done (for now)
                needs_clearing = False

            # Terminal in correct mode and clean (if necessary)
            step.build_demo()

            if step.python_lines:
                demo_mode = 'python'
            else:
                demo_mode = 'terminal'

        # If necessary, close down Python ready for the next slide
        if demo_mode == 'python':
            self.exit_python()

    @property
    def first_vo_line(self):
        for step in self.steps:
            if step.vo_lines:
                return step.vo_lines[0]
        return None

    @property
    def all_recordings_done(self):
        for step in self.steps:
            for vo_line in step.vo_lines:
                if vo_line.confirmed_recording is None:
                    return False
        return True

    def build_code_images(self):
        for step in self.steps:
            step.build_code_image()

    def build_step_videos(self):
        """
        For all the steps, create the separate components
            (slides, python code)

        then merge the different parts into one video per step
        """
        self.build_slides()
        self.build_demos()
        self.build_code_images()
        for step in self.steps:
            step.build_step_video()

