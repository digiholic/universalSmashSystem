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

def addTowards(_value, _addend, _base=0):
    """ Returns the median value of _base, _value, and _value+_addend. The behavior of this 
    function is not immediately obvious from this description, but think of it as an addition that 
    acts differently if the resulting difference passes or goes away from the base value. 

    Parameters
    -----------
    _value : float
        The value to be added to. 
    _addend : float
        The value to add. 
    _base : float
        The value against which to compare the sum. 
    """
    if hasattr(_value, '__getitem__'):
        return map(lambda x: addTowards(_value[x], _addend[x], _base), range(len(_value)))
    else:
        if _addend == 0: return _value
        sign = math.copysign(1, _addend)
        if sign*(_base-_value-_addend) > 0: return _value+_addend
        else: return max(_base, _value, key=lambda k: sign*k) 

def addAway (_value, _addend, _base=0):
    """ Returns the sum of _value and _addend if the sum would go away from _base, otherwise 
    returns _value.  

    Parameters
    -----------
    _value : float
        The value to be added to. 
    _addend : float
        The value to add. 
    _base : float
        The value against which to compare the sum. 
    """
    if hasattr(_value, '__getitem__'):
        return map(lambda x: addAway(_value[x], _addend[x], _base), range(len(_value)))
    elif _addend*(_base-_value) <= 0: return _value+_addend
    else: return _value
    
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
    if hasattr(_value, '__getitem__'):
        return map(lambda x: addFrom(_value[x], _addend[x], _base), range(len(_value)))
    elif _amount < 0 and -abs(_value-_base) > _amount: return _base
    else: return _amount*math.copysign(1, _value-_base) + _value

def bounded(_value, _min, _max):
    """ Returns _value is _value is between _min and _max, _min if _value is less than _min, 
    and _max is _value is greater than _max. This function assumes that _min < _max, and will 
    probably act strange otherwise. 
    
    Parameters
    -----------
    _value : float
        The value to be bounded. 
    _min : float
        The lower bounding value. 
    _max : float
        The upper bounding value. 
    """
    if hasattr(_value, '__getitem__'):
        return map(lambda x: bounded(_value[x], _min, _max), range(len(_value)))
    elif _value < _min: return _min
    elif _value > _max: return _max
    else: return _value

def inIntervals(_dict, _ranges):
    for key in _dict.keys().intersection(_ranges.keys()):
        if _dict[key] < _ranges[key][0] or _dict[key] > _ranges[key][1]:
            return False
    return True
