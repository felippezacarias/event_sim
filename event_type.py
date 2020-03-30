class EventType(object):
    def __init__(self,code_,name_):
        self.code = code_
        self.name = name_
        self.values = {}

    def set_event_type_value(self,key,value):
        if(self.values.get(key) == None):
            self.values[key] = []
        self.values[key].append(value)
    
    def __str__(self):
        return str(self.code) + " " + str(self.name) + " " + str(self.values)