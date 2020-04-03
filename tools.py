from enum_sim import GLOBAL_STATE_RUNNING,GLOBAL_STATE_WAITING
from event import Record,EventRecord,StateRecord,CommunicationRecord

def min_wait_duration(record_list,state_dict): 
    duration_list =  ([x.get_duration() for x in record_list 
                        if((state_dict[x.get_state()] == GLOBAL_STATE_WAITING) and 
                            (isinstance(x,StateRecord))) ])
    return min(duration_list)

def list_duration(record_list,state_dict,interf_task): 
    return ([x.get_duration() for x in record_list 
                if((state_dict[x.get_state()] == GLOBAL_STATE_RUNNING) and 
                    (isinstance(x,StateRecord)) and (x.get_task_id() == interf_task)) ])

def compute_ecdf(duration_list):
    xx = sorted(duration_list)
    n = len(xx)
    yy = [float(k)/n for k in range(0,n)]
    return xx,yy

def percentile_duration(ecdf,duration):
    # We return the first occurence
    duration_index = ecdf[0].index(duration)
    ref_percentile = ecdf[1][duration_index]

    prof_percent_index = ecdf[3].index(ref_percentile)
    prof_duration = ecdf[2][prof_percent_index]

    return prof_duration

def slowdown_duration_test(ecdf,duration,state):
    if(state == GLOBAL_STATE_RUNNING): # running
        return 1.5
    return 1

def slowdown_duration(ecdf,duration,state):
    if(state == GLOBAL_STATE_RUNNING): # running
        return percentile_duration(ecdf,duration)
    return duration

def update_record(record,state_dict,end_dict,ecdf,keep_ratio=False):
    update_status = True
    curr_begin = record.get_begin_time()
    if(isinstance(record,EventRecord)):
        if(curr_begin in end_dict):
            new_begin = end_dict[curr_begin]
            record.set_begin_time(new_begin)
        else: # first record
            end_dict[curr_begin] = curr_begin
    else:
        # If it is running keep the duration for non interfered tasks
        duration = record.get_duration()
        if not keep_ratio:
            state = state_dict[record.get_state()]
            #duration = slowdown_duration(ecdf,duration,state)
            duration = round(duration* slowdown_duration_test(ecdf,duration,state))
        
        curr_end = record.get_end_time()
        if(curr_begin in end_dict):
            new_begin = end_dict[curr_begin]        
            record.set_begin_time(new_begin)
            new_end = new_begin + duration
            
            if((keep_ratio) and (curr_end in end_dict) and
                (state_dict[record.get_state()] != GLOBAL_STATE_RUNNING)):
                new_end = max(new_end,end_dict[curr_end])

            record.set_end_time(new_end)
            end_dict[curr_begin] = new_begin
            end_dict[curr_end] = new_end
        else: #problem with the threads records
            print(record)
            update_status = False            

def update_comm_record(record,task_id,end_dict):
    task_id_send = record.get_task_id()
    task_id_recv = record.get_task_recv_id()

    if(task_id == task_id_send):
        lsend = record.get_lsend_time()
        psend = record.get_psend_time()
        record.set_lsend_time(end_dict[lsend])
        record.set_psend_time(end_dict[psend])

        #Checking the other task
        precv = record.get_precv_time()
        ppsend = end_dict[psend] #+ 100000
        if(precv < ppsend):
            end_dict[precv] = ppsend

    elif(task_id == task_id_recv):
        lrecv = record.get_lrecv_time()
        precv = record.get_precv_time()
        record.set_lrecv_time(end_dict[lrecv])
        record.set_precv_time(end_dict[precv])

#TODO: make it work with multiple threads per task
def scale_trace(record_list,state_dict,task_list,taskid,ecdf):
    status = True
    end_dict = {}
    comm_rec_list = []
    task_list_order = []
    min_wait = min_wait_duration(record_list,state_dict)

    for record in record_list:
        if(isinstance(record,CommunicationRecord)):
            comm_rec_list.append(record)
            if(record.get_task_id() == taskid):
                if(record.get_task_recv_id() not in task_list_order):
                    task_list_order.append(record.get_task_recv_id())
        elif(record.get_task_id() == taskid):
            status = update_record(record,state_dict,end_dict,ecdf,False)

    for record in comm_rec_list:
        update_comm_record(record,taskid,end_dict)

    for task_id_ in task_list:
        if(task_id_ not in task_list_order):
            task_list_order.append(task_id_)


    for task_id_ in task_list_order:
        for record in record_list:
            if(record.get_task_id() == task_id_):
                if((record.get_task_id() == task_id_) and
                    (not isinstance(record,CommunicationRecord))):
                    update_record(record,state_dict,end_dict,ecdf,True)
        
        for record in comm_rec_list:
            status = update_comm_record(record,task_id_,end_dict)