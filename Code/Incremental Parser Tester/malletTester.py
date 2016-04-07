import os;
from models import *;

execfile("./params.py");
execfile("./unigram.py");

splitpart = "test";
#JAVAPATH = "C:\\Program Files\\Java\\jre1.8.0_45\\bin\\java.exe";
JAVAPATH = "java";


v = load_data(OP_TOKEN_FN);
split = load_data(OP_SPLIT_FN);

def tags(inp):
    # Pass inp to mallet, get the answers back.
    # java -cp "mallet-deps.jar;class" cc.mallet.fst.SimpleTagger --model-file crf-model-1 mallet_test.txt
    d = os.getcwd();
    try:
        os.chdir('mallet/');
        
        with open("inp.txt", 'w') as f:
            f.write("\n".join(inp + [""]));
                
        out = "";        
        try:
            cmd = [JAVAPATH, "-cp", "\"mallet-deps.jar;class\"", "cc.mallet.fst.SimpleTagger", "--model-file", "crf-model-1", "inp.txt", ">", "out.txt"];
            os.system(" ".join(cmd));            
            
            with open("out.txt", 'r') as f:
                out = f.readlines();
                out = [o.strip() for o in out[0:-1]];
        except:
            print "Call to Mallet failed";
            exit();
            
        return out;
    finally:
        os.chdir(d);
        
        
sc = 0;
ct = 0;
hist = [0 for i in range(100)];
for i,(ln,spl) in enumerate(zip(v, split)):
    
    if spl != splitpart:
        continue;
    
    tk = [];
    pv = [];
    
    print i;

    for j in ln:
        tk.append(j);
        tg = tags(tk);

        
        score = sum(0 if (t==p) else 1 for t, p in zip(tg, pv));
        sc += score;
        ct += 1;
        hist[score] += 1;
        
        print " ".join(tg);
        pv = tg;
    
    print (sc*1./ct);
    print "";

print (sc*1./ct);
print hist