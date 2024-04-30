import sys
import os


class PatriciaNode:
    """
    Class representing a node in a Patricia tree.

    Attributes:
        key: The key of the node.
        value: The value of the node.
        index: The index of the node.
        children: The children of the node.

    Methods:
        insert: Inserts a key-value pair into the tree.
        search: Searches for a key in the tree.
        print: Prints the tree.
    """

    def __init__(self, key, value, index):
        """
        Constructor for PatriciaNode.

        Args:
            key: The key of the node.
            value: The value of the node.
            index: The index of the node.
        """
        self.key = key
        self.value = value
        self.index = index
        self.children = []

    def insert(self, key, value, index):
        """
        Inserts a key-value pair into the tree.

        Args:
            key: The key to insert.
            value: The value to insert.
            index: The index to insert.
        """
        if self.key == key:
            # If the key is the same as the node key, update the value
            self.value = value
            self.index = index
        else:
            i = 0
            while i < len(self.key) and i < len(key) and self.key[i] == key[i]:
                i += 1  # Find the first different character
            if i == len(self.key):  # If the key is a prefix of the node key
                if i == len(key):
                    # If the key is the same as the node key, update the value
                    self.value = value
                    self.index = index
                else:
                    # Search in the children
                    found = False
                    for child in self.children:
                        if child.key[0] == key[i]:
                            # Insert in the child with the rest of the key
                            child.insert(key[i:], value, index)
                            found = True
                            break
                    if not found:
                        # If no child is found, insert a new child
                        self.children.append(PatriciaNode(key[i:], value, index))
            else:  # If the key is not a prefix of the node key
                # Split the node into two nodes
                new_node = PatriciaNode(self.key[i:], self.value, self.index)
                new_node.children = self.children
                # Update the node
                self.key = self.key[:i]
                self.value = None
                self.index = None
                # Insert the new node and the new key
                self.children = [new_node]
                if i < len(key):
                    self.children.append(PatriciaNode(key[i:], value, index))

    def search(self, key):
        """
        Searches for a key in the tree.

        Args:
            key: The key to search.

        Returns:
            The value of the key if found, None otherwise.
        """
        if self.key == key:  # If the key is the same as the node key
            return self.value
        else:
            i = 0
            while i < len(self.key) and i < len(key) and self.key[i] == key[i]:
                i += 1  # Find the first different character
            if i == len(self.key):  # If the key is a prefix of the node key
                for child in self.children:  # Search in the children
                    # If the first character of the child key is the same as the next character of the key
                    if child.key[0] == key[i]:
                        # Search in the child with the rest of the key
                        return child.search(key[i:])
                # If no child is found, return None
                return None
            else:
                # If the key is not a prefix of the node key, return None
                return None

    def print(self, indent):
        """
        Function to print the tree.

        Args:
            indent: The indentation to print.
        """
        print(indent + self.key + " " + str(self.value) + " " + str(self.index))
        for child in self.children:
            child.print(indent + "  ")


class PatriciaTree:
    """
    Class representing a Patricia tree.

    Attributes:
        root: The root node of the tree.

    Methods:
        insert: Inserts a key-value pair into the tree.
        search: Searches for a key in the tree.
        print: Prints the tree.
    """

    def __init__(self):
        """
        Constructor for PatriciaTree.
        """
        self.root = PatriciaNode("", None, None)

    def insert(self, key, value, index):
        """
        Inserts a key-value pair into the tree.

        Args:
            key: The key to insert.
            value: The value to insert.
            index: The index to insert.
        """
        self.root.insert(key, value, index)

    def search(self, key):
        """
        Searches for a key in the tree.

        Args:
            key: The key to search.

        Returns:
            The value of the key if found, None otherwise.
        """
        return self.root.search(key)

    def print(self):
        """
        Function to print the tree.
        """
        self.root.print("")


def read_file(file_name):
    """
    Function to read a file.

    Args:
        file_name: The name of the file to read.

    Returns:
        A list of lines in the file.
    """
    with open(file_name, "r") as file:
        return file.read().splitlines()


def patricia_intersection(file1, file2):
    """
    Function to find the intersection of two files using Patricia tree.

    Args:
        file1: The first file.
        file2: The second file.

    Returns:
        The number of common lines between the two files.
    """
    lines1 = read_file(file1)
    lines2 = read_file(file2)
    patricia = PatriciaTree()
    for i, line in enumerate(lines1):  # Insert all lines of the first file into the Patricia tree
        patricia.insert(line, i, None)
    result = 0
    for i, line in enumerate(lines2):  # Search all lines of the second file in the Patricia tree
        if patricia.search(line) is not None:
            result += 1
    return result


def main():
    if len(sys.argv) != 3:
        print("Usage: python patricia.py file1 file2")
        sys.exit(1)
    file1 = sys.argv[1]
    file2 = sys.argv[2]
    if not os.path.isfile(file1):
        print("File " + file1 + " does not exist")
        sys.exit(1)
    if not os.path.isfile(file2):
        print("File " + file2 + " does not exist")
        sys.exit(1)
    result = patricia_intersection(file1, file2)
    print("Intersection: " + str(result))


if __name__ == "__main__":
    main()
