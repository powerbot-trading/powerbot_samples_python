"""
This snippet is a collection of commands used to work with risk settings in PowerBot
"""

from swagger_client import TenantsApi, PortfoliosApi, RiskManagementSettings, CashLimit, PositionLimit, TradingArea, OtrLimit
# Importing generated client from configuration
from configuration import client


"""
Get Tenant’s Risk Settings
"""
TenantsApi(client).get_tenant_risk_management(id="TENANT_ID")


"""
Update Tenant’s Risk Settings (Requires Master API Key)
"""
# Set Trading Area
trd_areas = [TradingArea(exchange="EXCHANGE", delivery_area="DELIVERY_AREA")]

# Set Position Limit
pos_lims = [PositionLimit(exchange="EXCHANGE", delivery_area="DELIVERY_AREA", min_netpos_limit=-10, max_netpos_limit=10,
                          abspos_limit=20)]

# Set Cash Limits
cash_lims = []
# Positive
cash_lims.append(CashLimit(direction="POS", currency="EUR", limit=1000))
# Negative
cash_lims.append(CashLimit(direction="NEG", currency="EUR", limit=-1000))

# Set OTR Limit
otr_lims = [OtrLimit(exchange="EXCHANGE", delivery_area="DELIVERY_AREA", otr_limit=100)]

# Create Risk Limit Object
risk_settings = RiskManagementSettings(portfolio_id="TENANT_ID", trading_areas=trd_areas, position_limits=pos_lims,
                                       cash_limits=cash_lims, otr_limits=otr_lims)

# Post new Settings
TenantsApi(client).update_tenant_risk_management_settings(id="TENANT_ID", value=risk_settings)


"""
Get Portfolio’s Risk Settings
"""
PortfoliosApi(client).get_portfolio_risk_management_settings(id="PORTFOLIO_ID")


"""
Update Portfolio’s Risk Settings
"""
# Set Trading Area
trd_areas = [TradingArea(exchange="EXCHANGE", delivery_area="DELIVERY_AREA")]

# Set Position Limit
pos_lims = [PositionLimit(exchange="EXCHANGE", delivery_area="DELIVERY_AREA", min_netpos_limit=-10, max_netpos_limit=10,
                          abspos_limit=20)]

# Set Cash Limits
cash_lims = []
# Positive
cash_lims.append(CashLimit(direction="POS", currency="EUR", limit=1000))
# Negative
cash_lims.append(CashLimit(direction="NEG", currency="EUR", limit=-1000))

# Set OTR Limit
otr_lims = [OtrLimit(exchange="EXCHANGE", delivery_area="DELIVERY_AREA", otr_limit=100)]

# Create Risk Limit Object
risk_settings = RiskManagementSettings(portfolio_id="PORTFOLIO_ID", trading_areas=trd_areas, position_limits=pos_lims,
                                       cash_limits=cash_lims, otr_limits=otr_lims)

# Post new Settings
PortfoliosApi(client).update_portfolio_risk_management_settings(id="PORTFOLIO_ID", value=risk_settings)