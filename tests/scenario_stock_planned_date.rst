==========================
Stock Update Date Scenario
==========================

Imports::

    >>> import datetime
    >>> from dateutil.relativedelta import relativedelta
    >>> from decimal import Decimal
    >>> from proteus import config, Model, Wizard
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company
    >>> today = datetime.date.today()
    >>> yesterday = today - relativedelta(days=1)
    >>> tomorrow = today + relativedelta(days=1)

Create database::

    >>> config = config.set_trytond()
    >>> config.pool.test = True

Install stock Module::

    >>> Module = Model.get('ir.module')
    >>> module, = Module.find([('name', '=', 'stock_update_planned_date')])
    >>> module.click('install')
    >>> Wizard('ir.module.install_upgrade').execute('upgrade')

Create company::

    >>> _ = create_company()
    >>> company = get_company()

Reload the context::

    >>> User = Model.get('res.user')
    >>> config._context = User.get_preferences(True, config.context)

Create customer::

    >>> Party = Model.get('party.party')
    >>> customer = Party(name='Customer')
    >>> customer.save()
    >>> supplier = Party(name='Supplier')
    >>> supplier.save()

Create category::

    >>> ProductCategory = Model.get('product.category')
    >>> category = ProductCategory(name='Category')
    >>> category.save()

Create product::

    >>> ProductUom = Model.get('product.uom')
    >>> ProductTemplate = Model.get('product.template')
    >>> Product = Model.get('product.product')
    >>> unit, = ProductUom.find([('name', '=', 'Unit')])
    >>> product = Product()
    >>> template = ProductTemplate()
    >>> template.name = 'Product'
    >>> template.category = category
    >>> template.default_uom = unit
    >>> template.type = 'goods'
    >>> template.list_price = Decimal('20')
    >>> template.cost_price = Decimal('8')
    >>> template.save()
    >>> product.template = template
    >>> product.save()

Get stock locations::

    >>> Location = Model.get('stock.location')
    >>> warehouse_loc, = Location.find([('code', '=', 'WH')])
    >>> supplier_loc, = Location.find([('code', '=', 'SUP')])
    >>> customer_loc, = Location.find([('code', '=', 'CUS')])
    >>> output_loc, = Location.find([('code', '=', 'OUT')])
    >>> storage_loc, = Location.find([('code', '=', 'STO')])

Stock Configuration::

    >>> Config = Model.get('stock.configuration')
    >>> config = Config(1)
    >>> config.update_shipment_out = True
    >>> config.save()

Stock Move::

    >>> StockMove = Model.get('stock.move')
    >>> incoming_move = StockMove()
    >>> incoming_move.product = product
    >>> incoming_move.uom = unit
    >>> incoming_move.quantity = 1
    >>> incoming_move.from_location = supplier_loc
    >>> incoming_move.to_location = storage_loc
    >>> incoming_move.planned_date = yesterday
    >>> incoming_move.effective_date = yesterday
    >>> incoming_move.company = company
    >>> incoming_move.unit_price = Decimal('100')
    >>> incoming_move.currency = company.currency
    >>> incoming_move.save()
    >>> incoming_move2 = StockMove()
    >>> incoming_move2.product = product
    >>> incoming_move2.uom = unit
    >>> incoming_move2.quantity = 1
    >>> incoming_move2.from_location = supplier_loc
    >>> incoming_move2.to_location = storage_loc
    >>> incoming_move2.planned_date = tomorrow
    >>> incoming_move2.effective_date = tomorrow
    >>> incoming_move2.company = company
    >>> incoming_move2.unit_price = Decimal('100')
    >>> incoming_move2.currency = company.currency
    >>> incoming_move2.save()

Create Shipment Out::

    >>> ShipmentOut = Model.get('stock.shipment.out')
    >>> shipment_out = ShipmentOut()
    >>> shipment_out.planned_date = yesterday
    >>> shipment_out.customer = customer
    >>> shipment_out.warehouse = warehouse_loc
    >>> shipment_out.company = company

Add two shipment lines of same product::

    >>> StockMove = Model.get('stock.move')
    >>> shipment_out.outgoing_moves.extend([StockMove(), StockMove()])
    >>> for move in shipment_out.outgoing_moves:
    ...     move.product = product
    ...     move.uom =unit
    ...     move.quantity = 1
    ...     move.from_location = output_loc
    ...     move.to_location = customer_loc
    ...     move.company = company
    ...     move.unit_price = Decimal('1')
    ...     move.currency = company.currency
    >>> shipment_out.save()
    >>> shipment_out.click('wait')

Create Shipment Out 2::

    >>> shipment_out2 = ShipmentOut()
    >>> shipment_out2.planned_date = tomorrow
    >>> shipment_out2.effective_date = yesterday
    >>> shipment_out2.customer = customer
    >>> shipment_out2.warehouse = warehouse_loc
    >>> shipment_out2.company = company

Add two shipment lines of same product::

    >>> StockMove = Model.get('stock.move')
    >>> shipment_out2.outgoing_moves.extend([StockMove(), StockMove()])
    >>> for move in shipment_out2.outgoing_moves:
    ...     move.product = product
    ...     move.uom =unit
    ...     move.quantity = 1
    ...     move.from_location = output_loc
    ...     move.to_location = customer_loc
    ...     move.company = company
    ...     move.unit_price = Decimal('1')
    ...     move.currency = company.currency
    >>> shipment_out2.save()
    >>> shipment_out2.click('wait')

Update planned/effective date::

    >>> wdate = Wizard('stock.update.planned.date')
    >>> wdate.execute('update_planned_date')

    >>> shipment_out.reload()
    >>> shipment_out.planned_date == today
    True
    >>> shipment_out2.reload()
    >>> shipment_out2.planned_date == tomorrow
    True
    >>> shipment_out2.effective_date == today
    True
    >>> move1, move2 = shipment_out.outgoing_moves
    >>> move1.planned_date == today
    True
    >>> incoming_move.reload()
    >>> incoming_move.planned_date == today
    True
    >>> incoming_move2.reload()
    >>> incoming_move2.planned_date == tomorrow
    True
