import itertools
import random
import sys
import collections
from matplotlib import pyplot as plt

# Agenda Density Calculator - Andrej Gomizelj (04/12/23)
# Tutorial video available on youtube.com/metropolegrid
#
# A utility to calculate the 'defensibility' of various agenda suites in Android: Netrunner

POINTS_TO_WIN = 7

# mad dash flags
MAD_DASHING = False
SIMULATE_MAD_DASH_DECK_ONE = False
SIMULATE_MAD_DASH_DECK_TWO = False
SIMULATE_MAD_DASH_DECK_THREE = False

# deck setup flags
FIRST_DECK_SETUP = True
SECOND_DECK_SETUP = False
THIRD_DECK_SETUP = False

# plotting options
PLOT_DATA = False
PLOT_WINRATE = False

# additional mode flags
NEG_AGENDAS = False
COMPARE = False
DOUBLE_COMPARE = False
DECKSIZE_OVERRIDE = False
LIMITED_MODE = False
SHOW_WORK = False
WRITE_OUTPUT = False
STANDARD_LOOPS = False

STANDARD_LOOP_NUMBER = 500000


def yes_no(message):

# returns True/False based on a yes/no text input

    while True:
        response = input(f"{message} (y/n)\n").lower()
        match response:
            case "y" | "yes":    
                return True
            case "n" | "no":               
                return False
            case _:
                print("\nApologies, I didn't understand your response.") 
                continue 


def flag_checker(args):

# reads command line arguments and sets corresponding flags

    global COMPARE
    global DOUBLE_COMPARE
    global MAD_DASHING       
    global NEG_AGENDAS    
    global POINTS_TO_WIN
    global PLOT_WINRATE
    global PLOT_DATA
    global SHOW_WORK 
    global DECKSIZE_OVERRIDE
    global LIMITED_MODE
    global WRITE_OUTPUT
    global STANDARD_LOOPS

    # compairson mode
    if '-c' in (args):
        COMPARE = True 

    # double comparison mode
    elif '-cc' in (args):
        DOUBLE_COMPARE = True 

    # fast mad dashing mode
    elif '-m' in (args):
        MAD_DASHING = True

    # debug mode
    if '-d' in (args):
        SHOW_WORK = True     

    # plot accessdata
    if '-pa' in (args):
        PLOT_DATA = True  

    # plot cumulative winrate
    if '-pwr' in (args):
        PLOT_WINRATE = True

    # plot cumulative winrate
    if '-wo' in (args):
        WRITE_OUTPUT = True

    # plot cumulative winrate
    if '-sl' in (args):
        STANDARD_LOOPS = True
     
    # allow negative agenda points 
    if '-n' in (args):
        NEG_AGENDAS = True 

    # limited mode (play to 6 points)
    if '-l' in (args):
        LIMITED_MODE = True

    # deck override mode (doesn't check to see if you're reaching required agenda points)
    if '-do' in (args):
        DECKSIZE_OVERRIDE = True

    if '-m' in (args) and '-c' in (args):
        print("'-m' is used for a comparison of the impact of 'Mad Dash'. It can not be combined with '-c'.\nDefaulting to comparison ('-c') mode!\n")

    if '-c' in (args) and '-cc' in (args):
        print("'-c' can not be combined with '-cc'.\nDefaulting to single comparison ('-c') mode!\n")


def get_deck_name(agenda_spread, deck_size):

    deck_name = "" + str(deck_size) + "/" + str(agenda_spread["total"]) + " | "    

    for x in agenda_spread:        
        if agenda_spread[x] != 0 and not x.startswith("total"):
            deck_name += str(agenda_spread[x]) + "x"            
            deck_name += str(x) + "'s, "   

    return deck_name[:-2]


def input_deck_size():

    while True:

        deck_size = input("How many cards are in your deck?\n")

        try:
            val = int(deck_size)
        except ValueError:
            print("Input is not an appropriate integer.\n")
            continue

        if val < 5:
            print("Kindly input a deck size larger than 5!\n")
        else:
            return val
 

def min_deck_size(deck_size):

    min_deck_size_diff = deck_size%5
    min_deck_size = deck_size - min_deck_size_diff

    return min_deck_size   


def required_agendas(min_deck_size):

    baseline = 40
    baseline_agenda_count = 18
    baseline_diff = (min_deck_size - baseline)/5

    required_agendas = baseline_agenda_count + (2*baseline_diff)

    return (int(required_agendas),int(required_agendas+1))


def fill_agendas(required_agendas):

    agenda_spread = {
        "3": 0,
        "GFI": 0,
        "2": 0,
        "1": 0,
        "-1": 0,
        "total": 0,
        "total_cards": 0
    }

    while True:

        print("\nKindly input how many agendas you have of each point denomination.")

        while True:
            val = input(" - Three point agendas: ")
            try:
                num_3s = int(val)
            except ValueError:
                print("Input is not an appropriate integer.")
                continue
            if num_3s >= 0:
                break
            else:
                print("Input is not an appropriate integer.")
      

        while True:
            val = input(" - Two point agendas: ")
            try:
                num_2s = int(val)
            except ValueError:
                print("Input is not an appropriate integer.")
                continue
            if num_2s >= 0:
                break
            else:
                print("Input is not an appropriate integer.")

        while True:
            val = input(" - One point agendas: ")
            try:
                num_1s = int(val)
            except ValueError:
                print("Input is not an appropriate integer.")
                continue
            if num_1s >= 0:
                break
            else:
                print("Input is not an appropriate integer.")

        # if we're modelling negative one point agendas        
        if NEG_AGENDAS:
                while True:
                    val = input(" - Negative one point agenda cards: ")
                    try:
                        num_neg_1s = int(val)
                    except ValueError:
                        print("Input is not an appropriate integer.")
                        continue
                    if num_neg_1s >= 0:
                        break
                    else:
                        print("Input is not an appropriate integer.")
        
        agenda_sum = (3*num_3s) + (2*num_2s) + (1*num_1s)
        
        if required_agendas is not None:
            if agenda_sum != required_agendas[0] and agenda_sum != required_agendas[1]:
                print(f"\nYour deck is expected to contain {required_agendas[0]}-{required_agendas[1]} agenda points, but currently contains {agenda_sum} agenda points.")
                print("Please re-enter your agenda selection!")
                continue
               
        num_agendas = num_3s+num_2s+num_1s
        if NEG_AGENDAS:
            total_agenda_type_cards = num_3s+num_2s+num_1s+num_neg_1s
        else:
            total_agenda_type_cards = num_agendas

        print(f"\nYour deck contains {agenda_sum} agenda points across {num_agendas} agendas:")
        print(f" - [{num_3s}] Three point agendas")
        print(f" - [{num_2s}] Two point agendas")        
        print(f" - [{num_1s}] One point agendas")
        if NEG_AGENDAS:
            print(f" - [{num_neg_1s}] Negative one point cards")  

        agenda_spread["3"] = num_3s
        agenda_spread["2"] = num_2s
        agenda_spread["1"] = num_1s
        agenda_spread["total"] = num_agendas
        agenda_spread["total_cards"] = total_agenda_type_cards
        
        if NEG_AGENDAS:
            agenda_spread["-1"] = num_neg_1s

        #if the deck contains 3's, ask if any are GFI and update accordingly
        if num_3s != 0:   
            agenda_spread = gfi_question(agenda_spread)

        if SHOW_WORK:
            if yes_no("[DEBUG] Would you like to see the Agenda spread information?"):
                print(f"Agenda Spread: {agenda_spread}\n")  

        return agenda_spread


