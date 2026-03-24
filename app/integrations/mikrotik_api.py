import asyncssh


class MikroTikSSH:
    def __init__(self, host, username, password, port=22, timeout=10):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.timeout = timeout
        self.conn = None

    async def connect(self):
        self.conn = await asyncssh.connect(
            self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            known_hosts=None,
            login_timeout=self.timeout,
            kex_algs=[
                'diffie-hellman-group14-sha1',
                'diffie-hellman-group1-sha1'
            ],
            encryption_algs=[
                'aes128-ctr',
                'aes192-ctr',
                'aes256-ctr'
            ],
            server_host_key_algs=['ssh-rsa']
        )

    async def run(self, command):
        result = await self.conn.run(command)
        return result.stdout, result.stderr

    async def close(self):
        if self.conn:
            self.conn.close()
            await self.conn.wait_closed()