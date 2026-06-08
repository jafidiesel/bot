import resource
import time
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


class _MessageProxy:
    __slots__ = ('_msg', '_calls')

    def __init__(self, msg, calls):
        object.__setattr__(self, '_msg', msg)
        object.__setattr__(self, '_calls', calls)

    async def reply_text(self, *args, **kwargs):
        self._calls.append(('reply', list(args), dict(kwargs)))

    def __getattr__(self, name):
        return getattr(self._msg, name)


class _BotProxy:
    __slots__ = ('_bot', '_calls')

    def __init__(self, bot, calls):
        object.__setattr__(self, '_bot', bot)
        object.__setattr__(self, '_calls', calls)

    async def send_message(self, *args, **kwargs):
        self._calls.append(('send', list(args), dict(kwargs)))

    def __getattr__(self, name):
        return getattr(self._bot, name)


class _UpdateProxy:
    __slots__ = ('_update', '_msg_proxy')

    def __init__(self, update, calls):
        object.__setattr__(self, '_update', update)
        object.__setattr__(self, '_msg_proxy', _MessageProxy(update.message, calls))

    @property
    def message(self):
        return self._msg_proxy

    def __getattr__(self, name):
        return getattr(self._update, name)


class _ContextProxy:
    __slots__ = ('_ctx', '_bot_proxy')

    def __init__(self, ctx, calls):
        object.__setattr__(self, '_ctx', ctx)
        object.__setattr__(self, '_bot_proxy', _BotProxy(ctx.bot, calls))

    @property
    def bot(self):
        return self._bot_proxy

    def __getattr__(self, name):
        return getattr(self._ctx, name)


def track_resources(func):
    """Mide tiempo, CPU y memoria de un handler y lo agrega al final del último mensaje."""
    @wraps(func)
    async def wrapper(update, context):
        ru_before = resource.getrusage(resource.RUSAGE_SELF)
        t_start = time.perf_counter()
        calls = []

        update_p = _UpdateProxy(update, calls)
        context_p = _ContextProxy(context, calls)

        await func(update_p, context_p)

        if not calls:
            return

        footer = _stats_footer(t_start, ru_before)

        orig_reply = update.message.reply_text
        orig_send = context.bot.send_message

        for i, (kind, args, kwargs) in enumerate(calls):
            if i == len(calls) - 1:
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