def gfi_question(agenda_spread):

    if yes_no("\nDoes your deck contain any copies of Global Food Initiative?"):
        
        while True:
            val = input("\nHow many Global Food Initiative's does the deck contain?\n")

            try:
                num_GFIs = int(val)            
            except ValueError:
                print("Input is not an appropriate integer.")
                continue
    
            if num_GFIs > agenda_spread["3"]:
                print("\nYou can not have more Global Food Initiative's than three point agendas in your deck!")
                continue

            else:
                agenda_spread["3"] = agenda_spread["3"] - num_GFIs
                agenda_spread["GFI"] = num_GFIs
               
                return agenda_spread

    return agenda_spread


def build_deck(deck_size, agenda_info):

    deck = []

    for _ in itertools.repeat(None,agenda_info["3"]):
        deck.append(3)
    for _ in itertools.repeat(None,agenda_info["GFI"]):
        deck.append("GFI")
    for _ in itertools.repeat(None,agenda_info["2"]):
        deck.append(2)
    for _ in itertools.repeat(None,agenda_info["1"]):
        deck.append(1)
    if NEG_AGENDAS:
        for _ in itertools.repeat(None,agenda_info["-1"]):
            deck.append(-1)

    #non agenda cards is deck size - number of agendas
    non_agendas = deck_size - agenda_info["total_cards"]   
    for _ in itertools.repeat(None, non_agendas):
        deck.append("X")

    if SHOW_WORK:
        if yes_no("[DEBUG] Would you like to see the deck?"):        
            print(f"Deck ({len(deck)}/{agenda_info['total']}): {deck}")

    return deck


def input_num_simulations():

    if STANDARD_LOOPS:
        return STANDARD_LOOP_NUMBER
    
    else:

        while True:

            val = input("\nHow many times would you like to run an agenda test?\n")

            try:
                num_simulations = int(val)
                return num_simulations  
            except ValueError:
                print("Input is not an appropriate integer.")
                continue


def show_test_access_results(access_list):

    print("")

    for x in range(len(access_list)):
        print(f"Test {x+1}: Cards Accessed: {access_list[x]['total_accesses']}, Points Scored: {access_list[x]['final_score']}, Agendas Stolen: {access_list[x]['agenda_cards_stolen']}")


def run_agenda_simulation(deck, num_simulations, dashing):

# returns an array (with length equal to num_simulations) containing the access information of each individual simulation
# each entry in the array returns a dict:
#   entry['total_accesses'] : the number of access to win in this simulation (int)
#   entry['final_score'] : the final score when the Runner won in this simulation (int)
#   entry['agenda_cards_stolen'] : the number of agendas stolen whenn the Runner won in this simulation (int)
#   entry['3'] : the number of 3 point agendas stolen in this simulation (int)
#   entry['GFI'] : the number of Global Food Initiatives stolen in this simulation (int)
#   entry['2'] : the number of 2 point agendas stolen in this simulation (int)
#   entry['1'] : the number of 1 point agendas stolen in this simulation (int)
#   entry['-1'] : the number of -1 point agendas stolen in this simulation (int)

    OUTPUT_TEST_RESULTS = False

    if SHOW_WORK:
        if yes_no("\n[DEBUG] Would you like to see the output of each individual simulation?\n(I would HEAVILY advise against this if you're running a high quantity of simulations.)"):
            OUTPUT_TEST_RESULTS = True

    full_cards_accessed_list = []

    if dashing:
        print(f"\nRunning Mad Dash simulation!\n(This may take a moment.)")
    else:
        print(f"\nRunning simulation!\n(This may take a moment.)")
    
    for x in range(num_simulations):
       
        if OUTPUT_TEST_RESULTS:
            print(f"\n-- Test {x+1} --")

        simulation_deck = deck
        random.shuffle(simulation_deck)

        single_simulation_cards_accessed_list = {            
            "total_accesses": 0,
            "final_score": 0,
            "agenda_cards_stolen": 0,            
            "3": 0,
            "GFI": 0,
            "2": 0,
            "1": 0,
            "-1": 0
        }  

        for card in simulation_deck:

            single_simulation_cards_accessed_list["total_accesses"] += 1            
            
            if isinstance(card, int): 
                single_simulation_cards_accessed_list["final_score"] += card
                single_simulation_cards_accessed_list[str(card)] += 1            
                if card >= 0:                    
                    single_simulation_cards_accessed_list["agenda_cards_stolen"] += 1                   

            elif card == "GFI":
                single_simulation_cards_accessed_list["final_score"] += 2                
                single_simulation_cards_accessed_list[card] += 1
                single_simulation_cards_accessed_list["agenda_cards_stolen"] += 1

            if OUTPUT_TEST_RESULTS:
                print(f"Card {single_simulation_cards_accessed_list['total_accesses']} = {card} [Total Points: {single_simulation_cards_accessed_list['final_score']}]")

            if single_simulation_cards_accessed_list["final_score"] >= POINTS_TO_WIN:  
                break

        if OUTPUT_TEST_RESULTS:  
            print(f"\nTest {x+1} Summary: {single_simulation_cards_accessed_list}")                      

        full_cards_accessed_list.append(single_simulation_cards_accessed_list)        

    if SHOW_WORK:
        if yes_no("\n[DEBUG] Would you like to see the summary of each simulation?\n(I would HEAVILY advise against this if you're running a high quantity of simulations.)"):
            show_test_access_results(full_cards_accessed_list)

    return full_cards_accessed_list


