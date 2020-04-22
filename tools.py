from enum_sim import *
from event import Record,EventRecord,StateRecord,CommunicationRecord

def arr_idx_task(id):
    return (id -1)

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

#Returns the avg noise of sync for each thread
def sync_noise(record_list,task_list):
    avg = []
    aux = []
    idx = 0
    for i in range(len(task_list)):
        avg.append(0)
    for record in record_list:
        if(isinstance(record,StateRecord) and 
            (record.get_state() == 5)):
            aux.append(record)

        if(len(aux) == len(task_list)):
            nmaxst = max([x.get_begin_time() for x in aux])
            for x in aux:
                avg[arr_idx_task(x.get_task_id())] += (x.get_end_time() - (nmaxst))
            aux = []
            idx += 1

    if(idx):
        avg = [round(x/idx) for x in avg]

    return avg

#Returns the avg noise of init/finalize for each thread
def init_finalize_noise(record_list,task_list,state_dict):
    avg_init = []
    avg_finalize = []
    aux_init = []
    aux_finalize = []
    size = len(task_list)
    idx = 0
    for i in range(len(task_list)):
        avg_init.append(0)
        avg_finalize.append(0)
    for record in record_list:
        if(isinstance(record,StateRecord) and
            ( state_dict[record.get_state()] == GLOBAL_STATE_OTHERS )):
            aux = record_list[idx+1]
            if(isinstance(aux,EventRecord) and
                (aux.has_event(50000003,31))):
                aux_init.append(record)
            if(isinstance(aux,EventRecord) and
                (aux.has_event(50000003,32))):
                aux_finalize.append(record)
        idx+=1


    nmaxst = max([x.get_begin_time() for x in aux_init])
    for x in aux_init:
        avg_init[arr_idx_task(x.get_task_id())] += (x.get_end_time() - (nmaxst))
    
    nmaxst = max([x.get_begin_time() for x in aux_finalize])
    for x in aux_finalize:
        avg_finalize[arr_idx_task(x.get_task_id())] += (x.get_end_time() - (nmaxst))

    # Only one init and finalize
    avg_init = [x for x in avg_init]
    avg_finalize = [x for x in avg_finalize]

    return [avg_init,avg_finalize]

                            

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
                return False,GLOBAL_STATE_INIT
            elif(isinstance(aux,EventRecord) and
                (aux.has_event(50000003,32))):
                dependency.append(record)
                task_record_idx[current_task]+=1 #I'm sure there are more records
                return False,GLOBAL_STATE_FINALIZE
        
        if(state == GLOBAL_STATE_SYNC): 
            aux = record_list[recordid+1]
            if(isinstance(aux,EventRecord) and
                (aux.has_event(50000002,8))): #barrier
                dependency.append(record)
                task_record_idx[current_task]+=1 #I'm sure there are more records
                return False,GLOBAL_STATE_SYNC

        if(state == GLOBAL_STATE_WAITING):
            # comm is the record with some_task_send:current_task_recv
            # record is the waiting line for 
            #comm_rec = [count for count, item in enumerate(dependency) if (comm.get_task_recv_id() == current_task)]
            comm = dependency.pop()
            lsend = comm.get_lsend_time()
            psend = comm.get_psend_time()
            lrecv = comm.get_lrecv_time()
            precv = comm.get_precv_time()
            curr_begin = record.get_begin_time()
            curr_end = record.get_end_time()
            duration = record.get_duration()

            new_end = end_dict[curr_begin]+duration
            # If they finish at the same time, use the previous value?
            # TODO: it works for hydro, but breaks other traces
            if(curr_end in end_dict):
                print(curr_end)
                new_end = end_dict[curr_end]
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
            #if(dependency):
            #     print([str(x) for x in dependency])
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

    sync_noise_avg = sync_noise(record_list,task_list)
    print(sync_noise_avg)

    init_finalize_noise_avg = init_finalize_noise(record_list,task_list,state_dict)
    print(init_finalize_noise_avg)

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
        elif((ret_task == GLOBAL_STATE_INIT) or
            (ret_task == GLOBAL_STATE_FINALIZE)): #came from init or finalize
            if(len(dependency) == len(task_list)):
                # id to get the correct "noise"
                is_fin = 0 if (ret_task == GLOBAL_STATE_INIT) else 1
                max_end = max([end_dict[x.get_begin_time()] for x in dependency])
                # It may be wrong if there are diff dependencies in the structure
                # but I'm assuming in this stage there is only dependencies for init/finalize
                for dep in dependency:
                    curr_begin = dep.get_begin_time()
                    new_begin = end_dict[curr_begin]
                    curr_end =  dep.get_end_time()
                    # Uses the highest beginning and apply the "noise"
                    new_end = max_end + init_finalize_noise_avg[is_fin][arr_idx_task(dep.get_task_id())]
                    if(new_begin > new_end):
                        new_end = max_end + abs(init_finalize_noise_avg[is_fin][arr_idx_task(dep.get_task_id())])
        
                    dep.set_begin_time(new_begin)
                    dep.set_end_time(new_end)
                    end_dict[curr_begin] = new_begin
                    end_dict[curr_end] = new_end
                #reset to the interf task   
                current_task = taskid
                #Important reset dependency list
                dependency = []
            else:
                aux = (current_task)%len(task_list)
                current_task = task_list[aux]
        elif(ret_task == GLOBAL_STATE_SYNC):
            # It may be wrong if there are diff dependencies in the structure
            # Assuming it is barrier on comm_world.
            if(len(dependency) == len(task_list)):
                max_start = max([end_dict[x.get_begin_time()] for x in dependency])
                min_duration = min([x.get_duration() for x in dependency])
                for dep in dependency:
                    rec_task_id = dep.get_task_id()
                    curr_begin = dep.get_begin_time()
                    curr_end = dep.get_end_time()
                    new_begin = end_dict[curr_begin]
                    new_end = new_begin + dep.get_duration() # maybe it is not the best
                    

                    new_end = max_start + abs(sync_noise_avg[arr_idx_task(rec_task_id)])
                    if(new_begin > new_end):
                        new_end = new_begin + min_duration
                    #if(new_begin < max_start):
                    #    new_end = max_start + abs(sync_noise_avg[arr_idx_task(rec_task_id)])
                    #    if(new_begin > new_end):
                    #        print(dep)  
                    #elif(new_begin == max_start):
                    #    #print("{} - {}".format(dep.get_duration(),abs(sync_noise_avg[arr_idx_task(rec_task_id)])))
                    #    new_end = max_start + abs(sync_noise_avg[arr_idx_task(rec_task_id)])



                    dep.set_begin_time(new_begin)
                    dep.set_end_time(new_end)
                    end_dict[curr_end] = new_end
                #reset to the interf task   
                current_task = taskid
                #Important reset dependency list
                dependency = []
            else:
                aux = (current_task)%len(task_list)
                current_task = task_list[aux]
        else:
            current_task = ret_task

# Check for backward communication and erros in the trace
def check_trace(record_list,task_list):
    check_time = [0 for x in task_list]
    # Change later
    main_thread = [(x-1)*8+1 for x in task_list]
    max_trace_time = 0
    print(check_time)
    for record in record_list:
        if(isinstance(record,CommunicationRecord)):
            if(record.get_psend_time() >  record.get_precv_time()):
                print("Backward comm -> {}".format(record))
        elif(isinstance(record,StateRecord)):
            if(record.get_begin_time() > record.get_end_time()):
                print("wrong timming -> {}".format(record))
            task_id = record.get_task_id()
            if((record.get_state() != 2) and 
                (main_thread[arr_idx_task(task_id)] == record.get_thread_id())):
                if(check_time[arr_idx_task(task_id)] and 
                    (check_time[arr_idx_task(task_id)]-record.get_begin_time()) != 0):
                        print("Time breaking -> {}".format(record))
                check_time[arr_idx_task(task_id)] = record.get_end_time()
        else:
            if(record.has_event(40000001,0)):
                max_trace_time = max(max_trace_time,record.get_begin_time())
    
    return max_trace_time