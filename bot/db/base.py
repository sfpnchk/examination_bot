import contextvars
import json
from typing import Any, Dict, Iterator, Optional, Tuple, Union

from sqlalchemy import BigInteger, Column, DateTime, MetaData, func, inspect, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker


class SessionProxy:
    def __init__(self, contextvar):
        self._contextvar = contextvar

    def __getattr__(self, attr):
        context = self._contextvar.get()
        assert context
        return getattr(context, attr)


convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)
Model = declarative_base(metadata=metadata)
Session = sessionmaker(class_=AsyncSession)

session_context = contextvars.ContextVar("session")
current_session = SessionProxy(session_context)


async def db_disconnect():
    await Session.kw["bind"].dispose()


async def db_connect(database_uri, echo: bool = False):
    Session.configure(
        bind=create_async_engine(
            database_uri,
            echo=echo,
            json_serializer=json.dumps,
            json_deserializer=json.loads,
        )
    )


# Bases
class Base(Model):
    __abstract__ = True
    id = Column(BigInteger, primary_key=True, autoincrement=True)

    def to_dict(self) -> Dict[str, Any]:
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

    @classmethod
    async def get_or_create(
        cls, defaults: Optional[dict] = None, **kwargs
    ) -> Tuple[Model, bool]:
        if obj := await cls.get(None, None, **kwargs):
            return obj, False

        defaults = defaults or {}
        return await cls.create(**kwargs, **defaults), True

    @classmethod
    async def _get(cls, iter_pks: Union[Any, Iterator[Any]] = None, *args, **kwargs):
        if iter_pks is not None:
            if not isinstance(iter_pks, (tuple, list)):
                iter_pks = (iter_pks,)

            where = {
                pk.name: cond for pk, cond in zip(cls.__table__.primary_key, iter_pks)
            }
            kwargs.update(where)

        query = select(cls).filter_by(**kwargs).filter(*args).order_by(cls.id)
        result = await current_session.execute(query)
        return result

    @classmethod
    async def get(cls, iter_pks: Union[Any, Iterator[Any]], *args, **kwargs):
        result = await cls._get(iter_pks, *args, **kwargs)
        return result.scalars().one_or_none()

    @classmethod
    async def get_list(cls, *args, **kwargs):
        result = await cls._get(None, *args, **kwargs)
        return result.scalars().all()

    @classmethod
    async def create(cls, **kwargs) -> Model:
        obj = cls(**kwargs)

        current_session.add(obj)
        await current_session.flush()
        await current_session.refresh(obj)

        return obj

    async def update(self, **kwargs) -> Model:
        for key, value in kwargs.items():
            setattr(self, key, value)

        await current_session.flush()
        await current_session.refresh(self)
        return self

    async def delete(self) -> bool:
        await current_session.delete(self)
        return True

    @classmethod
    async def exists(cls, iter_pks: Union[tuple, list] = None, **kwargs) -> bool:
        """
        Check if instance exists.
        Args:
            iter_pks: primary keys in the current table (table may contains several pks)

        Returns:
            True if instance exists, else false.
        """
        if iter_pks is not None:
            if not isinstance(iter_pks, (tuple, list)):
                iter_pks = [iter_pks]
            where = {
                pk.name: cond for pk, cond in zip(cls.__table__.primary_key, iter_pks)
            }
            kwargs.update(where)

        query = select([1]).select_from(cls).filter_by(**kwargs).exists().select()
        return bool((await current_session.execute(query)).scalars().one())


class CreatedMixin(Model):
    __abstract__ = True

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UpdatedMixin(Model):
    __abstract__ = True

    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
