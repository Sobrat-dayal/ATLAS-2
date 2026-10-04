import re

with open("src/config/atlas-modules.ts", "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace("settingsNamespace: string;", "settingsNamespace: string;\n  requiredPermission: string;")

modules = [
  'home', 'markets', 'charts', 'watchlists', 'screeners', 'companies',
  'economics', 'news', 'research', 'maps', 'intelligence', 'options',
  'trading', 'portfolios', 'risk', 'ai', 'data', 'saved', 'workspaces', 'agents'
]

for m in modules:
    pattern = rf'(id: "{m}",[\s\S]*?settingsNamespace: "[^"]+",)'
    replacement = rf'\1\n    requiredPermission: "module.{m}.view",'
    code = re.sub(pattern, replacement, code, count=1)

with open("src/config/atlas-modules.ts", "w", encoding="utf-8") as f:
    f.write(code)
