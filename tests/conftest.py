"""
Shared test setup: register the codec once for the whole session.
"""

import t61codec

# codecs.register() cannot be undone on all supported Python versions,
# so the codec is registered once, at import time.
t61codec.register()
