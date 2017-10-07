import math
from atlasbuggy import Robot, AsyncStream
from atlasbuggy.subscriptions import *
from atlasbuggy.plotters import RobotPlot, LivePlotter

from babybuggy import BabyBuggySerial


class SensorPlotter(AsyncStream):
    def __init__(self, enabled=True):
        super(ImuPlotter, self).__init__(enabled)

        self.serial_manager = None
        self.serial_manager_tag = "serial"
        self.require_subscription(self.serial_manager_tag, Subscription, BabyBuggySerial)

        self.l = 1

        self.imu_plot = RobotPlot("imu output", x_range=[-self.l, self.l], y_range=[-self.l, self.l])
        self.gps_plot = RobotPlot("gps output")

    def take(self, subscriptions):
        self.serial_manager = subscriptions[self.serial_manager_tag].get_stream()

    async def run(self):
        while self.is_running():
            angle = -self.serial_manager.imu.euler.z
            x0 = self.l * math.cos(angle)
            y0 = self.l * math.sin(angle)

            x1 = -self.l * math.cos(angle)
            y1 = -self.l * math.sin(angle)

            latitude = self.serial_manager.gps.latitude_deg
            longitude = self.serial_manager.gps.longitude_deg

            self.imu_plot.update([x0, x1], [y0, y1])
            self.gps_plot.append(latitude, longitude)

            await asyncio.sleep(0.01)


robot = Robot(write=False)

serial_manager = BabyBuggySerial()
sensor_plotter = SensorPlotter()

plotter = LivePlotter(2, sensor_plotter.imu_plot, sensor_plotter.gps_plot, default_resize_behavior=False)

sensor_plotter.subscribe(Subscription(sensor_plotter.serial_manager_tag, serial_manager))

robot.run(serial_manager, plotter, sensor_plotter)
