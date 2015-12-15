execfile("./params.py");
execfile("./unigram.py");


def computeDistribFromSNP(snp, sc, scsz):
    rv = {};
    for g in sc:
        p = 1.0;
        for w in snp:
            p *= prob(w, g, scsz);
        
        rv[g] = p;
    
    return rv;

topN = lambda dist, item, N:  dist[item] >= sorted(dist.values())[-N];
countSim = lambda dist, val: sum(1 for v in dist.values() if v == val);


def run():
    k = 0;
    
    scenes = load_scenes();
    split = load_data(OP_SPLIT_FN);
    tokens = load_data(OP_TOKEN_FN);
    img = load_data(OP_IMAGE_FN);
    prps = load_data("_PRP.tsv");
    
    ct = 0.0;
    ct2 = 0;
    tot = 0.0;
    
    
    for i,(sp,tok,(sc,ob),pr) in enumerate(zip(split, tokens, img, prps)):        
        if sp != "test":
            continue;
        
        #if "BETWEEN" not in pr:
        #    continue;
        
        
        ct += 1./sum(1 for o in scenes[sc] if o[:7] == "orange_");
        tot += 1;
        
        dist = computeDistribFromSNP(tok, scenes[sc], len(scenes[sc]));
        if topN(dist, 'orange_' + ob, 1):
            ct2 += 1.0/countSim(dist, dist['orange_' + ob]);
        #rv[i] = wlist;
    
    
    print ct/tot;
    print ct2/tot;
    
    

if __name__ == "__main__":
    run();