"""
Powerbot helper functions
(c) 2019 Inercomp GmbH
"""

import json
import random
from swagger_client.models import OrderModify, OrderModifyItem, BulkSignal
from datetime import datetime, timedelta

from swagger_client.rest import ApiException


def get_signal_value(contract, source, signal_name):
    """
    Helper function to retrieve the signal information for a certain source and signal key.

    :param contract: The contract for which to extract the signal information
    :param source: The name of the source.
    :param signal_name: The key of the signal.
    :return:
    """

    if contract and contract.signals:
        for s in contract.signals:
            if s.source == source and signal_name in s.value:
                return s.value[signal_name]

    return None


def get_previous_values(order):
    """
    Helper function to retrieve values from the previous iteration stored as JSON in the text field of an order.

    :param order: The order for which to extract the information.
    :return: Tuple(order_type, prev_hour_counter, prev_marginal_price)
    """

    order_type = None
    prev_hour_counter = None
    prev_marginal_price = None
    if order and order.txt:
        try:
            data = json.loads(order.txt)
            order_type = data['type']
            prev_hour_counter = data['hour_counter']
            prev_marginal_price = data['marginal_price']
        except:
            pass
    return order_type, prev_hour_counter, prev_marginal_price


def get_position_info(contract):
    """
    Helper function to extract the position signal information from a contract.

    :param contract: The contract for which to extract the position info.
    :return: Tuple(position_long, position_short)
    """

    if contract and contract.signals:
        for s in contract.signals:
            if s.source == "POSITION":
                return s.position_long, s.position_short

    return None, None


def delete_orders(orders_api, to_be_deleted, contract_id, portfolio_id, delivery_area):
    """
    This method will first try to delete all orders in the list [to_be_deleted].
    If this fails because an order in the list no longer exists or beacause it has been partially executed (revision number changed)
    retry the deletion process (max 3 times).

    :param orders_api: The orders api client created in the main file, which we reuse here to directly communicate with PowerBot.
    :param to_be_deleted: The initial list of orders, which shall be deleted. If the deletion fails, then this list is cleared and updated with newly fetched orders.
    :param contract_id: The id of the contract which we want to delete.
    :param portfolio_id: The portfolio in which the algorithm is active.
    :param delivery_area: The delivery area in which the algorithm is active.
    """

    max_tries = 3
    retry_counter = 0
    retry = True

    while retry and retry_counter < max_tries:
        try:
            if len(to_be_deleted) > 0:
                modify_items = []
                for order in to_be_deleted:
                    modify_item = OrderModifyItem(
                        order_id=order.order_id,
                        revision_no=order.revision_no,
                        changes=OrderModify(
                            action="DELE"
                        )
                    )

                    modify_items.append(modify_item)

                # With this call we can modify multiple orders at once.

                orders_api.modify_orders(modifications=modify_items)
            retry = False
        except ApiException as exception:
            # Check the http status code that PowerBot sent as response.
            # 400: may occur when, an order we want to delete no longer exists.
            # 409: may occur when, the backend has another revision number then the one we submitted with OrdrModify.
            # This happens when an order is partially executed.
            # In this case retry the deletion process (max. 3 times), which means we have to again fetch all orders.
            if exception.status in (400, 409):
                retry_counter += 1
                own_orders = orders_api.get_own_orders(contract_id=contract_id, portfolio_id=[portfolio_id], delivery_area=delivery_area)
                # Delete all orders in our list and add the updated ones.
                # We will now retry to delete these updated orders.
                to_be_deleted.clear()
                for order in own_orders:
                    order_type, _, _ = get_previous_values(order)
                    if order_type == "demo":
                        to_be_deleted.append(order)
            else:
                # In case another ApiException occurred and we want to stop the execution.
                raise


def create_signals(delivery_areas, portfolio_ids, position_long=False, position_short=False):
    """
    Helper function to create signals, which later can be sent to PowerBot as input for the algorithm.
    Note that this is a very simple implementation of the signals logic, with the only purpose to showcase certain functionalities.
    Normally, one would have a separate program that is completely independent of the algorithm(s).
    This program would then connect to the various data sources (database, csv files, external APIs etc.) and extract relevant information from there.
    Instead of fixed/random values for position long/short and marginal price, we then could submit the dynamically extracted values from the various
    data sources as trade signals that our algorithm is interested in.

    :param position_long: Boolean flag that indicates whether or not to set a random position_long value.
    :param position_short: Boolean flag that indicates whether or not to set a random position_short value.
    :param delivery_areas: List of delivery areas the signal shall be valid for (if no delivery area is explicitly specified,
                            then the signal is valid for all delivery areas that the submitting api key has access to).
    :param portfolio_ids: List of portfolio ids the signal shall be valid for (if no portfolio id is explicitly specified,
                            then the signal is valid for all portfolios the submitting api key has access to).
    :return: List of signals
    """

    # Set the delivery start/end time according to the contract for which the signal shall be valid for.
    # The timespan between delivery start/end is set to be 1 hour, because the algorithm will only trade hourly contracts.
    delivery_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    delivery_end = delivery_start + timedelta(hours=1)

    signals = []

    # We iterate over every hour of today and tomorrow (at EPEX the contracts for the next day are available after 3pm) and create new signals.
    hour = 0
    while hour <= 48:

        # Position long/short is a special kind of signal information and can't be combined with further key/value pairs in the "value" field.
        position_signal = BulkSignal(
            # The source is a simple string and can be chosen arbitrarily.
            source="ETRMSystem",
            # It is important to understand that the PowerBot server works with UTC time (as do the exchanges)!
            delivery_start=delivery_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
            delivery_end=delivery_end.strftime("%Y-%m-%dT%H:%M:%SZ"),
            portfolio_ids=portfolio_ids,
            delivery_areas=delivery_areas,
            # If the respective flags are set, we want to create random position values.
            position_long=random.randint(1, 10) if position_long else 0,
            position_short=random.randint(1, 10) if position_short else 0
        )

        # We can create another signal with the same timestamp as the above to add further signal information to the same contract.
        # Normally you would want to separate different signals according to their category/data source.
        fair_value_signal = BulkSignal(
            source="OptSystem",
            delivery_start=delivery_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
            delivery_end=delivery_end.strftime("%Y-%m-%dT%H:%M:%SZ"),
            portfolio_ids=portfolio_ids,
            delivery_areas=delivery_areas,
            # We can add an arbitrary number of key/value pairs to the "value" field.
            value={
                "marginal_price": round(random.uniform(30, 60), 2),
            }
        )

        signals.append(position_signal)
        signals.append(fair_value_signal)

        hour += 1

        delivery_start = delivery_end
        delivery_end = delivery_start + timedelta(hours=1)

    return signals
