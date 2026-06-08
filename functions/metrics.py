import resource
import time
import logging
from functools import wraps


def _stats_footer(t_start, ru_before):
    ru_after = resource.getrusage(resource.RUSAGE_SELF)
    total_s = round(time.perf_counter() - t_start, 2)
    cpu_s = round(
        (ru_after.ru_utime + ru_after.ru_stime) -
        (ru_before.ru_utime + ru_before.ru_stime), 2
    )
    mem_mb = round(ru_after.ru_maxrss / 1024, 1)
    return f"\n\n⏱ {total_s}s  cpu {cpu_s}s  mem {mem_mb}MB"


def track_resources(func):
    """Decorator que mide tiempo, CPU y memoria de un handler y lo agrega al final del último mensaje."""
    @wraps(func)
    async def wrapper(update, context):
        ru_before = resource.getrusage(resource.RUSAGE_SELF)
        t_start = time.perf_counter()
        calls = []

        orig_reply = update.message.reply_text
        orig_send = context.bot.send_message

        async def buf_reply(*args, **kwargs):
            calls.append(('reply', list(args), dict(kwargs)))

        async def buf_send(*args, **kwargs):
            calls.append(('send', list(args), dict(kwargs)))

        patched = False
        try:
            update.message.reply_text = buf_reply
            context.bot.send_message = buf_send
            patched = True
        except (AttributeError, TypeError):
            logging.warning(f"track_resources: no se pudo parchear métodos para {func.__name__}")

        try:
            await func(update, context)
        finally:
            if patched:
                try:
                    update.message.reply_text = orig_reply
                except Exception:
                    pass
                try:
                    context.bot.send_message = orig_send
                except Exception:
                    pass

        if not patched or not calls:
            return

        footer = _stats_footer(t_start, ru_before)

        for i, (kind, args, kwargs) in enumerate(calls):
            is_last = (i == len(calls) - 1)
            if is_last:
                if kind == 'reply':
                    if args:
                        args[0] = str(args[0]) + footer
                    else:
                        kwargs['text'] = str(kwargs.get('text', '')) + footer
                else:
                    kwargs['text'] = str(kwargs.get('text', '')) + footer

            if kind == 'reply':
                await orig_reply(*args, **kwargs)
            else:
                await orig_send(*args, **kwargs)

    return wrapper
