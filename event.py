from enum_sim import RecordType

class Record(object):

    #type:cpu_id:app_id:task_id:thread_id:begin_time:end_time:state
    #type:cpu_id:app_id:task_id:thread_id:absolute_time:event_type:event_value
    #type:cpu_send_id:ptask_send_id:task_send_id:thread_send_id:lsend:psend:cpu_send_id:ptask_recv_id:task_recv_id:thread_recv_id:lrecv:precv:size:tag

    def __init__(self, type_=0, cpu_id_=0, app_id_=0, task_id_=0, thread_id_=0):
        self.type       = type_
        self.cpu_id     = cpu_id_
        #For communication event this is ptask_id, according to manual
        self.app_id     = app_id_ 
        self.task_id    = task_id_
        self.thread_id  = thread_id_
        self.duration   = 0
        self.due_time   = 0
    
    def process_event_record():
        pass
    
    def get_type(self):
        return self.type
    
    def set_due_time(self, time_):
        self.due_time = time_
    
    def get_due_time(self):
        return self.due_time
    
    def get_duration(self):
        return self.duration
    
    def get_arriving_time(self):
        return 0

    def get_begin_time(self):
        return 0

    def get_end_time(self):
        return 0
    
    def get_state(self):
        return 0

    def get_task_id(self):
        return self.task_id

    def __str__(self):
        return str(self.cpu_id) + ":" + str(self.app_id)  + ":" + str(self.task_id) + ":" + str(self.thread_id)

class EventRecord(Record):

    def __init__(self, list_args):
        Record.__init__(self,RecordType.EVENT,list_args[1],list_args[2],
                        list_args[3],list_args[4])
        self.absolute_time  = list_args[5]
        self.event_type     = {}

        del list_args[0:6]
        while(list_args):
            key=list_args.pop(0)
            value=list_args.pop(0)
            self.event_type[key] = value

    def get_begin_time(self):
        return self.absolute_time
    
    def set_begin_time(self,time_):
        self.absolute_time = time_
    
    def get_arriving_time(self):
        return self.absolute_time

    def has_event(self,event_type_,value_):
        ret = False
        if(event_type_ in self.event_type):
            if(self.event_type[event_type_] == value_):
                ret = True
        return ret

    def __str__(self):
        return (str(self.type.value) +":"+ Record.__str__(self) + ":" + str(self.absolute_time) + ":" + 
                str(self.event_type).replace(', ',':').replace("u'","").replace("'","").replace(' ','')[1:-1])


class StateRecord(Record):

    def __init__(self, list_args):
        Record.__init__(self,RecordType.STATE,list_args[1],list_args[2],
                        list_args[3],list_args[4])
        self.begin_time = list_args[5]
        self.end_time   = list_args[6]
        self.state      = list_args[7]
        self.duration   = (self.end_time - self.begin_time)
        self.due_time   = self.duration

    def get_arriving_time(self):
        return self.begin_time
    
    def get_state(self):
        return self.state

    def get_begin_time(self):
        return self.begin_time
    
    def get_end_time(self):
        return self.end_time

    def set_begin_time(self,time_):
        self.begin_time = time_

    def set_end_time(self,time_):
        self.end_time = time_

    def __str__(self):
        return (str(self.type.value) +":"+  Record.__str__(self) + ":" + str(self.begin_time) + ":" + 
                str(self.end_time) + ":" + str(self.state))


class CommunicationRecord(Record):

    def __init__(self, list_args):
        Record.__init__(self,RecordType.COMMUNICATION,list_args[1],list_args[2],
                        list_args[3],list_args[4])
        self.lsend          = list_args[5]
        self.psend          = list_args[6]
        self.cpu_recv_id    = list_args[7]
        self.ptask_recv_id  = list_args[8]
        self.task_recv_id   = list_args[9]
        self.thread_recv_id = list_args[10]
        self.lrecv          = list_args[11]
        self.precv          = list_args[12]
        self.size           = list_args[13]
        self.tag            = list_args[14]


    def get_arriving_time(self):
        return self.lsend

    def get_lsend_time(self):
        return self.lsend

    def get_psend_time(self):
        return self.psend

    def get_lrecv_time(self):
        return self.lrecv

    def get_precv_time(self):
        return self.precv

    def set_lsend_time(self,time_):
        self.lsend = time_

    def set_psend_time(self,time_):
        self.psend = time_

    def set_lrecv_time(self,time_):
        self.lrecv = time_

    def set_precv_time(self,time_):
        self.precv = time_

    def get_task_recv_id(self):
        return self.task_recv_id
    
    def __str__(self):
        return (str(self.type.value) +":"+  Record.__str__(self) + ":" + str(self.lsend) + ":" + str(self.psend) + ":" + 
                str(self.cpu_recv_id) + ":" + str(self.ptask_recv_id) + ":" + str(self.task_recv_id) + ":" + str(self.thread_recv_id) + ":" + 
                str(self.lrecv) + ":" + str(self.precv) + ":" + str(self.size) + ":" + str(self.tag))

    def _eq_(self,comm):
        return (self.lsend == comm.get_lsend_time() and self.psend == comm.get_psend_time()
                and self.task_recv_id == comm.get_task_recv_id() and self.task_id == comm.get_task_id())

class ExecutedEvent(Record):

    def __init__(self, list_args):
        Record.__init__(self,RecordType.EXECUTED,list_args[1],list_args[2],
                        list_args[3],list_args[4])

    def __str__(self):
        return (str(self.type) +" -> "+  Record.__str__(self) + ":" + str(self.due_time))