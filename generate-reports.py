import pandas as pd
import matplotlib.pyplot as plt
import sys, getopt, os
from P1API import P1Helper
from tqdm import tqdm

def generateUPSReport(show, file):
    '''generate UPS report'''

    print('Generating UPS Report...')

    data = pd.read_csv(file)
    df = pd.DataFrame(data)

    # make qty positive
    df['QTY'] = df['QTY'].apply(lambda x: x*-1)

    # get total weight and volume for each row
    df['totWeight'] = df['QTY'] * df['UNIT_WEIGHT']
    df['totVolume'] = df['QTY'] * df['UNIT_VOLUME'] / (12 ** 3)
    
    generateUPSPlots(df, show)
    generateUPSGeneralReport(df)

def generateUPSGeneralReport(df):
    avgWeightPerDay = 0
    avgVolPerDay = 0
    maxWeightL30D = 0
    maxVolL30D = 0
    totalUnitsShipped = 0

    # generate values
    avgWeightPerDay = df.groupby('DATE')['totWeight'].sum().mean()
    avgVolPerDay = df.groupby('DATE')['totVolume'].sum().mean()
    maxWeightL30D = df.groupby('DATE')['totWeight'].sum().max()
    maxVolL30D = df.groupby('DATE')['totVolume'].sum().max()
    totalUnitsShipped = df['QTY'].sum()

    # write strings for report
    line1 = f"Average weight per day: {avgWeightPerDay} lbs\n"
    line2 = f"Average volume per day: {avgVolPerDay} ft^3\n"
    line3 = f"Maximum weight L30D: {maxWeightL30D} lbs\n"
    line4 = f"Maximum volume L30D: {maxVolL30D} ft^3\n"
    line5 = f"Total units shipped L30D: {totalUnitsShipped}\n"

    # write report to file
    file = open('UPS/UPS-Report.txt', 'w')
    file.writelines([line1, line2, line3, line4, line5])
    file.close()

def generateUPSPlots(df, show):
    qtyByDay = df.plot(x='DATE', y = ['QTY'], kind='scatter', title = 'QTY Per Day', grid = True, rot=45,figsize=(20,10))
    qtyBySku = df.plot(x='SKU', y = 'QTY', kind='bar', title = 'QTY by SKU', rot=90, figsize=(20,10))
    volByDay = df.plot(x='DATE', y = ['totWeight', 'totVolume'], kind='line', title = 'Volume Per Day', grid = True, subplots=True, rot=45,figsize=(20,10))
    volByDay[0].set_ylabel('Weight (lbs)')
    volByDay[1].set_ylabel('Volume (Cubic Feet)')


    # save plots to file
    qtyByDay.figure.savefig('UPS/QTY-By-Day.pdf')
    qtyBySku.figure.savefig('UPS/QTY-By-SKU.pdf')
    plt.savefig('UPS/Volume-By-Day.pdf')

    if show:
        plt.show()

''' ************************************ '''

def generateLTLReport(show, file):
    '''generate LTL report'''

    print('Generating LTL Report...', end = '\n')

    #progress bar
    tqdm.pandas()

    data = pd.read_csv(file)
    df = pd.DataFrame(data)
    
    # make qty positive
    df['QTY'] = df['QTY'].apply(lambda x: x*-1)

    # get total weight and volume
    df['totWeight'] = df['QTY'] * df['UNIT_WEIGHT']
    df['totVolume'] = df['QTY'] * df['UNIT_VOLUME'] / (12 ** 3)

    df['DELIVERY_DATE'] = pd.Series(dtype='str')
    
    # get tracking info from  P1 API
    Tracker = P1Helper() 

    trackingPbar = tqdm(df.iterrows(), total=len(df))
    
    for i, j in trackingPbar:        
        ordnum = df.loc[i, ['ORDER_NUMBER']][0] 
        trackingPbar.set_description(f'Tracking {ordnum}')
        try:
            trackstat = Tracker.track(ordnum)

            df.loc[i, ['DELIVERY_STATUS']] = trackstat['status']
            #print(df.loc[i, ['DELIVERY_STATUS']])
            df.loc[i, ['DELIVERY_DATE']] = trackstat['deliveryDate']

        except:
            continue
    
    # get just the ship-to state
    df['SHIP_TO_ADDRESS'] = df['SHIP_TO_ADDRESS'].apply(lambda x : x[-8:-6])
    df['DELIVERY_DATE'] = pd.to_datetime(df.DELIVERY_DATE)
    df['SHIP_DATE'] = pd.to_datetime(df.SHIP_DATE)
    

    generateLTLPlots(df, show)

