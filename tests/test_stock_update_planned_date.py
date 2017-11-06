# This file is part of the stock_update_planned_date module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase


class StockUpdatePlannedDateTestCase(ModuleTestCase):
    'Test Stock Update Planned Date module'
    module = 'stock_update_planned_date'


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        StockUpdatePlannedDateTestCase))
    return suite
