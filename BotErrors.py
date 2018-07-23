class DataBaseError(Exception):
    '''Base class for exceptions in this module.'''
    pass

class LocationInitError(DataBaseError):
    '''Error in initializing Location'''

class TunnelInitError(DataBaseError):
    '''Error in initializing Tunnel'''


class LocationLookUpError(DataBaseError):
    '''Error in finding location in database'''

class DeleteEntryError(DataBaseError):
    '''Error in deleting entry'''

class UsernameLookupFailed(Exception):
    '''Error in username lookup, is the player's nickname set correctly? *stares at aeskdar*'''

class PlayerNotFound(DataBaseError):
    '''Player not found in database.'''

class EntryNameNotUniqueError(DataBaseError):
    '''A location by that name is already in the database.'''

class StringTooLong(DataBaseError):
    '''Given string is too long.'''

class DatabaseValueError(DataBaseError):
    ''''String too long or number too large'''

class ItemNotFound(DataBaseError):
    '''No item matches found in database'''

class InvalidDimError(DataBaseError):
    """Invalid dimension name"""

class InvalidTunnelError(DataBaseError):
    """Invalid tunnel name"""



