from sqlalchemy import Column, Integer, String, ForeignKey, Enum
import enum
from sqlalchemy.ext.declarative import declarative_base
from BotErrors import *
from sqlalchemy import create_engine, exists, literal
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.exc import IntegrityError
import sqlalchemy
from MinecraftAccountInfoGrabber import *

SQL_Base = declarative_base()


class DatabaseInterface:

    def __init__(self, db_engine_arg):
        self.database = GeoffreyDatabase(db_engine_arg)

    def add_location(self, owner, name, x_pos, y_pos, z_pos, args):
        location = Location(name, x_pos, y_pos, z_pos, owner, args)
        self.database.add_object(location)
        return location

    def add_shop(self, owner, name, x_pos, y_pos, z_pos, args):
        shop = Shop(name, x_pos, y_pos, z_pos, owner, args)
        self.database.add_object(shop)
        return shop

    def add_item(self, owner, shop_name, item_name, price, amount):
        try:
            shop = self.find_shop_by_name_and_owner(owner, shop_name)

            item = ItemListing(item_name, price, amount, shop[0])
            self.database.add_object(item)
        except IndexError:
            raise LocationLookUpError

        return item

    def add_player(self, player_name, discord_id):

        try:
            player = self.find_player(player_name)
        except PlayerNotFound:
            try:
                uuid = grab_UUID(player_name)
                player = self.find_player_by_mc_uuid(uuid)
            except PlayerNotFound:
                player = Player(player_name)
                self.database.add_object(player, discord_id)
            finally:
                player.name = player_name

        self.database.session.commit()
        return player

    def find_location_by_name(self, name):
        expr = Location.name.ilike('%{}%'.format(name))
        return self.database.query_by_filter(Location, expr)

    def find_shop_by_name(self, name):
        expr = Location.name.ilike('%{}%'.format(name))
        return self.database.query_by_filter(Shop, expr)

    def find_location_by_owner(self, owner):
        expr = Location.owner == owner
        return self.database.query_by_filter(Location, expr)

    def find_location_by_owner_name(self, owner_name):
        owner = self.find_player(owner_name)
        return self.find_location_by_owner(owner)

    def find_shop_by_name_and_owner(self, owner, name):
        expr = (Shop.owner == owner) & (Shop.name.ilike(name))
        return self.database.query_by_filter(Shop, expr)

    def find_location_by_name_and_owner(self, owner, name):
        expr = (Location.owner == owner) & (Location.name.ilike(name))
        return self.database.query_by_filter(Location, expr)

    def find_location_around(self, x_pos, z_pos, radius, dimension):
        expr = (Location.x < x_pos + radius + 1) & (Location.x > x_pos - radius - 1) & (Location.z < z_pos + radius + 1) \
               & (Location.z > z_pos - radius - 1) & (Location.dimension == dimension)

        return self.database.query_by_filter(Location, expr)

    def find_item(self, item_name):
        expr = ItemListing.name.ilike('%{}%'.format(item_name))
        return self.database.query_by_filter(ItemListing, expr)

    def find_shop_selling_item(self, item_name):
        listings = self.find_item(item_name)

        shops = []
        for listing in listings:
            shops.append(listing.shop)
            shops.append(listing.__str__())

        return shops

    def find_player(self, player_name):
        expr = Player.name.ilike(player_name)

        try:
            player = self.database.query_by_filter(Player, expr)[0]
        except IndexError:
            raise PlayerNotFound

        return player

    def find_player_by_mc_uuid(self, uuid):
        expr = Player.id == uuid

        try:
            player = self.database.query_by_filter(Player, expr)[0]
        except IndexError:
            raise PlayerNotFound

        return player

    def find_player_by_discord_uuid(self, uuid):
        expr = Player.discord_uuid == uuid

        try:
            player = self.database.query_by_filter(Player, expr)[0]
        except IndexError:
            raise PlayerNotFound

        return player

    def get_shop_inventory(self, shop):
        expr = ItemListing.shop == shop

        return self.database.query_by_filter(ItemListing, expr)

    def delete_location(self, owner, name):
        expr = (Location.owner == owner) & (Location.name == name)

        self.database.delete_entry(Location, expr)


