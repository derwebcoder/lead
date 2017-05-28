
class ContainerStore:

    __store = None
    def __init__(self):
        if ContainerStore.__store is None:
            ContainerStore.__store = dict()
            ContainerStore.__store['container'] = list()

    def add_container(self, container=None):
        ContainerStore.__store['container'].append(container)

    def get_containers(self):
        return ContainerStore.__store['container']

    def remove_container(self, container=None):
        ContainerStore.__store['container'].remove(container)

    