def generateLTLPlots(df, show):
    ''' generate LTL Plots '''

    fig, ax = plt.subplots()
    
    qtyByDay = df.plot(x='SHIP_DATE', y = ['QTY'], kind='scatter', title = 'QTY Per Day', grid = True, rot=45,figsize=(20,10))
    qtyBySku = df['SKU'].value_counts().plot(ax=ax, kind='bar', xlabel='SKU', ylabel='Frequency', rot=90, figsize=(20,10), title='Quantity by SKU')
    volByDay = df.plot(x='SHIP_DATE', y = ['totWeight', 'totVolume'], kind='line', title = 'Volume Per Day', grid = True, subplots=True, rot=45,figsize=(20,10))
    volByDay[0].set_ylabel('Weight (lbs)')
    volByDay[1].set_ylabel('Volume (Cubic Feet)')

    # shipping cost by state bar plot
    costPivot = df.pivot_table(index='SHIP_TO_ADDRESS', columns = ['LTL_CARRIER'], values='SHIPPING_COST', aggfunc='mean')
    costplot = costPivot.plot(kind='barh', stacked=True, figsize=(20,10))
    costplot.set_title('Shipping Cost by State')

    # cost by carrier bar plot
    costPivot = df.pivot_table(index='LTL_CARRIER', columns = ['SHIP_TO_ADDRESS'], values='SHIPPING_COST', aggfunc='mean')
    costplot2 = costPivot.plot(kind='barh', stacked=True, figsize=(20,10))
    costplot2.set_title('Shipping Cost by Carrier')

    # transit time by carrier plot
    df['TRANSIT_TIME'] = (df['DELIVERY_DATE'] - df['SHIP_DATE']).dt.days
    tranplot = df.boxplot(column=['TRANSIT_TIME'], by=['LTL_CARRIER'], figsize=(20,10))
    tranplot.set_title('Transit Times by Carrier')

    # transit time by state plot
    tranplot2 = df.boxplot(column=['TRANSIT_TIME'], by=['SHIP_TO_ADDRESS'], figsize=(20,10))
    tranplot2.set_title('Transit Times by State')

    

    # save plot files
    qtyByDay.figure.savefig('LTL/QTY-By-Day.pdf')
    qtyBySku.figure.savefig('LTL/QTY-By-SKU.pdf')
    plt.savefig('LTL/Volume-By-Day.pdf')
    costplot.figure.savefig('LTL/Cost-by-State.pdf')
    costplot2.figure.savefig('LTL/Cost-by-Carrier.pdf')
    tranplot.figure.savefig('LTL/Transit-Time-by-Carrier.pdf')
    tranplot2.figure.savefig('LTL/Transit-Time-by-State.pdf')


    if show:
        plt.show()

    generateLTLGeneralReport(df)

def generateLTLGeneralReport(df):
    # generate values
    avgWeightPerDay = df.groupby('SHIP_DATE')['totWeight'].sum().mean()
    avgVolPerDay = df.groupby('SHIP_DATE')['totVolume'].sum().mean()
    maxWeightL30D = df.groupby('SHIP_DATE')['totWeight'].sum().max()
    maxVolL30D = df.groupby('SHIP_DATE')['totVolume'].sum().max()
    totalUnitsShipped = df['QTY'].sum()
    avgCostPerDay = df.groupby('SHIP_DATE')['SHIPPING_COST'].sum().mean()
    avgCostPerCarrier = df.groupby('LTL_CARRIER')['SHIPPING_COST'].sum().mean()
    avgCostPerState = df.groupby('SHIP_TO_ADDRESS')['SHIPPING_COST'].sum().mean()
    totalCostL30D = df['SHIPPING_COST'].sum()

    # write lines
    line1 = f"Average weight per day: {avgWeightPerDay} lbs\n"
    line2 = f"Average volume per day: {avgVolPerDay} ft^3\n"
    line3 = f"Maximum weight L30D: {maxWeightL30D} lbs\n"
    line4 = f"Maximum volume L30D: {maxVolL30D} ft^3\n"
    line5 = f"Total units shipped L30D: {totalUnitsShipped}\n"
    line6 = f"Average cost per day: {avgCostPerDay}\n"
    line7 = f"Average cost per state: {avgCostPerState}\n"
    line8 = f"Average cost per carrier: {avgCostPerCarrier}\n"
    line9 = f"Total cost L30D: {totalCostL30D}"

    # write report to file
    file = open('LTL/LTL-Report.txt', 'w')
    file.writelines([line1, line2, line3, line4, line5, line6, line7, line8, line9])
    file.close()



if __name__ == '__main__':

    showCharts = False
    uinputFile = 'UPS-Shipments_L30D.csv'
    linputFile = 'LTL-Shipments_L30D.csv'
    upsonly= False
    ltlonly = False

    # define arguments
    opts, args = getopt.getopt(sys.argv[1:], shortopts='hsul', longopts=['linput=', 'uinput=', 'show=', 'upsonly=', 'ltlonly='])

    # create directories
    try:
        os.mkdir('LTL')
        os.mkdir('UPS')
    except FileExistsError as e:
        pass

    # parse arguments
    for opt, arg in opts:
        if opt == '-h':
            print('generate-reports.py -s <show charts after running> -u <ups only> -l <ltl only>')

        elif opt in ('-s', '--show'):
            showCharts = True

        elif opt in ('-u', '--upsonly'):
            upsonly = True
        
        elif opt in ('-l', '--ltlonly'):
            ltlonly = True



    if (upsonly and not ltlonly):
        generateUPSReport(showCharts, uinputFile)

    elif (ltlonly and not upsonly):
        generateLTLReport(showCharts, linputFile)
               
    else:
        generateUPSReport(showCharts, uinputFile)
        generateLTLReport(showCharts, linputFile)
        
    print('Done.')

