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
    def __init__(self, data):
        self.__data = data

    def __repr__(self):
        return str(self.__data)

    def __str__(self):
        return str(self.__data)


class PL_INT(pl_object):
    def __init__(self, num):
        super().__init__(num)
        self.type = 'INT'
        self.__data = num

    def __int__(self):
        return int(self.__data)

    def __float__(self):
        return float(self.__data)
    
    def __pl_str__(self):
        return PL_STR(str(self.__data))
    
    def __add__(self, other):
        tp = pl_type(other)
        if tp in ['INT', 'FLOAT']:
            return self.__class__(self.__data + int(other))
        elif tp == 'STR':
            return PL_STR(str(self.__data) + str(other))
        else:
            raise TypeError()
    
    def __sub__(self, other):
        tp = pl_type(other)
        if tp in ['INT', 'FLOAT']:
            return self.__class__(self.__data - int(other))
        else:
            raise TypeError()
    
    def __mul__(self, other):
        tp = pl_type(other)
        if tp in ['INT', 'FLOAT']:
            return self.__class__(self.__data * int(other))
        else:
            raise TypeError("can't multiply sequence by non-int of type '{}'".format(other.type))

    def __div__(self, other):
        tp = pl_type(other)
        if tp in ['INT', 'FLOAT']:
            return self.__class__(self.__data / int(other))
        else:
            raise TypeError()


class PL_FLOAT(PL_INT):
    def __init__(self, num):
        super().__init__(num)
        self.type = 'FLOAT'
        self.__data = num

    def __add__(self, other):
        tp = pl_type(other)
        if tp in ['INT', 'FLOAT']:
            return self.__class__(self.__data + float(other))
        elif tp == 'STR':
            return PL_STR(str(self.__data) + str(other))
        else:
            raise TypeError()

    def __sub__(self, other):
        tp = pl_type(other)
        if tp in ['INT', 'FLOAT']:
            return self.__class__(self.__data - float(other))
        else:
            raise TypeError()
    
    def __mul__(self, other):
        tp = pl_type(other)
        if tp in ['INT', 'FLOAT']:
            return self.__class__(self.__data * float(other))
        else:
            raise TypeError("can't multiply sequence by non-int of type '{}'".format(other.type))

    def __div__(self, other):
        tp = pl_type(other)
        if tp in ['INT', 'FLOAT']:
            return self.__class__(self.__data / float(other))
        else:
            raise TypeError()


class PL_STR(pl_object):
    def __init__(self, s):
        self.type = 'STR'
        self.__data = s
    
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



def check_argtype(*types, **kwtypes):
    def wrapper(func):
        def wrapper2(*args, **kwargs):
            for i in range(len(args)):
                if type(args[i]) is not types[i]:
                    raise TypeError('error')
            for key in kwargs:
                if key in kwtypes:
                    if type(kwargs[key]) is not kwtypes[key]:
                        raise TypeError('error')
            return func(*args, **kwargs)
        return wrapper2
    return wrapper


def check_return_type(r_type):
    def wrapper(func):
        def wrapper2(*args, **kwargs):
            result = func(*args, **kwargs)
            if type(result) is not r_type:
                raise TypeError("Return type must be '{}'".format(r_type))
            return result
        return wrapper2
    return wrapper

