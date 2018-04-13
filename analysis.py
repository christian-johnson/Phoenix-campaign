import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import pandas as pd
import datetime as dt
from matplotlib import rcParams
from matplotlib.pyplot import rc
from matplotlib import gridspec

rcParams['text.usetex'] = True
rc('text.latex', preamble=r'\usepackage{amsmath}')
rcParams['font.size'] = 10
rcParams['axes.titlesize'] = 18
rcParams['legend.fontsize'] = 16
rcParams['font.family'] = 'serif'
rcParams['xtick.labelsize'] =16
rcParams['ytick.labelsize'] =16
rcParams['axes.labelsize'] = 20

electionDate2018 = dt.date(year=2018, month=11, day=6)
electionDate2016 = dt.date(year=2016, month=11, day=8)
districtZips = [91304, 91311, 91321, 91326, 91342, 91350, 91351, 91354, 91355, 91381, 91384, 91387, 91390, 93063, 93065, 93243, 93510, 93532, 93534, 93535, 93536, 93543,
93544, 93550, 93551, 93552, 93553, 93563, 93591]

infilePh = 'phoenix_contributions.csv'
infileCf = 'caforio_contributions.csv'
infileKn = 'knight_contributions.csv'


cols = ['contributor_first_name', 'contributor_middle_name', 'contributor_last_name', 'contributor_suffix', 'contributor_city', 'contributor_state', 'contributor_zip', 'contributor_employer',
'contributor_occupation', 'contribution_receipt_amount', 'contribution_receipt_date']

def consolidateNames(df):
    #Don't want to consolidate ActBlue payments, since those are basically individual contributions
    df1 = pd.DataFrame(df.loc[np.where(df['contributor_last_name']!='ActBlue')])
    df2 = pd.DataFrame(df.loc[np.where(df['contributor_last_name']=='ActBlue')])
    return pd.concat([df.groupby(['contributor_last_name', 'contributor_first_name', 'contributor_zip', 'contributor_state'], as_index = False).sum(), df2], axis=0)

def breakdownDonorsByMoney(df, bins):
    contributorBins = []
    df.index = range(len(df))
    for i in range(len(bins)-1):
        contributorBins.append(pd.DataFrame(df.loc[np.where(i+1==np.digitize(df['contribution_receipt_amount'], bins))]))
        contributorBins[i].index = range(len(contributorBins[i]))
    return contributorBins

def breakdownDonorsByDistrict(df):
    contributorBins = []
    #in-district
    inDistrictLocs = np.zeros((len(df)))
    for i in range(len(inDistrictLocs)):
        if len(str(df.loc[i]['contributor_zip'])) == 5:
            if df.loc[i]['contributor_zip'] in districtZips:
                inDistrictLocs[i] = 1
        else:
            zipString = str(((9-len(str(df.loc[i]['contributor_zip'])))*'0'+str(df.loc[i]['contributor_zip'])))[:5]
            if int(zipString) in districtZips:
                inDistrictLocs[i] = 1
    contributorBins.append(pd.DataFrame(df.loc[np.where(inDistrictLocs)]))
    contributorBins[0].index = range(len(contributorBins[0]))
    #out of district
    contributorBins.append(pd.DataFrame(df.loc[np.where(np.abs(1.0-inDistrictLocs))]))
    contributorBins[1].index = range(len(contributorBins[1]))

    return contributorBins


def contributionsOverTime(df, dfList, binLabels, figureName):
    #Make plot of contributions over time
    cMap = cm.tab10
    #ax.set_facecolor('#202020')
    fig = plt.figure(figsize=(8, 8))
    gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1])
    ax1 = plt.subplot(gs[0])

    for i in range(len(binLabels)):
        dates = (electionDate2018-dfList[i]['contribution_receipt_date']).dt.days
        ax1.plot(dates, np.cumsum(dfList[i]['contribution_receipt_amount'].data), color=cMap(float(i)/(2.*len(binLabels))), label=binLabels[i], linewidth=2.0)
    plt.ylabel('Cumulative Contributions [\$]')
    ax1.invert_xaxis()
    plt.xlim([600, 300])

    leg = plt.legend()
    text1, text2, text3, text4 = leg.get_texts()
    leg.get_frame().set_alpha(0.0)
    """
    text1.set_color('black')
    text2.set_color('black')
    text3.set_color('black')
    text4.set_color('black')
    """
    ax1.tick_params(axis='x',which='both',bottom='off',top='off',labelbottom='off')

    ax2 = plt.subplot(gs[1])

    dates = (electionDate2018-df['contribution_receipt_date']).dt.days
    ax2.hist(dates, bins=np.arange(min(dates), max(dates), 1), color='black')
    ax2.invert_xaxis()
    plt.xlim([600, 300])

    plt.ylabel('Donations')
    plt.xlabel('Days Until Election')
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=0.0)

    plt.savefig(figureName+'.pdf', bbox_inches='tight')
    #plt.show()

