from funkwhale_api import plugins


plugins.hooks.register(
    plugins.Hook("history.listening.created", providing_args=["listening"])
)