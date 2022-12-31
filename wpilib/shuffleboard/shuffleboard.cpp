
#include "rpygen_wrapper.hpp"
#include "ShuffleboardData.h"

RPYBUILD_PYBIND11_MODULE(m)
{
    initWrapper(m);

    // ensure that the shuffleboard data is released when python shuts down
    static int unused; // the capsule needs something to reference
    py::capsule cleanup(&unused, [](void *) {
        rpy::destroyShuffleboardData();
    });
    m.add_object("_sbd_cleanup", cleanup);
    m.def("_clearShuffleboardData", &rpy::clearShuffleboardData);
}
