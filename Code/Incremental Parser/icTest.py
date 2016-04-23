from incrementalParser import IncrementalParser;
import pickle;
import time;
execfile("./params.py");

fn = "test-output-c.pkl";
def load():
    try:
        with open(fn, 'r') as f:
            return pickle.load(f);
    except IOError as e:
        return {};
        
def save(rv, timing):
    with open(fn, 'w') as f:
        pickle.dump(rv, f);
    with open("timing.txt", 'w') as f:
        f.write("\n".join([str(t) for t in timing]));
    print "Saved to %s" % fn;

def run():
    k = 0;
    scenes = load_scenes();

    split = load_data(OP_SPLIT_FN);
    tokens = load_data(OP_TOKEN_FN);
    img = load_data(OP_IMAGE_FN);
    
    rv = load();
    timing = [];
    starti = 0;
    if rv:
        starti = max(rv.iterkeys()) + 1;
    
    for i,(sp,tok,(sc,ob)) in enumerate(zip(split, tokens, img)):        
        if sp != "test":
            continue;
    
        if i < starti:
            continue;            
        
        print str(i) + ": " + " ".join(tok);
        
        k = (k + 1) % 10;
        if k == 0:
            save(rv, timing);


                
        ip = IncrementalParser(scenes[sc]);
        wlist = [];        
        for w in tok:
            print w;
            t = time.clock();
            dist = ip.next(w);
            timing.append(time.clock() - t);
            wlist.append(dist);
        
        ip.close();
        rv[i] = wlist;
        
    save(rv, timing);
    #for w in inp:
    #    dist = ip.next(w);
    #    print dist;
    # print ", ".join(".3f" % dist[ob] for ob in sc)
    
    

if __name__ == "__main__":
    print ">>" + str(time.clock());
    run();