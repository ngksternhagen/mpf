"""Hold coil ejector."""
from mpf.devices.ball_device.ball_device_ejector import BallDeviceEjector


class HoldCoilEjector(BallDeviceEjector):

    """Hold balls by enabling and releases by disabling a coil."""

    def eject_all_balls(self):
        """Eject all balls."""
        raise NotImplementedError()

    def __init__(self, ball_device):
        """Initialise hold coil ejector."""
        super().__init__(ball_device)
        self.hold_release_in_progress = False

        # handle hold_coil activation when a ball hits a switch
        for switch in self.ball_device.config['hold_switches']:
            self.ball_device.machine.switch_controller.add_switch_handler(
                switch_name=switch.name, state=1,
                ms=0,
                callback=self.hold)

    def eject_one_ball(self):
        """Eject one ball by disabling hold coil."""
        # TODO: wait for some time to allow balls to settle for
        #       both entrance and after a release

        self._disable_hold_coil()
        self.hold_release_in_progress = True

        # allow timed release of single balls and reenable coil after
        # release. Disable coil when device is empty
        self.ball_device.delay.add(name='hold_coil_release',
                                   ms=self.ball_device.config['hold_coil_release_time'],
                                   callback=self._hold_release_done)

    def _disable_hold_coil(self):
        self.ball_device.config['hold_coil'].disable()
        if self.ball_device.debug:
            self.ball_device.log.debug("Disabling hold coil. New "
                                       "balls: %s.", self.ball_device.balls)

    def hold(self, **kwargs):
        """Event handler for hold event."""
        del kwargs
        # do not enable coil when we are ejecting
        if self.hold_release_in_progress:
            return

        self._enable_hold_coil()

    def _enable_hold_coil(self):
        self.ball_device.config['hold_coil'].enable()
        if self.ball_device.debug:
            self.ball_device.log.debug("Enabling hold coil. New "
                                       "balls: %s.", self.ball_device.balls)

    def _hold_release_done(self):
        self.hold_release_in_progress = False

        # reenable hold coil if there are balls left
        if self.ball_device.balls > 0:
            self._enable_hold_coil()

    def ball_search(self, phase, iteration):
        """Run ball search."""
        self.ball_device.config['hold_coil'].pulse()
        return True
