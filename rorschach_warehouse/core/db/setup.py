import os

from alembic import command
from alembic.config import Config

database_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
ini_location = os.path.join(database_root, "alembic.ini")


def run_migrations():
    """
    Run database migrations using Alembic.

    This needs to happen synchronously, before the asyncio
    mainloop is started, and before any database access.

    :param config: Database configuration.
    """

    # url = _async_to_sync_db_scheme(alembic_cfg.url)
    # ini_location = join(dirname(__file__), "alembic.ini")

    alembic_cfg = Config(ini_location)
    alembic_cfg.set_main_option(
        "sqlalchemy.url", ""
    )
    alembic_cfg.set_main_option("script_location", "rocky/core/db/migrations")
    alembic_cfg.set_main_option("prepend_sys_path", ".")
    alembic_cfg.set_main_option(
        "version_locations", "rocky/core/db/migrations/versions"
    )
    alembic_cfg.set_main_option("version_path_separator", ":")

    # alembic_cfg.set_main_option("pythagora_runtime", "true")
    if command.check(alembic_cfg):
        print(command.check(alembic_cfg))
        # command.revision(alembic_cfg, autogenerate=True, message="initial")
        # command.upgrade(alembic_cfg, "head")


__all__ = ["run_migrations"]
