import pandas as pd
import matplotlib.pyplot as plt
import sys, getopt, os

def generateWeeklyReport(show, file):
    # import data
    data = pd.read_csv(file)
    df = pd.DataFrame(data)

    # make qty positive
    df['QTY'] = df['QTY'].apply(lambda x: x*-1)
    
    # qty by sku pivot
    qtypivot = df.pivot_table(index='SKU', columns=['CARRIER'], values='QTY', aggfunc='sum')
    qtyplot = qtypivot.plot(kind='barh', stacked=True, figsize=(10,20), grid=True)
    qtyplot.set_title('Qty Shipped by Carrier')
    
    qtyplot.figure.savefig('Qty-Shipped-by-Carrier')
    
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