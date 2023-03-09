import itertools
import random
import sys
import collections
from matplotlib import pyplot as plt

POINTS_TO_WIN = 7
MAD_DASHING = False
SHOW_WORK = False
PLOT_DATA = False

def DeckSize():

    while True:

        deckSize = input("How many cards in your deck?\n")

        try:
            val = int(deckSize)            
            return val
        except ValueError:
            print("Input is not an appropriate integer.")
            

def MinDeckSize(deckSize):

    minDeckSizeDiff = deckSize%5
    minDeckSize = deckSize - minDeckSizeDiff
    return minDeckSize   

def RequiredAgendas(minDeckSize):

    baseLine = 40
    baseLineAgendaCount = 18
    baseLineDiff = (minDeckSize - baseLine)/5

    requiredAgendas = baseLineAgendaCount + (2*baseLineDiff)

    return (int(requiredAgendas),int(requiredAgendas+1))
    

def AgendaFiller(requiredAgendas):

    while True:

        print("\nKindly input how many agendas you have of each point denomination.")

        while True:
            val = input(" - Three point agendas: ")
            try:
                num3s = int(val)
            except ValueError:
                print("Input is not an appropriate integer.")
                continue
            if num3s >= 0:
                break
            else:
                print("Input is not an appropriate integer.")
      

        while True:
            val = input(" - Two point agendas: ")
            try:
                num2s = int(val)
            except ValueError:
                print("Input is not an appropriate integer.")
                continue
            if num2s >= 0:
                break
            else:
                print("Input is not an appropriate integer.")

        while True:
            val = input(" - One point agendas: ")
            try:
                num1s = int(val)
            except ValueError:
                print("Input is not an appropriate integer.")
                continue
            if num1s >= 0:
                break
            else:
                print("Input is not an appropriate integer.")
        
        agendaSum = (3*num3s) + (2*num2s) + (1*num1s)
        
        if agendaSum != requiredAgendas[0] and agendaSum != requiredAgendas[1]:
            print(f"Your deck is expected to contain {requiredAgendas[0]}-{requiredAgendas[1]} agenda points, but currently contains {agendaSum} agenda points.")
            print("Please re-enter your agenda selection!\n")
            continue
        
        numAgendas = num3s+num2s+num1s

        print(f"\nYour deck contains {agendaSum} agenda points across {numAgendas} agendas:")
        print(f" - [{num3s}] Three point agendas")
        print(f" - [{num2s}] Two point agendas")
        print(f" - [{num1s}] One point agendas\n")        

        agendaSpread = [num3s, num2s, num1s]  

        if num3s != 0:   
            agendaSpread = GFIQuestion(agendaSpread)  

        return agendaSpread, numAgendas

def GFIQuestion(agendaSpread):

    while True:

        response = input(f"Does your deck contain any copies of Global Food Initiative? (y/n)\n").lower()
        
        match response:

            case "y" | "yes":        
                
                while True:

                    numGFIs = input("\nHow many Global Food Initiative's does the deck contain?\n")

                    try:
                        numGFIs = int(numGFIs)            
                    except ValueError:
                        print("Input is not an appropriate integer.")
                        continue
                
                    if numGFIs > agendaSpread[0]:
                        print("\nYou can not have more Global Food Initiative's than three point agendas!")
                        continue

                    else:                        
                        ## TODO
                        #this breaks if we have 4 point agendas, and doesn't do 0 point agendas!
                        agendaSpread[0] = agendaSpread[0] - numGFIs
                        agendaSpread[1] = agendaSpread[1] + numGFIs 
                        #storing a GFI count here
                        agendaSpread.append(numGFIs)
                        
                        print("")
                        return agendaSpread

            case "n" | "no":
                print("")
                return agendaSpread

            case _:
                print("\nApologies, I didn't understand your response.") 
                continue  


