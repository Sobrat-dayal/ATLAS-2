import os

# Ensure tests run in development/debug mode for full coverage
os.environ["ATLAS_ENV"] = "test"
os.environ["ATLAS_DEBUG"] = "true"
