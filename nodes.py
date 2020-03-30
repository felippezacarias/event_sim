class Nodes(object):
    def __init__(self, node_id_=0, cores_=0):
        self.node_id = node_id_
        self.cores = cores_
        self.free_cores = cores_

    def get_cores(self):
        return self.cores

    def consume_core(self):
        self.free_cores -= 1

    def free_core(self):
        self.free_cores += 1

    def has_free_cores(self):
        return (self.free_cores == self.cores)

    def get_free_cores_count(self):
        return self.free_cores

    def get_node_id(self):
        return self.node_id

    def __str__(self):
        return "Node" + str(self.node_id) + " free_cores " + str(self.free_cores)