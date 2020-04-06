from enum_sim import GLOBAL_STATE_RUNNING,GLOBAL_STATE_WAITING,GLOBAL_STATE_SYNC,GLOBAL_STATE_OTHERS
from event import Record,EventRecord,StateRecord,CommunicationRecord

def min_wait_duration(record_list,state_dict): 
    duration_list =  ([x.get_duration() for x in record_list 
                        if((state_dict[x.get_state()] == GLOBAL_STATE_WAITING) and 
                            (isinstance(x,StateRecord))) ])
    if duration_list:
        return min(duration_list)
    return 0

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

def update_record1(record,state_dict,end_dict,min_wait,ecdf,non_interf_task=False):
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
        if not non_interf_task:
            state = state_dict[record.get_state()]
            duration = slowdown_duration(ecdf,duration,state)
            #duration = round(duration* slowdown_duration_test(ecdf,duration,state))
        
        curr_end = record.get_end_time()
        if(curr_begin in end_dict):
            new_begin = end_dict[curr_begin]        
            record.set_begin_time(new_begin)
            new_end = new_begin + duration
            
            if((non_interf_task) and (curr_end in end_dict) and
                (state_dict[record.get_state()] != GLOBAL_STATE_RUNNING)):
                new_end = max(new_end,end_dict[curr_end])

            if ((not non_interf_task) and 
                (state_dict[record.get_state()] == GLOBAL_STATE_WAITING) and
                (new_begin > curr_end)):
                new_end = new_begin + min_wait

            #if((non_interf_task) and
            #    (state_dict[record.get_state()] == GLOBAL_STATE_SYNC)):
            #    new_end = new_begin #+ (round(duration * 1.5))

            record.set_end_time(new_end)
            end_dict[curr_begin] = new_begin
            end_dict[curr_end] = new_end
        else: #problem with the threads records
            print(record)
            if(state_dict[record.get_state()] == 2): #first record
                end_dict[record.get_end_time()] = record.get_end_time()
                end_dict[record.get_begin_time()] = record.get_begin_time()
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
def scale_trace1(record_list,state_dict,task_list,taskid,ecdf):
    status = True
    end_dict = {}
    comm_rec_list = []
    task_list_order = []
    min_wait = min_wait_duration(record_list,state_dict)
    print(min_wait)

    for record in record_list:
        if(isinstance(record,CommunicationRecord)):
            comm_rec_list.append(record)
            if(record.get_task_id() == taskid):
                if(record.get_task_recv_id() not in task_list_order):
                    task_list_order.append(record.get_task_recv_id())
        elif(record.get_task_id() == taskid):
            status = update_record(record,state_dict,end_dict,min_wait,ecdf,False)

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
                    update_record(record,state_dict,end_dict,min_wait,ecdf,True)
        
        for record in comm_rec_list:
            status = update_comm_record(record,task_id_,end_dict)


