from jenks import classes as jenks_classes
from profiles.utils import values_to_lists

default_neg_colors = ['#f00', '#f99']
default_pos_colors = ['#EDF8FB', '#B2E2E2', '#66C2A4', '#2CA25F', '#006D2C']


def classes_and_colors(data, negative_colors=default_neg_colors, positive_colors=default_pos_colors):
    """ Break data into negative and positive color classes.
    Jenks natural breaks are used.
    """
    if not data:
        return None, None
    if None in data:
        return None, None

    neg_values = filter(lambda x: x < 0, data)
    pos_values = filter(lambda x: x >= 0, data)
    neg_classes = None
    pos_classes = None

    if neg_values:
        neg_classes = jenks_classes(neg_values, len(negative_colors))
    if pos_values:
        pos_classes = jenks_classes(pos_values, len(positive_colors))

    neg_classes = neg_classes or []
    pos_classes = pos_classes or []
    classes = neg_classes + pos_classes

    colors = []
    # If there are fewer classes than colors, we should take the most saturated
    # colors first (from the right for pos, from the left for neg)
    if len(neg_classes):
        colors.extend(negative_colors[:len(neg_classes)])
    if len(pos_classes):
        colors.extend(positive_colors[len(pos_classes) * -1:])

    return (classes, colors)

def breaks_from_values(value_list):
    out = {}
    n,p,m = values_to_lists(value_list)

    # we now have 3 distict lists
    out['number'], x = classes_and_colors(n)
    out['percent'], x = classes_and_colors(p)
    out['moe'], x = classes_and_colors(m)

    return out

def breaks_from_dataset(ds, times):
    """ Returns a natural_breaks dict given the dataset """

    out = {'indicator':{},'denominators':{}}
    time_keys = [t.name for t in times]
    vals = {}
    vals['indicators'] = {}
    vals['denominators'] = {}
    for i in ds.itervalues():
        # iterating over geos data set
        ind = i['indicator']
        denoms = i['denominators']
        for t in time_keys:
            if t not in vals['indicators']:
                vals['indicators'][t] = {
                    'numbers':[],
                    'percents':[],
                    'moes':[]
                }
            vals['indicators'][t]['numbers'].append(ind[t]['number'])
            vals['indicators'][t]['percents'].append(ind[t]['percent'])
            vals['indicators'][t]['moes'].append(ind[t]['moe'])

        for d in denoms:
            if not d in vals['denominators']:
                vals['denominators'][d] ={}
            for t in time_keys:
                if not t in vals['denominators'][d]:
                    vals['denominators'][d][t] = {
                        'numbers':[],
                        'percents':[],
                        'moes':[]
                    }
                vals['denominators'][d][t]['numbers'].append(denoms[d][t]['number'])
                vals['denominators'][d][t]['percents'].append(denoms[d][t]['percent'])
                vals['denominators'][d][t]['moes'].append(denoms[d][t]['moe'])

    # finally we have to pass all the collected values to breaks
    for i in vals['indicators']:
        for n in vals['indicators'][i]:
            # and update the values
            vals['indicators'][i][n], x = classes_and_colors(vals['indicators'][i][n])
    # do the denoms
    for dn in vals['denominators']:
        for time in vals['denominators'][dn]:
            for d in vals['denominators'][dn][time]:
                vals['denominators'][dn][time][d], x = classes_and_colors(vals['denominators'][dn][time][d])

    return vals



