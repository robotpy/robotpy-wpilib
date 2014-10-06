#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import weakref

class Resource:
    """Track resources in the program.
    The Resource class is a convenient way of keeping track of allocated
    arbitrary resources in the program. Resources are just indicies that
    have an lower and upper bound that are tracked by this class. In the
    library they are used for tracking allocation of hardware channels
    but this is purely arbitrary. The resource class does not do any actual
    allocation, but simply tracks if a given index is currently in use.

    WARNING: this should only be statically allocated. When the program
    loads into memory all the static constructors are called. At that time
    a linked list of all the "Resources" is created.  Then when the program
    actually starts - in the Robot constructor, all resources are
    initialized.  This ensures that the program is restartable in memory
    without having to unload/reload.
    """

    resources = weakref.WeakSet()

    @staticmethod
    def restartProgram():
        """Clears all allocated resources"""
        for r in Resource.resources:
            if r is not None:
                for i in range(len(r.numAllocated)):
                    r.numAllocated[i] = False

    def __init__(self, size):
        """Allocate storage for a new instance of Resource.
        Allocate a bool array of values that will get initialized to
        indicate that no resources have been allocated yet. The indicies
        of the resources are 0..size-1.

        :param size: The number of blocks to allocate
        """
        self.numAllocated = [False]*size
        Resource.resources.add(self)

    def allocate(self, index=None):
        """Allocate a resource.

        When index is None or unspecified, a free resource value within the
        range is located and returned after it is marked allocated.
        Otherwise, it is verified unallocated, then returned.

        :param index: The resource to allocate
        :returns: The index of the allocated block.
        :raises IndexError: If there are no resources available to be
            allocated or the specified index is already used.
        """
        if index is None:
            for i in range(len(self.numAllocated)):
                if not self.numAllocated[i]:
                    self.numAllocated[i] = True
                    return i
            raise IndexError("No available resources")

        if index >= len(self.numAllocated) or index < 0:
            raise IndexError("Index %d out of range" % index)
        if self.numAllocated[index]:
            raise IndexError("Resource at index %d already allocated" % index)
        self.numAllocated[index] = True
        return index

    def free(self, index):
        """Free an allocated resource.
        After a resource is no longer needed, for example a destructor is
        called for a channel assignment class, Free will release the resource
        value so it can be reused somewhere else in the program.

        :param index: The index of the resource to free.
        """
        if not self.numAllocated[index]:
            raise IndexError("No resource available to be freed")
        self.numAllocated[index] = False
