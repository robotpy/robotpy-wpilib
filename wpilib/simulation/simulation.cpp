
#include "rpygen_wrapper.hpp"

#ifndef __FRC_ROBORIO__

namespace frc::impl {
void ResetLiveWindow();
void ResetSmartDashboardInstance();
void ResetMotorSafety();
} // namespace frc::impl

namespace wpi::impl {
void ResetSendableRegistry();
} // namespace wpi::impl

void resetWpilibSimulationData() {
  frc::impl::ResetSmartDashboardInstance();
  frc::impl::ResetLiveWindow();
  frc::impl::ResetMotorSafety();
  wpi::impl::ResetSendableRegistry();
}

#else
void resetWpilibSimulationData() {}
#endif

RPYBUILD_PYBIND11_MODULE(m) {
  initWrapper(m);

  m.def("_resetWpilibSimulationData", &resetWpilibSimulationData,
        release_gil());
}