class DiscordDatabaseInterface(DatabaseInterface):
    def add_location(self, owner_uuid, name, x_pos, y_pos, z_pos, args):
        owner = DatabaseInterface.find_player_by_discord_uuid(self, owner_uuid)
        return DatabaseInterface.add_location(self, owner, name, x_pos, y_pos, z_pos, args)

    def add_shop(self, owner_uuid, name, x_pos, y_pos, z_pos, args):
        owner = DatabaseInterface.find_player_by_discord_uuid(self, owner_uuid)
        return DatabaseInterface.add_shop(self, owner, name, x_pos, y_pos, z_pos, args)

    def add_item(self, owner_uuid, shop_name, item_name, price, amount):
        owner = DatabaseInterface.find_player_by_discord_uuid(self, owner_uuid)
        return DatabaseInterface.add_item(self, owner, shop_name, item_name, price, amount)

    def add_player(self, player_name, discord_id):
        try:
            player = self.find_player(player_name)
        except PlayerNotFound:
            try:
                uuid = grab_UUID(player_name)
                player = self.find_player_by_mc_uuid(uuid)
            except PlayerNotFound:
                player = Player(player_name, discord_id)
                self.database.add_object(player)
            finally:
                player.name = player_name

        self.database.session.commit()
        return player

    def find_location_by_owner_uuid(self, owner_uuid):
        owner = DatabaseInterface.find_player_by_discord_uuid(self, owner_uuid)
        return DatabaseInterface.find_location_by_owner(self, owner)

    def find_shop_by_name_and_owner_uuid(self, owner_uuid, name):
        owner = DatabaseInterface.find_player_by_discord_uuid(self, owner_uuid)
        return DatabaseInterface.find_shop_by_name_and_owner(self, owner, name)

    def find_location_by_name_and_owner_uuid(self, owner_uuid, name):
        owner = DatabaseInterface.find_player_by_discord_uuid(self, owner_uuid)
        return DatabaseInterface.find_location_by_name_and_owner(self, owner, name)

    def delete_location(self, owner_uuid, name):
        owner = DatabaseInterface.find_player_by_discord_uuid(self, owner_uuid)
        return DatabaseInterface.delete_location(self, owner, name)


class GeoffreyDatabase:

    def __init__(self, engine_arg):
        self.engine = create_engine(engine_arg, echo=True)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        SQL_Base.metadata.create_all(self.engine)

    def add_object(self, obj):
        try:
            ret = not self.session.query(exists().where(type(obj).id == obj.id))
            if not ret:
                self.session.add(obj)
                self.session.commit()
        except IntegrityError:
            raise LocationNameNotUniqueError

    def query_by_filter(self, obj_type, * args):
        filter_value = self.combine_filter(args)
        return self.session.query(obj_type).filter(filter_value).all()

    def delete_entry(self, obj_type, * args):
        filter_value = self.combine_filter(args)
        entry = self.session.query(obj_type).filter(filter_value)

        if entry.first() is not None:
            entry.delete()
        else:
            raise DeleteEntryError

    def print_database(self, obj_type):
        obj_list = self.session.query(obj_type).all()

        s = ''

        for obj in obj_list:
                s = s + '\n' + obj.id
        return s

    def combine_filter(self, filter_value):
        return sqlalchemy.sql.expression.and_(filter_value[0])


class TunnelDirection(enum.Enum):
    North = 'green'
    East = 'blue'
    South = 'red'
    West = 'yellow'

    def str_to_tunnel_dir(arg):
        arg = arg.lower()
        if arg in TunnelDirection.North.value:
            return TunnelDirection.North
        elif arg in TunnelDirection.East.value:
            return TunnelDirection.East
        elif arg in TunnelDirection.South.value:
            return TunnelDirection.South
        elif arg in TunnelDirection.West.value:
            return TunnelDirection.West
        else:
            raise ValueError


