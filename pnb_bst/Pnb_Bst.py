from queue import Queue
from threading import Lock

from graphviz import Digraph

from pnb_bst.Node import Node


class Pnb_Bst:
    def __init__(self) -> None:
        self.root = None
        self.lock = Lock()
        self.versions = []

    def search(self, key):
        with self.lock:
            if self.root:
                copied_root = self.root.custom_deepcopy()
                return self._search(copied_root, key)
            else:
                return None

    def _search(self, node, key):
        if node is None:
            return None
        if node.key == key:
            return node
        elif key < node.key:
            return self._search(node.left, key)
        else:
            return self._search(node.right, key)

    def insert(self, key):
        with self.lock:
            if self.root is None:
                self.root = Node(key)
            else:
                self._insert(self.root, key)
            self.versions.append(self.root.custom_deepcopy())

    def _insert(self, node, key):
        with node.lock:
            if key < node.key:
                if node.left is None:
                    node.left = Node(key)
                else:
                    self._insert(node.left, key)
            elif key > node.key:
                if node.right is None:
                    node.right = Node(key)
                else:
                    self._insert(node.right, key)

    def delete(self, key):
        with self.lock:
            if self.root is not None:
                self._delete(self.root, None, key)
            self.versions.append(self.root.custom_deepcopy())

    def _delete(self, node, parent, key):
        with node.lock:
            if key < node.key:
                if node.left:
                    self._delete(node.left, node, key)
            elif key > node.key:
                if node.right:
                    self._delete(node.right, node, key)
            else:
                if node.left and node.right:
                    min_larger_node = self._get_min(node.right)
                    node.key = min_larger_node.key
                    self._delete(node.right, node, min_larger_node.key)
                elif node.left or node.right:
                    child = node.left if node.left else node.right
                    if parent:
                        if parent.left == node:
                            parent.left = child
                        else:
                            parent.right = child
                    else:
                        self.root = child
                else:
                    if parent:
                        if parent.left == node:
                            parent.left = None
                        else:
                            parent.right = None
                    else:
                        self.root = None

    def _get_min(self, node):
        while node.left is not None:
            node = node.left
        return node

    def find_key_range(self, low, high):
        with self.lock:
            if self.root:
                copied_root = self.root.custom_deepcopy()
                return self._find_key_range(copied_root, low, high, [])
            else:
                return []

    def _find_key_range(self, node, low, high, result):
        if node is None:
            return result
        if low <= node.key <= high:
            result.append(node.key)
        if node.key > low:
            self._find_key_range(node.left, low, high, result)
        if node.key < high:
            self._find_key_range(node.right, low, high, result)
        return result

    def visualize(self, version=None):
        if version is None:
            tree_to_visualize = self.root
        else:
            if version < 0 or version >= len(self.versions):
                raise IndexError("Version index out of range")
            tree_to_visualize = self.versions[version]

        dot = Digraph()
        if tree_to_visualize:
            q = Queue()
            q.put(tree_to_visualize)
            while not q.empty():
                node = q.get()
                dot.node(str(id(node)), str(node.key))
                if node.left:
                    q.put(node.left)
                    dot.edge(str(id(node)), str(id(node.left)), label="L")
                if node.right:
                    q.put(node.right)
                    dot.edge(str(id(node)), str(id(node.right)), label="R")
        return dot

    def visualize_versions(self):
        dot = Digraph()
        for i, version in enumerate(self.versions):
            subgraph = Digraph(name=f"cluster_{i}")
            subgraph.attr(label=f"Version {i}")
            if version:
                q = Queue()
                q.put(version)
                while not q.empty():
                    node = q.get()
                    subgraph.node(str(id(node)), str(node.key))
                    if node.left:
                        q.put(node.left)
                        subgraph.edge(str(id(node)), str(id(node.left)), label="L")
                    if node.right:
                        q.put(node.right)
                        subgraph.edge(str(id(node)), str(id(node.right)), label="R")
            dot.subgraph(subgraph)
        return dot
