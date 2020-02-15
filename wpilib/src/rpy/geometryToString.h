#include <string>

#include <frc/geometry/Rotation2d.h>
#include <frc/geometry/Translation2d.h>
#include <frc/geometry/Pose2d.h>

namespace rpy {

inline std::string toString(const frc::Rotation2d& self) {
  return "Rotation2d(" + std::to_string(self.Radians()()) + ")";
}

inline std::string toString(const frc::Translation2d& self) {
  return "Translation2d("
    "x=" + std::to_string(self.X()()) + ", "
    "y=" + std::to_string(self.Y()()) + ")";
}

inline std::string toString(const frc::Pose2d& self) {
  return "Pose2d("
    "translation=" + rpy::toString(self.Translation()) + ", "
    "rotation=" + rpy::toString(self.Rotation()) + ")";
}

}  // namespace rpy
