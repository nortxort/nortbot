## nortbot

A bot for tinychat chat rooms.

This started out with some improvements to a few files for the bot, in the room i go to. This bassicly led to a complete rewrite of almost everything.

For windows user that want a bot without having to deal with the python aspect, i have provided compiled windows executable in the [release](https://github.com/nortxort/nortbot/releases) section.


## Setup
It is somewhat based on pinylib-rtc/tinybot-rtc so python 2.7.15+ is recommended. It has been tested on windows 7.


### Requirements

See [requirements.txt](https://github.com/nortxort/nortbot/blob/master/requirements.txt) for information.


## Usage.

Change config.ini settings to fit your needs. Then run nortbot.py. 

For a explanation of the different config settings, read through [config settings](https://github.com/nortxort/nortbot/blob/master/CONFIG.md).

Commands explanation can be found [here](https://github.com/nortxort/nortbot/blob/master/COMMANDS.md).


## Compiling.

In order to compile you will need python 2.7.15+ 32bit version, also needed is [Microsoft Visual C++ 2008 Redistributable Package](http://www.microsoft.com/downloads/en/details.aspx?FamilyID=9b2da534-3e03-4391-8a4d-074b9f2bc1bf&displaylang=en) i believe. 

**The compile info is based on my own system, and is what i was using when compiling successfully.*

### Using Pyinstaller

You will need [pyinstaller](http://www.pyinstaller.org/), it can be installed with the follwing command: `pip install pyinstaller` 

Next, change directory to the directory containg the source codes: `cd path/to/source/code/files` 

from there run: `pyinstaller --onefile nortbot.py`.

2 new directorys will be created, build and dist. The **dist** directory will contain **nortbot.exe**. Copy **cacert.pem** and **config.ini** to the **dist** directory.

You should now be able to run nortbot.exe


## Submitting an issue.

Please read through the [issues](https://github.com/nortxort/nortbot/issues) before submitting a new issue. If you want to submit a new issue, then use the [ISSUE TEMPLATE](https://github.com/nortxort/nortbot/blob/master/ISSUE_TEMPLATE.md).


## Author

* [nortxort](https://github.com/nortxort)

## License

The MIT License (MIT)

See [LICENSE](https://github.com/nortxort/nortbot/blob/master/LICENSE) for more details.

## Acknowledgments

*Thanks to the following people, who in some way or another, has contributed to this project.*


