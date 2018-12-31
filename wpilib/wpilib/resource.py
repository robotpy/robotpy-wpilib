# validated: 2017-11-21 EN b65447b6f5a8 edu/wpi/first/wpilibj/Resource.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

import weakref
from typing import Optional

__all__ = ["Resource"]


class Resource:
    """Tracks resources in the program.
    
    The Resource class is a convenient way of keeping track of allocated
    arbitrary resources in the program. Resources are just indices that
    have an lower and upper bound that are tracked by this class. In the
    library they are used for tracking allocation of hardware channels
    but this is purely arbitrary. The resource class does not do any actual
    allocation, but simply tracks if a given index is currently in use.

    .. not_implemented: restartProgram
    """

    _resource_objects = []
    _global_resources = []

    @staticmethod
    def _reset() -> None:
        """
            This clears all resources in the program and calls free() on any
            objects that have a free method.
        """

        for resource in Resource._resource_objects:

            # free all the resources, if a free method is defined
            for ref in resource.numAllocated:
                if ref is None:
                    continue
                obj = ref()
                if obj is not None:
                    if hasattr(obj, "close"):
                        obj.close()
                    elif hasattr(obj, "free"):
                        obj.free()

            resource.numAllocated = [None] * len(resource.numAllocated)
        for ref in Resource._global_resources:
            obj = ref()
            if obj is not None:
                if hasattr(obj, "close"):
                    obj.close()
                elif hasattr(obj, "free"):
                    obj.free()
        del Resource._global_resources[:]

    @staticmethod
    def _add_global_resource(obj: object) -> None:
        Resource._global_resources.append(weakref.ref(obj))

    def __init__(self, size: int) -> None:
        """Allocate storage for a new instance of Resource.
        Allocate a bool array of values that will get initialized to
        indicate that no resources have been allocated yet. The indices
        of the resources are 0..size-1.

        :param size: The number of blocks to allocate
        """
        Resource._resource_objects.append(self)
        self.numAllocated = [None] * size

    def allocate(self, obj: object, index: Optional[int] = None) -> int:
        """Allocate a resource.

        When index is None or unspecified, a free resource value within the
        range is located and returned after it is marked allocated.
        Otherwise, it is verified unallocated, then returned.

        :param obj: The object requesting the resource.
        :param index: The resource to allocate
        :returns: The index of the allocated block.
        :raises IndexError: If there are no resources available to be
            allocated or the specified index is already used.
        """
        if index is None:
            for i in range(len(self.numAllocated)):
                r = self.numAllocated[i]
                if r is None or r() is None:
                    self.numAllocated[i] = weakref.ref(obj)
                    return i
            raise IndexError("No available resources")

        if index >= len(self.numAllocated) or index < 0:
            raise IndexError("Index %d out of range" % index)
        r = self.numAllocated[index]
        if r is not None and r() is not None:
            raise IndexError("Resource at index %d already allocated" % index)
        self.numAllocated[index] = weakref.ref(obj)
        return index

    def free(self, index: int) -> None:
        """Force-free an allocated resource.
        After a resource is no longer needed, for example a destructor is
        called for a channel assignment class, free will release the resource
        value so it can be reused somewhere else in the program.

        :param index: The index of the resource to free.
        """
        self.numAllocated[index] = None
