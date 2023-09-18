# Overview

This is a very simple tool that allows players to save their scores on [Pump It Up Phoenix](https://www.piugame.com/) to a sqlite3 database.

# Setup

To run the tool, you will need Python3 with a few extra libraries. You can install those libraries with the following command:

```
python3 -m pip install beautifulsoup4 pytz requests
```

# Retrieving your session cookie

For the time being, you'll need to manually retrieve your session cookie in order to perform the requests. Instructions:

* [Login to the website](https://www.piugame.com/login.php) by entering your username and password
* Upon successful login, open a Javascript console and enter `document.cookie`
  * Chrome users on Windows can access the console by typing Ctrl+Shift+I and clicking the 'Console' tab
* Save the entire result of `document.cookie` (single quotes included) to a file named `cookie.txt` in the same directory as `getplays.py`
  * For example, your cookie.txt file might look something like this: `'0123456789abcdef0123456789abcdef=MTk2; fedcba9876543210fedcba9876543210=ZW4tdXM%3D; sid=abcdefghijklmnopqrstuvwxyz; PHPSESSID=abcdefghijklmnopqrstuvwxyz'`

# Running

You can run the tool with:

```
python3 getplays.py
```

If there are no errors, this should create a file named `plays.db`, which contains all of the play data that is available on the website. Note that the website only saves play data from the last 30 days.

After you've played some more, you can run the tool again to add more play entries to the same database. It won't save the same play twice.

You can view the database using a graphical tool like [DB Browser](https://sqlitebrowser.org/dl/).

Since this tool has only been tested very lightly, I recommend saving a backup of your database before updating it.

# Interpreting the database

The database stores a row for each play. The columsn in the table are:

* `uniq TEXT`
  * A unique identifier for the chart, for convenience
  * (It combines `name`, `mode`, and `diff`)
* `name TEXT`
  * The name of the song
* `mode TEXT`
  * `S` for single, `D` for double, `C` for co-op
* `diff INT`
  * The difficulty of the chart (1-28)
* `score INT`
  * The player's score
  * Set to `0` if the song were prematurely exited due to 51 consecutive misses or Stage Break On
* `grade TEXT`
  * The player's grade
  * Grades include: `SSS+`, `SSS`, `SS+`, `SS`, `S+`, `S`, `AAA+`, `AAA`, `AA+`, `AA`, `A+`, `A`, `B`, `C`, `D`, `F`
  * Set to the empty string if the song were prematurely exited due to 51 consecutive misses or Stage Break On
* `passed INT`
  * `1` if the player passed, `0` if the player failed
  * Set to `0` if the song were prematurely exited due to 51 consecutive misses or Stage Break On
* `plate TEXT`
  * The plate awarded to the player, or the empty string if the song were not passed
  * Plates include: `PG`, `UG`, `EG`, `SG`, `MG`, `TG`, `FG`, `RG`
  * Set to the empty string if the song were prematurely exited due to 51 consecutive misses or Stage Break On
* `perfs INT`
  * The number of Perfect judgments
* `greats INT`
  * The number of Great judgments
* `goods INT`
  * The number of Gerfect judgments
* `bads INT`
  * The number of Bad judgments
* `misses INT`
  * The number of Miss judgments
* `date INT`
  * The date, represented as a Unix timestamp (seconds since the epoch)
* `date_pretty TEXT`
  * The date, formatted as a human-readable string in the local timezone, for convenience
  * Example format: `2023-12-31 23:59:59-05:00`
