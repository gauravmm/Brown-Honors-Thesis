import pickle;

global ALPHA, intersection, wordct, master;
(ALPHA, p_intersection, p_wordct, master) = pickle.load(open('unigram.p', 'rb'));

def prob(w, grnd, n_gnd):
    mult = 1.0;
    if grnd[0:7] == "orange_":
        grnd = "orange_";
        mult = 0.125;
        
    stdVirtualProbYes = (100 + ALPHA)/(100 + ALPHA * n_gnd);
    stdVirtualProbNo  = (0   + ALPHA)/(100 + ALPHA * n_gnd);
    
    # We patch in support for VIRTUAL_YOU and VIRTUAL_ME here.
    if w in ["me", "i", "I"]:
        if grnd == "VIRTUAL_ME":
            return stdVirtualProbYes;
        else:
            return stdVirtualProbNo;
    elif w in ["robot", "you"]:
        if grnd == "VIRTUAL_YOU":            
            return stdVirtualProbYes;
        else:
            return stdVirtualProbNo;
            

    if grnd not in p_intersection:
        return 0.0;        
    
    if w not in p_wordct:
        return 1/float(n_gnd);    
    elif w in p_intersection[grnd] and w in p_wordct:
        return (p_intersection[grnd][w]*mult + ALPHA)/float(p_wordct[w] + ALPHA * n_gnd);
    else:
        return ALPHA/float(p_wordct[w] + ALPHA * n_gnd);
