CreateCashflow = """        CREATE TABLE IF NOT EXISTS cashflow  (
            stock_id TEXT,
            date DATE,
            "Free_Cash_Flow" NUMERIC,
            "Repurchase_Of_Capital_Stock" NUMERIC,
            "Repayment_Of_Debt" NUMERIC,
            "Issuance_Of_Debt" NUMERIC,
            "Issuance_Of_Capital_Stock" NUMERIC,
            "Capital_Expenditure" NUMERIC,
            "Interest_Paid_Supplemental_Data" NUMERIC,
            "Income_Tax_Paid_Supplemental_Data" NUMERIC,
            "End_Cash_Position" NUMERIC,
            "Beginning_Cash_Position" NUMERIC,
            "Changes_In_Cash" NUMERIC,
            "Financing_Cash_Flow" NUMERIC,
            "Cash_Flow_From_Continuing_Financing_Activities" NUMERIC,
            "Net_Other_Financing_Charges" NUMERIC,
            "Cash_Dividends_Paid" NUMERIC,
            "Common_Stock_Dividend_Paid" NUMERIC,
            "Net_Common_Stock_Issuance" NUMERIC,
            "Common_Stock_Payments" NUMERIC,
            "Common_Stock_Issuance" NUMERIC,
            "Net_Issuance_Payments_Of_Debt" NUMERIC,
            "Net_Short_Term_Debt_Issuance" NUMERIC,
            "Net_Long_Term_Debt_Issuance" NUMERIC,
            "Long_Term_Debt_Payments" NUMERIC,
            "Long_Term_Debt_Issuance" NUMERIC,
            "Investing_Cash_Flow" NUMERIC,
            "Cash_Flow_From_Continuing_Investing_Activities" NUMERIC,
            "Net_Other_Investing_Changes" NUMERIC,
            "Net_Investment_Purchase_And_Sale" NUMERIC,
            "Sale_Of_Investment" NUMERIC,
            "Purchase_Of_Investment" NUMERIC,
            "Net_Business_Purchase_And_Sale" NUMERIC,
            "Purchase_Of_Business" NUMERIC,
            "Net_PPE_Purchase_And_Sale" NUMERIC,
            "Purchase_Of_PPE" NUMERIC,
            "Operating_Cash_Flow" NUMERIC,
            "Cash_Flow_From_Continuing_Operating_Activities" NUMERIC,
            "Change_In_Working_Capital" NUMERIC,
            "Change_In_Other_Working_Capital" NUMERIC,
            "Change_In_Other_Current_Liabilities" NUMERIC,
            "Change_In_Other_Current_Assets" NUMERIC,
            "Change_In_Payables_And_Accrued_Expense" NUMERIC,
            "Change_In_Payable" NUMERIC,
            "Change_In_Account_Payable" NUMERIC,
            "Change_In_Inventory" NUMERIC,
            "Change_In_Receivables" NUMERIC,
            "Changes_In_Account_Receivables" NUMERIC,
            "Other_Non_Cash_Items" NUMERIC,
            "Stock_Based_Compensation" NUMERIC,
            "Deferred_Tax" NUMERIC,
            "Deferred_Income_Tax" NUMERIC,
            "Depreciation_Amortization_Depletion" NUMERIC,
            "Depreciation_And_Amortization" NUMERIC,
            "Net_Income_From_Continuing_Operations" NUMERIC,
            PRIMARY KEY (stock_id, date)     

        );
    """


createStockPrice = """        CREATE TABLE IF NOT EXISTS stockPrice  (
            stock_id TEXT,
            date timestamp,
            "open" NUMERIC,
            "high" NUMERIC,
            "low" NUMERIC,
            "close" NUMERIC,
            "volume" NUMERIC,
            PRIMARY KEY (stock_id, date) 
        );
    """


createStockPrice = """        CREATE TABLE IF NOT EXISTS stockPrice  (
            stock_id TEXT,
            date timestamp,
            "open" NUMERIC,
            "high" NUMERIC,
            "low" NUMERIC,
            "close" NUMERIC,
            "volume" NUMERIC,
            PRIMARY KEY (stock_id, date) 
        );
    """
createMacro = """ CREATE TABLE IF NOT EXISTS MacroMonthly  (
                    'FEDFUNDS'      NUMERIC(10, 4)     -- Federal Funds Rate   -- Daily, lag one day
                    ,"MORTGAGE30US" NUMERIC(10, 4) -- Mortgage rates
                    ,"GS10"         NUMERIC(10, 4) -- 10-Year Treasury

                    -- Inflation & Prices
                    ,"CPIAUCSL"     NUMERIC(10, 4) -- CPI (Consumer Price Index)
                    ,"PCE"          NUMERIC(10, 4) -- PCE
                    ,"PPIACO"       NUMERIC(10, 4) -- Producer Price Index

                    -- Employment & Labor
                    ,"UNRATE"       NUMERIC(10, 4) -- Unemployment rate
                    ,"PAYEMS"       NUMERIC(10, 4) -- Nonfarm Payrolls

                    -- GDP & Growth	
                    , "GDP"         NUMERIC(10, 4) -- Real GDP
                    , "GDPC1"       NUMERIC(10, 4) -- Real Gross Domestic Product

                    -- Housing 
                    ,"HOUST"        NUMERIC(10, 4) -- New Housing Starts
                    ,"CSUSHPISA"    NUMERIC(10, 4) -- Home Price Index
                )
            """