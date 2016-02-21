import pickle;
from math import log, floor;
import matplotlib.pyplot as plt
import numpy as np;

execfile("./params.py");


fn = "test-output-a.pkl";
def load():
    try:
        with open(fn, 'r') as f:
            return pickle.load(f);
    except IOError as e:
        return {};


scenes = load_scenes();
split = load_data(OP_SPLIT_FN);
tokens = load_data(OP_TOKEN_FN);
img = load_data(OP_IMAGE_FN);
preps = load_data("_PRP.tsv");
irr = load_data("_interrater.csv");

topN = lambda dist, item, N:  dist[item] >= sorted(dist.values())[-N];
top1 = lambda dist, item:  dist[item] >= max(dist);
top2 = lambda dist, item:  dist[item] >= sorted(dist.values())[-2];
top3 = lambda dist, item:  dist[item] >= sorted(dist.values())[-3];

countSim = lambda dist, val: sum(1 for v in dist.values() if v == val);

    
pos = lambda dist, item: sum(1 for k,v in dist.iteritems() if k[1:7] == "orange_" and v >= dist[item]);

def run():
    plt.close("all");
    k = 0;
    
    rv = load();

    for i,(sp,tok,(sc,ob),lprp) in enumerate(zip(split, tokens, img, preps)):
        if i != 368:
            continue;
        if i in rv:
            dist = rv[i][-1];
            score = topN(dist, 'orange_' + ob, 1)*1./countSim(dist, dist['orange_' + ob]);
            
            if score == 1:
                print i;
                print tok;
                print sc;
                print ob;
                for di in rv[i]:
                    #print di;
                    v = [di['orange_' + str(o + 1)] for o in range(6)];
                    print [floor(val * 100) for val in v];
                    #print [1-floor(val * 100)/100 for val in v];

        #print rv[i];
    
    #computeBatchTable(rv);
    #plotNCorrectnessByFraction(rv, 5);
    #plotNCorrectnessByWord(rv, 5);
    #computeCorrectnessInterrater(rv);
    
    # scatterEntropy(rv);
    #plotNCorrectnessByWord(rv, 5);
            
    # for i,(sp,tok,(sc,ob)) in enumerate(zip(split, tokens, img)):
            
def computeCorrectnessInterrater(rv):

    # Build the interrater dict;
    intrr = {};
    for row in irr:
        intrr[int(row[0])] = int(row[1]);
    
    
    scr = [0, 0, 0, 0];
    total = [0, 0, 0, 0];
    top_n_v = 3;
    
    for i,(sp,tok,(sc,ob),lprp) in enumerate(zip(split, tokens, img, preps)):
        if i in rv:
            dist = rv[i][-1];
            score = topN(dist, 'orange_' + ob, top_n_v)*1./countSim(dist, dist['orange_' + ob]);
            
            for j in range(0, intrr[i] + 1):
                scr[j] += score;
                total[j] += 1;
                
    for i in range(4):
        print "%d\t%.1f%%\t%d" % (i, scr[i]*100./total[i], total[i])
        

def computeBatchTable(rv):
    prepositions = ['BETWEEN', 'NEAR', 'BEHIND', 'IN_FRONT_OF', 'LEFT_OF', 'RIGHT_OF', '*'];
    scoring = ['Human', 'Unigram', 'Random', 'Top-1', 'Top-3']
    correct = dict((p,dict((s,0) for s in scoring)) for p in prepositions);
    total = dict((p,0) for p in prepositions);

    # 'BETWEEN', 'NEAR', 'BEHIND', 'IN_FRONT_OF', 'LEFT_OF', 'RIGHT_OF', '*'
    human = [.882, .825, .769, .699, .898, .580, .790];
    unigram = [.143, .172, .157, .179, .161, .154, .161];
    human = dict(zip(prepositions, human));
    unigram = dict(zip(prepositions, unigram));
    
    for i,(sp,tok,(sc,ob),lprp) in enumerate(zip(split, tokens, img, preps)):
        if i in rv:
            dist = rv[i][-1];
            
            tlprp = ['*'] + [p for p in prepositions if p in lprp];
            
            scr = dict((s,0) for s in scoring);
            scr['Top-1'] = topN(dist, 'orange_' + ob, 1)*1./countSim(dist, dist['orange_' + ob]);
            scr['Top-3'] = topN(dist, 'orange_' + ob, 3)*1./countSim(dist, dist['orange_' + ob]);
            scr['Random'] = 1.0/len(scenes[sc]);
            
            for p in tlprp:
                for s in scr:
                    correct[p][s] += scr[s];
                total[p] += 1;

 
     # Output it all latex-like
    tt = float(total["*"]);
    for p in prepositions:
        t = float(total[p]);
        l = "%.1f\\%% & \\textit{%s}" % (t/tt*100, p.lower().replace("_", " "));

        l += " "* max(24 - len(l), 0)        
        
        for s in scoring:
            score = (correct[p][s]*100.0/t);
            if s == "Human":
                score = human[p]*100;

            if s == "Unigram":
                score = unigram[p]*100;            
            
            l += "\t& %.1f" % score;
        
        l += " \\\\"
        print l;
        print
