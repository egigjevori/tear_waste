from abc import ABC

import asyncpg


class Repository(ABC):

    def __init__(self, conn: asyncpg.Connection):
        self.conn = conn
