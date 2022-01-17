# `pyddh`

`pyddh` is the python dirver and software utilities for our in-house direct-drive hand.



# Install

1. Clone the repository

   ```shell
   git clone git@github.com:HKUST-RML/pyddh.git
   ```

2. Install depenencies

   ```shell
   cd pyddh
   pip3 install -r requirements.txt
   ```

3. Add `pyddh` to `PYTHONPATH`. If you are using Jupyter, the simpliest way is to add the following lines at the begining of the notebook.

   ```python
   import sys
   sys.path.append('path to pyddh')
   import pyddh
   ```



# Getting Started

First you need to assemble and calibrate the grippr following the instruction in [ddh_hardware]().

See  `examples/hello-world.ipynb` for a simple example.



# API

```python
from from pyddh import DDGripper
```

Connect to the gripper using `config/ddh_default.yaml`.

```python
gripper = DDGripper('ddh_default')
```

Arm and disarm the gripper.

```python
gripper.arm(gain=250,BW=500)  # gain and bandwidth optional
gripper.disarm()
```



### Control Individual Actuator

Control individual actuator, the same applies to `R0`, `R1`, `L0`, `L1`

```python
gripper.R0.armed = False
gripper.R0.armed = True
gripper.R0.bandwidth = 500
gripper.R0.stiffness = 250

# Read and write the linkage angle theta, unit is degrees
print(gripper.R0.theta)
gripper.R0.theta = 45

# Read and write the motor position, unit is degrees
print(gripper.R0.motor_pos)
gripper.motor_pos = 0

# Read the raw encoder raeding
print(gripper.R0.encoder)
```



### Control Finger

```python
# Control link angles directly
gripper.R0.theta = xxx
gripper.R1.theta = xxx

# Control using alpha1-alpha2 parameterization
print(gripper.right_a1)
print(gripper.right_a2)
gripper.set_right_a1_a1(10,10)
gripper.set_right_a1(10)
gripper.set_right_a2(10)
```