#   35.1\% & \textit{between}	  &    74.5 &  20.0 &   6.0 & 77.0 & 54.1 \\
    
        
            
            


def entropy(dist):
    return sum(-1*log(d)*d for v,d in dist.iteritems());
    
def plotCorrectnessByWord(rv, iscorrect):
    correct = [0] * 25;
    total = [0] * 25;
    
    for i,(sp,tok,(sc,ob)) in enumerate(zip(split, tokens, img)):
        if i in rv:
            for j,dist in enumerate(rv[i]):
                total[j] += 1;
                if iscorrect(dist, 'orange_' + ob):
                    correct[j] += 1;
    
    print correct;
    
    plt.figure();
    plt.plot(range(25), correct, range(25), total);
    plt.title("CDF of correct and total sentences.");
    plt.xlabel("Number of words.");
    plt.ylabel("Number of sentences.");
    plt.legend(["Correct", "Total"]);

    frac = [c/float(t) if t > 0 else 0 for c,t in zip(correct, total)];
    
    plt.figure();
    plt.plot(range(25), frac);
    plt.title("Fraction of total sentences correct.");
    plt.xlabel("Number of words.");
    plt.ylabel("Fraction of sentences correct.");


def plotNCorrectnessByWord(rv, numtot):
    total = [0] * 25;
    correct = np.zeros([numtot, 25]);
    
    for i,(sp,tok,(sc,ob)) in enumerate(zip(split, tokens, img)):
        if i in rv:
            for j,dist in enumerate(rv[i]):
                total[j] += 1;
                
                for k in range(numtot):
                    if topN(dist, 'orange_' + ob, k + 1):
                        correct[k, j] += 1./countSim(dist, dist['orange_' + ob]);
    
    print correct;
    
    plt.figure();
    plt.hold("on");

    legend_key = [];
    legend_val = [];    
    
    p1, = plt.plot(range(25), total);
    legend_key.append(p1);
    legend_val.append("Total");
    
    for k in range(numtot):
        p1, = plt.plot(range(25), correct[k, :])
        legend_key.append(p1);
        legend_val.append("Top-" + str(k + 1));

    plt.hold("off");
    
    plt.title("CDF of correct and total sentences.");
    plt.xlabel("Number of words.");
    plt.ylabel("Number of sentences.");
    plt.legend(legend_key, legend_val);

def plotNCorrectnessByFraction(rv, numtot):
    interpres = 100;
    intpX = np.arange(0,1,1.0/interpres);
    
    correct = np.zeros([numtot, interpres]);
    total = 0;
    
    for i,(sp,tok,(sc,ob)) in enumerate(zip(split, tokens, img)):
        if i in rv:
            print rv[i][0];
            
            total += 1;
            t = float(len(rv[i]));
            for k in range(numtot):                    
                t_x = [(n + 1)/t for n in range(len(rv[i]))];
                t_corr = [topN(dist, 'orange_' + ob, k + 1)*1./countSim(dist, dist['orange_' + ob]) for dist in rv[i]];
                correct[k,:] += np.interp(intpX, t_x, t_corr);
    
    #print correct;
    
    plt.figure();
    plt.hold("on");

    legend_key = [];
    legend_val = [];    
    
    for k in range(numtot):
        p1, = plt.plot(intpX, correct[k, :]/total)
        legend_key.append(p1);
        legend_val.append("Top-" + str(k + 1));
        
    plt.xlim([0, 1]);
    plt.ylim([0, 1]);
    
    plt.hold("off");
    
    plt.title("Correctness rate by fraction of sentence.");
    plt.xlabel("Fraction of sentence.");
    plt.ylabel("Fraction correct.");
    plt.legend(legend_key, legend_val, loc=2);



def scatterEntropy(rv):
    x = [];
    y = [];
    for i,dists in rv.iteritems():
        l = float(len(dists));
        for j,dist in enumerate(dists):
            x.append(j/l);
            y.append(entropy(dist));
            
    heatmap, xedges, yedges = np.histogram2d(x, y, bins=50)
    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    
    plt.clf()
    plt.imshow(heatmap, extent=extent)
    plt.show()


        
# test = load();

if __name__ == "__main__":
    run();