from sqlalchemy import Column, Integer, String, ForeignKey, Enum, create_engine, exists, MetaData
from sqlalchemy.orm import sessionmaker, relationship, column_property
from sqlalchemy.exc import IntegrityError, DataError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import expression
from difflib import SequenceMatcher
import enum
from BotErrors import *
from MinecraftAccountInfoGrabber import *

SQL_Base = declarative_base()


def check_similarity(a, b):
    ratio = SequenceMatcher(None, a, b).ratio()

    if (ratio > 0.6) or (a[0] == b[0]):
        return True
    else:
        return False


class DatabaseInterface:

    def __init__(self, db_engine_arg):
        self.database = GeoffreyDatabase(db_engine_arg)

    def add_location(self, owner, name, x_pos, z_pos, dimension=None):
        location = Location(name, x_pos, z_pos, owner, dimension)
        self.database.add_object(location)
        return location

    def add_shop(self, owner, name, x_pos, z_pos, dimension=None):
        shop = Shop(name, x_pos, z_pos, owner, dimension)
        self.database.add_object(shop)
        return shop

    def add_tunnel(self, owner, color, number, location_name):
        if location_name is None:
            if len(self.find_tunnel_by_owner(owner)):
                raise EntryNameNotUniqueError
            else:
                location = None
        else:
            try:
                location = self.find_location_by_name_and_owner(owner, location_name)[0]
            except IndexError:
                raise LocationLookUpError

        tunnel = Tunnel(owner, color, number, location)

        self.database.add_object(tunnel)
        return tunnel

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

    def find_shop_by_owner(self, owner):
        expr = Shop.owner == owner
        return self.database.query_by_filter(Shop, expr)

    def find_location_by_owner_name(self, owner_name):
        expr = Location.owner.has(Player.name.ilike(owner_name))
        return self.database.query_by_filter(Location, expr)

    def find_shop_by_name_and_owner(self, owner, name):
        expr = (Shop.owner == owner) & (Shop.name.ilike(name))
        return self.database.query_by_filter(Shop, expr)

    def find_location_by_name_and_owner(self, owner, name):
        expr = (Location.owner == owner) & (Location.name.ilike(name))
        return self.database.query_by_filter(Location, expr)

    def find_location_around(self, x_pos, z_pos, radius, dimension):
        dimension_obj = Dimension.str_to_dimension(dimension)
        expr = (Location.x < x_pos + radius + 1) & (Location.x > x_pos - radius - 1) & (Location.z < z_pos + radius + 1) \
               & (Location.z > z_pos - radius - 1) & (Location.dimension == dimension_obj)

        return self.database.query_by_filter(Location, expr)

    def find_tunnel_by_owner(self, owner):
        expr = Tunnel.owner == owner

        return self.database.query_by_filter(Tunnel, expr)

    def find_tunnel_by_owner_name(self, owner_name):
        expr = Tunnel.owner.has(Player.name.ilike(owner_name))
        return self.database.query_by_filter(Tunnel, expr)

    def find_item(self, item_name):
        expr = ItemListing.name.ilike('%{}%'.format(item_name))
        return self.database.query_by_filter(ItemListing, expr)

    def find_shop_selling_item(self, item_name):
        listings = self.find_item(item_name)

        shops = []
        for listing in listings:
            shops.append(listing.selling_info())

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

    def search_all_fields(self, search):
        loc_string = ''
        count = 0

        expr = Location.owner.has(Player.name.ilike('%{}%'.format(search))) | Location.name.ilike('%{}%'.format(search))
        for loc in self.database.query_by_filter(Location, expr):
            loc_string = "{}\n{}".format(loc_string, loc)
            count += 1

        expr = Tunnel.owner.has(Player.name.ilike('%{}%'.format(search))) & Tunnel.location is None
        for loc in self.database.query_by_filter(Tunnel, expr):
            loc_string = "{}\n{}".format(loc_string, loc)
            count += 1

        if count == 0:
            raise LocationLookUpError
        else:
            return loc_string

    def delete_location(self, owner, name):
        expr = (Location.owner == owner) & (Location.name == name)
        self.database.delete_entry(Location, expr)


