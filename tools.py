from enum_sim import GLOBAL_STATE_RUNNING

def list_duration(state_list,state_dict): #improve using the dict for idle entry
    return ([x.get_duration() for x in state_list 
                if(state_dict[x.get_state()] == GLOBAL_STATE_RUNNING)])

def compute_ecdf(duration_list):
    xx = sorted(duration_list)
    n = len(xx)
    yy = [float(k)/n for k in range(0,n)]
    print(xx[0:10])
    print(yy[0:10])
    return xx,yy

def get_scale(state,state_dict):
    if(state_dict[state] == GLOBAL_STATE_RUNNING): # running
        return 2 #change to percentile
    return 1

#TODO: merge update and adjust func. Add var, to enable the last if
def update_state_record(record,state_dict,begin_dict,end_dict):
    duration = record.get_duration() * get_scale(record.get_state(),state_dict)
    curr_begin = record.get_begin_time()
    curr_end = record.get_end_time()
    if(curr_begin in end_dict):
        new_begin = end_dict[curr_begin]
        new_end = new_begin + duration
        record.set_begin_time(new_begin)
        record.set_end_time(new_end)
        begin_dict[curr_begin] = new_begin
        end_dict[curr_end] = new_end
        
def adjust_state_records(record,state_dict,begin_dict,end_dict):
    duration = record.get_duration()
    curr_begin = record.get_begin_time()
    curr_end = record.get_end_time()
    if(curr_begin in end_dict):
        new_begin = end_dict[curr_begin]        
        record.set_begin_time(new_begin)
        new_end = new_begin + duration
        #if it is running maintain the ratio
        if((curr_end in end_dict) & 
            (state_dict[record.get_state()] != GLOBAL_STATE_RUNNING)):
            new_end = end_dict[curr_end]

        record.set_end_time(new_end)
        begin_dict[curr_begin] = new_begin
        end_dict[curr_end] = new_end

def scale_trace(state_list,state_dict,task_list,taskid):
    first_record = True
    begin_dict = {}
    end_dict = {}

    for record in state_list:
        curr_begin = record.get_begin_time()
        curr_end = record.get_end_time()
        if((record.get_task_id() == taskid) &
            (first_record)):
            begin_dict[curr_begin] = curr_begin
            end_dict[record.get_end_time()] = curr_end
            first_record = False
        elif(record.get_task_id() == taskid):
            update_state_record(record,state_dict,begin_dict,end_dict)

    for task_id_ in task_list:
        first_record = True
        for record in state_list:
            if(record.get_task_id() == task_id_):
                curr_begin = record.get_begin_time()
                curr_end = record.get_end_time()
                if((record.get_task_id() == task_id_) &
                    (first_record)):
                    begin_dict[curr_begin] = curr_begin
                    end_dict[record.get_end_time()] = curr_end
                    first_record = False
                elif(record.get_task_id() == task_id_):
                    adjust_state_records(record,state_dict,begin_dict,end_dict)