def pieChartMoney(dfList, binLabels, figureName, binLabels2 = ['\$0-\$100','\$100-\$250','\$250-\$500','\$500-\$2000','\$2000+']):
    tot_knight_donors = 180.0
    tot_caforio_donors = 1275.0
    tot_knight_contributions = 190898.28
    tot_caforio_contributions = 562725.41

    fig = plt.figure(figsize=[12,4])
    plt.subplot(121)
    #Make pie chart breaking down # of donors by category
    sizes = np.zeros((len(dfList)))
    for i in range(len(sizes)):
        sizes[i] = len(dfList[i]['contribution_receipt_amount'].data)
    print('Numbers of donors:')
    print(str(sizes) + ' ' + str(100.0*sizes/np.sum(sizes))+str('%'))
    print(np.sum(sizes))
    print('knight: ' + str(100.0*sizes/tot_knight_donors))
    print('caforio: ' + str(100.0*sizes/tot_caforio_donors))

    sizes *= 1.0/np.sum(sizes)
    plt.pie(sizes, labels=binLabels)
    plt.axis('equal')
    plt.title('Number of Donors', y = 1.08)
    plt.subplot(122)

    #Make pie chart breaking down $ by category
    sizes = np.zeros((len(dfList)))
    for i in range(len(sizes)):
        sizes[i] = np.sum(dfList[i]['contribution_receipt_amount'].data)
    print('Summed amounts:')
    print(str(sizes) + ' ' + str(100.0*sizes/np.sum(sizes))+str('%'))
    print(np.sum(sizes))
    print('knight: ' + str(100.0*sizes/tot_knight_contributions))
    print('caforio: ' + str(100.0*sizes/tot_caforio_contributions))

    sizes *= 1.0/np.sum(sizes)
    plt.pie(sizes, labels=binLabels2)
    plt.axis('equal')
    plt.title('Amount Raised', y = 1.08)

    plt.savefig(figureName+'.pdf',bbox_inches='tight')
    #plt.show()
    print(' ')

