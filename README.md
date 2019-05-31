## Nortbot

A bot for Tinychat chat rooms.

This started out with some improvements to a few files for the bot in the room I go to. This basically led to a complete rewrite of almost everything.
Join the discord for help https://discord.gg/zhAsp9


## Setup
For a Windows user that wants a bot without having to deal with the Python aspect, I have provided a compiled Windows executable in the [Releases](https://github.com/nortxort/nortbot/releases) section.

It is somewhat based on pinylib-rtc/tinybot-rtc so Python 2.7.16+ is recommended. It has been tested on Windows 7, Windows 10, Debian 8/9, and Ubuntu 16/18.


### Requirements

See [requirements.txt](https://github.com/nortxort/nortbot/blob/master/requirements.txt) for information.


## Usage

Change config.ini settings to fit your needs. ***Don’t forget to change the default key!*** Then run nortbot.py. 
For an explanation of the different config settings, read through [config settings](https://github.com/nortxort/nortbot/blob/master/CONFIG.md).
Command explanations can be found [here](https://github.com/nortxort/nortbot/blob/master/COMMANDS.md).


## Compiling

In order to compile simply run `compile.bat`, located in the `compile` folder. You will need the following:
* Python 2.7.16+ in your path.
* Possibly [Microsoft Visual C++ 2008 Redistributable Package](http://www.microsoft.com/downloads/en/details.aspx?FamilyID=9b2da534-3e03-4391-8a4d-074b9f2bc1bf&displaylang=en)

*More details about pyinstaller's requirements can be found [HERE](https://pyinstaller.readthedocs.io/en/v3.3.1/usage.html#windows)*


### Using Pyinstaller

You will need [pyinstaller](http://www.pyinstaller.org/), it can be installed with the following command: `pip install pyinstaller` 

Next, change directory to the directory containing the source code: `cd path/to/source/code/files` 

from there run: `pyinstaller --onefile nortbot.py`.

2 new directories will be created, build and dist. The **dist** directory will contain **nortbot.exe**. Copy **cacert.pem** and **config.ini** to the **dist** directory.

You should now be able to run **nortbot.exe**


## Submitting an issue

Please read through the [ISSUES](https://github.com/nortxort/nortbot/issues) before submitting a new one. If you want to submit a new issue, then use an [ISSUE TEMPLATE](https://github.com/nortxort/nortbot/issues/new/choose). **_Please_ use an issue template**, they're there for a reason!


## Author

* [nortxort](https://github.com/nortxort)


## License

The MIT License (MIT)
See [LICENSE](https://github.com/nortxort/nortbot/blob/master/LICENSE) for more details.


## Acknowledgments

*Thanks to the following people, who in some way or another, have contributed to this project:*

[Technetium1](https://github.com/Technetium1)

[Aida](https://github.com/Autotonic)
