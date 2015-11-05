import pickle;

global ALPHA, intersection, wordct, master;
(ALPHA, p_intersection, p_wordct, master) = pickle.load(open('unigram.p', 'rb'));

def prob(w, grnd, n_gnd):
    mult = 1.0;
    if grnd[0:7] == "orange_":
        grnd = "orange_";
        mult = 0.125;

    if grnd not in p_intersection:
        return 0.0;        
    
    if w not in p_wordct:
        return 1/float(n_gnd);    
    elif w in p_intersection[grnd] and w in p_wordct:
        return (p_intersection[grnd][w]*mult + ALPHA)/float(p_wordct[w] + ALPHA * n_gnd);
    else:
        return ALPHA/float(p_wordct[w] + ALPHA * n_gnd);