class DiscordDatabaseInterface(DatabaseInterface):
    def add_location(self, owner_uuid, name, x_pos, z_pos, dimension=None):
        owner = DatabaseInterface.find_player_by_discord_uuid(self, owner_uuid)
        return DatabaseInterface.add_location(self, owner, name, x_pos, z_pos, dimension)

    def add_shop(self, owner_uuid, name, x_pos, z_pos, dimension=None):
        owner = DatabaseInterface.find_player_by_discord_uuid(self, owner_uuid)
        return DatabaseInterface.add_shop(self, owner, name, x_pos, z_pos, dimension)

    def add_tunnel(self, owner_uuid, color, number, location_name=""):
        owner = DatabaseInterface.find_player_by_discord_uuid(self, owner_uuid)
        return DatabaseInterface.add_tunnel(self, owner, color, number, location_name)

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

    def find_shop_by_owner_uuid(self, owner_uuid):
        owner = DatabaseInterface.find_player_by_discord_uuid(self, owner_uuid)
        return DatabaseInterface.find_shop_by_owner(self, owner)

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
        self.meta = MetaData()
        SQL_Base.metadata.create_all(self.engine)

    def add_object(self, obj):
        try:
            ret = not self.session.query(exists().where(type(obj).id == obj.id))
            if not ret:
                self.session.add(obj)
                self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise EntryNameNotUniqueError
        except DataError:
            self.session.rollback()
            raise StringTooLong


    def query_by_filter(self, obj_type, * args):
        filter_value = self.combine_filter(args)
        return self.session.query(obj_type).filter(filter_value).all()

    def delete_entry(self, obj_type, * args):
        filter_value = self.combine_filter(args)
        entry = self.session.query(obj_type).filter(filter_value)

        if entry.first() is not None:
            entry.delete()
            self.session.commit()
        else:
            raise DeleteEntryError

    def print_database(self, obj_type):
        obj_list = self.session.query(obj_type).all()

        s = ''

        for obj in obj_list:
                s = s + '\n' + obj.id
        return s

    def combine_filter(self, filter_value):
        return expression.and_(filter_value[0])


class TunnelDirection(enum.Enum):
    North = 'green'
    East = 'blue'
    South = 'red'
    West = 'yellow'

    def str_to_tunnel_dir(arg):
        arg = arg.lower()

        if check_similarity(TunnelDirection.North.value, arg):
            return TunnelDirection.North
        elif check_similarity(TunnelDirection.East.value, arg):
            return TunnelDirection.East
        elif check_similarity(TunnelDirection.South.value, arg):
            return TunnelDirection.South
        elif check_similarity(TunnelDirection.West.value, arg):
            return TunnelDirection.West
        else:
            raise ValueError


class Dimension(enum.Enum):
    overworld = 'overworld'
    nether = 'nether'
    end = 'end'

    def str_to_dimension(arg):
        arg = arg.lower()
        if check_similarity(Dimension.overworld.value, arg):
            return Dimension.overworld
        elif check_similarity(Dimension.nether.value, arg):
            return Dimension.nether
        elif check_similarity(Dimension.end.value, arg):
            return Dimension.end
        else:
            raise ValueError


class Player(SQL_Base):
    __tablename__ = 'Players'
    id = Column(Integer, primary_key=True, autoincrement=True)
    mc_uuid = Column(String(128))
    discord_uuid = Column(String(128))
    name = Column(String(128))
    locations = relationship("Location", back_populates="owner", lazy='dynamic',
                             cascade="save-update, merge, delete, delete-orphan")

    tunnels = relationship("Tunnel", back_populates="owner", lazy='dynamic',
                           cascade="save-update, merge, delete, delete-orphan")

    def __init__(self, name, discord_id=None):
        self.mc_uuid = grab_UUID(name)
        self.discord_uuid = discord_id
        self.name = name


