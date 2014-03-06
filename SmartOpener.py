import sublime, sublime_plugin
import os

# Note: This plugin uses 'Verbose' plugin available in 'Package Control' to log some messages for debug purpose but it works fine without.


PluginName = 'SmartOpener'

class Prefs:
    @staticmethod
    def load():
        settings = sublime.load_settings(PluginName + '.sublime-settings')
        Prefs.env = settings.get('env', [])

    @staticmethod
    def show():
        sublime.run_command("verbose", {"plugin_name": PluginName, "log": "############################################################"})
        envs = Prefs.env
        for env in envs:
            for key, value in env.items():
                sublime.run_command("verbose", {"plugin_name": PluginName, "log": key + ": " + value})
        sublime.run_command("verbose", {"plugin_name": PluginName, "log": "############################################################"})


Prefs.load()


### OpenFileFromEnv ###

# Find root directory
# Get base directory with name
# foreach env test if file exit
class OpenFileFromEnvCommand(sublime_plugin.TextCommand):

    # Set by is_enabled()
    m_srcEnv = ""

    # List of existing files in other environments
    m_envFiles = []

    def run(self, edit):
        sublime.run_command("verbose", {"plugin_name": PluginName, "log": "run()"})

        # Find baseName by removing the source environment
        baseName = self.view.file_name().lower().replace(self.m_srcEnv.lower(), "")

        sublime.run_command("verbose", {"plugin_name": PluginName, "log": "m_srcEnv: " + self.m_srcEnv})
        sublime.run_command("verbose", {"plugin_name": PluginName, "log": "baseName: " + baseName})

        if len(baseName) > 0:

            # Remove first slash or backslash from baseName
            if baseName[0] == os.sep:
                baseName = baseName.replace(os.sep, "", 1)

            # Create a list of file which exist in other environment
            self.m_envFiles = []
            envs = Prefs.env
            for env in envs:
                for key, value in env.items():

                    # Bypass source environment
                    if self.m_srcEnv == value:
                        continue

                    # Check if the file exists in an another environment
                    envFileName = os.path.join(value, baseName)
                    if os.path.exists(envFileName):
                        sublime.run_command("verbose", {"plugin_name": PluginName, "log": "[X] envFileName " + envFileName})
                        self.m_envFiles.append([key, envFileName])
                    else:
                        sublime.run_command("verbose", {"plugin_name": PluginName, "log": "[ ] envFileName " + envFileName})

            if len(self.m_envFiles) > 0:
                self.view.window().show_quick_panel(self.m_envFiles, self.quick_panel_done)
            else:
                sublime.status_message("No file found in other environments")


    def quick_panel_done(self, index):
        if index == -1:
            return
        # Open selected file in an another environment
        self.view.window().open_file(self.m_envFiles[index][1])


    # Return True if the file is part of an environment
    def is_enabled(self):
        Prefs.show()
        sublime.run_command("verbose", {"plugin_name": PluginName, "log": "is_enabled()"})

        fileName = self.view.file_name()
        self.m_srcEnv = None
        if fileName and len(fileName) > 0:
            fileName = fileName.lower()
            sublime.run_command("verbose", {"plugin_name": PluginName, "log": "fileName: " + fileName})
            # Loop into registered environment
            envs = Prefs.env
            for env in envs:
                for key, value in env.items():
                    # Test if fileName is part of an environment
                    if fileName.startswith(os.path.normpath(value).lower()):
                        # Keep the environments with the longest size as origin
                        if self.m_srcEnv and len(value) <= len(self.m_srcEnv):
                            continue
                        self.m_srcEnv = value

        if self.m_srcEnv:
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
