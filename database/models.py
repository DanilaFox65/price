import sqlalchemy as sa
from sqlalchemy import Column, String, Integer, ForeignKey, TIMESTAMP, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

convention = {
  "ix": "ix_%(column_0_label)s",
  "uq": "%(table_name)s_%(column_0_name)s_key",
  "ck": "ck_%(table_name)s_%(constraint_name)s",
  "fk": "%(table_name)s_%(column_0_name)s_fkey",
  "pk": "%(table_name)s_pkey",
}

metadata = sa.MetaData(naming_convention=convention)

Base = declarative_base(metadata=metadata)

NOW_AT_UTC = sa.text("timezone('utc', now())")


class TimestampMixin:
  """
  Миксин для добавления временных меток создания и обновления записи.

  Атрибуты:
  ----------
  :param created_at: время создания записи.
  :type datetime.datetime
  :param updated_at: время обновления записи.
  :type datetime.datetime
  """

  created_at = Column(
    sa.TIMESTAMP(timezone=False), server_default=NOW_AT_UTC, nullable=False
  )
  updated_at = Column(
    sa.TIMESTAMP(timezone=False),
    server_default=NOW_AT_UTC,
    nullable=False,
    onupdate=NOW_AT_UTC,
  )


class SoftDeleteMixin:
  """
  Миксин для добавления пометки об удалении записи.

  Атрибуты:
  ----------
  :param deleted_at: время удаления записи.
  :type datetime.datetime
  """

  deleted_at = Column(sa.TIMESTAMP(timezone=False), nullable=True, index=True)


class User(Base, TimestampMixin, SoftDeleteMixin):
  """
    Модель пользователя

    Таблица: users
  """
  __tablename__ = 'users'

  id: int = Column(Integer, primary_key=True, autoincrement=True)
  username: str = Column(String, nullable=False)
  password_hash: str = Column(String, nullable=False)
  phone: str = Column(String, nullable=False)
  refresh_token: str = Column(String, nullable=True)


class Shop(Base, TimestampMixin, SoftDeleteMixin):
  """
    Модель магазина

    Таблица: shops
  """
  __tablename__ = 'shops'

  id: int = Column(Integer, primary_key=True)
  name: str = Column(String, nullable=False)
  description: str = Column(String, nullable=True)
  address: str = Column(String, nullable=False)

  products_in_store = relationship("ProductsInStore", back_populates="shop")


class ProductCategory(Base, TimestampMixin, SoftDeleteMixin):
  """
    Модель категорий продуктов

    Таблица: product_categories
  """
  __tablename__ = 'product_categories'

  id: int = Column(Integer, primary_key=True)
  name: str = Column(String, nullable=False)
  description: str = Column(String, nullable=True)

  products = relationship("Product", back_populates="category")


class Product(Base, TimestampMixin, SoftDeleteMixin):
  """
    Модель продукта

    Таблица: products
  """
  __tablename__ = 'products'

  id: int = Column(Integer, primary_key=True)
  name: str = Column(String, nullable=False)
  description: str = Column(String, nullable=True)
  category_id: int = Column(
    Integer,
    ForeignKey("product_categories.id", onupdate="CASCADE", ondelete="CASCADE"),
    nullable=False,
  )

  category = relationship("ProductCategory", back_populates="products")
  products_in_store = relationship("ProductsInStore", back_populates="product")


class ProductsInStore(Base, TimestampMixin, SoftDeleteMixin):
  """
    Модель товаров в магазине

    Таблица: products_in_store
  """
  __tablename__ = 'products_in_store'

  id: int = Column(Integer, primary_key=True)
  product_id: int = Column(
    Integer,
    ForeignKey("products.id", onupdate="CASCADE", ondelete="CASCADE"),
    nullable=False,
  )
  shop_id: int = Column(
    Integer,
    ForeignKey("shops.id", onupdate="CASCADE", ondelete="CASCADE"),
    nullable=False,
  )
  price: int = Column(Integer, nullable=False)

  product = relationship("Product", back_populates="products_in_store")
  shop = relationship("Shop", back_populates="products_in_store")
