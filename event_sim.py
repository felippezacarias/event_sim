import bisect
from nodes import Nodes
from event import Record,EventRecord,StateRecord,CommunicationRecord,ExecutedEvent


class Simulator(object):
    def __init__(self, time_=0):
        self.time = time_
        self.event_queue =  []
        self.processing_event_queue =  []

    def run(self):
        pass

    def schedule_event(self, event_record):
        self.event_queue.append(event_record)
    
    def can_execute_event(self, event_record):
        pass

    
    def schedule_processing_event(self, event_record):
        ret, event = self.can_execute_event(event_record)
        if(ret): #insert sorted by due time
            self.processing_event_queue.append(event)
        return ret


class EventSim(Simulator):
    def __init__(self, time_=0, nodes_conf_=[]):
        Simulator.__init__(self,time_)
        self.nodes_conf = [Nodes(ind,x) for ind, x in enumerate(nodes_conf_)]

    def run(self):
        has_record = 1
        print("Starting the event simulation!")
        while(has_record):
            print("sim_time {}".format(self.time))
            while(len(self.processing_event_queue)): 
                if(self.time >= self.processing_event_queue[0].get_due_time()):
                    event = self.processing_event_queue.pop(0)
                    self.process_event(event)
                else:
                    break 

            if(len(self.processing_event_queue)):
                print("Next processing_event due at {}".format(self.processing_event_queue[0].get_due_time()))  

            while(len(self.event_queue)): 
                if(self.time >= self.event_queue[0].get_arriving_time()):
                    event = self.event_queue.pop(0)
                    self.process_event(event)
                else:
                    break
            
            if(len(self.event_queue)):
                print("Next arriving_event at {}".format(self.event_queue[0].get_arriving_time()))
                print([str(x) for x in self.nodes_conf])
            
            has_record = (len(self.processing_event_queue) +
                            len(self.event_queue))
            
            self.time += 1
        
        print("Finishing the event simulation at {} sim time!".format(self.time))

            

    def can_execute_event(self, event_record):
        node_id = event_record.task_id - 1
        if(self.nodes_conf[node_id].has_free_cores()):
            self.nodes_conf[node_id].consume_core()
            list_args = [event_record.type,event_record.cpu_id,
                    event_record.app_id,event_record.task_id,event_record.thread_id]
            event = ExecutedEvent(list_args)
            event.set_due_time(self.time + event_record.get_duration())
            return True,event
        return False,None

    def process_event(self,event_record):
        node_id = event_record.task_id - 1
        if(isinstance(event_record, ExecutedEvent)):
            self.nodes_conf[node_id].free_core()
            return True
        else:
            return self.schedule_processing_event(event_record)