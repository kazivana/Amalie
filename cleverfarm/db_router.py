from .models import *

ROUTED_MODELS = [Sensors, Swp, Tmp, Hum, Prs, Rnf, Lfw, Wns, Wng, Wnd]


class CFRouter(object):
    def db_read(self, model, **hints):
        if model in ROUTED_MODELS:
            return 'cleverfarm'
        return None

    def db_write(self, model, **hints):
        if model in ROUTED_MODELS:
            return 'cleverfarm'
        return None