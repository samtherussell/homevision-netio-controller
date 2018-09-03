# HomeVision NetIO Controller

A python api for controlling a homevision system via the netio interface.

The commands are sent over the a socket to the netio server running in HomeVision XL.

## Quick Start:

Download from [PyPI](https://pypi.org/project/homevision-netio-controller):
```bash
pip install homevision-netio-controller
```

Usage:
```python
from homevision_netio_controller import HomeVisionController, Macro

actions = {
  "HOT WATER 1 HOUR": Macro(42)
}

controller = HomeVisionController("192.168.1.100", 9999, "f498m0M9j87Hj743RgK8HI", actions = actions)

controller.action_command({"command": "HOT WATER 1 HOUR"})
```

##Links

For more information on NetIO visit it's [homepage](https://netioapp.com/en/)

For more information on NetIO Homevision plugin visit the [website](http://hv.tclcode.com/netio.html)

For more information on further commands see the help pages of the plugin.