def main():
    #Load the data from the FEC spreadsheets
    ph = pd.read_csv(infilePh, parse_dates=['contribution_receipt_date'])[cols]
    ph = ph.sort_values(by=['contribution_receipt_date'])
    ph.index=range(len(ph))
    cf = pd.read_csv(infileCf, parse_dates=['contribution_receipt_date'])[cols]
    #Remove data from before the 2018 election cycle
    cf = cf.where((electionDate2018-cf['contribution_receipt_date']).dt.days<585)
    cf = cf[pd.notnull(cf['contribution_receipt_date'])]
    cf = cf.sort_values(by=['contribution_receipt_date'])
    cf.index = range(len(cf))

    kn = pd.read_csv(infileKn, parse_dates=['contribution_receipt_date'])[cols]
    #Remove data from before the 2018 election cycle
    kn = kn.where((electionDate2018-kn['contribution_receipt_date']).dt.days<585)
    kn = kn[pd.notnull(kn['contribution_receipt_date'])]
    kn = kn.sort_values(by=['contribution_receipt_date'])
    kn.index = range(len(kn))

    #First, plot donations over time for each candidate
    contributionsOverTime(ph, breakdownDonorsByMoney(ph, bins=[0.0, 100.01, 500.01, 1000.01, 2700.01]), binLabels=['\$0-\$100', '\$100-\$500', '\$500-1000', '\$1000+'], figureName = 'Phoenix_Totals_overTime')
    contributionsOverTime(cf, breakdownDonorsByMoney(cf, bins=[0.0, 100.01, 500.01, 1000.01, 2700.01]), binLabels=['\$0-\$100', '\$100-\$500', '\$500-1000', '\$1000+'], figureName = 'Caforio_Totals_overTime')
    contributionsOverTime(kn, breakdownDonorsByMoney(kn, bins=[0.0, 100.01, 500.01, 1000.01, 2700.01]), binLabels=['\$0-\$100', '\$100-\$500', '\$500-1000', '\$1000+'], figureName = 'Knight_Totals_overTime')

    #Statistics & plots on each candidate's individual donors
    #Exclude PACs etc by removing any donor who donated more than $2700
    ph = breakdownDonorsByMoney(consolidateNames(ph), bins=[0, 2700.01, 100000.01])[0]
    cf = breakdownDonorsByMoney(consolidateNames(cf), bins=[0, 2700.01, 100000.01])[0]
    kn = breakdownDonorsByMoney(consolidateNames(kn), bins=[0, 2700.01, 100000.01])[0]

    bins = [0, 100.01, 250.01, 500.01, 2000.01, 2701.01]
    binLabels = ['\$0-\$100','\$100-\$250','\$250-\$500','\$500-\$2000','\$2000+']

    [indist, outdist] = breakdownDonorsByDistrict(cf)
    print('Caforio: in District')
    pieChartMoney(breakdownDonorsByMoney(indist, bins = bins), binLabels = binLabels, figureName = 'Caforio_InDistrict')
    print('Caforio: Out of district')
    pieChartMoney(breakdownDonorsByMoney(outdist, bins = bins), binLabels = binLabels, figureName = 'Caforio_OutDistrict')


    [indist, outdist] = breakdownDonorsByDistrict(kn)
    print('Knight: in District')
    pieChartMoney(breakdownDonorsByMoney(indist, bins = bins), binLabels = binLabels, figureName = 'Knight_InDistrict')
    print('Knight: Out of district')
    pieChartMoney(breakdownDonorsByMoney(outdist, bins = bins), binLabels = binLabels, figureName = 'Knight_OutDistrict')


    [indist, outdist] = breakdownDonorsByDistrict(ph)
    print('Phoenix: in district:')
    pieChartMoney(breakdownDonorsByMoney(indist, bins = bins), binLabels = binLabels, figureName = 'Phoenix_InDistrict')
    print('Phoenix: out of district')
    pieChartMoney(breakdownDonorsByMoney(outdist, bins = bins), binLabels = binLabels, figureName = 'Phoenix_OutDistrict')

    print('Phoenix: Total')
    pieChartMoney(breakdownDonorsByMoney(ph, bins = bins), binLabels = binLabels, figureName = 'Phoenix_Totals')
    print('Caforio: Total')
    pieChartMoney(breakdownDonorsByMoney(cf, bins = bins), binLabels = binLabels, figureName = 'Caforio_Totals')
    print('Knight: Total')
    pieChartMoney(breakdownDonorsByMoney(kn, bins = bins), binLabels = binLabels, figureName = 'Knight_Totals', binLabels2 = ['','\$100-\$250','\$250-\$500','\$500-\$2000','\$2000+'])


    print('total phoenix raised: $' + str(np.sum(ph['contribution_receipt_amount'].data)) + ' for an mean of $' + str(np.sum(ph['contribution_receipt_amount'].data)/len(ph)) + ' per donor')
    print('Median: ' + str(np.median(ph['contribution_receipt_amount'].data)))

    print('total caforio raised: $' + str(np.sum(cf['contribution_receipt_amount'].data)) + ' for an mean of $' + str(np.sum(cf['contribution_receipt_amount'].data)/len(cf)) + ' per donor')
    print('Median: ' + str(np.median(cf['contribution_receipt_amount'].data)))

    print('total knight raised: $' + str(np.sum(kn['contribution_receipt_amount'].data)) + ' for an mean of $' + str(np.sum(kn['contribution_receipt_amount'].data)/len(kn)) + ' per donor')
    print('Median: ' + str(np.median(kn['contribution_receipt_amount'].data)))




if __name__ == '__main__':
    main()
