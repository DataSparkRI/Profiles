from decimal import Decimal

# jenks natural breaks implementation from http://danieljlewis.org/2010/06/07/jenks-natural-breaks-algorithm-in-python/
def getJenksBreaks(dataList, numClass):
    dataList.sort()
    
    if len(dataList) == 1:
        return [0] + dataList * numClass

    mat1 = []
    for i in range(0,len(dataList)+1):
        temp = []
        for j in range(0,numClass+1):
            temp.append(0)
        mat1.append(temp)
    
    mat2 = []
    for i in range(0,len(dataList)+1):
        temp = []
        for j in range(0,numClass+1):
            temp.append(0)
        mat2.append(temp)

    for i in range(1,numClass+1):
        mat1[1][i] = 1
        mat2[1][i] = 0
        for j in range(2,len(dataList)+1):
            mat2[j][i] = float('inf')
    v = 0.0
    for l in range(2,len(dataList)+1):
        s1 = 0.0
        s2 = 0.0
        w = 0.0
        
        for m in range(1,l+1):
            i3 = l - m + 1
            val = float(dataList[i3-1])
            s2 += val * val # sum of squares
            s1 += val # sum of values
            
            w += 1
            v = s2 - (s1 * s1) / w
            i4 = i3 - 1
            
            if i4 != 0:
                for j in range(2,numClass+1):
                    if mat2[l][j] >= (v + mat2[i4][j - 1]):
                        mat1[l][j] = i3
                        mat2[l][j] = v + mat2[i4][j - 1]
        mat1[l][1] = 1
        mat2[l][1] = v

    k = len(dataList)
    kclass = []
    for i in range(0,numClass+1):
        kclass.append(0)
    kclass[numClass] = float(dataList[len(dataList) - 1])
    countNum = numClass
    while countNum >= 2:
        id = int((mat1[k][countNum]) - 2)
        
        kclass[countNum - 1] = dataList[id]
        k = int((mat1[k][countNum] - 1))
        countNum -= 1

    return kclass

def breaks_to_classes(breaks):
    if len(breaks) == 0:
        return breaks
    breaks = list(set(breaks))
    breaks.sort()
    classes = []
    c = []
    for i in range(0, len(breaks)-1):
        classes.append([breaks[i], breaks[i+1]])
                
    return classes
        
def classes(data, num_classes):
    data.sort()
    if data[0] < 0 and data[-1] > 0:
        raise ValueError('negative and positive values must be separated')
    
    negate_breaks = False
    if data[0] < 0:
        # our jenks implementation works better with positive values
        data = map(lambda v: v*-1, data)
        negate_breaks = True
    
    breaks = getJenksBreaks(data, num_classes)

    if negate_breaks:
        breaks = map(lambda v: v*-1, breaks)

    # breaks don't sort properly unless they're all Decimal (or we provide a custom sort)
    def ensure_decimal(val):
        return Decimal(str(val))
    breaks.sort()
    return breaks_to_classes(breaks)

    neg_breaks = map(ensure_decimal, neg_breaks)
    if len(neg_values) > 0 and len(pos_values) > 0:
        neg_breaks = getJenksBreaks(neg_values, 2)
        pos_breaks = getJenksBreaks(pos_values, 4)
        neg_breaks = map(lambda v: v*-1, neg_breaks) # revert back to neg values
        neg_breaks.sort()
        pos_breaks.sort()
    elif len(pos_values) > 0 and len(neg_values) == 0:
        pos_breaks = getJenksBreaks(pos_values, 5)
        pos_breaks.sort()
    else:
        # all negative, use 5 breaks, as if positive        
        neg_breaks = getJenksBreaks(neg_values, 5)
        neg_breaks = map(lambda v: v*-1, neg_breaks)
        neg_breaks.sort()
    
    # breaks don't sort properly unless they're all Decimal (or we provide a custom sort)
    def ensure_decimal(val):
        return Decimal(str(val))

    neg_breaks = map(ensure_decimal, neg_breaks)
    pos_breaks = map(ensure_decimal, pos_breaks)

    return breaks_to_classes(neg_breaks), breaks_to_classes(pos_breaks)

    
