from decimal import Decimal
import sys
import os
from datetime import datetime


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import polygonapi
from polygon import RESTClient
from postgresql import execSql


def QueryAndInsert(ticker):
    details = QueryCompanyInfo(ticker)
    InsertSql(ticker, details)

def QueryCompanyInfo(ticker):

    client = RESTClient(polygonapi)

    details = client.get_ticker_details(
        ticker,
        )
    return details
    
def InsertSql(ticker, details):
    
    query = f"""INSERT INTO [stock].[dbo].[CompanyInfo] values (?, ?, ?, ?, ?,
                                                                ?, ?, ?, ?, ?,
                                                                ?, ?, ?, ?, ?,
                                                                ?
                                                                )     """
        
    try:
        values = (ticker, 
                details.name,    
                details.active,        
                details.address.city,        
                details.address.state,     
                details.currency_name,    
                datetime.strptime(details.list_date, "%Y-%m-%d"),   
                details.locale,        
                details.market,       
                str(Decimal(details.market_cap)),        
                details.sic_code,        
                details.sic_description,     
                str(Decimal(details.total_employees)),          
                str(Decimal(details.share_class_shares_outstanding)),        
                str(Decimal(details.weighted_shares_outstanding)),
                datetime.now()
                )    
            
        execSql(query, values, "SqlServer")
    except:
        pass


if __name__ ==  '__main__':
    ticker = "TSLA"
    QueryAndInsert(ticker)