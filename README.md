# Geoffrey: A Discord Bot for Minecraft Servers
Geoffrey was created to be an information source for base and shop locations on Minecraft severs. The bot mainly tracks
base, shop, and tunnel locations. This allows for users to quickly find each other's builds and find shops selling
goods.

Geoffrey can be used on a Discord server or in a private message with the bot.

## Information
Geoffrey was written in python and uses the [Discord.py rewrite](https://discordpy.readthedocs.io/en/rewrite/)
 to interface with Discord and [SQLAlchemy](https://docs.sqlalchemy.org/en/latest/) for database
access.

## Adding a base
First you must register with the bot if you are a new user.
```
?register
```

This allows Geoffrey to link your MC name with your Discord account.

Then you can add your first base:
```
?add_base 500 550
```

Your first base does not need a name, it defaults to "[Username]'s Base"

If you want to specify a name:
```
?add_base 500 550 My New Base
```

To delete a base:
```
?delete "My Base"
```
## Adding a shop
A shop can be added like a base:
```
?add_shop 500 550
```

or

```
?add_shop 500 550 Cool Shop
```

The following command then adds dirt to the shop with the price of 5 dirt for 1 diamond:
```
?add_item Dirt 5 1 
```

Then you could delete that entry by:
```
?delete_item dirt
```

To delete a shop:
```
?delete "My shop"
```
## Adding a shop

If you have more than one shop, you need to specify the shop name.

## Searching in the database
The `?find` command is used to find bases and shops in Geoffrey. `?find` searches for both location names and owner names:
```
?find ZeroHD
```

Then to find out more info about a location, use `?info`:
```
?info ZeroHD's Base
```


`?selling` can be used to find items for sale. Tip is better search for a subset of the item name. 
ig for `enderchests` search `ender`:
```
?selling ender
```

You can also search around a position for locations with `?find_around`:
```
?find_around 0 0
```

## Editing Locations
To rename a base/shop you can do the following (the quotations around the location names are important!):
```
?edit_name "Cool New Name" "Current Name"
```

To move a location's position, use `?edit_pos`
```
?edit_pos 420 69 Cool Base
```

To change the tunnel of a base, use `?edit_tunnel`:
```
?edit_tunnel North 545
```