def BuildDeck(deckSize, agendaInfo):

    nonAgendas = deckSize - agendaInfo[1]    

    deck = []

    for _ in itertools.repeat(None, nonAgendas):
        deck.append("X")

    for _ in itertools.repeat(None,agendaInfo[0][0]):
        deck.append(3)
    for _ in itertools.repeat(None,agendaInfo[0][1]):
        deck.append(2)
    for _ in itertools.repeat(None,agendaInfo[0][2]):
        deck.append(1)

    return deck

def NumOfLoops():

    while True:

        val = input("How many times would you like to run an agenda test?\n")

        try:
            testLoops = int(val)
            return testLoops  
        except ValueError:
            print("Input is not an appropriate integer.")
            continue

def showWorkAccessedList(accessList):

    print("")

    for x in range(len(accessList)):
        print(f"Test {x+1}: Cards Accessed: {accessList[x][0]}, Points Scored: {accessList[x][1]}, Agendas Stolen: {accessList[x][2]}")


def DensityTest(deck,loops):

    cardsAccessedList = []

    for x in range(loops):
       
        if SHOW_WORK:
            print(f"\n-- Test {x+1} --")
        testingDeck = Deck
        agendaPointsStolen = 0
        agendasStolen = 0
        cardsAccessed = 0
        random.shuffle(testingDeck)

        for card in testingDeck:
            cardsAccessed += 1
            if SHOW_WORK:
                print(f"Card {cardsAccessed} = {card}")
            if isinstance(card,int):
                agendaPointsStolen += card
                agendasStolen += 1

            if agendaPointsStolen >= POINTS_TO_WIN:  
                break

        cardsAccessedList.append((cardsAccessed,agendaPointsStolen,agendasStolen))
        

    if SHOW_WORK:
            showWorkAccessedList(cardsAccessedList)

    return cardsAccessedList

def average(list):
    return sum(list) / len(list)

def PlotData(cardsAccessedData, loops, dashedCardsAccessedData, agendaInfo, deckSize):

    accessFreqData = collections.Counter(cardsAccessedData)
    
    if SHOW_WORK:
        print(f"Number of Accesses: {accessFreqData.keys()}")
        print(f"Their corresponding frequencies: {accessFreqData.values()}")    

    plt.style.use('fivethirtyeight')

    plt.bar(accessFreqData.keys(),accessFreqData.values(), label="No Mad Dash")

    if dashedCardsAccessedData is not None:
        dashedAccessFreqData = collections.Counter(dashedCardsAccessedData)
        plt.bar(dashedAccessFreqData.keys(),dashedAccessFreqData.values(), alpha=0.75, label="Mad Dash")
        plt.legend()

    plt.xlabel("Number of Accesses to Win")
    plt.ylabel(f"Freq. in {loops} Simulations")
    

    if len(agendaInfo[0]) > 3:
        strNumGFIs = str(agendaInfo[0][3]) + "xGFI's, "
        strNum3s = str(agendaInfo[0][0]) + "x3's, " if agendaInfo[0][0] != 0 else ""
        strNum2s = str((agendaInfo[0][1])-agendaInfo[0][3]) + "x2's, " if agendaInfo[0][1]-agendaInfo[0][3] != 0 else ""
        strNum1s = str(agendaInfo[0][2]) + "x1's, " if agendaInfo[0][2] != 0 else ""
    
    else:
        strNumGFIs = ""
        strNum3s = str(agendaInfo[0][0]) + "x3's, " if agendaInfo[0][0] != 0 else ""
        strNum2s = str(agendaInfo[0][1]) + "x2's, " if agendaInfo[0][1] != 0 else ""
        strNum1s = str(agendaInfo[0][2]) + "x1's, " if agendaInfo[0][2] != 0 else ""

    plotTitle = str(f"Winning Accesses | {deckSize}/{agendaInfo[1]} | {strNum3s} {strNumGFIs} {strNum2s} {strNum1s}").rstrip()
    plotTitle = " ".join(plotTitle.split())   
    
    plt.title(plotTitle[:-1])  
    
    plt.tight_layout()
    
    plt.show()

