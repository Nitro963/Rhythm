import logging
from musicbot.bot import load_cogs, client

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    load_cogs()
    client.run('NzY3MDQ2MDUwOTYzNjUyNjQ4.X4sNTQ.9i_3xb5jTXOPPUeeQ-IaYYrw1jo')
