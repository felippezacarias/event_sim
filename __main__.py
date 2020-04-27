import re
import read_trace_file
import sys
import tools
from event import Record,EventRecord,StateRecord,CommunicationRecord
from enum_sim import RecordType


if __name__ == '__main__':

    if(len(sys.argv) <= 3):
        print("Arg filename required! Run python main.py <filename_ref> <filename_interf_profile> interf_task")
        exit(0)

    filename_ref = sys.argv[1]
    state_dict, event_dict = read_trace_file.read_pcf_file(filename_ref+".pcf")
    header, nodes_conf, record_list = read_trace_file.read_prv_file(filename_ref+".prv")

    filename_interf_profile = sys.argv[2]
    _, _, profile_list = read_trace_file.read_prv_file(filename_interf_profile+".prv")
    state_dict_prof, _ = read_trace_file.read_pcf_file(filename_interf_profile+".pcf")

    print(nodes_conf)

    task_list = [i for i in range(1,nodes_conf[1]+1)]

    # TODO: check if task exists
    task_id = int(sys.argv[3])

    print(task_id)
    print(task_list)
    print(len(task_list))

    # Calculating the percentile of the reference and profile trace
    duration_ref = tools.list_duration(record_list,state_dict,task_id)
    print(len(duration_ref))
    xx, yy = tools.compute_ecdf(duration_ref)

    check_task_ref = 1
    if(filename_ref == filename_interf_profile):
        check_task_ref = task_id
    # always task one, cause it was the interfered
    duration_prof = tools.list_duration(profile_list,state_dict_prof,check_task_ref)
    xxp, yyp = tools.compute_ecdf(duration_prof)

    ecdf = [xx, yy, xxp, yyp]

    tools.scale_trace(record_list,state_dict,task_list,task_id,ecdf)

    # Updating header
    max_trace_time = tools.check_trace(record_list,task_list)
    regex = re.compile(r"[0-9]*_ns", re.IGNORECASE)
    header = regex.sub(str(max_trace_time)+"_ns", header)

    output = filename_ref.split("/")[-1]
    file = open(output+"_mod.prv","w") 
    file.write(header) 
    for record in record_list:
        file.write(str(record)+"\n")
    file.close()
    #
    ##simulation = EventSim(0,nodes_conf)
    ##for event in state_list:
    ##    simulation.schedule_event(event)
    ##simulation.run()