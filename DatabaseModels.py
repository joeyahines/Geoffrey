from sqlalchemy import Column, Integer, String, ForeignKey, Enum
import enum
from sqlalchemy.ext.declarative import declarative_base
from BotErrors import *
from sqlalchemy import create_engine, exists, func
from sqlalchemy.orm import sessionmaker, relationship
import sqlalchemy
from MinecraftAccountInfoGrabber import *

SQL_Base = declarative_base()


class GeoffreyDatabase:

    def __init__(self, engine_arg):
        self.engine = create_engine(engine_arg, echo=True)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        SQL_Base.metadata.create_all(self.engine)

    def add_location(self, player_name, name, x_pos, y_pos, z_pos, args):
        owner = self.add_player(player_name)
        location = Location(name, x_pos, y_pos, z_pos, owner, args)
        self.add_object(location)
        return location

    def add_shop(self, player_name, name, x_pos, y_pos, z_pos, args):
        owner = self.add_player(player_name)
        shop = Shop(name, x_pos, y_pos, z_pos, owner, args)
        self.add_object(shop)
        return shop

    def add_item(self, player_name, shop_name, item_name, price):
        try:
            shop = self.find_location_by_name_and_owner(player_name, shop_name)

            item = ItemListing(item_name, price, shop[0])
        except IndexError:
            raise LocationLookUpError

        return item

    def add_player(self, player_name):

        try:
            player = self.find_player(player_name)
        except PlayerNotFound:
            try:
                uuid = grab_UUID(player_name)
                player = self.find_player_by_uuid(uuid)
            except PlayerNotFound:
                player = Player(player_name)
                self.add_object(player)
            finally:
                player.name = player_name

        self.session.commit()
        return player

    def add_object(self, obj):
        ret = not self.session.query(exists().where(type(obj).id == obj.id))
        if not ret:
            self.session.add(obj)
            self.session.commit()

    def find_location_by_owner(self, owner_name):
        player = self.find_player(owner_name)
        expr = Location.owner == player
        return self.query_by_filter(Location, expr)

    def find_location_by_name_and_owner(self, owner_name, name):
        player = self.find_player(owner_name)
        expr = (Location.owner == player) & (Location.name == name)
        return self.query_by_filter(Location, expr)

    def find_location_around(self, x_pos, z_pos, radius):
        expr = (Location.x < x_pos + radius) & (Location.x > x_pos - radius) & (Location.z < z_pos + radius) & \
               (Location.z > z_pos - radius)

        return self.query_by_filter(Location, expr)

    def find_item(self, item_name):
        expr = ItemListing.name == item_name
        return self.query_by_filter(ItemListing, expr)

    def find_shop_selling_item(self, item_name):
        listings = self.find_item(item_name)

        shops = []
        for listing in listings:
            shops.append(listing.shop)

        return shops

    def find_player(self, player_name):
        expr = func.lower(Player.name) == func.lower(player_name)

        try:
            player = self.query_by_filter(Player, expr)[0]
        except IndexError:
            raise PlayerNotFound

        return player

    def find_player_by_uuid(self, uuid):
        expr = Player.id == uuid

        try:
            player = self.query_by_filter(Player, expr)[0]
        except IndexError:
            raise PlayerNotFound

        return player

    def query_by_filter(self, obj_type, * args):
        filter_value = self.combine_filter(args)
        return self.session.query(obj_type).filter(filter_value).all()

    def delete_base(self, player_name, base_name):
        player = self.find_player(player_name)
        expr = (Location.owner == player) & (Location.name == base_name)

        self.delete_entry(Location, expr)

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
        if arg == TunnelDirection.North.value:
            return TunnelDirection.North
        elif arg == TunnelDirection.East.value:
            return TunnelDirection.East
        elif arg == TunnelDirection.South.value:
            return TunnelDirection.South
        elif arg == TunnelDirection.West.value:
            return TunnelDirection.West
        else:
            raise ValueError


class Player(SQL_Base):
    __tablename__ = 'Players'

    id = Column(String, primary_key=True, autoincrement=False)
    name = Column(String)
    locations = relationship("Location", back_populates="owner", lazy='dynamic')

    def __init__(self, name):
        self.id = grab_UUID(name)
        self.name = name


class Location(SQL_Base):
    __tablename__ = 'Locations'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    x = Column(Integer)
    y = Column(Integer)
    z = Column(Integer)
    tunnelNumber = Column(Integer)
    direction = Column(Enum(TunnelDirection))
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

        except (ValueError, IndexError):
            raise LocationInitError

    def pos_to_str(self):
        return '(x= {}, y= {}, z= {})'.format(self.x, self.y, self.z)

    def nether_tunnel_addr_to_str(self):
        return '{} {}'.format(self.direction.value.title(), self.tunnelNumber)

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

    shop_id = Column(Integer, ForeignKey('Shops.shop_id'))
    shop = relationship("Shop", back_populates="inventory")

    def __init__(self, name, price, shop):
        self.name = name
        self.price = price
        self.shop = shop

    def __str__(self):
        return "Item: {}, Price: {}".format(self.name, self.price)
