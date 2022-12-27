from datetime import date, timedelta
from statistics import median, mean
import pandas as pd
import numpy as np
import requests
import json
import csv

enctoken = 'FHD++iWKGSNraOTp68+CcArTgKfDxLnfXyx4vxl0eYungLdcr/WBzV8jq8HJu0nqaq6HR1geYKWBrSpYc+BYsR7xQFcLzCRG/eUwG7xGWkZqh9HufHc6Sg=='
s_date = date(2021, 2, 5)
e_date = date(2022, 6, 20)

equities = {'NIFTY' : 256265}#, 'RELIANCE' : 738561, 'HDFCBANK' : 341249, 'INFY' : 408065, 'ICICIBANK' : 1270529,
            #'HDFC' : 340481, 'TCS' : 2953217, 'KOTAKBANK' : 492033, 'ITC' : 424961, 'LT' : 2939649, 'HINDUNILVR' : 356865}


def level_extractor(enctoken, first_date, last_date, c_id):

        def support_finder(low, high, price_action):
                temp_support = {}
                d_pa = pa*1.4
                u_pa = pa*2.1
                floor, ceil = 0,0
                down_move, up_move = 0,0
                for i in range(len(low)):
                        try:
                                if (low[i] > low[i+1]) and not up_move:
                                        if not ceil:
                                                ceil = high[i]
                                        down_move = ceil - low[i+1]
                                elif (low[i] < low[i+1]) and down_move:
                                        if not floor:
                                                floor = low[i]
                                                touch = i
                                        up_move = high[i+1] - floor

                                if up_move and (low[i] > low[i+1]):
                                        sup = round(floor,2)
                                        if (up_move >= u_pa and down_move >= d_pa) or (up_move > u_pa*1.6):
                                                while sup in temp_support:
                                                    sup -= 0.1
                                                temp_support[round(sup,2)] = [round(up_move,2), i-touch]
                                        elif up_move > 0:
                                                territory = [int(sup-pa**0.5), int(sup+pa**0.5)]
                                                for i in temp_support:
                                                        if i >= territory[0] and i <= territory[1]:
                                                                while sup in temp_support:
                                                                        sup -= 0.1
                                                                temp_support[round(sup,2)] = [round(up_move,2), i-touch]
                                        down_move, up_move = 0,0
                                        floor, ceil = 0,0
                        except:
                                if (i == len(low)-1) and floor:
                                        if (up_move >= u_pa and down_move >= d_pa) or (up_move > u_pa*1.6):
                                                sup = round(floor,2)
                                                while sup in temp_support:
                                                    sup -= 0.1
                                                temp_support[round(sup,2)] = [round(up_move,2), i-touch]
                return temp_support

        def resistance_finder(low, high, pa):
                temp_resistance = {}
                d_pa = pa*2.1
                u_pa = pa*1.4
                floor, ceil = 0,0
                down_move, up_move = 0,0
                for i in range(len(high)):
                        try:
                                if (high[i] < high[i+1]) and not down_move:
                                        if not floor:
                                                floor = low[i]
                                        up_move = high[i+1] - floor
                                elif (high[i] > high[i+1]) and up_move:
                                        if not ceil:
                                                ceil = high[i]
                                                touch = i
                                        down_move = ceil - low[i+1]

                                if down_move and (high[i] < high[i+1]):
                                        res = round(ceil,2)
                                        if (up_move >= u_pa and down_move >= d_pa) or (down_move > d_pa*1.6):
                                                res = int(ceil)
                                                while res in temp_resistance:
                                                    res += 0.1
                                                temp_resistance[round(res,2)] = [round(down_move,2), i-touch]
                                        elif down_move > 0:
                                                territory = [int(res-pa**0.5), int(res+pa**0.5)]
                                                for i in temp_resistance:
                                                        if i >= territory[0] and i <= territory[1]:
                                                                while res in temp_resistance:
                                                                        res += 0.1
                                                                temp_resistance[round(res,2)] = [round(down_move,2), i-touch]
                                        down_move, up_move = 0,0
                                        floor, ceil = 0,0
                        except:
                                if (i == len(high)-1) and ceil:
                                        if (up_move >= u_pa and down_move >= d_pa) or (down_move > d_pa*1.6):
                                                res = round(ceil,2)
                                                while res in temp_resistance:
                                                    res += 0.1
                                                temp_resistance[round(res,2)] = [round(down_move,2), i-touch]
                return temp_resistance

        e_date = date.today()
        s_date = e_date - timedelta(days=14)

        headers = {'Authorization': 'enctoken %s' %(enctoken),
                           'Content-Type': 'application/x-www-form-urlencoded'}
        params = (('from', s_date),('to', e_date))
        response = requests.get('https://kite.zerodha.com/oms/instruments/historical/%s/5minute' %(c_id), headers = headers, params = params)

        ohlc = pd.DataFrame(response.json()['data']['candles'])
        candle_swing = ohlc[2]-ohlc[3]
        pa = np.sqrt((candle_swing**2).sum()/len(candle_swing))
        print(pa, ' - ', 1.4*pa, 2.1*pa)

        ohlc = []
        while first_date <= last_date:
                if last_date - first_date >= timedelta(days=60):
                        params = (('from', first_date),('to', first_date+timedelta(days=60)))
                        first_date += timedelta(days=60)
                else:
                        params = (('from', first_date),('to', last_date))
                        first_date = last_date + timedelta(days=1)
                response = requests.get('https://kite.zerodha.com/oms/instruments/historical/%s/5minute' %(c_id), headers = headers, params = params)
                ohlc += response.json()['data']['candles']

        high = []
        low = []
        for i in ohlc[::][:]:
                high.append(i[2])
                low.append(i[3])

        resistance = resistance_finder(low, high, pa)
        support = support_finder(low, high, pa)

        ltp = requests.get('https://kite.zerodha.com/oms/instruments/historical/%s/day' %(c_id), headers = headers,
                           params=(('from', last_date),('to', last_date))).json()['data']['candles'][-1][4]
        baseline = int(ltp)
        lower_limit = baseline - (pa*15)
        upper_limit = baseline + (pa*15)

        ranged_level_s = {k:support[k] for k in support.keys() if k >= lower_limit and k <= upper_limit}
        ranged_level_r = {k:resistance[k] for k in resistance.keys() if k >= lower_limit and k <= upper_limit}

        return ranged_level_s, ranged_level_r
        #return support, resistance

