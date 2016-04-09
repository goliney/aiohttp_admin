import yaml
import motor.motor_asyncio as aiomotor


def load_config(fname):
    with open(fname, 'rt') as f:
        data = yaml.load(f)
    # TODO: add config validation
    return data


async def init_mongo(conf, loop):
    url = "mongodb://{}:{}".format(conf['host'], conf['port'])
    db = conf['database']
    client = aiomotor.AsyncIOMotorClient(
        url, max_pool_size=conf['max_pool_size'], io_loop=loop)
    await client.open()
    return client[db]
