import read_trace_file
import sys
import tools
from event import Record,EventRecord,StateRecord,CommunicationRecord
from enum_sim import RecordType


if __name__ == '__main__':

    if(len(sys.argv) <= 1):
        print("Arg filename required! Run python main.py <filename>")
        exit(0)

    filename = sys.argv[1]
    state_dict, event_dict = read_trace_file.read_pcf_file(filename+".pcf")

    header, nodes_conf, record_list = read_trace_file.read_prv_file(filename+".prv")
    state_list, event_list, communication_list = read_trace_file.separate_trace_record(record_list)

    duration = tools.list_duration(state_list,state_dict)
    tools.compute_ecdf(duration)

    print(nodes_conf)
    print(state_list[0])
    print(event_list[0])
    print(communication_list[0])

    task_list = [i for i in range(1,nodes_conf[0]+1)]

    task_id = task_list.pop(1)

    tools.scale_trace(state_list,state_dict,task_list,task_id)
    file = open("test_state.prv","w") 
    file.write(header)
    for record in state_list:
        file.write(str(record)+"\n")
    file.close()

    #simulation = EventSim(0,nodes_conf)
    #for event in state_list:
    #    simulation.schedule_event(event)
    #simulation.run()