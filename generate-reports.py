import pandas as pd
import matplotlib.pyplot as plt
import sys, getopt, os
from P1API import P1Helper

def generateUPSReport(show, file):
    '''generate UPS report'''

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
    file = open('UPS-Report.txt', 'w')
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
    print('Getting tracking from Priority1.', end='')
    for i, j in df.iterrows():
        if (i % 50 == 0):
            print('.', end = '')
        try:
            ordnum = df.loc[i, ['ORDER_NUMBER']][0]
            trackstat = Tracker.track(ordnum)

            df.loc[i, ['DELIVERY_STATUS']] = trackstat['status']
            #print(df.loc[i, ['DELIVERY_STATUS']])
            df.loc[i, ['DELIVERY_DATE']] = trackstat['deliveryDate']
            #print(df.loc[i, ['DELIVERY_DATE']])
        except:
            continue

    print('Done', end='\n')
    generateLTLPlots(df, show)

def generateLTLPlots(df, show):
    ''' generate LTL Plots '''
    print('Generating LTL Plots...')
    qtyByDay = df.plot(x='SHIP_DATE', y = ['QTY'], kind='scatter', title = 'QTY Per Day', grid = True, rot=45,figsize=(20,10))
    qtyBySku = df.plot(x='SKU', y = 'QTY', kind='bar', title = 'QTY by SKU', rot=90, figsize=(20,10))
    volByDay = df.plot(x='SHIP_DATE', y = ['totWeight', 'totVolume'], kind='line', title = 'Volume Per Day', grid = True, subplots=True, rot=45,figsize=(20,10))
    volByDay[0].set_ylabel('Weight (lbs)')
    volByDay[1].set_ylabel('Volume (Cubic Feet)')

    # save plot files
    qtyByDay.figure.savefig('LTL/QTY-By-Day.pdf')
    qtyBySku.figure.savefig('LTL/QTY-By-SKU.pdf')
    plt.savefig('LTL/Volume-By-Day.pdf')

    if show:
        plt.show()

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

