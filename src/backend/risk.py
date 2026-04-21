def risk_analysis(prob:float)->str:
    if prob<=0.1:
        return 'low'
    elif prob>0.1 and prob<=0.2:
        return 'moderate'
    elif prob>0.2 and prob<=0.3:
        return 'medium'
    elif prob>0.3 and prob<=0.4:
        return 'high'
    else:
        return 'very high'