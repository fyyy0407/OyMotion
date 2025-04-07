from Glove import *
from ROHand import *

async def main():
    NODE_ID=2
    COM_PORT="/dev/ttyUSB0"
    client = ROHand(COM_PORT,NODE_ID)
    client.connect()
    glove_ctrl = Glove()
    await glove_ctrl.connect_gforce_device()

    await glove_ctrl.calib(False)
    print("finish calib\n")
    client.reset()
    
    while not glove_ctrl.terminated:
        glove_ctrl.get_pos()
        resp = client.set_finger_pos(ROH_FINGER_POS_TARGET0, glove_ctrl.finger_data,NODE_ID)

    await glove_ctrl.gforce_device.stop_streaming()
    await glove_ctrl.gforce_device.disconnect()
    

if __name__ == "__main__":
    asyncio.run(main())
