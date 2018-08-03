# SendNewsBot

This is a Telegram bot that sends a daily report about a specific subject. One or more subjects can be defined using
RSS feeds. Currently it uses two RSS feeds that are subject to change depending on the needs of the repository's owner.
Therefore it is suggested to change them if you clone this repository.

## Installation

Run the command:

`git clone https://github.com/giaccone/SendNewsBot.git`

Then you need to:

* create a folder called `admin_only`
* put inside `admin_only` a plain text file called `admin_list.txt`. This file must include the telegram id of each admin (listed in column)
* put inside `admin_only` a plain text file called `SendNewsBot_token.txt`. This file must include `TOKEN` of your bot

At the first run the bot also creates a folder called `users` which will include the database of the users and groups that will use the bot. This database is called `users_database.db`.

At the end of the process your repo should look like this:

```
/
|-- admin_only
|     |-- admin_list.txt
|     |-- SendNewsBot_token.txt
|-- LICENSE
|-- README.md
|-- SendNewsBot.py
|--  users
      |-- users_database.db
```