def average(list):
    return sum(list) / len(list)


def get_textbox_limits(access_freq_data_1, access_freq_data_2, access_freq_data_3):

    if access_freq_data_3 is None:
        textbox_x_max = max(max(access_freq_data_1.keys()), max(access_freq_data_2.keys()))
        textbox_y_max = max(max(access_freq_data_1.values()), max(access_freq_data_2.values()))        

    else:
        textbox_x_max = max(max(access_freq_data_1.keys()), max(access_freq_data_2.keys()), max(access_freq_data_3.keys()))
        textbox_y_max = max(max(access_freq_data_1.values()), max(access_freq_data_2.values()), max(access_freq_data_3.values()))

    return [textbox_x_max, textbox_y_max]


def plot_access_data(cards_accessed_data_1, deck_name_1, num_simulations, dashed_cards_accessed_data, cards_accessed_data_2, deck_name_2):
   
    TEXT_Y_OFFSET = num_simulations/400

    # create the data sets we will be plotting
    access_freq_data_1 = collections.Counter(cards_accessed_data_1["num_cards_accessed_list"])
    pos_winrate_accesses_1 = cards_accessed_data_1['cumulative_sum_winrate_data']['num_accesses_for_positive_winrate']    

    if cards_accessed_data_2 is not None:
        access_freq_data_2 = collections.Counter(cards_accessed_data_2["num_cards_accessed_list"])
        pos_winrate_accesses_2 = cards_accessed_data_2['cumulative_sum_winrate_data']['num_accesses_for_positive_winrate']
        
    if dashed_cards_accessed_data is not None:            
            dashed_access_freq_data = collections.Counter(dashed_cards_accessed_data["num_cards_accessed_list"])
            dashed_pos_winrate_accesses = dashed_cards_accessed_data['cumulative_sum_winrate_data']['num_accesses_for_positive_winrate']            
    
    # if debugging, show the raw data that will be plotted
    if SHOW_WORK:
        if yes_no("[DEBUG] Would you like to see the data that will be plotted?"):
            print(f"\n-- {deck_name_1} --")
            print(f"Number of Accesses / Corresponding Frequency: {access_freq_data_1}")
            if MAD_DASHING:
                print(f"\n-- {deck_name_1} w/ Mad Dash --")
                print(f"Number of Accesses / Corresponding Frequency: {dashed_access_freq_data}")
            if COMPARE:
                print(f"\n-- {deck_name_2} --")
                print(f"Number of Accesses / Corresponding Frequency: {access_freq_data_2}")

    plt.style.use('fivethirtyeight')
   
    # if we're doing a simple mad dashing comparison
    if dashed_cards_accessed_data is not None:
       
        textbox_limits = get_textbox_limits(access_freq_data_1, dashed_access_freq_data, None)

        # plot 'main' data
        plt.bar(access_freq_data_1.keys(),
                access_freq_data_1.values(),
                label="No Mad Dash")

        plt.text(x = textbox_limits[0], 
                 y = textbox_limits[1] - 4.5*TEXT_Y_OFFSET,
                 s = 'P≥0.5 = ' + str(pos_winrate_accesses_1) + ' accesses', 
                 horizontalalignment='right', 
                 verticalalignment='top', 
                 fontsize = 12, 
                 bbox=dict(facecolor = '#008FD5', alpha = 0.6, edgecolor = 'black')) 
        
        # plot dashing information
        plt.bar(dashed_access_freq_data.keys(),
                dashed_access_freq_data.values(),
                alpha=0.75,
                label="Mad Dash")
        
        plt.text(x = textbox_limits[0], 
                 y = textbox_limits[1] - 6.5*TEXT_Y_OFFSET,
                 s = 'P≥0.5 = ' + str(dashed_pos_winrate_accesses) + ' accesses', 
                 horizontalalignment='right', 
                 verticalalignment='top', 
                 fontsize = 12, 
                 bbox=dict(facecolor = '#FC4F30', alpha = 0.6, edgecolor = 'black'))

        # include a legend
        plt.legend()

    # if we're doing a single comparison
    elif cards_accessed_data_2 is not None:        

        textbox_limits = get_textbox_limits(access_freq_data_1, access_freq_data_2, None)

        # plot basic data
        plt.bar(access_freq_data_1.keys(),
                access_freq_data_1.values(),
                label = deck_name_1)
        
        plt.text(x = textbox_limits[0], 
                 y = textbox_limits[1] - 4.5*TEXT_Y_OFFSET,
                 s = 'P≥0.5 = ' + str(pos_winrate_accesses_1) + ' accesses', 
                 horizontalalignment='right', 
                 verticalalignment='top', 
                 fontsize = 12, 
                 bbox=dict(facecolor = '#008FD5', alpha = 0.6, edgecolor = 'black'))

        # plot single comparison data
        plt.bar(access_freq_data_2.keys(),
                access_freq_data_2.values(),
                alpha = 0.75,
                label = deck_name_2)    

        plt.text(x = textbox_limits[0], 
                 y = textbox_limits[1] - 6.5*TEXT_Y_OFFSET,
                 s = 'P≥0.5 = ' + str(pos_winrate_accesses_2) + ' accesses', 
                 horizontalalignment='right', 
                 verticalalignment='top', 
                 fontsize = 12, 
                 bbox=dict(facecolor = '#FC4F30', alpha = 0.6, edgecolor = 'black'))
          
        # include a legend
        plt.legend()

    else:
        # otherwise plot basic data
        plt.bar(access_freq_data_1.keys(),
                access_freq_data_1.values(), 
                label = deck_name_1)
        
        plt.text(x = max(access_freq_data_1.keys()), 
                 y = max(access_freq_data_1.values()),
                 s = 'P≥0.5 = ' + str(pos_winrate_accesses_1) + ' accesses', 
                 horizontalalignment='right', 
                 verticalalignment='top', 
                 fontsize = 12, 
                 bbox=dict(facecolor = '#008FD5', alpha = 0.6, edgecolor = 'black'))

    plt.xlabel("Number of Accesses to Win")
    plt.ylabel(f"Freq. in {num_simulations} Simulations")    

    if not COMPARE:
        if not LIMITED_MODE:
            plotTitle = "Freq. of # of Accesses to Win\n" + str(num_simulations) + " Simulations | " + str(deck_name_1) 
        else:
             plotTitle = "Freq. of # of Accesses to Win (6 Pt. Limited)\n" + str(num_simulations) + " Simulations | " + str(deck_name_1) 
    else:
        if not LIMITED_MODE:
            plotTitle = "Freq. of # of Number of Accesses to Win\nacross " + str(num_simulations) + " Simulations"
        else:
            plotTitle = "Freq. of # of Number of Accesses to Win (6 Pt. Limited)\nacross " + str(num_simulations) + " Simulations"
    
    plt.title(plotTitle)  
    
    plt.tight_layout()
    
    plt.show()


