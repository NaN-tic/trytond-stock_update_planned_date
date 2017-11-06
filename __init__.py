# This file is part of the stock_update_planned_date module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from . import shipment


def register():
    Pool.register(
        shipment.Configuration,
        shipment.Move,
        shipment.UpdatePlannedDateStart,
        module='stock_update_planned_date', type_='model')
    Pool.register(
        shipment.UpdatePlannedDate,
        module='stock_update_planned_date', type_='wizard')
