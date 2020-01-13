/*----------------------------------------------------------------------------*/
/* Copyright (c) 2016-2018 FIRST. All Rights Reserved.                        */
/* Open Source Software - may be modified and shared by FRC teams. The code   */
/* must be accompanied by the FIRST BSD license file in the root directory of */
/* the project.                                                               */
/*----------------------------------------------------------------------------*/

#include "rpy/SpeedControllerGroup.h"

#include "frc/smartdashboard/SendableBuilder.h"

using namespace frc;


void PySpeedControllerGroup::Set(double speed) {
  for (auto speedController : m_speedControllers) {
    speedController->Set(m_isInverted ? -speed : speed);
  }
}

double PySpeedControllerGroup::Get() const {
  if (!m_speedControllers.empty()) {
    return m_speedControllers.front()->Get() * (m_isInverted ? -1 : 1);
  }
  return 0.0;
}

void PySpeedControllerGroup::SetInverted(bool isInverted) {
  m_isInverted = isInverted;
}

bool PySpeedControllerGroup::GetInverted() const { return m_isInverted; }

void PySpeedControllerGroup::Disable() {
  for (auto speedController : m_speedControllers) {
    speedController->Disable();
  }
}

void PySpeedControllerGroup::StopMotor() {
  for (auto speedController : m_speedControllers) {
    speedController->StopMotor();
  }
}

void PySpeedControllerGroup::PIDWrite(double output) { Set(output); }

void PySpeedControllerGroup::InitSendable(frc::SendableBuilder& builder) {
  builder.SetSmartDashboardType("Speed Controller");
  builder.SetActuator(true);
  builder.SetSafeState([=]() { StopMotor(); });
  builder.AddDoubleProperty("Value", [=]() { return Get(); },
                            [=](double value) { Set(value); });
}
