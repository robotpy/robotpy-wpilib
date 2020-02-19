#include <tuple>

namespace rpy {

std::tuple<bool, bool, bool> GetControlState();
bool IsAutonomousEnabled();
bool IsOperatorControlEnabled();

}  // namespace rpy
