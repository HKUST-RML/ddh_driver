# Direct-Drive Hand Driver

The repository contains the driver and user interface to our [direct-drive hand](https://github.com/HKUST-RML/ddh_hardware).



# Install

1. Clone the repository

   ```shell
   git clone https://github.com/HKUST-RML/ddh_software
   ```

2. Install dependencies

   ```shell
   cd ddh_software
   pip3 install -r requirements.txt
   ```

3. Add `ddh_software` to `PYTHONPATH`. If you are using Jupyter, the simpliest way is to add the following lines at the begining of the notebook.

   ```python
   import sys
   sys.path.append('path to ddh_software')
   import pyddh
   ```



# Getting Started

After assembling the direct-drive gripper by following the instructions in [ddh_hardware](https://github.com/HKUST-RML/ddh_hardware), run [tutorial.ipynb](https://github.com/HKUST-RML/pyddh/blob/master/examples/tutorial.ipynb) for a simple example. Comprehensive examples can be found in [APIs.ipynb](https://github.com/HKUST-RML/pyddh/blob/master/examples/APIs.ipynb).



# Utilities



### Calibrate ODrive

```shell
python3 -m ddh_driver.odrive_calib
```

This command is only used during hardware assembly, please check the [ddh_hardware](https://github.com/HKUST-RML/ddh_hardware) page for its usage.



### Check Raw Encoder Readings

```shell
python3 -m ddh_driver.check_encoder
```

This command will print the raw real-time readings from the 4 encoders. Unit is revolution, 1.0 means rotated 360 degrees.



### Check Rotor Positions

```shell
python3 -m ddh_driver.check_motor_pos
```

This command will print the rotational position of the four actuators. Unit is degrees. It requires calibrating the zero position of the motors. Please refer to the  [ddh_hardware](https://github.com/HKUST-RML/ddh_hardware) page for more details.



### Check Proximal Link Positions

```shell
python3 -m ddh_driver.check_theta
```

This command will print the rotational position of the four proximal links. Unit is degrees.



### Real-time Data Visualization via PlotJuggler

1. Install PlotJuggler

   ```shell
   snap install plotjuggler
   ```

2. Install dependencies

   ```shell
   conda install -c conda-forge liblsl
   ```

3. Enable `data_streamer` in your code

   ```python
   from pyddh.lsl_streamer import LslStreamer
   streamer = LslStreamer(gripper_object)
   streamer.enabled = True
   ```

4. Launch `PlotJuggler` App and subscribe to the `ddh` channel



## Maintenance
For any technical issues, please contact Pu Xu (pxuaf@connect.ust.hk) and Ka Hei Mak (khmakac@connect.ust.hk)
