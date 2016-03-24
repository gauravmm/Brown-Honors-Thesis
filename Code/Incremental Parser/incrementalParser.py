import os;
from models import *;

execfile("./params.py");
execfile("./unigram.py");

splitpart = "test";
#JAVAPATH = "C:\\Program Files\\Java\\jre1.8.0_45\\bin\\java.exe";
JAVAPATH = "java";

UNK_OBJ = "**UNK_OBJ**";
NEXT_PRP_OBJ = "**NEXT_PRP_OBJ**";

def prod(l):
    p = 1.;
    for i in l:
        p *= i;
    return p;


class IncrementalParser(object):
    
    def __init__(self, sc):
        self.sc = sc;
        self.scsz = len(sc);
        self.inp = [];
        self.tags = [];
        self.snpcache = {};
        self.prpcache = {};
        self.uniformPrior = dict((q, 1/float(self.scsz)) for q in self.sc);
        
        # Load prepositional model
        self.mod = model_logistic();
        #mod = model_normal();
        self.mod.load();


    def next(self, w):
        self.inp.append(w);
        self.tags = self.newTags();
               
        # Repeat the tree building:        
        nodes = get_nodes(self.tags, self.inp); 
        nodes = [n for n in nodes if node_filter(n)];
        struc = self.nodesToStructure(nodes);
        
        
        struc['tgt'] = self.getSNPDist(struc['tgt']); 
        struc['qual'] = [self.getPRPDist(typ, snp) for (typ, snp) in struc['qual'] if typ in preps];

        self.dist = self.mergeDist([struc['tgt']] + struc['qual']);

        return self.dist;
        
    
    def mergeDist(self, dists):
        return self.normDist(self.filterDist(dict((o, prod(d[o] for d in dists)) for o in self.sc)));

    def filterDist(self, dist):
        return dict((o, dist[o]) for o in dist if not o[0:8] == "VIRTUAL_");
    
    def normDist(self, dist):
        s = sum(dist.itervalues());
        return dict((o, dist[o]/s) for o in dist);
        
    def getPRPDist(self, k, p):
        
        if isinstance(p, basestring):
            p = [[p]];
        
        if isinstance(p[0], basestring):
            p = [p];
        
        prp_sig = k + "_" + "__".join("_".join(o) for o in p);            
            
        if prp_sig not in self.prpcache:
            snps = [self.uniformPrior] + [self.getSNPDist(s) for s in p];
            
            bf_ground, bf, transform, model_filter, bf_generator = self.mod.get_features(k);        
            dist_out = dict((o,0) for o in self.sc);
            for gnd in bf_generator(self.sc.keys()):
                # Zip the distributions with the groundings and calculate the value:
                prob_gnd = prod(dst[g] for dst, g in zip(snps,gnd));
                
                if prob_gnd == 0:
                    continue;
                dist_out[gnd[0]] += prob_gnd * self.mod.test(k, [self.sc[o] for o in gnd]);
                
                
            self.prpcache[prp_sig] = dist_out;        
            
        return self.prpcache[prp_sig];
        
    
    def snpToString(self, snp):
        return ("_".join(snp)).lower();
        
    def computeDistribFromSNP(self, snp):
        rv = {};
        for g in self.sc:
            p = 1.0;
            for w in snp:
                p *= prob(w, g, self.scsz);
            
            rv[g] = p;
        
        return rv;
    
    def getSNPDist(self, snp):
        strsnp = self.snpToString(snp);
        if strsnp not in self.snpcache:
            self.snpcache[strsnp] = self.computeDistribFromSNP(snp);
        return self.snpcache[strsnp];


    def nodesToStructure(self, nodes):        
        rv = {};
        rv['tgt'] = [];
        rv["qual"] = [];
                
        PREV_CONJ_ELLIGIBLE = False;
        while nodes:
            (p_type, p_items) = nodes[0];
            nodes = nodes[1:];
                        
            if p_type == "SNP":
                rv['tgt'] += p_items;
                PREV_CONJ_ELLIGIBLE = False;
                
            elif p_type == "PRP":
                PREV_CONJ_ELLIGIBLE = False;
                # Assume that the only multiple-binding preposition is BETWEEN.
                # Other single-binding prepositions other SNPs (or other PRPs)
                # if a CONJ is next to them
            
                p_sim = simplify_prp(p_items);
                if p_sim == "PRP_UNKNOWN":
                    pass; # Drop it.
                elif p_sim == "BETWEEN":
                    # Evaluate the between clauses:
                    p_between = (p_sim, []);
                    while len(nodes) >= 2:
                        if nodes[0][0] == "SNP" and nodes[1][0] == "PRP" and intersection(nodes[1][1], ["and", ",", "&"]):
                            p_between[1].append(nodes[0][1]);
                            nodes = nodes[2:];
                        else:
                            break;
                    if nodes and nodes[0][0] == "SNP":
                        p_between[1].append(nodes[0][1]);
                        nodes = nodes[1:];
                    # Pad it out.
                    while len(p_between[1]) < 2:
                        p_between[1].append([UNK_OBJ]);
                    rv["qual"].append(p_between);
                else:
                    if nodes and nodes[0][0] == "SNP":
                        rv["qual"].append((p_sim, nodes[0][1]));
                        nodes = nodes[1:];
                        PREV_CONJ_ELLIGIBLE = True;
                    elif nodes and nodes[0][0] == "CONJ":
                        rv["qual"].append((p_sim, NEXT_PRP_OBJ));
                        nodes = nodes[1:];
                    else:
                        rv["qual"].append((p_sim, UNK_OBJ));
            elif p_type == "REL":
                PREV_CONJ_ELLIGIBLE = False;
                rv["qual"].append((p_type, p_items));
            elif p_type == "CONJ":
                # Do nothing
                if PREV_CONJ_ELLIGIBLE and nodes and nodes[0][0] == "SNP":
                    rv["qual"].append((rv["qual"][-1][0], nodes[0][1]));
                    nodes = nodes[1:];
            else:
                PREV_CONJ_ELLIGIBLE = False;
            
        return rv;
            
        
    def newTags(self):
        # Pass self.inp to mallet, get the answers back.
        # java -cp "mallet-deps.jar;class" cc.mallet.fst.SimpleTagger --model-file crf-model-1 mallet_test.txt
        d = os.getcwd();
        try:
            os.chdir('mallet/');
            
            with open("inp.txt", 'w') as f:
                f.write("\n".join(self.inp + [""]));
                    
            out = "";        
            try:
                cmd = [JAVAPATH, "-cp", "\"mallet-deps.jar;class\"", "cc.mallet.fst.SimpleTagger", "--model-file", "crf-model-1", "inp.txt", ">", "out.txt"];
                os.system(" ".join(cmd));            
                
                with open("out.txt", 'r') as f:
                    out = f.readlines();
                    out = [o.strip() for o in out[0:-1]];
            except:
                print "Call to Mallet failed";
                raise;
                
            return out;
        finally:
            os.chdir(d);
        

def run():
    # inp = ['hand', 'me', 'the', 'orange', 'cube', 'that', 'is', 'in', 'front', 'of', 'yellow', 'bowl'];
    #inp = ['it', 'is', 'the', 'orange', 'cube', 'between', 'the', 'tan', 'and', 'blue', 'bowls', 'near', 'you'];
    inp = ['the', 'orange', 'cube', 'closest', 'to', 'you'];


    scene_name = '3';
    
    scenes = load_scenes();
    sc = scenes[scene_name];
    
    ip = IncrementalParser(sc);
    
    

    for w in inp:
        dist = ip.next(w);
        print w + "\t" + ", ".join(str(ob) + ": " + str(dist["orange_" + str(ob)]) for ob in range(1, 8) if "orange_" + str(ob) in sc);
    
    

if __name__ == "__main__":
    run();

