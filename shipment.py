# This file is part of the stock_update_planned_date module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool, PoolMeta
from trytond.model import ModelView, fields
from trytond.wizard import Wizard, StateView, StateTransition, Button
from trytond.transaction import Transaction
from sql import Cast, Literal
from sql.functions import Substring, Position
from sql.operators import Like

__all__ = ['ShipmentOut', 'UpdatePlannedDateStart', 'UpdatePlannedDate']
__metaclass__ = PoolMeta


class ShipmentOut:
    __name__ = 'stock.shipment.out'

    @classmethod
    def renew_planned_date(cls, date=None):
        'Renew planned date'
        pool = Pool()
        Date_ = Pool().get('ir.date')
        Period = pool.get('stock.period')
        Move = pool.get('stock.move')

        if not date:
            date = Date_.today()

        periods = Period.search([
            ('state', '=', 'closed'),
            ], order=[('date', 'DESC')], limit=1)

        # search shipment out
        domain = [
            ('state', 'in', ['draft', 'waiting', 'assigned']),
            ('planned_date', '<', date),
            ]
        if periods:
            period, = periods
            domain.append(
                ('planned_date', '>', period.date),
                )
        shipments = cls.search(domain)
        if shipments:
            cls.write(shipments, {'planned_date': date})

        # search moves shipment out
        domain = [
            ('state', 'in', ['draft', 'assigned']),
            ('planned_date', '<', date),
            ('shipment', 'like', 'stock.shipment.out,%'),
            ]
        if periods:
            period, = periods
            domain.append(
                ('planned_date', '>', period.date),
                )
        moves = Move.search(domain)
        if moves:
            Move.write(moves, {'planned_date': date})

    @classmethod
    def update_planned_date(cls, args=None):
        'Update planned date'
        Date = Pool().get('ir.date')

        cls.renew_planned_date(Date.today())


class UpdatePlannedDateStart(ModelView):
    'Update Planned Date Start'
    __name__ = 'stock.update.planned.date.start'
    date = fields.Date('Date', required=True)

    @staticmethod
    def default_date():
        Date = Pool().get('ir.date')
        return Date.today()


class UpdatePlannedDate(Wizard):
    'Update Planned Date'
    __name__ = 'stock.update.planned.date'
    start = StateView('stock.update.planned.date.start',
        'stock_update_planned_date.update_planned_date_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('OK', 'update_planned_date', 'tryton-ok', True),
            ])
    update_planned_date = StateTransition()

    def transition_update_planned_date(self):
        ShipmentOut = Pool().get('stock.shipment.out')

        ShipmentOut.renew_planned_date(self.start.date)
        return 'end'
