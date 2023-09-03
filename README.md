# Overview

This is a very simple tool that allows players to save their scores on [url=https://www.piugame.com/]Pump It Up Phoenix[/url] to a sqlite3 database.

# Setup

To run the tool, you will need Python3 with a few extra libraries. You can install those libraries with the following command:

```
python3 -m pip install beautifulsoup4 pytz requests
```

# Retrieving your session cookie

For the time being, you'll need to manually retrieve your session cookie in order to perform the requests. Instructions:

* [https://www.piugame.com/login.php]Login to the website[/url] by entering your username and password
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

You can view the database using a graphical tool like [url=https://sqlitebrowser.org/dl/]DB Browser[/url].

Since this tool has only been tested very lightly, I recommend saving a backup of your database before updating it.
