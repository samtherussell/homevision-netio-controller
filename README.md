# HomeVision NetIO Controller

A python api for controlling a homevision system via the netio interface.

The commands are sent over the a socket to the netio server running in HomeVision XL.

How to use:

```python
from homevision_netio_controller import HomeVisionController, Macro

actions = {
  "HOT WATER 1 HOUR": Macro(42)
}

controller = HomeVisionController("192.168.1.100", 9999, "f498m0M9j87Hj743RgK8HI", actions = actions)

controller.action_command({"command": "HOT WATER 1 HOUR"})
```
