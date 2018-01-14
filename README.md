# NeverSpoons
/r/CasualUK Bot to comment on every Wetherspoons post or comment

# Requirements

Python 3.6

praw 5.3

A terminal, running 24/7!

Modules required in the code

Tested on Windows

# Contents

Main bot - spoons.py

Config - pint.py

Database - wetherspoons.db

# Execution

All files must be in the same folder

Add login credentials (for oAuth2) into the Config file

Use a batch file to run Main bot

# Installation Instructions

Install [Python 3.6](https://www.python.org/ftp/python/3.6.4/python-3.6.4.exe) or get it from Python.org

When installed (environment variables should auto-set), load Admin privilidges CMD (type cmd into start menu, and press CTRL+SHIFT+ENTER to load) and press Yes when prompted for elevation.

Type `pip install praw` into cmd and enter for it to download and install.

You may need to do another module the same way, but I can't remember at this point.

Then, you just need to create a batch file and drop it into the same folder.

In notepad, type this

    @echo off
    @python spoons.py
    @pause

And save it as `"Run_bot.bat"` (including quote marks in Notepad save as window) in the same direcetory.

Run the batch file to kick it off.
