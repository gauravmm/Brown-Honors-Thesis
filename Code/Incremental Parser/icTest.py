from incrementalParser import IncrementalParser;
import pickle;
execfile("./params.py");


fn = "test-output-a.pkl";
def load():
    try:
        with open(fn, 'r') as f:
            return pickle.load(f);
    except IOError as e:
        return {};
        
def save(rv):
    with open(fn, 'w') as f:
        pickle.dump(rv, f);
    print "Saved to %s" % fn;

def run():
    k = 0;
    scenes = load_scenes();
    # inp = ['hand', 'me', 'the', 'orange', 'cube', 'that', 'is', 'in', 'front', 'of', 'yellow', 'bowl'];
    # inp = ['it', 'is', 'the', 'orange', 'cube', 'between', 'the', 'tan', 'and', 'blue', 'bowls', 'near', 'you'];

    split = load_data(OP_SPLIT_FN);
    tokens = load_data(OP_TOKEN_FN);
    img = load_data(OP_IMAGE_FN);
    
    rv = load();
    starti = 0;
    if rv:
        starti = max(rv.iterkeys()) + 1;
    
    for i,(sp,tok,(sc,ob)) in enumerate(zip(split, tokens, img)):        
        if sp != "test":
            continue;
    
        if i < starti:
            continue;            
        
        print i;
        
        k = (k + 1) % 10;
        if k == 0:
            save(rv);

                
        ip = IncrementalParser(scenes[sc]);
        
        wlist = [];        
        for w in tok:
            dist = ip.next(w);
            wlist.append(dist);
            
        rv[i] = wlist;
        
    save(rv);
    #for w in inp:
    #    dist = ip.next(w);
    #    print dist;
    # print ", ".join(".3f" % dist[ob] for ob in sc)
    
    

if __name__ == "__main__":
    run();