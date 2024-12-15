def exp_manual(x, terms=50):
    result = 1.0  
    term = 1.0    # First term of the series (x^0 / 0!)
    
    for n in range(1, terms):
        term *= x / n  # x^n / n!
        result += term 
        
        if abs(term) < 1e-10:
            break
    
    return result