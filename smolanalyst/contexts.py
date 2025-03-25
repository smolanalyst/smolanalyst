import matplotlib
from audit_hook import register_hook, activate_hook, deactivate_hook


class MatplotlibServerContext:
    def __enter__(self):
        self.original_matplot_lib_backed = matplotlib.get_backend()
        matplotlib.use("Agg")

    def __exit__(self, exc_type, exc_val, exc_tb):
        matplotlib.use(self.original_matplot_lib_backed)


class RestrictedWriteContext:
    def __enter__(self):
        register_hook()
        activate_hook()

    def __exit__(self, exc_type, exc_val, exc_tb):
        deactivate_hook()