def plot_access_data_double_comparison(cards_accessed_data_1, deck_name_1, num_simulations, dashed_cards_accessed_data, cards_accessed_data_2, deck_name_2, cards_accessed_data_3, deck_name_3):
   
    TEXT_Y_OFFSET = num_simulations/400

    # create the data sets we will be plotting
    access_freq_data_1 = collections.Counter(cards_accessed_data_1["num_cards_accessed_list"])
    access_freq_data_2 = collections.Counter(cards_accessed_data_2["num_cards_accessed_list"])
    access_freq_data_3 = collections.Counter(cards_accessed_data_3["num_cards_accessed_list"])

    pos_winrate_accesses_1 = cards_accessed_data_1['cumulative_sum_winrate_data']['num_accesses_for_positive_winrate']
    pos_winrate_accesses_2 = cards_accessed_data_2['cumulative_sum_winrate_data']['num_accesses_for_positive_winrate']    
    pos_winrate_accesses_3 = cards_accessed_data_3['cumulative_sum_winrate_data']['num_accesses_for_positive_winrate']        

    if SHOW_WORK:
        if yes_no("[DEBUG] Would you like to see the data that will be plotted?"):
            print(f"\n-- {deck_name_1} --")
            print(f"Number of Accesses / Corresponding Frequency: {access_freq_data_1}")
            if COMPARE or DOUBLE_COMPARE:
                print(f"\n-- {deck_name_2} --")
                print(f"Number of Accesses / Corresponding Frequency: {access_freq_data_2}")
            if DOUBLE_COMPARE:
                print(f"\n-- {deck_name_3} --")
                print(f"Number of Accesses / Corresponding Frequency: {access_freq_data_3}")

    plt.style.use('fivethirtyeight')

    textbox_limits = get_textbox_limits(access_freq_data_1, access_freq_data_2, access_freq_data_3)

    # plot basic data
    plt.plot(access_freq_data_1.keys(),
             access_freq_data_1.values(),
             label=deck_name_1)
    
    plt.text(x = textbox_limits[0], 
             y = textbox_limits[1] - 6.5*TEXT_Y_OFFSET,
             s = 'P≥0.5 = ' + str(pos_winrate_accesses_1) + ' accesses', 
             horizontalalignment='right', 
             verticalalignment='top', 
             fontsize = 12, 
             bbox=dict(facecolor = '#008FD5', alpha = 0.6, edgecolor = 'black')) 

    # plot single comparison data
    plt.plot(access_freq_data_2.keys(),
             access_freq_data_2.values(),
             label=deck_name_2) 
    
    plt.text(x = textbox_limits[0], 
             y = textbox_limits[1] - 8.5*TEXT_Y_OFFSET,
             s = 'P≥0.5 = ' + str(pos_winrate_accesses_2) + ' accesses', 
             horizontalalignment='right', 
             verticalalignment='top', 
             fontsize = 12, 
             bbox=dict(facecolor = '#FC4F30', alpha = 0.6, edgecolor = 'black'))
    
    # plot double comparison data
    plt.plot(access_freq_data_3.keys(),
             access_freq_data_3.values(),
             label=deck_name_3) 

    plt.text(x = textbox_limits[0], 
             y = textbox_limits[1] - 10.5*TEXT_Y_OFFSET,
             s = 'P≥0.5 = ' + str(pos_winrate_accesses_3) + ' accesses', 
             horizontalalignment='right', 
             verticalalignment='top', 
             fontsize = 12, 
             bbox=dict(facecolor = '#E5AE38', alpha = 0.6, edgecolor = 'black'))

    plt.legend()

    plt.xlabel("Number of Accesses to Win")
    plt.ylabel(f"Freq. in {num_simulations} Simulations")

    plotTitle = "Freq. of # of Accesses to Win\nacross " + str(num_simulations) + " Simulations"
    
    plt.title(plotTitle)  
    
    plt.tight_layout()
    
    plt.show()


