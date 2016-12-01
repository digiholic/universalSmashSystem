import math

def getXYFromDM(_direction,_magnitude):
    """A helper function to get the X and Y magnitudes from the Direction and Magnitude of a trajectory
    
    Parameters
    -----------
    _direction : int
        A direction in degrees, 0 being right, 90 being up
    _magnitude : float
        The magnitude of the direction vector
    """
    rad = math.radians(_direction)
    x = round(math.cos(rad) * _magnitude,5)
    y = -round(math.sin(rad) * _magnitude,5)
    return (x,y)


def getDirectionBetweenPoints(_p1, _p2):
    """ Get the direction between two points. 0 means the second point is to the right of the first,
    90 is straight above, 180 is straight left. Used in some knockback calculations.
    
    Parameters
    -----------
    _p1, _p2 : tuple(int,int)
        Two points to determine direction between. Order unimportant.
    """
    (x1, y1) = _p1
    (x2, y2) = _p2
    dx = x2 - x1
    dy = y1 - y2
    return (180 * math.atan2(dy, dx)) / math.pi 

def hasClass(_object, _class):
    """ Determines if an object has a class of the given name, whether or not that object is imported.
    Functionally similar to isinstance, but can be done without causing circular import issues.
    
    Parameters
    -----------
    _object : Object
        The object we are checking classes from
    _class : String
        The name of the class we are checking for
    """
    return _class in list(map(lambda x :x.__name__,_object.__class__.__bases__)) + [_object.__class__.__name__]