import pandas as pd
import matplotlib.pyplot as plt
import sys, getopt, os

def generateWeeklyReport(show, file):
    # import data
    data = pd.read_csv(file)
    df = pd.DataFrame(data)

    # make qty positive
    df['QTY'] = df['QTY'].apply(lambda x: x*-1)
    # date formatting
    df['SHIP_DATE'] = pd.to_datetime(df.SHIP_DATE)
    df['DATE'] = pd.to_datetime(df.DATE)
    
    # qty by sku pivot
    qtypivot = df.pivot_table(index='SKU', columns=['CARRIER'], values='QTY', aggfunc='sum')
    qtyplot = qtypivot.plot(kind='barh', stacked=True, figsize=(10,20), grid=True)
    qtyplot.set_title('Qty Shipped by Carrier')
    
    qtyplot.figure.savefig('Qty-Shipped-by-Carrier')
    
    # time to fulfill
    df['FULFILLMENT_TIME'] = (df['SHIP_DATE'] - df['DATE']).dt.days
    fulfillplot = df.boxplot(column=['FULFILLMENT_TIME'], by=['QTY'], figsize=(20,10))
    fulfillplot.set_title('Fulfillment Time by Order Size')
    fulfillplot.figure.savefig('Fullfillment-Time-by-Order-Size')
    
    fulfillplot2 = df.boxplot(column=['FULFILLMENT_TIME'], by=['DATE'], figsize=(20,10))
    fulfillplot2.set_title('Fulfillment Time by Day')
    fulfillplot2.figure.savefig('Fullfillment-Time-by-Day')
    
    fulfillplot3 = df.plot(kind='barh', x='ORDER_NUMBER', y=['FULFILLMENT_TIME'], figsize=(10,30), grid=True, title='Fulfillment Time by Order', fontsize=10)
    fulfillplot3.figure.savefig('Fullfill-Time-by-Order')
    plt.xlabel('Days')
    
    if show:
        plt.show()
        
if __name__ == '__main__':

    show = False
    
    inputfile = 'Denago-Weekly-Data.csv'

    opts, args = getopt.getopt(sys.argv[1:], shortopts='s', longopts=['show='])
    
    for opt, arg in opts:
        if opt == '-s':
            show = True
            
    generateWeeklyReport(show, inputfile)
