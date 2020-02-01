import pandas as pd
from copy import deepcopy
import funcy
import itertools
from datetime import timedelta
import holidays


def get_horizon_dates(horizon_start, horizon_end, country):
    # get date range for horizon
    rng = pd.date_range(horizon_start, horizon_end)
    country_holidays = holidays.CountryHoliday(country, years=rng.year)

    # create list of timestamps and each date's cost (0 for weekend or public holiday, 1 for weekdays)
    date_list = []
    for x in rng:
        date_list.append(
            [x, 0 if x in country_holidays or x.weekday() in (5, 6) else 1])

    return date_list


def get_options(date_list):
    # accepts:
    #   list of timestamps and each dates cost (0 for weekend or public holiday, 1 for weekdays)
    # returns:
    #   a set of allocation options

    options = []
    for i in range(len(date_list)):

        # initialize option start and end
        option_start = date_list[i][0]
        option_end = date_list[i][0]

        # initialize cost with cost value of first day
        option_cost = initial_cost = date_list[i][1]
        # initialize benefit with 1 as current day is accounted for in cost
        option_benefit = 1

        # initialize secondary index
        j = i

        # search options for current main index date until the end of date list
        while (option_end < date_list[-1][0]):
            # set secondary index to next day
            while (j < len(date_list)-1):
                j += 1
                # current_date = date_list[j][0]  # debug variable
                option_cost += date_list[j][1]
                option_benefit += 1

                # end of opten is when:
                #   secondary date is last date in date list
                #   or
                #       some budget was consumed and
                #       current day (j) costs nothing but next day (j+1) does
                if (date_list[j][0] == date_list[-1][0]
                        or (option_cost >= (initial_cost + 1) and (date_list[j+1][1] == 1 and date_list[j][1] == 0))):

                    option_end = date_list[j][0]
                    options.append({'start': option_start.isoformat(), 'end': option_end.isoformat(), 'benefit': option_benefit,
                                    'cost': option_cost, 'benefit_cost_ratio': (option_benefit / option_cost)})
                    break

    return options


def remove_conflicting_options(option, option_list):
    # accepts:
    #   specific option
    #   list of options
    # returns:
    #   list of options that has no overlappings with given option
    option_date_range = pd.date_range(option['start'], option['end'])
    remaining_options = []
    for list_entry in option_list:
        list_entry_range = pd.date_range(
            list_entry['start'], list_entry['end'])
        if (len(option_date_range.intersection(list_entry_range)) <= 0):
            remaining_options.append(list_entry)

    return remaining_options


def get_all_allocation_proposals(budget, options, level=0):
    # accepts:
    #   budget to be allocated
    #   list of options
    # returns:
    #   a nested list of all possible allocation proposals with the best benefit cost ratios


    # filter options for affordable options and sort by cost benefit ratio
    max_benefit_cost_ratio = 0
    affordable_best_options = []
    for o in options:
        if o['cost'] <= budget:
            if o['benefit_cost_ratio'] > max_benefit_cost_ratio:
                max_benefit_cost_ratio = o['benefit_cost_ratio']
                del affordable_best_options[:]
            if o['benefit_cost_ratio'] == max_benefit_cost_ratio:
                affordable_best_options.append(o)

    if (len(affordable_best_options) > 0):
        proposals = []

        # select the best options
        for current_element in affordable_best_options:

            downstream_options = remove_conflicting_options(
                current_element, options)

            current_element['level'] = level
          
            downstream_elements = get_all_allocation_proposals(budget - current_element['cost'],
                                                               deepcopy(downstream_options), 
                                                               level + 1)
            if (len(downstream_elements) > 0):
                proposals.append([current_element] + downstream_elements)
            else:
                proposals.append([current_element])
    
        return proposals
    else:
        return []

def cleanse_allocation_proposals(raw_proposals):
    # accepts:
    #   a list of nested allocation proposals
    # returns:
    #   a filtered, flattened list of unique proposals

    #flatten proposals with funcy
    raw_proposals = funcy.lflatten(raw_proposals)

    #go through flattened list and create a list entry for each proposal path based on proposal level
    cleansed_proposals = []
    cleansed_proposal_entry = []
    previous_p_level = -1
    for rp in raw_proposals:

        #complete unique proposal and start new one when
        # level is 0 and entry is not empty (i.e. not the first iteration)
        # level is lower than previous one (i.e. new downstream proposal path)
        if ((len(cleansed_proposal_entry) > 0 and rp['level'] == 0) or rp['level'] <= previous_p_level ):
            cleansed_proposals.append(cleansed_proposal_entry[:])
            del cleansed_proposal_entry[rp['level']:]

        previous_p_level = rp['level']
        #remove no longer needed attributes
        del rp['level']
        #del rp['downstream_budget']

        cleansed_proposal_entry.append(rp)

    #add last element to final proposals    
    cleansed_proposals.append(deepcopy(cleansed_proposal_entry))

    #sort proposals by date
    raw_proposals = cleansed_proposals[:]
    del cleansed_proposals[:]
    for rp in raw_proposals:
        cleansed_proposals.append(sorted(rp, key=lambda x: (x['start'])))

    cleansed_proposals = list(cleansed_proposals for cleansed_proposals,_ in itertools.groupby(cleansed_proposals))
    return cleansed_proposals




def get_allocation_proposals(budget, horizon_start, horizon_end, holiday_country):
    # accepts:
    #   budget to be allocated
    #   horizon start date
    #   horizon end date
    # returns:
    #   a list of allocation proposals

    horizon_dates = get_horizon_dates(
        horizon_start, horizon_end, holiday_country)

    # get all options and filter for affordable ones based on budget
    affordable_options = [x for x in get_options(
        horizon_dates) if x['cost'] <= budget and x['benefit_cost_ratio'] > 1]
    #print('start')
    #print(affordable_options)
    #print('end')
    proposals = get_all_allocation_proposals(budget, affordable_options)
    proposals = cleanse_allocation_proposals(proposals)

    # calculate budget leftovers
    for p in proposals:
        p.append({'unallocated_budget' : (budget - sum(x['cost'] for x in p))})

    return proposals


proposals = get_allocation_proposals(15, '2020-01-01', '2020-01-27', 'CH')
print(proposals)
