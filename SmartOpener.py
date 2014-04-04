import sublime, sublime_plugin
import os

# Note: This plugin uses 'Verbose' plugin available in 'Package Control' to log some messages for debug purpose but it works fine without.


PluginName = 'SmartOpener'


def verbose(**kwargs):
    kwargs.update({'plugin_name': PluginName})
    sublime.run_command("verbose", kwargs)


class Prefs:
    @staticmethod
    def load():
        settings = sublime.load_settings(PluginName + '.sublime-settings')
        Prefs.environment = settings.get('environment', [])
        Prefs.expand_alias = settings.get('expand_alias', True)

    @staticmethod
    def show():
        verbose(log="############################################################")
        for env in Prefs.environment:
            for key, values in env.items():
                verbose(log=key + ": " + ';'.join(values))
        verbose(log="############################################################")


if int(sublime.version()) < 3000:
    Prefs.load()


### OpenFileFromEnv ###

# Find root directory
# Get base directory with name
# foreach env test if file exit
class OpenFileFromEnvCommand(sublime_plugin.TextCommand):

    # Set by is_enabled()
    initial_env_name = ''
    base_name = ''

    # List of existing files in other environments
    env_files = []

    def run(self, edit):
        verbose(log="run()")

        verbose(log="initial_env_name: " + self.initial_env_name)
        verbose(log="base_name: " + self.base_name)

        if len(self.base_name) > 0:
            # Create a list of files which exist in other environment
            self.env_files = []
            for env in Prefs.environment:
                for env_name, root_alias in env.items():

                    # Bypass initial environment
                    if env_name == self.initial_env_name:
                        continue

                    # Loop in path alias of the current environment
                    available_file_names = []
                    for root in root_alias:
                        env_file_name = os.path.join(root, self.base_name)
                        state = ' '
                        if os.path.exists(env_file_name):
                            state = 'X'
                            if Prefs.expand_alias:
                                self.env_files.append([env_name, env_file_name])
                            else:
                                available_file_names.append(env_file_name)
                        verbose(log='[%s] %15s %s' % (state, env_name, env_file_name))

                    if len(available_file_names) > 0:
                        # available_file_names used only with expand_alias = False
                        current_id = self.view.id()
                        is_file_opened = False
                        # Find the first file of the environment which is already opened in st
                        for v in self.view.window().views():
                            if v.id() == current_id:
                                continue
                            for file_name in available_file_names:
                                if file_name.lower() == v.file_name().lower():
                                    self.env_files.append([env_name, file_name])
                                    is_file_opened = True
                                    break
                            if is_file_opened:
                                break
                        # Or choose the file of the environment of the main path
                        if not is_file_opened:
                            self.env_files.append([env_name, available_file_names[0]])

            if len(self.env_files) > 0:
                self.view.window().show_quick_panel(self.env_files, self.quick_panel_done)
            else:
                sublime.status_message("No file found in other environments")


    def quick_panel_done(self, index):
        if index > -1:
            # Open selected file in an another environment
            self.view.window().open_file(self.env_files[index][1])


    def is_filename_part_of_env(self, file_name, root_alias):
        for root in root_alias:
            # Remove trailing os.sep
            root = os.path.normpath(root).lower()
            if file_name.startswith(root):
                base_name = file_name.replace(root.lower(), "")
                if base_name[0] == os.sep:
                    # Get back the original case
                    file_name = self.view.file_name()
                    # Remove first os.sep character and get base name
                    self.base_name = file_name[len(file_name)-len(base_name)+1:]
                    return True
        return False

    # Return True if the file is part of an environment
    def is_enabled(self):
        Prefs.show()
        verbose(log="is_enabled()")

        file_name = self.view.file_name()
        self.initial_env_name = ''
        base_name = ''
        if file_name is not None and len(file_name) > 0:
            file_name = file_name.lower()
            verbose(log="file_name: " + file_name)

            # Loop into registered environment
            for env in Prefs.environment:
                for env_name, root_alias in env.items():
                    # Test if file_name is part of an environment
                    if self.is_filename_part_of_env(file_name, root_alias):
                        self.initial_env_name = env_name
                        return True

        sublime.status_message("The current file is not part of an environment")
        return False


### OpenUnderSelection ###

def is_legal_path_char(c):
    # XXX make this platform-specific?
    return c not in " \n\"|*<>{}[]()"

def move_while_path_character(view, start, is_at_boundary, increment=1):
    while True:
        if not is_legal_path_char(view.substr(start)):
            break
        start = start + increment
        if is_at_boundary(start):
            break
    return start

class OpenUnderSelectionCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        sel = self.view.sel()[0]
        if not sel.empty():
            file_name = self.view.substr(sel)
        else:
            caret_pos = self.view.sel()[0].begin()
            current_line = self.view.line(caret_pos)

            left = move_while_path_character(
                                            self.view,
                                            caret_pos,
                                            lambda x: x < current_line.begin(),
                                            increment=-1)
            right = move_while_path_character(
                                            self.view,
                                            caret_pos,
                                            lambda x: x > current_line.end(),
                                            increment=1)
            file_name = self.view.substr(sublime.Region(left + 1, right))

        # Add current path if relative file
        if self.view.file_name():
            file_name = os.path.join(os.path.dirname(self.view.file_name()), file_name)

        if os.path.exists(file_name):
            if os.path.isdir(file_name):
                # Walaround for UNC path
                if file_name[0] == '\\':
                    file_name = '\\' + file_name
                # Open a directory
                self.view.window().run_command("open_dir", {"dir": file_name})
            else:
                # Open a file
                self.view.window().open_file(file_name)