def plot_winrate_data(cards_accessed_data_1, deck_name_1, num_simulations, dashed_cards_accessed_data, cards_accessed_data_2, deck_name_2, cards_accessed_data_3, deck_name_3):

    TEXT_Y_OFFSET = 0.1

    num_cards_accessed_1, winrate_at_num_accesses_1, pos_winrate_point_1, pos_winrate_x_1, pos_winrate_y_1, = generate_winrate_data(cards_accessed_data_1)    
    textbox_x_min = num_cards_accessed_1[0] 

    if cards_accessed_data_2 is not None:        
        num_cards_accessed_2, winrate_at_num_accesses_2, pos_winrate_point_2, pos_winrate_x_2, pos_winrate_y_2, = generate_winrate_data(cards_accessed_data_2)    
        textbox_x_min = min(num_cards_accessed_1[0], num_cards_accessed_2[0])

    if cards_accessed_data_3 is not None:
        num_cards_accessed_3, winrate_at_num_accesses_3, pos_winrate_point_3, pos_winrate_x_3, pos_winrate_y_3, = generate_winrate_data(cards_accessed_data_3)    
        textbox_x_min = min(num_cards_accessed_1[0], num_cards_accessed_2[0], num_cards_accessed_3[0])
   
    plt.rcdefaults()

    if dashed_cards_accessed_data is not None: 
        
        dashed_num_cards_accessed, dashed_winrate_at_num_accesses, dashed_pos_winrate_point, dashed_pos_winrate_x, dashed_pos_winrate_y, = generate_winrate_data(dashed_cards_accessed_data)     

        plt.plot(num_cards_accessed_1, 
                 winrate_at_num_accesses_1, 
                 label = "No Mad Dash", 
                 color = '#008FD5', 
                 marker = 'o', 
                 markevery = pos_winrate_point_1, 
                 markersize = 10)    
        
        plt.text(x = dashed_num_cards_accessed[0], 
                 y = 1.0,
                 s = 'P≥0.5 = [' + str(pos_winrate_x_1[0]) +', '+ str(pos_winrate_y_1) +']', 
                 horizontalalignment='left', 
                 verticalalignment='top', 
                 fontsize = 12, 
                 bbox=dict(facecolor = '#008FD5', alpha = 0.6, edgecolor = 'black'))

        plt.plot(dashed_num_cards_accessed, 
                 dashed_winrate_at_num_accesses, 
                 label = "Mad Dash", 
                 color = '#FC4F30', 
                 marker = 'o', 
                 markevery = dashed_pos_winrate_point, 
                 markersize = 10)                
        
        plt.text(x = dashed_num_cards_accessed[0], 
                 y = 1.0 - TEXT_Y_OFFSET,
                 s = 'P≥0.5 = [' + str(dashed_pos_winrate_x[0]) +', '+ str(dashed_pos_winrate_y) +']', 
                 horizontalalignment='left', 
                 verticalalignment='top', 
                 fontsize = 12, 
                 bbox=dict(facecolor = '#FC4F30', alpha = 0.6, edgecolor = 'black')) 

        plt.legend(fontsize=14, loc = 'lower right')

    else:

        plt.plot(num_cards_accessed_1, 
                 winrate_at_num_accesses_1, 
                 label = deck_name_1, 
                 marker = 'o', 
                 markevery = pos_winrate_point_1, 
                 markersize = 10)        

        plt.text(x = textbox_x_min, 
                 y = 1.0, 
                 s = 'P≥0.5 = [' + str(pos_winrate_x_1[0]) +', '+ str(pos_winrate_y_1) +']', 
                 horizontalalignment='left', 
                 verticalalignment='top',
                 fontsize = 12, 
                 bbox=dict(facecolor = '#008FD5', alpha = 0.6, edgecolor = 'black'))

        if cards_accessed_data_2 is not None:

            plt.plot(num_cards_accessed_2, 
                     winrate_at_num_accesses_2, 
                     label = deck_name_2,
                     color = '#FC4F30',  
                     marker = 'o',                      
                     markevery = pos_winrate_point_2, 
                     markersize = 10)

            plt.text(x = textbox_x_min, 
                     y = 1.0 - TEXT_Y_OFFSET,
                     s = 'P≥0.5 = [' + str(pos_winrate_x_2[0]) +', '+ str(pos_winrate_y_2) +']', 
                     horizontalalignment='left', 
                     verticalalignment='top', 
                     fontsize = 12, 
                     bbox=dict(facecolor = '#FC4F30', alpha = 0.6, edgecolor = 'black'))

            if cards_accessed_data_3 is not None:

                plt.plot(num_cards_accessed_3, 
                        winrate_at_num_accesses_3, 
                        label = deck_name_3,
                        color = '#E5AE38',  
                        marker = 'o',                      
                        markevery = pos_winrate_point_3, 
                        markersize = 10)

                plt.text(x = textbox_x_min, 
                        y = 1.0 - TEXT_Y_OFFSET - TEXT_Y_OFFSET,
                        s = 'P≥0.5 = [' + str(pos_winrate_x_3[0]) +', '+ str(pos_winrate_y_3) +']', 
                        horizontalalignment='left', 
                        verticalalignment='top', 
                        fontsize = 12, 
                        bbox=dict(facecolor = '#E5AE38', alpha = 0.6, edgecolor = 'black'))

            plt.legend(fontsize=14, loc = 'lower right')

            
    plt.xlabel("Number of Accesses", fontsize=18)
    plt.ylabel(f"Probability of Winning", fontsize=18)    

    if cards_accessed_data_2 is None:
        plotTitle = "Probability of Winning vs. # Accesses\n" + str(num_simulations) + " Simulations | " + str(deck_name_1) 
    else:
        plotTitle = "Probability of Winning vs. # Accesses\nacross " + str(num_simulations) + " Simulations"    
    
    plt.title(plotTitle, fontsize=22) 
    
    plt.tight_layout()

    plt.grid(which='major', color='#DDDDDD', linewidth=0.8)
    plt.grid(which='minor', color='#EEEEEE', linewidth=0.7)
    plt.minorticks_on()
   
    plt.show()