class Tunnel(SQL_Base):
    __tablename__ = 'Tunnels'
    id = Column(Integer, primary_key=True, autoincrement=True)
    tunnel_number = Column(Integer)
    tunnel_direction = Column(Enum(TunnelDirection))
    owner_id = Column(Integer, ForeignKey('Players.id'))
    owner = relationship("Player", back_populates="tunnels", cascade="save-update, merge, delete")
    location_id = Column(Integer, ForeignKey('Locations.id', ondelete='CASCADE'))
    location = relationship("Location", back_populates="tunnel")

    def __init__(self, owner, tunnel_color, tunnel_number, location=None):
        try:
            self.owner = owner
            self.location = location
            self.tunnel_direction = TunnelDirection.str_to_tunnel_dir(tunnel_color)
            self.tunnel_number = tunnel_number
        except (ValueError, IndexError):
            raise TunnelInitError

    def __str__(self):
        return '{} {}'.format(self.tunnel_direction.value.title(), self.tunnel_number)


class Location(SQL_Base):
    __tablename__ = 'Locations'

    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True, )
    x = Column(Integer)
    z = Column(Integer)

    tunnel = relationship("Tunnel",  uselist=False, cascade="all, delete-orphan")
    dimension = Column(Enum(Dimension))

    owner_id = Column(Integer, ForeignKey('Players.id', ondelete='CASCADE'))
    owner = relationship("Player", back_populates="locations", cascade="all, delete-orphan", single_parent=True)
    type = Column(String(128))

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'Location'
    }

    def __init__(self, name, x, z, owner, dimension):
        try:
            self.name = name
            self.x = x
            self.z = z
            self.owner = owner

            if self.dimension is not None:
                self.dimension = self.dimension = Dimension.str_to_dimension(dimension)
            else:
                self.dimension = Dimension.overworld

        except (ValueError, IndexError):
            raise LocationInitError

    def pos_to_str(self):
        return '(x= {}, z= {}) in the {}'.format(self.x, self.z, self.dimension.value.title())

    def info_str(self):
        return "Name: **{}**, Type: **{}** Position: **{}**".format(self.name, self.type, self.pos_to_str())

    def full_str(self):
        return self.__str__()

    def __str__(self):
        if self.tunnel is not None:
            return "{}, Tunnel: **{}**".format(self.info_str(), self.tunnel)
        else:
            return self.info_str()


class Shop(Location):
    __tablename__ = 'Shops'
    shop_id = Column(Integer, ForeignKey('Locations.id', ondelete='CASCADE'), primary_key=True)
    name = column_property(Column(String(128)), Location.name)
    inventory = relationship('ItemListing', back_populates='shop', cascade='all, delete-orphan')
    __mapper_args__ = {
        'polymorphic_identity': 'Shop',
    }

    def inv_to_str(self):

        if len(self.inventory.all()) != 0:
            inv = '\n\t*Inventory:*'
            str_format = '{}\n\t\t{}'

            for item in self.inventory:
                inv = str_format.format(inv, item)

            return inv
        else:
            return ''

    def full_str(self):
        return Location.full_str(self) + self.inv_to_str()

    def __str__(self):
        return Location.__str__(self)

    def __init__(self, name, x, z, owner, dimension=None):
        Location.__init__(self, name, x, z, owner, dimension)


class ItemListing(SQL_Base):
    __tablename__ = 'Items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128))
    price = Column(Integer)
    amount = Column(Integer)

    shop_id = Column(Integer, ForeignKey('Shops.shop_id', ondelete='CASCADE'))
    shop = relationship("Shop", back_populates="inventory", single_parent=True)

    def __init__(self, name, price, amount, shop):
        self.name = name
        self.price = price
        self.amount = amount
        self.shop = shop

    def selling_info(self):
        return 'Shop: **{}**, {}'.format(self.shop.name, self.__str__())

    def __str__(self):
        return "Item: **{}**, Price: **{}** for **{}**D".format(self.name, self.amount, self.price)
