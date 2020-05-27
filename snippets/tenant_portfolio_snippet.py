"""
This snippet is a collection of commands used to work with tenants & portfolios in PowerBot
"""

from swagger_client import TenantsApi, PortfoliosApi, NewTenant, NewPortfolio
# Importing generated client from configuration
from configuration import client

"""
List Tenants/ Portfolios
"""
# Tenants
TenantsApi(client).get_tenants()
# Portfolios
PortfoliosApi(client).get_portfolios()


"""
Create Tenant/ Portfolio
"""
# Tenants
tenant = NewTenant(id="TENANT_ID", name="TENANT_NAME", risk_management="RISK_LIMIT_OBJECT")
TenantsApi(client).add_tenant(tenant)
# Portfolios
portfolio = NewPortfolio(id="PORTFOLIO_ID", name="PORTFOLIO_NAME", tenant_id="TENANT_ID",
                         risk_management="RISK_LIMIT_OBJECT")
PortfoliosApi(client).add_portfolio(portfolio)


"""
Update Tenant/ Portfolio Information (Name only)
"""
# Tenants
TenantsApi(client).update_tenant(id="TENANT_ID", value="NEW_TENANT_NAME")
# Portfolios
PortfoliosApi(client).update_portfolio(id="PORTFOLIO_ID", value="NEW_PORTFOLIO_NAME")


"""
Get Risk Management Settings
"""
# Tenants
TenantsApi(client).get_tenant_risk_management()
# Portfolios
PortfoliosApi(client).get_portfolio_risk_management_settings()


"""
Change Risk Management Settings (see risk_management_snippet for Risk Limit Object)
"""
# Tenants
TenantsApi(client).update_tenant_risk_management_settings(id="TENANT_ID", value="NEW_RISK_LIMIT_OBJECT")
# Portfolios
PortfoliosApi(client).update_portfolio_risk_management_settings(id="PORTFOLIO_ID", value="NEW_RISK_LIMIT_OBJECT")


"""
Delete Tenants/ Portfolios
"""
# Tenants
TenantsApi(client).delete_tenant(id="TENANT_ID")
# Portfolios
PortfoliosApi(client).delete_portfolio(id="PORTFOLIO_ID")