def generate_winrate_data(cards_accessed_data):

    num_cards_accessed = []
    winrate_at_num_accesses = []    

    for x in cards_accessed_data['cumulative_sum_winrate_data']['freq_accessed_table']:
        num_cards_accessed.append(x[0])
        winrate_at_num_accesses.append(x[1])     

    pos_winrate_point = [num_cards_accessed.index(cards_accessed_data['cumulative_sum_winrate_data']['num_accesses_for_positive_winrate'])]    

    pos_winrate_x = cards_accessed_data['cumulative_sum_winrate_data']['freq_accessed_table'][(pos_winrate_point[0])]
    pos_winrate_y = round(pos_winrate_x[1],2)

    return num_cards_accessed, winrate_at_num_accesses, pos_winrate_point, pos_winrate_x, pos_winrate_y  


def find_full_range(data_1, data_2, data_3):

    full_range = []

    start = min(data_1[0][0], data_2[0][0], data_3[0][0])    
    end = max(data_1[-1][0], data_2[-1][0], data_3[-1][0])       

    for i in range(start, end+1):
        full_range.append(i)
  
    return full_range


def pair_across_full_range(values, full_range):

    on_full_range = []

    FOUND = False

    for x in full_range:
        for y in values:
            if y[0] == x:
                on_full_range.append(y[1])
                FOUND = True
                break
        if not FOUND:
            on_full_range.append(0)
        found = False
   
    return on_full_range
 

def compile_data(accessed_data, num_simulations):

# returns a dictionary containing compiled data from the results of all simulations
# dict['average_num_cards_accessed'] : the average number of accesses needed to win across all simulations (we originally thought this would be useful. It ain't.) (float)
# dict['cumulative_sum_winrate_data'] : returns a dictionary containing cumulative wirate data - see cumulative_sum_winrate_by_accesses() for more info (dict)
# dict['average_agenda_points_stolen'] : the number average number of agenda points stolen to win across all simulations (float)
# dict['agendas_stolen_data'] : returns a list containing data about the amount of agendas stolen to win - see num_agendas_stolen_data() for more info (list)
# dict['num_cards_accessed_list'] : an ordered len(num_simulations) list containing the number of cards accessed in each simulation (list(int))
# dict['num_negatives_stolen_list'] : a len(num_simulations) list containing the number of negative 1 agenda points stolen in each simulation (list(int))

    # a len(num_simulations) long list of the total numbers of accesses to win
    num_cards_accessed_list = []

    # a len(num_simulations) long list of the final agenda scores    
    final_scores_list = []

    # a len(loop) long list of the number of agenda cards stolen
    num_agenda_cards_stolen_list = []

    # a len(loop) long list of the number of negative one point agendas stolen
    num_negatives_stolen_list = []

    for simulation in accessed_data:        
        num_cards_accessed_list.append(simulation["total_accesses"])
        num_negatives_stolen_list.append(simulation["-1"])
        final_scores_list.append(simulation["final_score"])
        num_agenda_cards_stolen_list.append(simulation["agenda_cards_stolen"])        

    final_scores_list.sort()
    num_cards_accessed_list.sort()

    compiled_data = {
        # the average number of agendas in which our simulation wins
        # this is not the number we should be highlighting
        "average_num_cards_accessed": average(num_cards_accessed_list),

        # the cumulative winrate data across all simulations       
        "cumulative_sum_winrate_data": cumulative_sum_winrate_by_accesses(num_cards_accessed_list, num_simulations),

        # the average number of agenda points the simulation wins on. Not super useful
        "average_agenda_points_stolen": average(final_scores_list),

        # the average number of agendas the Runner stole, and their corresponding likeliness
        "agendas_stolen_data": num_agendas_stolen_data(num_agenda_cards_stolen_list),        

        # a len(num_simulations) sorted list of all the number of cards accessed in each simulation
        "num_cards_accessed_list": num_cards_accessed_list,

        # a len(num_simulations) list of all the negative agenda points stolen in each simulation
        "num_negatives_stolen_list": num_negatives_stolen_list
    } 

    return compiled_data


def cumulative_sum_winrate_by_accesses(cards_accessed_list, num_simulations):

# returns the cumulative win rate of each unique number of accesses across all simulations     
# returns a dict
# dict['freq_accessed_table'] returns a sorted list
#   for each list entry:
#   - entry[0] : amount of accesses which won the game (eg. we won in '12' accesses) (int)
#   - entry[1] : the cumulative winrate at that number of accesses (eg. at 12 accesses, our cumulative winrate was 0.265) (float)
# dict['num_accesses_for_positive_winrate'] returns an int
#   - the number of accesses needed to reach a ≥ 50% winrate (int)

    unique_num_accessed_values_list = list(set(cards_accessed_list))
    unique_num_accessed_values_list.sort()    
   
    unique_accesses_with_freq = []

    for x in unique_num_accessed_values_list:
        unique_accesses_with_freq.append([x,cards_accessed_list.count(x)])  

    if SHOW_WORK:
        if yes_no("\n[DEBUG] Would you like to see the list of unique number of accesses and their corresponding frequencies?"):
            for x in unique_accesses_with_freq:
                print(f"{x[0]} accesses: {x[1]} occurences")

    # freq_accessed_table [x,y]:
    #   x is the number of accesses
    #   y is the corresponding cumulative winrate at x accesses
    #   eg: P(x3) = P(x3) + P(x2) + P(x1)
    #
    # num_accesses_for_positive_winrate:
    #   the number of accesses in which we hit a 50% win rate

    win_rate_at_num_accesses_list = {
        "freq_accessed_table": [],
        "num_accesses_for_positive_winrate": 0
    }    

    running_freq = 0    
    FOUND50 = False

    for x in unique_accesses_with_freq:
        next_weight = (x[1]/num_simulations+ running_freq)
        if not FOUND50:
            if next_weight >= 0.5:
                FOUND50 = True
                win_rate_at_num_accesses_list["num_accesses_for_positive_winrate"] = x[0]
                #print(f"We've hit a >50% win rate at {x[0]} accesses!")
        running_freq = next_weight
        win_rate_at_num_accesses_list["freq_accessed_table"].append([x[0], next_weight])

    if SHOW_WORK:
        if yes_no("\n[DEBUG] Would you like to see a summary of the cumulative winrate?"):
            print("\n-- Cumulative Chance to Win at X Number of Accesses --")
            for x in win_rate_at_num_accesses_list["freq_accessed_table"]:
                print("{num_accesses} accesses: {win_percent}% chance to win.".format(num_accesses = x[0], win_percent = round(x[1]*100, 3)))

    return win_rate_at_num_accesses_list


