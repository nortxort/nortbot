
## Commands

This document describes the different commands.
Commands have been grouped together depending on the user level required to use them.

The default prefix for commands is `!`. It can be changed within the config.ini file. The prefix will be referred to as `[p]` in this document.

Commands will only be enabled if the bot is using a moderator account. Commands work by both private and public messages.

*Commands marked with  * are private message commands only.*

## User Level System

The user level system is as follows:

**Level 0 CLIENT** - This is reserved for the bot.

**Level 1 OWNER** -  This is assigned to the room owner. Or it can be assigned to a user who has the correct super key, but **ONLY** if the bot is using the room owner account.

**Level 2 SUPER** - This user level is assigned to a user that has the correct key.

**Level 3 MODERATOR** - This user level is assigned room moderators.

**Level 4 APPROVED** - This level is for approved accounts.

**Level 5 BOT_OP** - Users can be assigned this level, by user level 1,2 and 3.

**Level 6 DEFAULT** - This user level is assigned a normal user.

### Some user level examples.

When a user attempts to use a command, the bot will check if the user has the correct user level.

This means, that a user with **BOT\_OP** can use **BOT_OP** and **DEFAULT** commands. A user with **SUPER** can use **SUPER**, **MODERATOR**, **APPROVED**, **BOT\_OP** and **DEFAULT** commands.

The same applies to banning. **A user can not ban a more privileged user!**


## OWNER(1) Commands.

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


## SUPER(2) Commands.

`[p]mi` - Show media information.


## MODERATOR(3) Commands.

`[p]op (username)` - Make a user a temporary bot controller. User will only be a bot operator for as long as the user or bot stays in the room.

`[p]deop (username)` - Remove a temporary bot controller.

`[p]apr (username)` - Make a user a permanent bot controller. This is only possible if the user is signed in.

`[p]dapr (account)` - Remove an account from the permanent bot controller file.

`[p]bb (mod account)` - Count users banned by a specific moderator. If no moderator account is provided, then the bot's account will be used.

`[p]noguest` - Toggle if guests should be allowed to join the room.

`[p]lurkers` - Toggle if lurkers should be allowed to join the room.

`[p]guestnick` - Toggle if usernames containing guest, should be allowed to join the room.

`[p]greet` - Toggle greet message.

`[p]pub` - Toggle if public commands should be enabled. This means if the **DEFAULT** commands should be enabled for any user.

`[p]kab` - Toggle kick as ban option.

`[p]nob` - Toggle notify on ban/kick.

`[p]vip` - Toggle vip mode.

`[p]vo` - Toggle voting.

`[p]rs` - Show room settings.

`[p]top (number)` - Create a playlist from the most played tunes on last.fm. The number option determines the max number of tunes to get.

`[p]ran (number)` - Create a playlist from tunes other people are listening to on last.fm. The number option determines the max number of tunes to get.

`[p]tag (search term)` - Search last.fm for tunes matching the search term(tag).

`[p]pls (search term)` - Search youtube for a playlist matching the search term.

`[p]plp (playlist index)` - Add playlist from playlist search.

`[p]ssl` - Show the contents of the search list.

`[p]lc (room name)` - Start the live count. Room name is optional, if not provided, the live count will still be active.

`[p]lcw (room name)` - Set or change the live count watch room.

`[p]lcr (room name)` - Remove a room name from the live count.

`[p]lci (interval)` - Set the live count interval. the interval is in seconds.

`[p]lcm` - Show the most active room on the live count.

`[p]lcs` - Show live count status.

`[p]lcc` - Close the live count.

`[p]cv` - Cancel a vote session.

## APPROVED(4) Commands.

`[p]skip` - Skip to the next track in the playlist.

`[p]del (indexes)` - Delete tracks by index from the playlist.

`[p]mbpl` - Play a track that is in pause state.

`[p]mbpa` - Pause a media playing.

`[p]seek (time)` - Time seek a track.

`[p]cm` - Close a media playing.

`[p]cpl` - Clear the playlist.

`[p]spl (ammount of tracks)` - Show playlist information. If amount of tracks is not set, then default of 3 will be used.

`[p]yts (search term)` - Search youtube. This returns a list of items.

`[p]pyts (search index)` - Play a previous search by index.


## BOT_OP(5) Commands.

`[p]clr` - Clear the chat box.

`[p]nick (new bot nick)` - Set a new nick for the bot.

`[p]ban (username)` - Ban a user.

`[p]bn (ban nick)` - Add a ban nick to the ban nicks file.*

`[p]rmbn (ban nick)` - Remove a ban nick from the ban nicks file.

`[p]bs (ban string)` - Add a ban string to the ban string file.**

`[p]rmbs (ban string)` - Remove a ban string from file.

`[p]ba (ban account)` - Add a ban account to the ban account file.

`[p]rmba (ban account)` - Remove a ban account from the ban account file.

`[p]list (list type)` - Count list items based on list type. Supported list types is `ap, bn, bs, ba, bl and mods`.

`[p]uinfo (username)` - Show information about a user.

`[p]cam (username)` - Allow a user to cam in green room enabled room.

`[p]cbc (username)` - Toggle if a user is allowed to broadcast.

`[p]is (instagram user)` - Search instagram.

`[p]porn (keyword)` - Search Eporner API for porn.

`[p]close (username)` - Close a users broadcast.

`[p]sbl (username)` - Search the banlist.

`[p]fg (usernane)` - Forgive a banned user.

`[p]unb (username)` - Unban a banned user.

`[p]jcd` - Get directory information from [jumpin.chat](http://jumpin.chat/)

`[p]jcr (room name)` - Get user and broadcaster count for a room on [jumpin.chat](http://jumpin.chat/)

`[p]jcu (account)` - Search [jumpin.chat](http://jumpin.chat/) rooms for a user matching the account name.


<sub>* Use asterisk at the beginning of a nickname as a wildcard, i.e. *ickname matches nicknanme</sub>

<sub>** Use asterisk as a wildcard, i.e. "*example.com" would ban any message containing "example.com"</sub>


## DEFAULT(6) Commands.

`[p]pmme` - Open a private session with the bot.

`[p]opme (key)` - Change user level based on provided key. *

`[p]v` - Show bot version.

`[p]help` - Show a link to this help file.

`[p]t` - Show the bot's uptime.

`[p]yt (search term)` - Search youtube.

`[p]q` - Show the playlist queue count.

`[p]n` - Show the next track in the playlist.

`[p]np` - Show information about the currently playing track.

`[p]wp` - Show who played the current track.

`[p]acspy (account)` - Show information about a Tinychat account.

`[p]urb (search term)` - Search UrbanDictionary for definitions.

`[p]wea (city)` - Show weather data for a given city.

`[p]ip (IP or domain)` - Show whois information for a given IP/domain.

`[p]wiki (search term)` - Search wikipedia.

`[p]cn` - Random Chuck Norris quote/joke.

`[p]8ball (question)` - Magic 8ball.

`[p]roll` - Roll a die.

`[p]flip` - Flip a coin.

### Voting Commands

*These commands needs to be enabled in the config.ini. Alternatively, they can be enabled by a moderator as described under **MODERATOR** commands. **A vote session can only be started by a user who has been in the room for more than 5 minuttes.*** 

`[p]vtb (username)` - Start a vote to ban session.

`[p]vtk (username)` - Start a vote to kick session.

`[p]vtc (username)` - Start a vote to close session.

`[p]vote (yes/no)` - Cast a yes/no vote to a vote session.
