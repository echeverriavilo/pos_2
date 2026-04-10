from contextlib import contextmanager
import threading

_thread_locals = threading.local()


def set_current_tenant(tenant):
    _thread_locals.tenant = tenant


def get_current_tenant():
    return getattr(_thread_locals, 'tenant', None)


def clear_current_tenant():
    if hasattr(_thread_locals, 'tenant'):
        del _thread_locals.tenant


@contextmanager
def tenant_scope(tenant):
    previous = get_current_tenant()
    set_current_tenant(tenant)
    try:
        yield
    finally:
        if previous is None:
            clear_current_tenant()
        else:
            set_current_tenant(previous)
