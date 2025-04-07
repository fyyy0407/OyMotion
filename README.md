# OyMotion
## Environment Requirement
```python
python==3.10
bleak==0.22.3
numpy==1.26.4
pymodbus==3.7.2
pyserial==3.5
```
## Connection
### Robot Hand
everytime restart, run the following code.
```/dev/ttyUSB0``` is the COM_PORT of the robot hand
```python
sudo chmod 777 /dev/ttyUSB0
```
change the ```COM_PORT``` and ```NODE_ID``` for different device
```python
COM_PORT = "/dev/ttyUSB0"
NODE_ID = 2  # default value
```
change the resolution to modify the preciseness of control
```python
# sample resolution:BITS_8 or BITS_12
SAMPLE_RESOLUTION = 8
```
### Glove
press the bottom for 3 seconds until the green light shoots every 2 seconds
```python
# Device filters
DEV_NAME_PREFIX = ""  # filter device
DEV_MIN_RSSI = -128  # signal strength threshold
```

## Usage
* API for Robot Hand is in ```ROHand.py```
* API for Glove is in ```Glove.py```
