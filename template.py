# project_pl

class pl_object():
    def __init__(self):
        pass
    
    def pr(self):
        return type(self) + id(self)


class PL_INT(pl_object):
    def __init__(self, num):
        self.data = num

    def pr(self):
        return str(self.data)
    
    def add(self, arg):
        tp = type(arg)
        if tp is int:
            self.data += arg
        elif tp is str:
            temp = PL_STR(str(self.data) + arg)


class PL_STR(pl_object):
    def __init__(self, s):
        self.data = s

    def pr(self):
        return self.data

def PL_PRINT(obj):
    print(obj.pr())