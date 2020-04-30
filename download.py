from collections import defaultdict
import dill
from itertools import chain
import ClauseWizard

file_path = 'gamestate'
curr_save_date = '1457_07_10'
curr_year = '1457'

RELOAD = False


def inverse_dict_list_vals(old_dict):
    new_dict = {}
    for k, v in old_dict.items():
        for x in v:
            new_dict[x] = k
    return new_dict


def get_ledger_data_dict(statistic_type):
    return {country['name']: country['data'][curr_year] for country in
            json_formatted_string[statistic_type]['ledger_data']}


def print_statistics_per_team_from_ledger(stat_dict, team_dict):
    for team in team_dict.keys():
        print(
            team,
            f'total: {sum([stat_dict[tag] for tag in team_dict[team] if isinstance(stat_dict[tag], (int, float))])}',
            [(tag, stat_dict[tag]) for tag in team_dict[team] if isinstance(stat_dict[tag], (int, float))],
        )
    print('\n')


def print_statistics_per_team_from_countries(stat_dict, team_dict, stat):
    print(stat)
    for team in team_dict.keys():
        print(
            f'{team} total: {sum([stat_dict[tag][stat] for tag in team_dict[team] if isinstance(stat_dict[tag][stat], (int, float))])}')
        print(
            [(tag, stat_dict[tag][stat]) for tag in team_dict[team] if isinstance(stat_dict[tag][stat], (int, float))])
    print('\n')


def get_all_loans(stat_dict, team_dict):
    print('loans')
    for team in team_dict.keys():
        team_loans = []
        for tag in team_dict[team]:
            if isinstance(stat_dict[tag]['loan'], defaultdict):
                team_loans.append((tag, stat_dict[tag]['loan']['amount'] or 0))
            else:
                team_loans.append((tag, sum([loan['amount'] for loan in stat_dict[tag]['loan']])))
        print(f'{team} total: {sum([loan_size for (country, loan_size) in team_loans])}')
        print(team_loans)
    print('\n')


if RELOAD is True:
    with open(file_path, 'r', encoding='iso8859_4') as f:
        data = f.read()
        tokens = ClauseWizard.cwparse(data)  # returns a list of tokens
        json_formatted_string = ClauseWizard.cwformat(tokens)  # returns a JSON-formatted string

    with open(f'{curr_save_date}_data_string.pkl', "wb") as f:
        dill.dump(json_formatted_string, f)
else:
    with open(f'{curr_save_date}_data_string.pkl', "rb") as f:
        json_formatted_string = dill.load(f)

players = json_formatted_string['players_countries'][::2]
player_tags = json_formatted_string['players_countries'][1::2]
player_tag_dict = dict(zip(players, player_tags))

team_members_dict = {team['name']: team['member'] for team in json_formatted_string['teams']['team']}
tag_team_dict = inverse_dict_list_vals(team_members_dict)

teams = team_members_dict.keys()

income_dict = get_ledger_data_dict('income_statistics')
score_dict = get_ledger_data_dict('score_statistics')

print_statistics_per_team_from_ledger(income_dict, team_members_dict)
print_statistics_per_team_from_ledger(score_dict, team_members_dict)

country_dict = json_formatted_string['countries']
print_statistics_per_team_from_countries(country_dict, team_members_dict, 'manpower')
print_statistics_per_team_from_countries(country_dict, team_members_dict, 'max_manpower')

team_vassal_dict = {team: [] for team in teams}
for tag in country_dict.keys():
    overlord = country_dict[tag]['overlord']
    if overlord:
        overlord_team = tag_team_dict.get(overlord)
        if overlord_team:
            team_vassal_dict[overlord_team].append(tag)
vassal_team_dict = inverse_dict_list_vals(team_vassal_dict)

team_vassal_squared_dict = {team: [] for team in teams}
for tag in country_dict.keys():
    overlord = country_dict[tag]['overlord']
    if overlord:
        overlord_team = vassal_team_dict.get(overlord)
        if overlord_team:
            team_vassal_squared_dict[overlord_team].append(tag)

faction_dict = {team: team_vassal_dict[team] + team_members_dict[team] + team_vassal_squared_dict[team] for team in
                teams}
print_statistics_per_team_from_countries(country_dict, faction_dict, 'manpower')
print_statistics_per_team_from_countries(country_dict, faction_dict, 'max_manpower')
print_statistics_per_team_from_countries(country_dict, faction_dict, 'raw_development')
print_statistics_per_team_from_countries(country_dict, faction_dict, 'estimated_monthly_income')
print_statistics_per_team_from_countries(country_dict, faction_dict, 'estimated_monthly_income')
print_statistics_per_team_from_countries(country_dict, faction_dict, 'treasury')
print_statistics_per_team_from_countries(country_dict, faction_dict, 'total_war_worth')
get_all_loans(country_dict, faction_dict)

[col for col in country_dict['FRA'].keys() if 'str' in col]
country_dict['FRA']['army']