# This file is part of the stock_update_planned_date module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from datetime import datetime
from trytond.pool import Pool, PoolMeta
from trytond.model import ModelView, fields
from trytond.transaction import Transaction
from trytond.wizard import Wizard, StateView, StateTransition, Button
from sql.operators import Or

__all__ = ['Configuration', 'Move', 'UpdatePlannedDateStart',
    'UpdatePlannedDate', 'Cron']


class Cron(metaclass=PoolMeta):
    __name__ = 'ir.cron'

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls.method.selection.extend([
            ('stock.move|update_configured_planned_date', 'Update Planned Date'),
        ])

class Configuration(metaclass=PoolMeta):
    __name__ = 'stock.configuration'
    update_shipment_out = fields.Boolean('Update Planned Dates of '
        'Customer Shipments')
    update_shipment_in = fields.Boolean('Update Planned Dates of '
        'Supplier Shipments')
    update_shipment_internal = fields.Boolean('Update Planned Dates of '
        'Internal Shipments')
    update_move_out = fields.Boolean('Update Planned Dates of Sales Moves')
    update_move_in = fields.Boolean('Update Planned Dates of Purchase Moves')
    update_move_shipment = fields.Boolean('Update Planned of Dates Moves')


class Move(metaclass=PoolMeta):
    __name__ = 'stock.move'

    @classmethod
    def renew_move_planned_date(cls, origins, date=None):
        Date_ = Pool().get('ir.date')

        move = cls.__table__()
        cursor = Transaction().connection.cursor()

        if not date:
            date = Date_.today()

        origs = [move.shipment.like(o + ',%') for o in origins]

        for field in ['planned_date', 'effective_date']:
            if origs:
                sql_where = (
                    ~move.state.in_(['cancel', 'done'])
                    & (getattr(move, field) < date) & Or ( origs ))
            else:
                sql_where = (
                    ~move.state.in_(['cancel', 'done'])
                    & (getattr(move, field) < date))

            # move.select(move.id, where=sql_where)
            cursor.execute(*move.update(
                    columns=[getattr(move, field), move.write_date],
                    values=[date, datetime.now()],
                    where=sql_where))

    @classmethod
    def renew_shipment_planned_date(cls, shipment_types, date=None):
        'Renew planned date and effective date'
        pool = Pool()
        Date_ = Pool().get('ir.date')
        ShipmentOut = pool.get('stock.shipment.out')
        ShipmentOutReturn = pool.get('stock.shipment.out.return')
        ShipmentIn = pool.get('stock.shipment.in')
        ShipmentInReturn = pool.get('stock.shipment.in.return')
        ShipmentInternal = pool.get('stock.shipment.internal')

        shipment_out = ShipmentOut.__table__()
        shipment_out_return = ShipmentOutReturn.__table__()
        shipment_in = ShipmentIn.__table__()
        shipment_in_return = ShipmentInReturn.__table__()
        shipment_internal = ShipmentInternal.__table__()
        cursor = Transaction().connection.cursor()

        if not date:
            date = Date_.today()

        # shipment out
        if 'stock.shipment.out' in shipment_types:
            for shipment_th in [shipment_out, shipment_out_return]:
                for field in ['planned_date', 'effective_date']:
                    sql_where = (
                        ~shipment_th.state.in_(['cancel', 'done']) & (
                            getattr(shipment_th, field) < date))
                    cursor.execute(*shipment_th.update(
                            columns=[
                                getattr(shipment_th, field),
                                getattr(shipment_th, 'write_date'),
                                ],
                            values=[date, datetime.now()],
                            where=sql_where))

        # shipment in
        if 'stock.shipment.in' in shipment_types:
            for shipment_th in [shipment_in, shipment_in_return]:
                for field in ['planned_date', 'effective_date']:
                    sql_where = (
                        ~shipment_th.state.in_(['cancel', 'done']) & (
                            getattr(shipment_th, field) < date))
                    cursor.execute(*shipment_th.update(
                            columns=[
                                getattr(shipment_th, field),
                                getattr(shipment_th, 'write_date'),
                                ],
                            values=[date, datetime.now()],
                            where=sql_where))

        # shipment internal
        if 'stock.shipment.internal' in shipment_types:
            for field in ['planned_date', 'effective_date']:
                sql_where = (
                    ~shipment_internal.state.in_(['cancel', 'done']) & (
                        getattr(shipment_internal, field) < date))
                cursor.execute(*shipment_internal.update(
                        columns=[
                            getattr(shipment_internal, field),
                            getattr(shipment_internal, 'write_date'),
                            ],
                        values=[date, datetime.now()],
                        where=sql_where))

    @classmethod
    def update_planned_date(cls, date=None):
        'Update planned date of moves and shipments as configured'
        pool = Pool()
        Date_ = pool.get('ir.date')
        Configuration = pool.get('stock.configuration')

        conf = Configuration(1)
        if not date:
            date = Date_.today()

        # stock.shipment
        shipment_types = []
        if conf.update_shipment_out:
            shipment_types.append('stock.shipment.out')
        if conf.update_shipment_in:
            shipment_types.append('stock.shipment.in')
        if conf.update_shipment_internal:
            shipment_types.append('stock.shipment.internal')
        if shipment_types:
            cls.renew_shipment_planned_date(shipment_types, date=date)

        # stock.move
        origins = []
        if conf.update_move_in:
            origins.append('purchase.line')
        if conf.update_move_out:
            origins.append('sale.line')
        if conf.update_move_shipment:
            origins.append('stock.shipment.out')
            origins.append('stock.shipment.out.return')
            origins.append('stock.shipment.in')
            origins.append('stock.shipment.in.return')
            origins.append('stock.shipment.internal')
        cls.renew_move_planned_date(origins, date=date)


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
        Move = Pool().get('stock.move')

        Move.update_planned_date(self.start.date)
        return 'end'
