
#pragma once

#include <frc/smartdashboard/Sendable.h>
#include <robotpy_build.h>

namespace rpy {

//
// These functions must be called with the GIL held
//

void addSmartDashboardData(py::str &key, std::shared_ptr<frc::Sendable> data);
void clearSmartDashboardData();

} // namespace rpy