class TunnelSide(enum.Enum):
    right = 'right'
    left = 'left'

    def str_to_tunnel_side(arg):
        arg = arg.lower()
        if arg in TunnelSide.right.value:
            return TunnelSide.right
        elif arg in TunnelSide.left.value:
            return TunnelSide.left
        else:
            raise ValueError


class Dimension(enum.Enum):
    overworld = 'overworld'
    nether = 'nether'
    end = 'end'

    def str_to_dimension(arg):
        arg = arg.lower()
        if arg in Dimension.overworld.value:
            return Dimension.overworld
        elif arg in Dimension.nether.value:
            return Dimension.nether
        elif arg in Dimension.end.value:
            return Dimension.end
        else:
            raise ValueError


class Player(SQL_Base):
    __tablename__ = 'Players'
    id = Column(Integer, primary_key=True, autoincrement=True)
    mc_uuid = Column(String)
    discord_uuid = Column(String)
    name = Column(String)
    locations = relationship("Location", back_populates="owner", lazy='dynamic')

    def __init__(self, name, discord_id=None):
        self.mc_uuid = grab_UUID(name)
        self.discord_uuid = discord_id
        self.name = name


class Location(SQL_Base):
    __tablename__ = 'Locations'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    x = Column(Integer)
    y = Column(Integer)
    z = Column(Integer)
    tunnelNumber = Column(Integer)
    direction = Column(Enum(TunnelDirection))
    tunnel_side = Column(Enum(TunnelSide))
    dimension = Column(Enum(Dimension))

    owner_id = Column(Integer, ForeignKey('Players.id'))
    owner = relationship("Player", back_populates="locations")
    type = Column(String)

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'Location'
    }

    def __init__(self, name, x, y, z, owner, args):
        try:
            self.name = name
            self.x = x
            self.y = y
            self.z = z
            self.owner = owner

            if len(args) > 0:
                self.direction = TunnelDirection.str_to_tunnel_dir(args[0])
                self.tunnelNumber = int(args[1])
                self.tunnel_side = TunnelSide.str_to_tunnel_side(args[2])

                if len(args) > 3:
                    self.dimension = Dimension.str_to_dimension(args[3])

            if self.dimension is None:
                self.dimension = Dimension.overworld

        except (ValueError, IndexError):
            raise LocationInitError

    def pos_to_str(self):
        return '(x= {}, y= {}, z= {}) in the {}'.format(self.x, self.y, self.z, self.dimension.value.title())

    def nether_tunnel_addr_to_str(self):
        return '{} {} {}'.format(self.direction.value.title(), self.tunnelNumber, self.tunnel_side.value.title())

    def __str__(self):
        if self.direction is not None:
            return "Name: {}, Position: {}, Tunnel: {}".format(self.name, self.pos_to_str(),
                                                               self.nether_tunnel_addr_to_str())
        else:
            return "Name: {}, Position: {}".format(self.name, self.pos_to_str())


class Shop(Location):
    __tablename__ = 'Shops'
    shop_id = Column(Integer, ForeignKey('Locations.id'), primary_key=True)
    name = Column(String)
    inventory = relationship('ItemListing', back_populates='shop', lazy='dynamic')
    __mapper_args__ = {
        'polymorphic_identity': 'Shop',
    }

    def __init__(self, name, x, y, z, owner, args):
        Location.__init__(self, name, x, y, z, owner, args)


class ItemListing(SQL_Base):
    __tablename__ = 'Items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    price = Column(Integer)
    amount = Column(Integer)

    shop_id = Column(Integer, ForeignKey('Shops.shop_id'))
    shop = relationship("Shop", back_populates="inventory")

    def __init__(self, name, price, amount, shop):
        self.name = name
        self.price = price
        self.amount = amount
        self.shop = shop

    def __str__(self):
        return "Item: {}, Price: {} for {}D".format(self.name, self.amount, self.price)
