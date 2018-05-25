# validated: 2018-09-30 EN 0614913f1abb edu/wpi/first/wpilibj/NidecBrushless.java
# ----------------------------------------------------------------------------
#  Copyright (c) 2017 FIRST. All Rights Reserved.
#  Open Source Software - may be modified and shared by FRC teams. The code
#  must be accompanied by the FIRST BSD license file in the root directory of
#  the project.
# ----------------------------------------------------------------------------
import hal

from .digitaloutput import DigitalOutput
from .interfaces.speedcontroller import SpeedController
from .motorsafety import MotorSafety
from .pwm import PWM
from .sendablebase import SendableBase
from .sendablebuilder import SendableBuilder


__all__ = ["NidecBrushless"]


class NidecBrushless(SendableBase, MotorSafety, SpeedController):
    """Nidec Brushless Motor"""

    def __init__(self, pwmChannel: int, dioChannel: int) -> None:
        """
        :param pwmChannel: The PWM channel that the Nidec Brushless controller is attached to.
                0-9 are on-board, 10-19 are on the MXP port
        :param dioChannel: The DIO channel that the Nidec Brushless controller is attached to.
                0-9 are on-board, 10-25 are on the MXP port
        """
        super().__init__()
        self.dio = DigitalOutput(dioChannel)
        self.addChild(self.dio)
        self.dio.setPWMRate(15625)
        self.dio.enablePWM(0.5)

        self.pwm = PWM(pwmChannel)
        self.addChild(self.pwm)

        MotorSafety.__init__(self)
        self.speed = 0.0
        self.isInverted = False
        self.disabled = False

        hal.report(hal.UsageReporting.kResourceType_NidecBrushless, pwmChannel)
        self.setName("Nidec Brushless", pwmChannel)

    def close(self) -> None:
        """Free the resources used by this object."""
        super().close()
        self.dio.close()
        self.pwm.close()

    def set(self, speed: float) -> None:
        """ 
        Set the PWM value.
    
        The PWM value is set using a range of -1.0 to 1.0, appropriately scaling the value for the FPGA.

        :param speed: The speed value between -1.0 and 1.0 to set.
        """
        if not self.disabled:
            self.speed = speed
            self.dio.updateDutyCycle(0.5 + 0.5 * (-speed if self.isInverted else speed))
            self.pwm.setRaw(0xFFFF)
        self.feed()

    def get(self) -> float:
        """
        Get the recently set value of the PWM.  

        :returns: The most recently set value for the PWM between -1.0 and 1.0.
        """
        return self.speed

    def setInverted(self, isInverted: bool) -> None:
        """
        """
        self.isInverted = isInverted

    def getInverted(self) -> bool:
        return self.isInverted

    def pidWrite(self, output: float) -> None:
        """ 
        Write out the PID value as seen in the PIDOutput base object. 

        :param output: Write out the PWM value as was found in the PIDController
        """
        self.set(output)

    def stopMotor(self) -> None:
        """
        Stop the motor. This is called by the MotorSafetyHelper object
        when it has a timeout for this PWM and needs to stop it from running.
        Calling :meth:`set` will re-enable the motor.
        """
        self.dio.updateDutyCycle(0.5)
        self.pwm.setDisabled()

    def getDescription(self) -> str:
        return "Nidec %s" % (self.getChannel(),)

    def disable(self) -> None:
        """
        Disable the motor.  The :meth:`enable` function must be called to re-enable
        the motor.
        """
        self.disabled = True
        self.dio.updateDutyCycle(0.5)
        self.pwm.setDisabled()

    def enable(self) -> None:
        """
        Re-enable the motor after :meth:`disable` has been called.  
        The :meth:`set` function must be called to set a new motor speed.
        """
        self.disabled = False

    def getChannel(self) -> int:
        """
        Gets the channel number associated with the object.

        :returns: The channel number.
        """
        return self.pwm.getChannel()

    def initSendable(self, builder: SendableBuilder) -> None:
        builder.setSmartDashboardType("Nidec Brushless")
        builder.setActuator(True)
        builder.setSafeState(self.stopMotor)
        builder.addDoubleProperty("Value", self.get, self.set)
