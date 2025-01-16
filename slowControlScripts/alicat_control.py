import asyncio
from alicat import FlowController

async def get():
    async with FlowController('ip-address:/dev/ttyUSB1') as flow_controller:
        print(await flow_controller.get())

asyncio.run(get())