def num_agendas_stolen_data(agenda_points_stolen_data):

# returns a sorted list containing the information about the number of agendas stolen across all simulations
# for each list entry:
#   - entry[0] : amount of agendas stolen (eg. we won in '3' agenda steals) (int)
#   - entry[1] : # of occurences said amount of agendas were stolen (eg. we won in 3 agenda steals '612' times) (int)
#   - entry[2] : percent chance of winning in given # of occurences across all simluations (eg. we won in 3 agenda steals '0.23' of the time) (float)

    agenda_points_stolen_values_list = [] 
    agenda_points_stolen_counts_list = []

    for datapoint in agenda_points_stolen_data:
        if datapoint not in agenda_points_stolen_values_list:
            agenda_points_stolen_values_list.append(datapoint)
            agenda_points_stolen_counts_list.append(1)
        else:
            agenda_points_stolen_counts_list[agenda_points_stolen_values_list.index(datapoint)] += 1

    agenda_points_stolen_final_values_list = []    

    for x in range(len(agenda_points_stolen_values_list)):
        agenda_points_stolen_final_values_list.append((agenda_points_stolen_values_list[x], agenda_points_stolen_counts_list[x], (agenda_points_stolen_counts_list[x]/len(agenda_points_stolen_data))))

    agenda_points_stolen_final_values_list.sort()   
    
    return agenda_points_stolen_final_values_list


def print_results(deck_name, deck, deck_number, agenda_info, average_data):
   
    if deck_number is not None:
        print(f"\nDeck {deck_number}: | {deck_name}\n")
    else:
        print(f"\nDeck: | {deck_name}\n")

    print(f"Agenda Density: 1 agenda per {len(deck) / agenda_info['total']:.1f} cards")    
    print(f"The Runner reaches a ≥50% win rate at {average_data['cumulative_sum_winrate_data']['num_accesses_for_positive_winrate']} accesses.")

    if WRITE_OUTPUT:
        print("outputting!")        
        output = str(deck_name) + ": " + str(average_data['cumulative_sum_winrate_data']['num_accesses_for_positive_winrate']) + "\n"        
        with open('readme.txt', 'a') as f:
            f.write(output)            
    
    print_number_of_winning_agenda_outcomes(average_data) 


def print_number_of_winning_agenda_outcomes(average_data):

    for x in range(len(average_data['agendas_stolen_data'])):
        print(" - The Runner wins by stealing {agenda_count} agendas {average:.0%} of the time.".format(agenda_count = average_data['agendas_stolen_data'][x][0], average = average_data['agendas_stolen_data'][x][2]))   


def print_comparison_results(average_data_1, average_data_2):

    access_diff = average_data_2['cumulative_sum_winrate_data']['num_accesses_for_positive_winrate'] - average_data_1['cumulative_sum_winrate_data']['num_accesses_for_positive_winrate']

    if access_diff > 0:
        print(f"\nDeck Two requires {access_diff} more accesses for the Runner to reach a ≥50% win rate.")
    elif access_diff < 0:
        print(f"\nDeck One requires {abs(access_diff)} more accesses for the Runner to reach a ≥50% win rate.")
    else:
        print(f"\nBoth decks require the same amount of accesses ({average_data_2['cumulative_sum_winrate_data']['num_accesses_for_positive_winrate']}) for the Runner to hit a ≥50% win rate.")    


# START

print("\nWelcome to the Netrunner Agenda Density Calculator!\n")

# check the command line arguments and set the appropriate modifiers
flag_checker(sys.argv)

# -- RUN SIMLUATIONS SECTION --

