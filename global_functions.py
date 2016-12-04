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

def subtractTowards(_value, _difference, _base=0):
    """ Returns the median value of _base, _value, and _value-_difference. The behavior of this 
    function is not immediately obvious from this description, but think of it as a subtraction that 
    acts differently if the resulting difference passes or goes away from the base value. 

    Parameters
    -----------
    _value : float
        The value to be subtracted from. 
    _difference : float
        The value to subtract. 
    _base : float
        The value against which to compare the difference. 
    """
    if _difference == 0: return _value
    sign = math.copysign(1, _difference)
    if sign*(_value-_difference-_base) > 0: return _value-_difference
    else: return min(_base, _value, key=lambda k: sign*k) 
    """
    if _difference > 0:
        if _base < _value-_difference: return _value-_difference
        else: return min(_base, _value)
    elif _difference < 0:
        if _base > _value-_difference: return _value-_difference
        else return max(_base, _value)
    else: 
        return _value
    """
    
def addFrom(_value, _amount, _base=0):
    """ Returns the sum of _amount multiplied by the sign of (_value - _base) to _value. 
    
    Parameters
    -----------
    _value : float
        The value to be added to/subtracted from. 
    _difference : float
        The value to add/subtract. Add to go away from _base, subtract to approach it. 
    _base : float
        The value to approach or recede from. 
    """
    sign = math.copysign(1, _value-_base)
    return _amount*sign + _value