def CompileData(cardsAccessedData):

    cardsAccessedList = []
    agendaPointsStolen = []
    agendasStolen = []

    for datapoint in cardsAccessedData:        
        cardsAccessedList.append(datapoint[0])
        agendaPointsStolen.append(datapoint[1])
        agendasStolen.append(datapoint[2])

    agendasStolen.sort()

    avgCardsAccessed = average(cardsAccessedList)
    avgAgendaPointsStolen = average(agendaPointsStolen)
    avgAgendasStolen = AgendaPointsStolenRatio(agendasStolen)

    return (avgCardsAccessed, avgAgendaPointsStolen, avgAgendasStolen, cardsAccessedList)

def AgendaPointsStolenRatio(agendaPointsStolen):

    agendaPointsStolenValues = [] 
    agendaPointsStolenCounts = []

    for datapoint in agendaPointsStolen:
        if datapoint not in agendaPointsStolenValues:
            agendaPointsStolenValues.append(datapoint)
            agendaPointsStolenCounts.append(1)
        else:
            agendaPointsStolenCounts[agendaPointsStolenValues.index(datapoint)] += 1

    agendaPointsStolenFinalValues = []

    for x in range(len(agendaPointsStolenValues)):
        agendaPointsStolenFinalValues.append((agendaPointsStolenValues[x],agendaPointsStolenCounts[x],(agendaPointsStolenCounts[x]/len(agendaPointsStolen))))

    return agendaPointsStolenFinalValues

   
print("\nWelcome to the Netrunner Agenda Density Calculator!\n")

if '-m' in (sys.argv):
    MAD_DASHING = True

if '-w' in (sys.argv):
    SHOW_WORK = True     

if '-p' in (sys.argv):
    PLOT_DATA = True    

deckSize = DeckSize()
minDeckSize = MinDeckSize(deckSize)
requiredAgendas = RequiredAgendas(minDeckSize)
print(f"\nYour deck contains {deckSize} cards, and requires {requiredAgendas[0]}-{requiredAgendas[1]} points of agendas!")

agendaInfo = AgendaFiller(requiredAgendas)

if SHOW_WORK:
    print(agendaInfo)

Deck = BuildDeck(deckSize,agendaInfo)

loops = NumOfLoops()

cardsAccessedData = DensityTest(Deck, loops)

finalAvgData = CompileData(cardsAccessedData)

if MAD_DASHING:
    POINTS_TO_WIN = 6
    dashingCardsAccessedData = DensityTest(Deck, loops)
    dashingFinalAvgData = CompileData(dashingCardsAccessedData)

print(f"\nThe deck has an agenda density of 1 agenda per {deckSize/agendaInfo[1]:.1f} cards.")
print(f"\nOn average, to win a game, a Runner would need to access {finalAvgData[0]} cards.")

for x in range(len(finalAvgData[2])):
    print(" - The Runner wins by stealing {agendaCount} agendas {average:.0%} of the time.".format(agendaCount = finalAvgData[2][x][0], average = finalAvgData[2][x][2]))   

print("")

if MAD_DASHING:
    print(f"If the Runner is playing Mad Dash, that average is instead {dashingFinalAvgData[0]} cards.")   
    for x in range(len(dashingFinalAvgData[2])):
        print(" - The Runner wins by stealing {dashingAgendaCount} agendas {dashingAverage:.0%} of the time.".format(dashingAgendaCount = dashingFinalAvgData[2][x][0], dashingAverage = dashingFinalAvgData[2][x][2]))   

    print("\nThe Mad Dash is 'worth' {dashability:.4f} extra accesses!".format(dashability = finalAvgData[0]-dashingFinalAvgData[0]))

if PLOT_DATA:
    if MAD_DASHING:    
        PlotData(finalAvgData[3], loops, dashingFinalAvgData[3], agendaInfo, deckSize)
    else:
        PlotData(finalAvgData[3], loops, None, agendaInfo, deckSize)

#TODO
#add 0 point agendas? That messess up the Mad Dash math.
#add negative points?
