/*----------------------------------------------------------------------------*/
/* Copyright (c) 2008-2019 FIRST. All Rights Reserved.                        */
/* Open Source Software - may be modified and shared by FRC teams. The code   */
/* must be accompanied by the FIRST BSD license file in the root directory of */
/* the project.                                                               */
/*----------------------------------------------------------------------------*/

#include "rpy/Notifier.h"

#include <utility>

#include <hal/FRCUsageReporting.h>
#include <hal/Notifier.h>
#include <wpi/SmallString.h>

#include "frc/Timer.h"
#include "frc/Utility.h"
#include "frc/WPIErrors.h"

using namespace frc;
using namespace pybind11::literals;

PyNotifier::PyNotifier(std::function<void()> handler) {
  if (handler == nullptr)
    wpi_setWPIErrorWithContext(NullParameter, "handler must not be nullptr");
  m_handler = handler;
  int32_t status = 0;
  m_notifier = HAL_InitializeNotifier(&status);
  wpi_setHALError(status);

  std::function<void()> target([=] {
    py::gil_scoped_release release;
    for (;;) {
      int32_t status = 0;
      HAL_NotifierHandle notifier = m_notifier.load();
      if (notifier == 0)
        break;
      uint64_t curTime = HAL_WaitForNotifierAlarm(notifier, &status);
      if (curTime == 0 || status != 0)
        break;

      std::function<void()> handler;
      {
        std::scoped_lock lock(m_processMutex);
        handler = m_handler;
        if (m_periodic) {
          m_expirationTime += m_period;
          UpdateAlarm();
        } else {
          // need to update the alarm to cause it to wait again
          UpdateAlarm(UINT64_MAX);
        }
      }

      // call callback
      if (handler)
        handler();
    }
  });

  // create a python thread and start it
  auto Thread = py::module::import("threading").attr("Thread");
  m_thread = Thread("target"_a = target, "daemon"_a = true,
                    "name"_a = "notifier-thread");
  m_thread.attr("start")();
}

PyNotifier::~PyNotifier() {
  int32_t status = 0;
  // atomically set handle to 0, then clean
  HAL_NotifierHandle handle = m_notifier.exchange(0);
  HAL_StopNotifier(handle, &status);
  wpi_setHALError(status);

  // Join the thread to ensure the handler has exited.
  if (m_thread)
    m_thread.attr("join")();

  HAL_CleanNotifier(handle, &status);
}

PyNotifier::PyNotifier(PyNotifier &&rhs)
    : ErrorBase(std::move(rhs)), m_thread(std::move(rhs.m_thread)),
      m_notifier(rhs.m_notifier.load()), m_handler(std::move(rhs.m_handler)),
      m_expirationTime(std::move(rhs.m_expirationTime)),
      m_period(std::move(rhs.m_period)), m_periodic(std::move(rhs.m_periodic)) {
  rhs.m_notifier = HAL_kInvalidHandle;
}

PyNotifier &PyNotifier::operator=(PyNotifier &&rhs) {
  ErrorBase::operator=(std::move(rhs));

  m_thread = std::move(rhs.m_thread);
  m_notifier = rhs.m_notifier.load();
  rhs.m_notifier = HAL_kInvalidHandle;
  m_handler = std::move(rhs.m_handler);
  m_expirationTime = std::move(rhs.m_expirationTime);
  m_period = std::move(rhs.m_period);
  m_periodic = std::move(rhs.m_periodic);

  return *this;
}

void PyNotifier::SetName(const wpi::Twine &name) {
  wpi::SmallString<64> nameBuf;
  int32_t status = 0;
  HAL_SetNotifierName(m_notifier,
                      name.toNullTerminatedStringRef(nameBuf).data(), &status);
}

void PyNotifier::SetHandler(std::function<void()> handler) {
  std::scoped_lock lock(m_processMutex);
  m_handler = handler;
}

void PyNotifier::StartSingle(double delay) {
  StartSingle(units::second_t(delay));
}

void PyNotifier::StartSingle(units::second_t delay) {
  std::scoped_lock lock(m_processMutex);
  m_periodic = false;
  m_period = delay.to<double>();
  m_expirationTime = Timer::GetFPGATimestamp() + m_period;
  UpdateAlarm();
}

void PyNotifier::StartPeriodic(double period) {
  StartPeriodic(units::second_t(period));
}

void PyNotifier::StartPeriodic(units::second_t period) {
  std::scoped_lock lock(m_processMutex);
  m_periodic = true;
  m_period = period.to<double>();
  m_expirationTime = Timer::GetFPGATimestamp() + m_period;
  UpdateAlarm();
}

void PyNotifier::Stop() {
  int32_t status = 0;
  HAL_CancelNotifierAlarm(m_notifier, &status);
  wpi_setHALError(status);
}

void PyNotifier::UpdateAlarm(uint64_t triggerTime) {
  int32_t status = 0;
  // Return if we are being destructed, or were not created successfully
  auto notifier = m_notifier.load();
  if (notifier == 0)
    return;
  HAL_UpdateNotifierAlarm(notifier, triggerTime, &status);
  wpi_setHALError(status);
}

void PyNotifier::UpdateAlarm() {
  UpdateAlarm(static_cast<uint64_t>(m_expirationTime * 1e6));
}