def grouper(iterable):
        cluster = []
        group = []
        head = iterable[0]
        for i in range(len(iterable)):
                if iterable[i] - head <= 15:
                        group.append(iterable[i])
                else:
                        if len(group) == 0:
                                group.append(head)
                        cluster.append(group)
                        group = []
                        head = iterable[i]
        return cluster


def print_stats(dct):
        for clusters in grouper(sorted(list(dct.keys()))):
                x = []
                t = []
                least_reversal = [0, float('inf')]
                for element in clusters:
                        reversal = dct[element][0]
                        if reversal < least_reversal[1]:
                                least_reversal[1] = reversal
                                least_reversal[0] = element
                        x.append(reversal)
                        t.append(dct[element][1])
                print(f'{clusters[0]} - {clusters[-1]} [{len(clusters)}]')
                #print(f'\tmin rejection - {int(min(x))}')
                print(f'\tmin rejection - {least_reversal}')
                print(f'\tmax rejection - {int(max(x))}')
                print(f'\tmedian rejection - {int(median(x))}')
                print(f'\tmin time - {int(min(t)*5)}')
                print(f'\tmax time - {int(max(t)*5)}')

for key, value in equities.items():
        supports, resistances = level_extractor(enctoken, s_date, e_date, value)
        with open('%s.csv' %(key), 'w',  newline="") as level_file:
                csvwriter = csv.writer(level_file)
                csvwriter.writerow(['support'])
                csvwriter.writerow(supports)
                csvwriter.writerow(['resistance'])
                csvwriter.writerow(resistances)
        print('levels saved for %s' %(key))
        print('support')
        print_stats(supports)
        print('resistance')
        print_stats(resistances)
        print('\n')
