import os

pkg_dir = r"e:\proooo\Atlas\python\atlas\src\atlas\realtime\websocket"
files = [
    "__init__.py",
    "enums.py",
    "settings.py",
    "auth.py",
    "connection.py",
    "registry.py",
    "subscriptions.py",
    "dispatcher.py",
    "gateway.py",
    "protocol.py",
    "backpressure.py",
    "errors.py",
    "router.py",
]

for f in files:
    path = os.path.join(pkg_dir, f)
    if not os.path.exists(path):
        with open(path, "w") as fp:
            fp.write('"""\n"""\n')

print("Created empty files.")
