# project_pl

typelist = {int: 'INT', str: 'STR'}

def pl_type(obj):
    if hasattr(obj, 'type'):
        return obj.type
    else:
        tp = type(obj)
        for t in typelist:
            if tp is t:
                return typelist[t]
        raise IndexError()

class pl_object():
    def __init__(self):
        pass


class PL_INT(pl_object):
    def __init__(self, num):
        self.type = 'INT'
        self.__data = num

    def __repr__(self):
        return str(self.__data)

    def __int__(self):
        return self.__data
    
    def __pl_str__(self):
        return PL_STR(str(self.__data))
    
    def __add__(self, other):
        tp = pl_type(other)
        if tp == 'INT':
            return self.__class__(self.__data + other)
        elif tp == 'STR':
            return PL_STR(str(self.__data) + int(other))
        else:
            raise TypeError()
    
    def __sub__(self, other):
        tp = pl_type(other)
        if tp == 'INT':
            return self.__class__(self.__data - int(other))
        else:
            raise TypeError()
    
    def __mul__(self, other):
        tp = pl_type(other)
        if tp == 'INT':
            return self.__class__(self.__data * int(other))
        else:
            raise TypeError("can't multiply sequence by non-int of type '{}'".format(other.type))

    def __div__(self, other):
        tp = pl_type(other)
        if tp == 'INT':
            return self.__class__(self.__data / int(other))
        else:
            raise TypeError()


class PL_STR(pl_object):
    def __init__(self, s):
        self.type = 'STR'
        self.__data = s

    def __repr__(self):
        return self.__data
    
    def __add__(self, other):
        return self.__class__(self.__data + str(other))

    def __sub__(self, other):
        return self.__class__(self.__data.replace(other, ''))

    def __mul__(self, other):
        tp = pl_type(other)
        if tp == 'INT':
            return self.__class__(self.__data * int(other))
        else:
            raise TypeError("can't multiply sequence by non-int of type '{}'".format(tp))

        
