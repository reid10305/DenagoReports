import pandas as pd
import matplotlib.pyplot as plt
import sys

def generateUPSReport():
    '''generate UPS report'''

    data = pd.read_csv('UPS-Shipments_L30D.csv')
    df = pd.DataFrame(data)

    # make qty positive
    df['QTY'] = df['QTY'].apply(lambda x: x*-1)

    # get total weight and volume for each row
    df['totWeight'] = df['QTY'] * df['UNIT_WEIGHT']
    df['totVolume'] = df['QTY'] * df['UNIT_VOLUME'] / (12 ** 3)
    
    generateUPSPlots(df)
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

def generateUPSPlots(df):
    qtyByDay = df.plot(x='DATE', y = ['QTY'], kind='scatter', title = 'QTY Per Day', grid = True, rot=45,figsize=(20,10))
    qtyBySku = df.plot(x='SKU', y = 'QTY', kind='bar', title = 'QTY by SKU', rot=90, figsize=(20,10))
    volByDay = df.plot(x='DATE', y = ['totWeight', 'totVolume'], kind='line', title = 'Volume Per Day', grid = True, subplots=True, rot=45,figsize=(20,10))
    volByDay[0].set_ylabel('Weight (lbs)')
    volByDay[1].set_ylabel('Volume (Cubic Feet)')


    # save plots to file
    qtyByDay.figure.savefig('QTY-By-Day.pdf')
    qtyBySku.figure.savefig('QTY-By-SKU.pdf')
    plt.savefig('Volume-By-Day.pdf')

    #plt.show()

def generateLTLReport():
    '''generate LTL report'''

if __name__ == '__main__':
    generateUPSReport()
    generateLTLReport()