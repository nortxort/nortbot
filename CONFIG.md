## Config.

This document describes the different config settings in config.ini. The different settings are grouped together, based on what type of value they return.

## Settings.

`[strings]`

**Room** - The room the bot should enter.

**Nick** - The nick name of the bot.

**Account** - The account the bot should use.

**Password** - The password for the account.

**AntiCaptchaKey** - An [anti-captcha](https://anti-captcha.com/) API key.

**WeatherApiKey** - A valid API key for [apixu](https://www.apixu.com/)

**FallbackRtcVersion** - Fall back RTC version, in case parsing fails.

**DebugFileName** - The name of the debug file.

**ConfigPath** - Configuration path for rooms.

**Prefix** - The command prefix.

**Key** - Bot operator key. **Change this!**

**SuperKey** - Super bot operator key. **Change this!**

**ApprovedFileName** - File name for approved accounts.

**NickBansFileName** - File name for nick bans.

**AccountBansFileName** - File name for account bans.

**StringBansFileName** - File name for string bans.


`[booleans]`

**AutoLogin** - Attempt to login with te credentials given in config.ini.

**ChatLoggin**g - Enable chat event logging. Saved in the rooms config directory.

**DebugMode** - Show some limited debug information in console.

**DebugToFile** - Create a debug log.

**ConsoleColors** - Use console colors.

**Use24Hour** - Use 24 hour time stamp in console.

**PublicCmd** - Enable public commands. See [commands](https://github.com/nortxort/nortbot/blob/master/COMMANDS.md) for more info.

**Greet** - Greet users when they enter the room.

**AllowGuests** - Allow guests to enter the room.

**AllowLurkers** - Allow lurkers to enter the room.

**AllowGuestsNicks** - Allow guest nicks to enter the room. (still relevant?)

**KickAsAutoban** - Use kick instead of ban for auto ban.

**NotifyOnBan** - Send a room message when a user gets banned/kicked.

**TryTimeBasedCheck** - Try time based checks to prevent spam.

**VipMode** - In vip mode, only moderators and accounts in the approved file will be allowed to join the room.  The action for unapproved users depends on **KickAsAutoban**.

**EnableVoting** - If enabled, users will be able to vote to ban/kick/close other users.


`[integers]`

**DebugLevel** - Debug level for the python logging module. For more information about debug levels, see [this](https://docs.python.org/2/library/logging.html#logging-levels)

**MaxMatchBans** - Maximum match ban.

**ThreadPool** - The number of threads in the pool.