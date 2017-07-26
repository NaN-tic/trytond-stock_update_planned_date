# This file is part of the stock_update_planned_date module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from .shipment import *


def register():
    Pool.register(
        Move,
        ShipmentOut,
        UpdatePlannedDateStart,
        StockConfiguration,
        module='stock_update_planned_date', type_='model')
    Pool.register(
        UpdatePlannedDate,
        module='stock_update_planned_date', type_='wizard')
