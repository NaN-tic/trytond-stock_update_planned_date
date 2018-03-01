# This file is part of the stock_update_planned_date module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
try:
    from trytond.modules.stock_update_planned_date.tests.test_stock_update_planned_date import suite
except ImportError:
    from .test_stock_update_planned_date import suite

__all__ = ['suite']
