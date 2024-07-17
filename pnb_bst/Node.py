from threading import Lock


class Node:
    def __init__(self, key, left=None, right=None):
        self.key = key
        self.left = left
        self.right = right
        self.deleted = False
        self.lock = Lock()

    def custom_deepcopy(self):
        # Custom deep copy that excludes the Lock object
        new_node = Node(self.key)
        if self.left:
            new_node.left = self.left.custom_deepcopy()
        if self.right:
            new_node.right = self.right.custom_deepcopy()
        return new_node
