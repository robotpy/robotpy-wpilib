/*----------------------------------------------------------------------------*/
/* Copyright (c) 2016-2019 FIRST. All Rights Reserved.                        */
/* Open Source Software - may be modified and shared by FRC teams. The code   */
/* must be accompanied by the FIRST BSD license file in the root directory of */
/* the project.                                                               */
/*----------------------------------------------------------------------------*/

#pragma once

#include <functional>
#include <vector>
#include <memory>


#include "frc/SpeedController.h"
#include "frc/smartdashboard/Sendable.h"
#include "frc/smartdashboard/SendableHelper.h"

namespace frc {

class PySpeedControllerGroup : public Sendable,
                             public SpeedController,
                             public SendableHelper<PySpeedControllerGroup> {
 public:
  PySpeedControllerGroup(std::vector<std::shared_ptr<frc::SpeedController>> &&args) :
    m_speedControllers(args) {}
  ~PySpeedControllerGroup() override = default;

  PySpeedControllerGroup(PySpeedControllerGroup&&) = default;
  PySpeedControllerGroup& operator=(PySpeedControllerGroup&&) = default;

  void Set(double speed) override;
  double Get() const override;
  void SetInverted(bool isInverted) override;
  bool GetInverted() const override;
  void Disable() override;
  void StopMotor() override;
  void PIDWrite(double output) override;

  void InitSendable(SendableBuilder& builder) override;

 private:
  bool m_isInverted = false;
  std::vector<std::shared_ptr<frc::SpeedController>> m_speedControllers;
};

}  // namespace rpy
