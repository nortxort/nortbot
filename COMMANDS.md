## Commands (76)

This document describes the different commands.
Commands have been grouped together depending on the user level required to use them.

The default prefix `!` for commands can be changed within the config.ini file. The prefix will be refereed to as `[p]` in this document.

Commands will only be enabled, if the bot is using a moderator account. Also, commands work both by private and public chat message, unless otherwise stated.

*Commands marked with  * are private message commands only.*

## User Level System

The user level system is as such:

**Level 0 CLIENT** - This is reserved for the bot.

**Level 1 OWNER** -  This is assigned to the room owner. Or it can be assigned to a user who has the correct super key, but **ONLY** if the bot is using the room owner account.

**Level 2 SUPER** - This user level is assigned to a user that has the correct key.

**Level 3 MODERATOR** - This user level is assigned room moderators.

**Level 4 BOT_OP** This user level is assigned a user who has been made a bot controller by one of the following user levels: 1,2,3. It is also used for approved accounts.

**Level 5 DEFAULT** - This user level is assigned a normal user.

### Some user level examples.

When a user attempts to use a command, the bot will check if the user has the correct user level.

This means, that a user with **Level 4 BOT_OP** can use **Level 4 BOT_OP** and **Level 5 DEFAULT** commands. A user with **Level 2 SUPER** can use **Level 2 SUPER**, **Level 3 MODERATOR**, **Level 4 BOT_OP** and **Level 5 DEFAULT** commands.

The same applies to banning. **A user can not ban a user with a lower user level!**


## Level 1 OWNER Commands.

`[p]key (new key)` - Sets a new secret key or shows the current key. If no new key is provided, the current key is shown. *


`[p]clrbn` - Clear the nick bans file and memory.

`[p]clrbs` - Clear the string bans file and memory.

`[p]clrba` - Clear the account bans file and memory.

`[p]clrap` - Clear the approved users file and memory.

`[p]kill` - Kills the bot. Complete disconnect.

`[p]reboot` - Reboots the bot.

*These commands are **ONLY** available if the bot is using the room owner account.*

`[p]mod (account)` - Make a user a room moderator.

`[p]rmod (account)` - Remove a room moderator.

`[p]dir` - Toggle if the room should be shown on the directory.

`[p]p2p` - Toggle if the room should be in push to talk mode.


## Level 2 SUPER Commands.

`[p]mi` - Show media information.

`[p]dev` - Not implemented.


## Level 3 MODERATOR Commands.

`[p]op (username)` - Make a user a temporary bot controller. User will only be a bot operator for as long as the user or bot stays in the room.

`[p]deop (username)` - Remove a temporary bot controller .

`[p]apr (username)` - Make a user a permanent bot controller. This is only possible if the user is signed.

`[p]dapr (account)` - Remove a account from the permanent bot controller file.

`[p]bb (mod account)` - Count user banned by a specific moderator.

`[p]noguest` - Toggle if guests should be allowed to join the room.

`[p]lurkers` - Toggle if lurkers should be allowed to join the room.

`[p]guestnick` - Toggle if usernames containing guest, should be allowed to join the room.

`[p]greet` - Toggle greet message.

`[p]pub` - Toggle if public commands should be enabled. This means if the **Level 5 DEFAULT** commands should be enabled for any user.

`[p]kab` - Toggle kick as ban option.

`[p]rs` - Show room settings.

`[p]top (number)` - Creates a playlist from the most played tunes on last.fm. The number option determines the max number of tunes to get.

 `[p]ran (number)` - Creates a playlist from tunes other people are listening to on last.fm. The number option determines the max number of tunes to get.

`[p]tag (search term)` - Searches last.fm for tunes matching the search term(tag).

`[p]pls (search term)` - Search youtube for a playlist matching the search term.

`[p]plp (playlist index)` - Add playlist from playlist search.

`[p]ssl` - Show the contents of the search list.


## Level 4 BOT_OP Commands.

`[p]skip` - Skip to the next track in the playlist.

`[p]del (indexes)` - Delete tracks by index from the playlist.

`[p]mbpl` - Play a track that is in pause state.

`[p]mbpa` - Pause a media playing.

`[p]seek (time)` - Time seek a track.

`[p]cm` - Close a media playing.

`[p]cpl` - Clear the playlist.

`[p]spl` - Show playlist information.

`[p]yts (search term)` - Search youtube. This returns a list of items.

`[p]pyts (search index)` - Play a previous search by index.

`[p]clr` - Clear the chat box.

`[p]nick (new bot nick)` - Set a new nick for the bot.

`[p]ban (username)` - Ban a user.

`[p]bn (ban nick)` - Add a ban nick to the ban nicks file.

`[p]rmbn (ban nick)` - Remove a ban nick from the ban nicks file.

`[p]bs (ban string)` - Add a ban string to the ban string file.

`[p]rmbs (ban string)` - Remove a ban string from file.

`[p]ba (ban account)` - Add a ban account to the ban account file.

`[p]rmba (ban account)` - Remove a ban account from the ban account file.

`[p]list (list type)` - Show list information based on list type. Supported list types is `ap, bn, bs, ba, bl and mods`.

`[p]uinfo (username)` - Shows information about a user.

`[p]cam (username)` - Allow a user to cam in green room enabled room.

`[p]cbc (username)` - Toggle if a user is allowed to broadcast.

`[p]is (instagram user)` - Search instagram.

`[p]close (username)` - Close a users broadcast.

`[p]sbl (username)` - Search the banlist.

`[p]fg (usernane)` - Firgive a banned user.

`[p]unb (username)` - Unban a banned user.


## Level 5 DEFAULT Commands.

`[p]pmme` - Open a private session with the bot.

`[p]opme (key)` - Change user level based on provided key. *

`[p]v` - Shows bot version.

`[p]help` - Shows a help link.

`[p]t` - Shows the bots uptime.

`[p]yt (search term)` - Search youtube.

`[p]q` - Show the playlist queue count.

`[p]n` - Show the next track in the playlist.

`[p]np` - Show information about the currently playing track.

`[p]wp` - Show who played the current track.

`[p]acspy (account)` - Shows information about a tinychat account.

`[p]urb (search term)` - Search urbandictionary for definitions.

`[p]wea (city)` - Shows weather data for a given city.

`[p]ip (IP or domain)` - Shows whois information for a given IP/domain.

`[p]cn` - Random Chuck Norris quote/joke.

`[p]8ball (question)` - Magic 8ball.

`[p]roll` - Roll a dice.

`[p]flip` - Flip a coin.

