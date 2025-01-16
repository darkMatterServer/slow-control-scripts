import asyncio
from alicat import FlowController

async def get():
    async with FlowController('ip-address:/dev/bus/usb/005/005') as flow_controller:
        print(await flow_controller.get())

asyncio.run(get())
