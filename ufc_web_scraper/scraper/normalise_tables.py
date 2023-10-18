#Import libraries for data cleaning
import pandas as pd
import os

def add_primary_keys(ufc_events,ufc_fights,ufc_fight_stats,ufc_fighters):

    #Creates unique keys for each row in table
    event_id = [num for num in range(1,len(ufc_events)+1)]
    fight_id = [num for num in range(1,len(ufc_fights)+1)]
    fight_stat_id = [num for num in range(1,len(ufc_fight_stats)+1)]
    fighter_id = [num for num in range(1,len(ufc_fighters)+1)]

    #Check if primary key is already present in table
    #If not present, adds primary key to each table
    #(reversed so that new data will retain same primary key order)
    if 'event_id' not in ufc_events.columns:
        ufc_events['event_id'] = event_id[::-1]

    if 'fight_id' not in ufc_fights.columns:
        ufc_fights['fight_id'] = fight_id[::-1]

    if 'fight_stat_id' not in ufc_fight_stats.columns:
        ufc_fight_stats['fight_stat_id'] = fight_stat_id[::-1]

    if 'fighter_id' not in ufc_fighters.columns:
        ufc_fighters['fighter_id'] = fighter_id[::-1]

def add_foreign_key(ufc_events,ufc_fights,ufc_fight_stats,ufc_fighters):
    
    #Add fighter name column to ufc_fighters match with fighter names in ufc_fights/ufc_fight_stats
    ufc_fighters['fighter_name'] = ufc_fighters['fighter_f_name'] + ' ' + ufc_fighters['fighter_l_name']
    
    """
    Create dictionaries of primary keys and column in primary table to match with foreign table
    """
    
    #Dictionary of all event names and their corresponding ID
    event_id_dict = {}
    for num in range(len(ufc_events)):
        event_id_dict[ufc_events.loc[num,'event_name']]=ufc_events.loc[num,'event_id']
    
    #Dictionary of all fight urls and their corresponding ID
    fight_url_dict = {}
    for num in range(len(ufc_fights)):
        fight_url_dict[ufc_fights.loc[num,'fight_url']]=ufc_fights.loc[num,'fight_id']
    
    #Dictionary of all fighter names and their corresponding ID
    fighter_id_dict = {}
    for num in range(len(ufc_fighters)):
        fighter_id_dict[ufc_fighters.loc[num,'fighter_name']]=ufc_fighters.loc[num,'fighter_id']
    
    """
    Set foreign keys
    """
    
    #Add event_id to ufc_fights if not already present
    if 'event_id' not in ufc_fights.columns:
        ufc_fights['event_id'] = ufc_events['event_name'].map(event_id_dict)

    #Replace fighter names in ufc_fights with their fighter_id if not already changed
    if type(ufc_fights['f_1'][0])==str:
        ufc_fights['f_1'] = ufc_fights['f_1'].map(fighter_id_dict)

    if type(ufc_fights['f_2'][0])==str:
        ufc_fights['f_2'] = ufc_fights['f_2'].map(fighter_id_dict)

    if type(ufc_fights['winner'][0])==str:
        ufc_fights['winner'] = ufc_fights['winner'].map(fighter_id_dict)

    #Replace fighter names in ufc_fight_stats with their fighter_id
    if type(ufc_fight_stats['fighter_id'])==str:
        ufc_fight_stats['fighter_id'] = ufc_fight_stats['fighter_id'].map(fighter_id_dict)

    #Add fight_id to ufc_fight_stats
    if 'fight_id' not in ufc_fight_stats.columns:
        ufc_fight_stats['fight_id'] = ufc_fight_stats['fight_url'].map(fight_url_dict)


def save_to_file(ufc_events,ufc_fights,ufc_fight_stats,ufc_fighters):
    
    #Define columns for final output
    event_columns = ['event_id', 'event_name', 'event_date', 'event_city', 'event_state',
           'event_country', 'event_url']
    fight_columns = ['fight_id','event_id','referee', 'f_1', 'f_2', 'winner', 'num_rounds', 'title_fight',
           'weight_class', 'gender', 'result', 'result_details', 'finish_round',
           'finish_time', 'fight_url']
    fight_stat_columns = ['fight_stat_id', 'fight_id', 'fighter_id', 'knockdowns', 'total_strikes_att',
           'total_strikes_succ', 'sig_strikes_att', 'sig_strikes_succ',
           'takedown_att', 'takedown_succ', 'submission_att', 'reversals',
           'ctrl_time', 'fight_url']
    fighter_columns = ['fighter_id','fighter_f_name', 'fighter_l_name', 'fighter_nickname',
           'fighter_height_cm', 'fighter_weight_lbs', 'fighter_reach_cm',
           'fighter_stance', 'fighter_dob', 'fighter_w', 'fighter_l', 'fighter_d',
           'fighter_nc_dq', 'fighter_url']

    #Set columns for final output
    ufc_events = ufc_events[event_columns]
    ufc_fights = ufc_fights[fight_columns]
    ufc_fight_stats = ufc_fight_stats[fight_stat_columns]
    ufc_fighters = ufc_fighters[fighter_columns]

    #Set primary key as index
    ufc_events.set_index('event_id',inplace=True)
    ufc_fights.set_index('fight_id',inplace=True)
    ufc_fight_stats.set_index('fight_stat_id',inplace=True)
    ufc_fighters.set_index('fighter_id',inplace=True)
    
    #Saves dataframes to CSV file
    path = os.getcwd() + '/scraped_files'
    
    ufc_events.to_csv(path + '/' + 'ufc_event_data.csv')
    ufc_fights.to_csv(path + '/' + 'ufc_fight_data.csv')
    ufc_fighters.to_csv(path + '/' + 'ufc_fighter_data.csv')
    ufc_fight_stats.to_csv(path + '/' + 'ufc_fight_stat_data.csv')


def normalise_tables():

    #Import csv files to Pandas dataframe
    path = os.getcwd() + '/scraped_files'
    ufc_events = pd.read_csv(path + '/' +'ufc_event_data.csv')
    ufc_fights = pd.read_csv(path + '/' + 'ufc_fight_data.csv')
    ufc_fight_stats = pd.read_csv(path + '/' + 'ufc_fight_stat_data.csv')
    ufc_fighters = pd.read_csv(path + '/' + 'ufc_fighter_data.csv')

    #Add primary keys to tables
    print('Adding primary keys')
    add_primary_keys(ufc_events,ufc_fights,ufc_fight_stats,ufc_fighters)
    
    #Add foreign key to tables
    print('Adding foreign keys')
    add_foreign_key(ufc_events,ufc_fights,ufc_fight_stats,ufc_fighters)
    
    #Save dataframes to CSV file
    save_to_file(ufc_events,ufc_fights,ufc_fight_stats,ufc_fighters)

    print('Tables normalised')


normalise_tables()