def update_record(record_list,state_dict,end_dict,min_wait,ecdf,current_task,taskinterf,task_record_idx,dependency):
    update_status = True
    recordid = task_record_idx[current_task]
    record = record_list[recordid]
    curr_begin = record.get_begin_time()
    if(isinstance(record,CommunicationRecord)):
        dependency.append(record)
        task_record_idx[current_task]+=1
        return False,record.get_task_recv_id()
    elif(isinstance(record,EventRecord)):
        if(curr_begin in end_dict):
            new_begin = end_dict[curr_begin]
            record.set_begin_time(new_begin)
        else: # first record
            end_dict[curr_begin] = curr_begin
        return True,current_task
    else:
        # If it is running keep the duration for non interfered tasks
        duration = record.get_duration()
        state = state_dict[record.get_state()]
        # check if it mpi init and returns if it is true
        if(state == GLOBAL_STATE_OTHERS): 
            aux = record_list[recordid+1]
            if(isinstance(aux,EventRecord) and
                (aux.has_event(50000003,31))):
                dependency.append(record)
                task_record_idx[current_task]+=1 #I'm sure there are more records
                return False,0

        if(state == GLOBAL_STATE_WAITING):
            # comm is the record with some_task_send:current_task_recv
            # record is the waiting line for current_task
            comm = dependency.pop()
            lsend = comm.get_lsend_time()
            psend = comm.get_psend_time()
            lrecv = comm.get_lrecv_time()
            precv = comm.get_precv_time()
            curr_begin = record.get_begin_time()
            curr_end = record.get_end_time()
            duration = record.get_duration()
            
            new_end = end_dict[curr_begin]+duration
            if(end_dict[psend] > new_end):
                new_end = end_dict[psend] #plus a constant??
            else:
                #print(record)
                #print(comm)
                #print("{} {} {} {} {}".format(psend,end_dict[psend],end_dict[curr_begin],duration,min_wait))
                new_end_min_wait = end_dict[curr_begin]+min_wait
                if(end_dict[psend] < new_end_min_wait):
                    new_end = new_end_min_wait
                else:
                    new_end = end_dict[psend] + min_wait

            end_dict[curr_end] = new_end

            comm.set_lsend_time(end_dict[lsend])
            comm.set_psend_time(end_dict[psend])
            comm.set_lrecv_time(end_dict[lrecv])
            comm.set_precv_time(end_dict[precv])

            record.set_begin_time(end_dict[curr_begin])
            record.set_end_time(new_end)
            task_record_idx[current_task]+=1
            return True,comm.get_task_id()

        if (current_task == taskinterf):           
            duration = slowdown_duration(ecdf,duration,state)
            #duration = round(duration* slowdown_duration_test(ecdf,duration,state))
        
        curr_end = record.get_end_time()
        if(curr_begin in end_dict):
            new_begin = end_dict[curr_begin]        
            record.set_begin_time(new_begin)
            new_end = new_begin + duration
            
            record.set_end_time(new_end)
            end_dict[curr_begin] = new_begin
            end_dict[curr_end] = new_end   
            return True,current_task
        else: #problem with the threads records
            print("else - {}".format(record))
            if(state_dict[record.get_state()] == 2): #first record or ??thread???
                end_dict[record.get_end_time()] = record.get_end_time()
                end_dict[record.get_begin_time()] = record.get_begin_time()
            return True,current_task   

def check_bound(task_record_idx,current_task,task_list,record_length):
    if(task_record_idx[current_task] == record_length):
        aux = (current_task)%len(task_list)
        current_task = task_list[aux]
    return current_task

def scale_trace(record_list,state_dict,task_list,taskid,ecdf):
    status = True
    end_dict = {}
    task_record_idx = []
    dependency = []
    comm_rec_list = []
    task_list_order = []
    min_wait = min_wait_duration(record_list,state_dict)
    print(min_wait)

    # +1 to match the taskid and list id
    for i in range(len(task_list)+1):
        task_record_idx.append(0)
    

    #interfering task
    current_task = taskid
    record_length = len(record_list)
    print(record_length)
    task_record_idx[0] = record_length

    while (min(task_record_idx) != record_length):
        status = True
        current_task = check_bound(task_record_idx,current_task,task_list,record_length)
        #sanity check
        if(task_record_idx[current_task] == record_length):
            break
        recordid = task_record_idx[current_task]
        record = record_list[recordid]
        ret_task = current_task
        if(record.get_task_id() == current_task):
            status, ret_task = update_record(record_list,state_dict,end_dict,min_wait,ecdf,current_task,taskid,task_record_idx,dependency)
        if((status) and (current_task == ret_task)):
            task_record_idx[current_task]+=1
        elif(ret_task == 0): #came from init or other place
            if(len(dependency) == len(task_list)):
                max_end = max([end_dict[x.get_begin_time()]+x.get_duration() for x in dependency])
                for dep in dependency:
                    curr_begin = dep.get_begin_time()
                    new_begin = end_dict[curr_begin]
                    curr_end =  dep.get_end_time()
        
                    dep.set_begin_time(new_begin)
                    dep.set_end_time(max_end)
                    end_dict[curr_begin] = new_begin
                    end_dict[curr_end] = max_end
                #reset to the interf task   
                current_task = taskid
                dependency = []
            else:
                aux = (current_task)%len(task_list)
                current_task = task_list[aux]
        else:
            current_task = ret_task

def check_backward_comm(record_list):
    for record in record_list:
        if(isinstance(record,CommunicationRecord)):
            if(record.get_psend_time() >  record.get_precv_time()):
                print("Backward comm -> {}".format(record))