# This file is part of the stock_update_planned_date module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool, PoolMeta
from trytond.model import ModelView, fields
from trytond.transaction import Transaction
from trytond.wizard import Wizard, StateView, StateTransition, Button


__all__ = ['Move', 'ShipmentOut', 'UpdatePlannedDateStart',
    'UpdatePlannedDate', 'StockConfiguration']


class Move:
    __metaclass__ = PoolMeta
    __name__ = 'stock.move'

    @classmethod
    def renew_planned_date(cls, args=None, date=None):
        pool = Pool()
        Date_ = Pool().get('ir.date')
        Period = pool.get('stock.period')

        if not date:
            date = Date_.today()

        domain = [
            ('state', 'in', ['draft', 'assigned']),
            ('planned_date', '<', date),
            ]
        if args and 'shipment' in args:
            domain.append(
                ('shipment', 'like', args + ',%'),
                )
        elif args and ('purchase.line' in args or 'sale.line' in args):
            domain.append(
                ('origin', 'like', args + ',%'),
                )

        periods = Period.search([
            ('state', '=', 'closed'),
            ], order=[('date', 'DESC')], limit=1)
        if periods:
            period, = periods
            domain.append(
                ('planned_date', '>', period.date),
                )
        with Transaction().set_user(1):
            moves = cls.search(domain)
            if moves:
                cls.write(moves, {'planned_date': date})

    @classmethod
    def update_configured_planned_date(cls):
        'Update planned date of move in and shipment out as configured'
        pool = Pool()
        ShipmentOut = pool.get('stock.shipment.out')
        Date = pool.get('ir.date')
        Configuration = pool.get('stock.configuration')
        configuration = Configuration(1)
        today = Date.today()

        if configuration.update_move_in:
            cls.renew_planned_date(args='purchase.line', date=today)
        if configuration.update_shipment_out:
            ShipmentOut.update_planned_date()


class ShipmentOut:
    __metaclass__ = PoolMeta
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
        Move.renew_planned_date(cls.__name__, date=date)

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


class StockConfiguration:
    __metaclass__ = PoolMeta
    __name__ = 'stock.configuration'

    update_shipment_out = fields.Boolean('Update Planned Dates of Customer '
        'Shipments')
    update_move_in = fields.Boolean('Update Planned Dates of Purchase '
        'Movements')
