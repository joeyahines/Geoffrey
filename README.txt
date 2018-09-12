#Geoffrey: A Discord Bot for Minecraft Servers
Geoffrey was created to be an information source for base and shop locations on Minecraft severs. The bot mainly tracks
base, shop, and tunnel locations. This allows for users to quickly find each other's builds and find shops selling
goods.

Geoffrey can be used on a Discord server or in a private message with the bot.

##Information
Geoffrey was written in python and uses the [Discord.py rewrite](https://discordpy.readthedocs.io/en/rewrite/)
 to interface with Discord and [SQLAlchemy](https://docs.sqlalchemy.org/en/latest/) for database
access.

##Use Case
Say I am a new user and I want to add my base to the database. I would first register with Geoffrey:
```
?register
```

This allows Geoffrey to link your MC name with your Discord account.

I would then be able to add my base to Geoffrey by using the following command:
```
?add_base 500 550
```

Your first base does not need a name, it defaults to "[Username]'s Base"

If I wanted to specify a name, I could do the following:
```
?add_base 500 550 My New Base
```

If you want to rename a base you can do the following (the quotations around the base names are important!):
```
?edit_name "Cool New Name" "Current Name"
```

If you are so done with that base, you could delete it by doing the following:
```
?delete "My Base"
```

Geoffrey can do many more things. Make sure to checkout ?help for all the commands he can do! You can also do
?help [Command] to get more info about a particular command.


