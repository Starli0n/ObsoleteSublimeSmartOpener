SmartOpener
===========

Sublime Text plugin which allows to open file smartly


Description
===========

**SmartOpener** offers several ways to open files.

#### `Open File From Env`

This command tries to open the current file in an other environnement defined in the settings.

While developing a project, we often need to open the same file as it is in a production environnement or an another one.

The plugin will find the root environnement of the current file and then will offer the list of files available in other environnements.


#### `Open Under Selection`

This command tries to open the file or directory under the selection or the cursor from the current file.

If the file is a directory, it opens the folder.

If the file is a relative path, it try to open it relatively to the current file.


Package Installation
====================

Bring up a command line in the Packages/ folder of your Sublime user folder, and execute the following:
> git clone https://github.com/Starli0n/SmartOpener.git SmartOpener


Settings
========

env: Array of environnements
> key: Name of the environnements

> value: Path of the environnements


Key Bindings
============

`Open File From Env`

* Mac OS X: `CTRL+CMD+O`
* Windows:  `CTRL+ALT+O`
* Linux:    `CTRL+ALT+O`

`Open Under Selection`

* Mac OS X: `F2`
* Windows:  `F2`
* Linux:    `F2`


Usage
=====

* Copy/Paste the **SmartOpener.sublime-settings** into your **User** folder
* Replace by your own environnement variables

example:

* Open the file `path/to/Dev/common/file/path`
* `Open File From Env`
* If the files exist, the plugin will offer to open the files:
  `path/to/Prod/common/file/path`
  `path/to/UAT/common/file/path`


Version
=======

- **v1.0.0**

First Release
