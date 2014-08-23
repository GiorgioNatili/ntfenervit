# -*- coding: utf-8 -*-

"""
Reporting Object that retrieves data from db using SQL
Not using models as no table should be created
"""

from django.db import connection

def ifnone(value, replace):
    if value is None:
        return replace
    else:
        return value


class BaseReport(object):
    '''
    A base report object that will retrieve data from db and place result in .rows property.
    To use it, override the following property:

    _list_rows: If True, .rows will be a list of tuples, otherwise it's populated with list of dictionaries
    _sql:       Set the SQL to be used to return the data
    fields:     Set the verbose name of the columns.  Defaults to column names

    Note: When _list_rows is False, .fields will contain dictionary with resultset column name as key.  This
          allow django templates to retrieve verbose name the same way as the retrieving data from .rows.  E.g.:

          <label>{{ rpt.fields.id }}</label> <div>{{ rpt.rows.id }}</div>

    '''
    _list_rows = True
    _sql = None
    fields = None
    rows = None

    def __init__(self, *args):
        '''Populate the .rows from database'''
        if self._sql is None:
            raise RuntimeError("Required SQL not defined for report object.")

        self.cursor = connection.cursor()

        self.rows = self.get_rows(self._sql, *args)

    def get_rows(self, sql, *args):
        '''Call db and return data formatted as per _list_rows'''
        # Pass the argument to the SQL
        if args:
            res = self.cursor.execute(self._sql, args)
        else:
            res = self.cursor.execute(self._sql)

        # Release list of field name from db if not defined
        col_title = [ col[0] for col in self.cursor.description ]
        col_result = self.cursor.fetchall()

        if self.fields is None:
            self.fields = col_title

        # Return list of data
        if self._list_rows:
            return col_result
        else:
            # Transform fields into a dict
            self.fields = dict(zip(col_title, self.fields))

            return [
                dict(zip(col_title, row))
                for row in col_result
            ]

class ListOfYear(BaseReport):
    _sql = "select distinct year(date) year from campaigns_event order by year desc;"


class ConsumerReport(BaseReport):
    '''
    Consumer and Sale Report.  Computes following 3 values:
    * .total_customers
    * .total_sales
    * .pct_sales_to_customers
    '''
    _list_rows = False
    fields = (
        "id", u"Attività",
        u"T.C. Attività", u"T.C. Consumatori",
        u"Participanti", u"Contatti Lordi", u"Contatti Netti" )

    def __init__(self, year):
        start_of_year = "%s-01-01" % year
        end_of_year = "%s-12-31" % year
        # start_of_year passed twice because it is used twice in the SQL
        super(ConsumerReport, self).__init__(start_of_year, end_of_year, start_of_year, end_of_year)

        # Post Processing
        total_customers = 0
        total_sales = 0
        for row in self.rows:
            total_customers += ifnone(row["customers"], 0)
            total_sales += ifnone(row["sales"], 0)

        self.total_customers = total_customers
        self.total_sales = total_sales

        if total_customers == 0:
            self.pct_sales_to_customers = None
        else:
            self.pct_sales_to_customers = (total_sales/total_customers) * 100


    _sql = """
select u.*
from (
    select
        t.eventtype_id,
        et.description,
        et.contact_to_customer,
        et.customer_to_sale * 100 customer_to_sale,
        SUM(COALESCE(t.population, 0)) contacts,
        SUM(COALESCE(t.population, 0) * et.contact_to_customer) customers,
        SUM(COALESCE(t.population, 0) * et.contact_to_customer * et.customer_to_sale) sales
    from
        campaigns_event t
        join campaigns_eventtype et on (t.eventtype_id = et.id)
    where
        t.date between %s and %s
        and t.owner_id is not NULL
    group by
        et.description

    UNION

    select
        et.id eventtype_id,
        et.description,
        et.contact_to_customer,
        et.customer_to_sale * 100 customer_to_sale,
        SUM(COALESCE(t.population, 0)) contacts,
        SUM(COALESCE(t.population, 0) * et.contact_to_customer) customers,
        SUM(COALESCE(t.population, 0) * et.contact_to_customer * et.customer_to_sale) sales
    from
        campaigns_event t,
        campaigns_eventtype et
    where
        t.date between %s and %s
        and et.id = 5
        and t.owner_id is NULL
) u
order by u.eventtype_id;
"""


class RevenueReport(BaseReport):
    '''
    Revenue Estimate Report that needs to be initialized with ConsumerReport.total_sales.
    Calculates the revenue and place the sum under .total_revenue property
    '''
    _list_rows = False
    fields = ("Livello", "Consumo Annuale", "T.C.", "Sell In", "Stima Fatturati")

    def __init__(self, total_sales):
        super(RevenueReport, self).__init__()

        # Calculate the revenue and total_revenue
        total_revenue = 0
        for row in self.rows:
            row["revenue"]  = total_sales * ifnone(row["sell_in_alloc"],0) * ifnone(row["sell_in_amount"], 0)
            total_revenue += row["revenue"]
            row["sell_in_alloc"] *= 100
        self.total_revenue = total_revenue

    _sql = """
    SELECT
        t.id,
        t.description,
        t.sell_in_alloc,
        t.sell_in_amount,
        0 revenue
    FROM
        campaigns_productgroup t
    ORDER BY
        t.id
    """

