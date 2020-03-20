import json, random
from datetime import datetime, timedelta
from swagger_client.models import BulkSignal


def get_order_info(order, field):
    '''
    Helper function to retrieve a certain value from the json object stored in an order's txt field.
    '''
    order_info = None
    if order and order.txt:
        try:
            data = json.loads(order.txt)
            order_info = data[field]
        except:
            pass
    return order_info


def get_signal_value(contract, source, signal_name):
    '''
    Retrieves the signals from the contract.
    '''
    if contract and contract.signals:
        for s in contract.signals:
            if s.source == source and signal_name in s.value:
                return s.value[signal_name]
    return None


def get_imbalance(contract):
    '''
    Helper function to calculate the imbalance based on the submitted long/short position signal.
    '''
    if contract and contract.signals:
        for s in contract.signals:
            if s.source == "POSITION":
                return s.position_long - s.position_short
    return 0


def create_signals(position_long, position_short, delivery_areas, portfolio_ids):
    '''
    Helper function to create signals, which later can be sent to PowerBot as input for the algorithm.
    '''
    delivery_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    delivery_end = delivery_start + timedelta(minutes=15)

    quarter_hour = 0

    signals = []

    while quarter_hour < 96:

        position_signal = BulkSignal(
            source="ETRMSystem",
            delivery_start=delivery_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
            delivery_end=delivery_end.strftime("%Y-%m-%dT%H:%M:%SZ"),
            portfolio_ids=portfolio_ids,
            delivery_areas=delivery_areas,
            position_long=position_long,
            position_short=position_short
        )

        fair_value_signal = BulkSignal(
            source="OptSystem",
            delivery_start=delivery_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
            delivery_end=delivery_end.strftime("%Y-%m-%dT%H:%M:%SZ"),
            portfolio_ids=portfolio_ids,
            delivery_areas=delivery_areas,
            value={
                "fair_value": round(random.uniform(30, 60), 2),
                "margin": round(random.uniform(0, 1), 2),
                "max_spread": round(random.uniform(20, 30), 2),
                "max_price": round(random.uniform(100, 150), 2),
                "min_price": round(random.uniform(0, 10), 2)
            }
        )

        signals.append(position_signal)
        signals.append(fair_value_signal)

        quarter_hour += 1

        delivery_start = delivery_end
        delivery_end = delivery_start + timedelta(minutes=15)

    return signals
