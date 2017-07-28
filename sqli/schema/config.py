import trafaret as T


CONFIG_SCHEMA = T.Dict({
    T.Key('db'): T.Dict({
        'user': T.String(),
        'password': T.String(),
        'host': T.String(),
        'port': T.Int(),
        'database': T.String(),
    }),
    T.Key('redis'): T.Dict({
        'host': T.String(),
        'port': T.Int(),
        'db': T.Int(),
    }),
    T.Key('app'): T.Dict({
        'host': T.String(),
        'port': T.Int(),
    }),
})
