# validated: 2017-12-08 DV 85157a56c3a7 edu/wpi/first/wpilibj/filters/LinearDigitalFilter.java
# ----------------------------------------------------------------------------
#  Copyright (c) 2017 FIRST. All Rights Reserved.                             
#  Open Source Software - may be modified and shared by FRC teams. The code   
#  must be accompanied by the FIRST BSD license file in the root directory of 
#  the project.                                                               
# ----------------------------------------------------------------------------
import hal
from .digitaloutput import DigitalOutput
from .sendablebase import SendableBase
from .motorsafety import MotorSafety
from .pwm import PWM
from .interfaces.speedcontroller import SpeedController


__all__ = ['NidecBrushless']


class NidecBrushless(SendableBase, MotorSafety, SpeedController):
    def __init__(self, pwmChannel, dioChannel):
        """
        :param pwmChannel: The PWM channel that the Nidec Brushless controller is attached to.
                0-9 are on-board, 10-19 are on the MXP port
        :param dioChannel: The DIO channel that the Nidec Brushless controller is attached to.
                0-9 are on-board, 10-25 are on the MXP port
        """
        super().__init__()
        self.dio = DigitalOutput(dioChannel)
        self.dio.setPWMRate(15625)
        self.dio.enablePWM(0.5)

        self.pwm = PWM(pwmChannel)
        self.pwm.setRaw(0xffff)

        MotorSafety.__init__(self)
        self.speed = 0.0
        self.isInverted = False

        hal.report(hal.UsageReporting.kResourceType_NidecBrushless, pwmChannel)
        self.setName("Nidec Brushless", pwmChannel)

    def free(self):
        super().free()
        self.dio.free()
        self.pwm.free()

    def set(self, speed):
        """ 
        Set the PWM value.
    
        The PWM value is set using a range of -1.0 to 1.0, appropriately scaling the value for the FPGA.

       :param speed: The speed value between -1.0 and 1.0 to set.
        """
        self.speed = speed
        self.dio.updateDutyCycle(0.5 + 0.5 * (-speed if self.isInverted else speed))
        self.feed()

    def get(self):
        """
        Get the recently set value of the PWM.  

        :returns: The most recently set value for the PWM between -1.0 and 1.0. 
        :rtype: float
        """
        return self.speed

    def setInverted(self, isInverted):
        """
        :type isInverted: bool
        """
        self.isInverted = isInverted

    def getInverted(self):
        """
        :rtype: bool
        """
        return self.isInverted

    def pidWrite(self, output):
        """ 
        Write out the PID value as seen in the PIDOutput base object. 

        :param output: Write out the PWM value as was found in the PIDController
        :type output: float
        """
        self.set(output)

    def stopMotor(self):
        """
        Stop the motor. This is called by the MotorSafetyHelper object
        when it has a timeout for this PWM and needs to stop it from running.
        """
        self.disable()

    def getDescription(self):
        """
        :rtype: str
        """
        return "Nidec %s" % (self.getChannel(),)

    def disable(self):
        self.dio.updateDutyCycle(0.5)

    def getChannel(self):
        """
        Gets the channel number associated with the object.
        :returns: The channel number.
        :rtype: int
        """
        return self.pwm.getChannel()

    def initSendable(self, builder):
        builder.setSmartDashboardType("Nidec Brushless")
        builder.setSafeState(self.stopMotor)
        builder.addDoubleProperty("Value", self.get, self.set)
