import pandas as pd

#Import Excel
data=pd.read_excel("Data_Market.xlsx")


#Set Parameters
intial_day_text = "2020-02-20"
period=30 #apply technique during x days
number_test=1 #test x times
test_each_x_days=period #shift the window by x days after each test

fees=0.001


#Find index of the date (might lead to an error if weekend or public holiday)
intial_day= data.loc[data['Date'] == intial_day_text].index.values[0]


#Initialization (_All are arrays which store the value at each test)
Profit_All=[]
Profit_neverwait_All=[]
Profit_benchmark_All=[]
buy_count_All=[]
dif_sell_buy_All=[]
stuck_count_All=[]





#Benchmark
#######################

for test in range(number_test):
    day = (intial_day) + test * test_each_x_days

    Profit_benchmark=data.loc[day+period]["S&P Close"]/data.loc[day]["S&P Open"]

    Profit_benchmark_All.append(Profit_benchmark)





wrong=0

#Technique 1: Buy if signal, sell same day or when goes back up
###############################################################

for test in range(number_test):

    #Intialize
    Profit = 1
    buy_count = 0 #how many times I buy
    sell_count = 0 #just to make sure sell as many times as I buy
    stuck_count = 0 #how many days I am stuck because cannot sell (price went down)

    day = (intial_day-1) + test * test_each_x_days


    while day < intial_day + test * test_each_x_days + period:
        day=day+1

        data_day = data.loc[day]

        #Buy if signal
        if data_day["Japan Close"]/data_day["Japan Open"]>1:
            Pbuy=data_day["S&P Open"]
            day_buy=day
            buy_count=buy_count+1

            #Sell same day if close higher than open
            if data_day["S&P Close"]>Pbuy:
                wrong = wrong + 1
                Psell=data_day["S&P Close"]
                Profit = Profit * Psell/Pbuy * (1-fees)
                sell_count=sell_count+1

            #If couldnt sell wait
            else:
                while day < intial_day + test * test_each_x_days + period:
                    day = day + 1
                    data_day = data.loc[day]
                    stuck_count=stuck_count+1

                    #sell if price reach buy price
                    if data_day["S&P High"]>Pbuy:
                        Psell = data_day["S&P High"]
                        Profit = Profit * (1-fees)
                        sell_count = sell_count + 1
                        break #if manage to sell break this while and start again to look for sell signal

                    #if after 2 still days stuck, try also to sell even if lower than buy
                    elif day > day_buy+2 and data_day["S&P Close"] >  data.loc[day-1]["S&P Close"]:
                        Psell = data_day["S&P Close"]
                        Profit = Profit * Psell / Pbuy * (1-fees)
                        sell_count = sell_count + 1
                        break #if manage to sell break this while and start again to look for sell signal



    #If not sold (closed higher than opened and could not find price higher than buy) I need to sell
    if data_day["S&P High"] < Pbuy: #if still not sold because price went down
        data_day = data.loc[day]
        Psell = data_day["S&P Close"]
        Profit = Profit * Psell / Pbuy * (1-fees)


    #print(round(Profit,1))
    Profit_All.append(Profit)
    buy_count_All.append(buy_count)
    dif_sell_buy_All.append(buy_count-sell_count)
    stuck_count_All.append(stuck_count)






#Technique 2: Buy if signal, sell same day (even if lower)
##########################################################

for test in range(number_test):
    Profit_neverwait=1

    day = (intial_day - 1) + test  * test_each_x_days

    while day< intial_day + test*test_each_x_days + period:
        day = day + 1

        data_day = data.loc[day]

        if data_day["Japan Close"] / data_day["Japan Open"] > 1:
            Pbuy = data_day["S&P Open"]
            Profit_neverwait = Profit_neverwait*data_day["S&P Close"]/data_day["S&P Open"] * (1-fees)

    #print(round(Profit_neverwait,1))
    Profit_neverwait_All.append(Profit_neverwait)




#Result
#######

#Convert to dataframe, easier to manipulate
Profit_All_df=pd.DataFrame(Profit_All)
Profit_neverwait_All_df=pd.DataFrame(Profit_neverwait_All)
Profit_benchmark_All_df=pd.DataFrame(Profit_benchmark_All)

buy_count_All_df=pd.DataFrame(buy_count_All)
dif_sell_buy_All_df=pd.DataFrame(dif_sell_buy_All)
stuck_count_All_df=pd.DataFrame(stuck_count_All)


print(data_day["Date"])
#Benchmark

print("\n", "Benchmark")
print("Average Profit: ", round(Profit_benchmark_All_df.mean()[0],2))
print("Percentage profit < 1: ", Profit_benchmark_All_df[Profit_benchmark_All_df < 1 ].count()[0]/Profit_benchmark_All_df.size)

#Tech1
print("\n", "Technique 1")
print("Average Profit: ", round(Profit_All_df.mean()[0],2))
print("Percentage profit < 1: ", Profit_All_df[Profit_All_df < 1 ].count()[0]/Profit_All_df.size)
print("How many days buy: ", round(buy_count_All_df.mean()[0],2))
print("Wrong", wrong)
print("How many days stuck: ", round(stuck_count_All_df.mean()[0],2))
print("How many couldnt sell: ", dif_sell_buy_All_df[dif_sell_buy_All_df > 0 ].count()[0])


#Tech2: same day
print("\n","Technique 2 (same day)")
print("Average Profit: ",round(Profit_neverwait_All_df.mean()[0],2))
print("Percentage profit < 1: ", Profit_All_df[Profit_neverwait_All_df < 1 ].count()[0]/Profit_All_df.size)