while True:
    
    # ask's for deck size
    deck_size = input_deck_size()

    if DECKSIZE_OVERRIDE:
        agenda_info = fill_agendas(None)

    else:
        # calculates mininmum deck size, and required amount of agenda points       
        required_agenda_total = required_agendas(min_deck_size(deck_size))
        print(f"\nYour deck contains {deck_size} cards, and requires {required_agenda_total[0]}-{required_agenda_total[1]} points of agendas!")

        # input amounts of different denominations of agendas
        agenda_info = fill_agendas(required_agenda_total)

    # creates deck with corresponding decksize and distribution of agendas
    deck = build_deck(deck_size, agenda_info)
   
    # asks if a single or double comparison deck should be mad dashing
    if COMPARE or DOUBLE_COMPARE:
        if yes_no("\nWould you like to simulate Mad Dash (the Runner wins on 6 points stolen)?"):
            if FIRST_DECK_SETUP:
                SIMULATE_MAD_DASH_DECK_ONE = True                       
            elif SECOND_DECK_SETUP:
                SIMULATE_MAD_DASH_DECK_TWO = True                  
            elif THIRD_DECK_SETUP:
                SIMULATE_MAD_DASH_DECK_THREE = True                
   
    # generate deck name
    deck_name = get_deck_name(agenda_info, deck_size)    
   
    # ask for number of simulations
    if FIRST_DECK_SETUP:
        num_simulations = input_num_simulations()

    # runs simulation #loop times

    # if doing a comparison
    if COMPARE or DOUBLE_COMPARE:
        
        if LIMITED_MODE:
            POINTS_TO_WIN = 6   
        else:    
            POINTS_TO_WIN = 7   

        # checks if we're mad dashing, and runs simulations
        if FIRST_DECK_SETUP:
            if SIMULATE_MAD_DASH_DECK_ONE:        
                POINTS_TO_WIN -= 1  
            cards_accessed_data = run_agenda_simulation(deck, num_simulations, False)

        # checks if we're mad dashing the second deck, and runs simulations
        elif SECOND_DECK_SETUP:
            if SIMULATE_MAD_DASH_DECK_TWO:        
                POINTS_TO_WIN -= 1                     
            cards_accessed_data = run_agenda_simulation(deck, num_simulations, False)

        # checks if we're mad dashing the third deck, and runs simulations
        elif THIRD_DECK_SETUP:
            if SIMULATE_MAD_DASH_DECK_THREE:        
                POINTS_TO_WIN -= 1                     
            cards_accessed_data = run_agenda_simulation(deck, num_simulations, False)

    # otherwise runs simulations
    else:

        if LIMITED_MODE:
            POINTS_TO_WIN = 6 

        cards_accessed_data = run_agenda_simulation(deck, num_simulations, False)

    # calculates average data
    final_compiled_data = compile_data(cards_accessed_data, num_simulations)

    # if mad dashing, calculate the 'dashing' simulation of the given deck
    if MAD_DASHING:
        POINTS_TO_WIN -= 1
        dashing_cards_accessed_data = run_agenda_simulation(deck, num_simulations, True)
        dashing_final_compiled_data = compile_data(dashing_cards_accessed_data, num_simulations)

    # if we're doing a single or double comparison
    if COMPARE or DOUBLE_COMPARE:

        if FIRST_DECK_SETUP:            
            # assign deckNameONE
            if SIMULATE_MAD_DASH_DECK_ONE:
                deck_name_1 = deck_name + " w/ Mad Dash"
            else:
                deck_name_1 = deck_name  
            # lock in information regarding deckONE
            agenda_info_1 = agenda_info
            deck_1 = deck        
            cards_accessed_data_1 = cards_accessed_data
            final_compiled_data_1 = final_compiled_data   
            # loop back to ask for deckTWO
            print(f"\nFirst deck (| {deck_name_1}) locked in!\nPlease enter your second deck's information:\n")
            FIRST_DECK_SETUP = False     
            SECOND_DECK_SETUP = True
            continue

        if SECOND_DECK_SETUP:
            # assign deckNameTWO
            if SIMULATE_MAD_DASH_DECK_TWO:
                deck_name_2 = deck_name + " w/ Mad Dash"
            else:    
                deck_name_2 = deck_name   
            # lock in information regarding deckTWO
            agenda_info_2 = agenda_info
            deck_2 = deck
            cards_accessed_data_2 = cards_accessed_data
            final_compiled_data_2 = final_compiled_data
            # if doing a double comparison, loop back to ask for deckTHREE
            if DOUBLE_COMPARE:
                print(f"\nFirst deck (| {deck_name_1}) locked in!")
                print(f"Second deck (| {deck_name_2}) locked in!\nPlease enter your third deck's information:\n")
                SECOND_DECK_SETUP = False
                THIRD_DECK_SETUP = True
                continue
            else:
                break

        if THIRD_DECK_SETUP:
            # assign deckNameTHREE
            if SIMULATE_MAD_DASH_DECK_THREE:
                deck_name_3 = deck_name + " w/ Mad Dash"
            else:    
                deck_name_3 = deck_name
            # lock in information regarding deckTHREE    
            agenda_info_3 = agenda_info
            deck_3 = deck
            cards_accessed_data_3 = cards_accessed_data
            final_compiled_data_3 = final_compiled_data
            break

    else:
        break

# -- DISPLAY RESULTS SECTION --

# if not doing a comparison
if not COMPARE and not DOUBLE_COMPARE:

    # print results for deck
    print_results(deck_name, deck, None, agenda_info, final_compiled_data)

    # if mad dashing, calculate and show the dashed-deck infor and calculate and display 'dashability'
    if MAD_DASHING:
        print(f"\nIf the Runner is playing Mad Dash, they need to access {dashing_final_compiled_data['cumulative_sum_winrate_data']['num_accesses_for_positive_winrate']} cards instead:")
        print_number_of_winning_agenda_outcomes(dashing_final_compiled_data)    
        print("\nThe Mad Dash is 'worth' {dashability} extra accesses!".format(dashability = final_compiled_data['cumulative_sum_winrate_data']['num_accesses_for_positive_winrate']-dashing_final_compiled_data['cumulative_sum_winrate_data']['num_accesses_for_positive_winrate']))        
        
        # plot data
        if PLOT_DATA:   
            plot_access_data(final_compiled_data, deck_name, num_simulations, dashing_final_compiled_data, None, None) 
        if PLOT_WINRATE:
                plot_winrate_data(final_compiled_data, deck_name, num_simulations, dashing_final_compiled_data, None, None, None, None)        

    # plot data
    else:   
        if PLOT_DATA:
            plot_access_data(final_compiled_data, deck_name, num_simulations, None, None, None)
        if PLOT_WINRATE:
            plot_winrate_data(final_compiled_data, deck_name, num_simulations, None, None, None, None, None)
        

# if doing a single or double comparison
else:

    # print results for deckONE and deckTWO
    print_results(deck_name_1, deck_1, "One", agenda_info_1, final_compiled_data_1)
    print_results(deck_name_2, deck_2, "Two", agenda_info_2, final_compiled_data_2) 

    if COMPARE:

        # show the difference in ≥50% win rates accesses between the two single comparison decks
        print_comparison_results(final_compiled_data_1, final_compiled_data_2)
        
        # plot single comparison results
        if PLOT_DATA:
            plot_access_data(final_compiled_data_1, deck_name_1, num_simulations, None, final_compiled_data_2, deck_name_2)  
        if PLOT_WINRATE:
            plot_winrate_data(final_compiled_data_1, deck_name_1, num_simulations, None, final_compiled_data_2, deck_name_2, None, None)
        
    
    elif DOUBLE_COMPARE:

        # print results for deckTHREE
        print_results(deck_name_3, deck_3, "Three", agenda_info_3, final_compiled_data_3)

        # plot double comparison results
        if PLOT_DATA:
            plot_access_data_double_comparison(final_compiled_data_1, deck_name_1, num_simulations, None, final_compiled_data_2, deck_name_2, final_compiled_data_3, deck_name_3)
        if PLOT_WINRATE:
            plot_winrate_data(final_compiled_data_1, deck_name_1, num_simulations, None, final_compiled_data_2, deck_name_2, final_compiled_data_3, deck_name_3)
    

print("")


