from .base import *


MIGRATION_MODULES = {app: '%s.dev_migrations' % app for app in MIGRATE_APPS}
