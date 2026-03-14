from librouteros import connect

def connect_router(router):

    api = connect(
        host=router.ip_address,
        username=router.username,
        password=router.password
    )

    return api