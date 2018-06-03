from sqlalchemy import Column, Integer, String, ForeignKey, Enum
import enum
from sqlalchemy.ext.declarative import declarative_base
from BotErrors import *
from sqlalchemy import create_engine
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

    def add_object(self, obj):
        self.session.add(obj)

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

    uuid = Column(String, primary_key=True)

    def __init__(self, name):
        if name == 'dootb.in ꙩ ⃤' :
            name = 'aeskdar'

        self.uuid = grab_UUID(name)


class Location(SQL_Base):
    __tablename__ = 'Locations'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    x = Column(Integer)
    y = Column(Integer)
    z = Column(Integer)
    tunnelNumber = Column(Integer)
    direction = Column(Enum(TunnelDirection))
    owner_uuid = Column(String, ForeignKey('Players.uuid'))
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
            self.owner_uuid = owner

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

    id = Column(Integer, ForeignKey('Locations.id'), primary_key=True)
    name = Column(String)
    inventory = relationship('ItemListing', back_populates='shop')

    __mapper_args__ = {
        'polymorphic_identity': 'Shop'
    }

    def __init__(self, name, x, y, z, owner, args):
        Location.__init__(name, x, y, z, owner, args)


class ItemListing(SQL_Base):
    __tablename__ = 'Items'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Integer)

    shop_id = Column(Integer, ForeignKey('Shops.id'))

    shop = relationship('Shop', back_populates='inventory')

    def __init__(self, name, price) :
        self.name = name
        self.price = price

    def __str__(self):
        return "Item: {}, Price: {}".format(self.name, self.price)
