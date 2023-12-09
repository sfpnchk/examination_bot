import functools

from .base import Session, session_context


def session_decorator(
    db_session=Session, expire_on_commit: bool = False, add_param: bool = False
):
    """
    Decorator with parameter for async session usage.

    Usage example:

    @session_decorator(Session)
    async def resolve_query_escalation_reasons(
        session,
        parent: Optional[Any],
        args: Dict[str, Any],
        ctx: Dict[str, Any],
        info: ResolveInfo,
    ) -> Optional[Dict[str, Any]]:
        pass
    """

    def decorated_get_session(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            async with db_session(expire_on_commit=expire_on_commit) as session:
                async with session.begin():
                    token = session_context.set(session)
                    try:
                        if add_param:
                            args = list(args)
                            args.insert(0, session)
                        return await func(*args, **kwargs)
                    finally:
                        session_context.reset(token)

        return wrapper

    return decorated_get_session
