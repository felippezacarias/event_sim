import read_trace_file
import sys
import tools
from event import Record,EventRecord,StateRecord,CommunicationRecord
from enum_sim import RecordType


if __name__ == '__main__':

    if(len(sys.argv) <= 2):
        print("Arg filename required! Run python main.py <filename_ref> <filename_interf_profile>")
        exit(0)

    filename_ref = sys.argv[1]
    state_dict, event_dict = read_trace_file.read_pcf_file(filename_ref+".pcf")

    header, nodes_conf, record_list = read_trace_file.read_prv_file(filename_ref+".prv")

    filename_interf_profile = sys.argv[2]
    _, _, profile_list = read_trace_file.read_prv_file(filename_interf_profile+".prv")

    duration = tools.list_duration(profile_list,state_dict)
    xx, yy = tools.compute_ecdf(duration)

    print(nodes_conf)

    task_list = [i for i in range(1,nodes_conf[0]+1)]

    task_id = task_list.pop(1)
    print(task_id)
    print(task_list)

    tools.scale_trace(record_list,state_dict,task_list,task_id)
    file = open("test_state.prv","w") 
    file.write(header)
    #TODO: Sort list 
    for record in record_list:
        #if(isinstance(record,StateRecord)):
        file.write(str(record)+"\n")
    file.close()

    #simulation = EventSim(0,nodes_conf)
    #for event in state_list:
    #    simulation.schedule_event(event)
    #simulation.run()