from enum_sim import RecordType
from event import Record,EventRecord,StateRecord,CommunicationRecord
from event_type import EventType

def open_file(filename):
    try:
        f = open(filename, "r")
        return f
    except IOError as x:
        print(x)
        print("Could not open " + filename + "!")
        return None

def func_sort_time(e):
  return e.get_arriving_time()

def read_prv_file(filename):
    record_list = []
    header = ""
    f = open_file(filename)
    if(f == None):
        exit(0)
    line = f.readline()
    header += line
    tmp = line.split(",")
    nodes_ = (line.split(":"))[3]
    nodes_ = [int(x) for x in nodes_.replace("("," ").replace(")"," ").replace(","," ").split()]
    nodes_.pop(0)
    # The pointer is alread in position to start the skip
    to_skip = int(tmp[len(tmp)-1])

    for _ in range(to_skip):
        #next(f)
        header += f.readline()
    
    for line in f:
        list_ = [int(x) for x in line.split(":")]
        type_ = list_[0]
        if(type_ == RecordType.STATE.value):
            record_list.append(StateRecord(list_))
        elif(type_ == RecordType.EVENT.value):
            record_list.append(EventRecord(list_))
        else:
            record_list.append(CommunicationRecord(list_))
    
    f.close()

    return header,nodes_,record_list

def separate_trace_record(record_list_):
    state_list = []
    event_list = []
    communication_list = []

    state_list = [x for x in record_list_ if isinstance(x,StateRecord)]
    event_list = [x for x in record_list_ if isinstance(x,EventRecord)]
    communication_list = [x for x in record_list_ if isinstance(x,CommunicationRecord)]

    return state_list,event_list,communication_list

def separate_record(record_list_):
    record_list = []
    communication_list = []

    record_list = [x for x in record_list_ if (isinstance(x,StateRecord) or isinstance(x,EventRecord))]
    communication_list = [x for x in record_list_ if isinstance(x,CommunicationRecord)]

    return record_list,communication_list

def read_pcf_file(filename):

    f = open_file(filename)
    if(f == None):
        exit(0)

    state_dict = read_state(f)

    event_dict = read_event_type(f)
        
    return state_dict, event_dict

def read_state(f):
    state_dict = {}

    for line in f:
        if line.strip() == "STATES":
            break
    
    line = f.readline().split()

    while(len(line) > 0):
        key = line.pop(0)
        s = [str(i) for i in line] 
        res = " ".join(s)
        state_dict[int(key)] = res
        line = f.readline().split()
    
    return state_dict

def read_event_type(f):
    event_dict = {}
    key=""
    line = f.readline()
    while(line):
        if line.strip() == "EVENT_TYPE":
            line = f.readline().split()
            line.pop(0)
            key = line.pop(0)
            s = [str(i) for i in line] 
            res = " ".join(s)
            event_dict[int(key)] = EventType(int(key),res)

            line = f.readline()

            if line.strip() == "VALUES":
                line_list = f.readline().split()
                while(len(line_list) > 1):
                    key_value = line_list.pop(0)
                    s = [str(i) for i in line_list] 
                    res = " ".join(s)
                    event_dict[int(key)].set_event_type_value(int(key_value),res)
                    line = f.readline()
                    line_list = line.split()
            else:
                line_list = f.readline().split()
                while(len(line_list) > 3):
                    line_list.pop(0)
                    key = line_list.pop(0)
                    s = [str(i) for i in line_list] 
                    res = " ".join(s)
                    event_dict[int(key)] = EventType(int(key),res)
                    line = f.readline()
                    line_list = line.split()
        else:
            line = f.readline()

    return event_dict