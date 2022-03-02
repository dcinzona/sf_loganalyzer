from Operations.Operation import Operation
# LIFO Stack implementation using a linked list
# as its underlying storage


class OperationStack:
    # ----------------------Nested Node Class ----------------------

    # This Node class stores a piece of data (element) and
    # a reference to the Next node in the Linked List
    class Node:
        def __init__(self, e: Operation):
            self.element = e
            self.next = None   # reference to the next Node

# ---------------------- stack methods -------------------------
    # Create an empty stack
    def __init__(self):
        self._size = 0
        # reference to head node (top of stack)
        self.head = None

    # Add element e to the top of the stack.
    def push(self, e: Operation):
        # New node inserted at Head
        newest = self.Node(e)
        newest.next = self.head
        self.head = newest
        self._size += 1

    # Remove and return the element from the top of the stack
    # (i.e., LIFO). Raise exception if the stack is empty.
    def pop(self) -> Operation:
        if self.is_empty():
            raise IndexError('Stack is empty')

        elementToReturn = self.head.element
        self.head = self.head.next
        self._size -= 1

        return elementToReturn

    # Return (but do not remove) the element at the top of
    # the stack. Raise Empty exception if the stack is empty.
    def peek(self) -> Operation:
        if self.is_empty():
            raise IndexError('Stack is empty')
        return self.head.element

    # Return True if the stack is empty.
    def is_empty(self) -> bool:
        return self._size == 0

    # Return the number of elements in the stack.
    def size(self) -> int:
        return self._size
