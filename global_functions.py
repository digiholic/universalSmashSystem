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
    if _addend*(_base-_value) <= 0: return _value+_addend
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
    if _amount < 0 and -abs(_value-_base) > _amount: return _base
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
    if _value < _min: return _min
    elif _value > _max: return _max
    else: return _value

def dictDecay(_value, _dict, _decayAmount=1.0):
    """ Returns _value decayed according to the piecewise linear decay function defined by _dict. 
    If _decayAmount is provided, it is the decay value; otherwise, the decay factor is assumed 
    to be 1. 

    Parameters
    -----------
    _value : float
        The value to be decayed from
    _dict : dict(float: float)
        The dict defining the piecewise linear decay function, in the form of maxThreshold: slope
    _decayAmount : float
        The decay factor
    """

    # Get our bucket
    current_bucket = None
    key_candidates = sorted(filter(lambda k: k is not None, _dict.keys()))
    current_bucket_index = len(key_candidates)
    for candidate in key_candidates:
        if _value <= candidate:
            current_bucket = candidate
            current_bucket_index = key_candidates.index(candidate)
            break

    working_value = _value
    working_decay = _decayAmount
    while working_decay > 0.0:
        decay_factor = _dict[current_bucket]
        if decay_factor == 0.0: #Won't be moving from here, just return the value
            return working_value
        elif decay_factor > 0.0: #Move upward
            if current_bucket is None: #No limits, just move forward
                return working_value + decay_factor * working_decay
            else: #There's a higher entry
                if working_value + decay_factor*working_decay > current_bucket: # BONK
                    next_bucket_index = current_bucket_index + 1
                    if next_bucket_index == len(key_candidates): next_bucket = None
                    else: next_bucket = key_candidates[next_bucket_index]
                    if _dict[next_bucket] <= 0.0: #We'll stop here
                        return current_bucket
                    else:
                        decay_used = (current_bucket-working_value)/decay_factor
                        working_value = current_bucket
                        working_decay -= decay_used
                        current_bucket_index = next_bucket_index
                        current_bucket = next_bucket
                        continue
                else: return working_value + decay_factor*working_decay
        else: #Move downward
            if current_bucket_index == 0: #No limits, just move backward
                return working_value + decay_factor * working_decay
            else: #There's a lower entry
                if working_value + decay_factor*working_decay <= key_candidates[current_bucket_index-1]:
                    next_bucket_index = current_bucket_index - 1
                    next_bucket = key_candidates[next_bucket_index]
                    if _dict[next_bucket] >= 0.0: #We'll stop here
                        return next_bucket
                    else:
                        decay_used = (next_bucket-working_value)/decay_factor
                        working_value = next_bucket
                        working_decay -= decay_used
                        current_bucket_index = next_bucket_index
                        current_bucket = next_bucket
                        continue
                else: return working_value + decay_factor*working_decay
    return working_value
           
                 
                    
    









