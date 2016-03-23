import os, csv; 

_batch = "Batch_2069005"

OP_LINES_FN = "_line.txt";
OP_INPUT_FN = "_input.txt";
OP_TOKEN_FN = "_tokens.tsv";
OP_PSTAG_FN = "_tags.tsv";
OP_IMAGE_FN = "_image.csv";
OP_REJEC_FN = "_rejected.tsv";
OP_SPLIT_FN = "_split.txt"

# preps = ["BETWEEN", "LEFT_OF", "RIGHT_OF", "NEAR", "BEHIND", "IN_FRONT_OF", "FURTHEST"];
preps = ["BETWEEN", "LEFT_OF", "RIGHT_OF", "NEAR", "BEHIND", "IN_FRONT_OF"];

def GET_PATH(fn):
    if fn[0] == "/":
        return os.path.join(".", _batch, _batch, fn[1:]);
    return os.path.join(".", _batch, _batch+fn);

def save_data(v, fn):
    with open(GET_PATH(fn), 'w') as fp:
        if v and v[0] and type(v[0]) is list:
            for line in v:
                fp.write("\t".join(str(l) for l in line));
                fp.write('\n');
        else:
            for line in v:
                fp.write(str(line));
                fp.write('\n');

def load_data(fn, typec=str):
    rv = []
    with open(GET_PATH(fn), 'r') as fp:
        delim = "\t";
        if fn[-4:] == ".csv":
            delim = ",";      
        
        inpreader = csv.reader(fp, delimiter=delim);
        if fn[-2:] == "sv" and fn[-4] == ".":
            for line in inpreader:
                rv.append([typec(v) for v in line]);
        else:
            for line in inpreader:
                rv.append(typec(line[0]));
    return rv;

B2F_REFERENCE_PT = 0.2;
b2f_wrapper_cache = {};
def b2f_wrapper((x0, y0), (x1, y1), (x2, y2), wrap=None):
    if x1 == x2 and y1 == y2:
        return 0;
        
    key = (x1, y1, x2, y2);
    if key not in b2f_wrapper_cache:
        # Virtual perpendicular point, used to constrain the skew:
        d = B2F_REFERENCE_PT;
        perp = np.matrix([[0, -1], [1, 0]]) * np.matrix([[x2-x1],[y2-y1]]) + np.matrix([[x1], [y1]]);
        # Calculate the to and from projection matrices
        to = np.matrix([[-d, d, -d],[0, 0, 2*d],[1, 1, 1]]);
        fr = np.matrix([[x1, x2, perp[0,0]],[y1, y2, perp[1,0]], [1, 1, 1]]);
        trans = to * np.linalg.inv(fr);
        b2f_wrapper_cache[key] = trans;
    
    v = np.dot(b2f_wrapper_cache[key], np.matrix([x0, y0, 1.0]).T)[:-1].transpose().tolist()[0];
    
    if wrap:
        return wrap(v);
    else:
        return v;

b1f = [];
b1f.append(lambda (x0, y0), (x1, y1): ((x0-x1)**2 + (y0-y1)**2)**0.5);
b1f.append(lambda (x0, y0), (x1, y1): (x0-x1));
b1f.append(lambda (x0, y0), (x1, y1): (y0-y1));
b1f_transform = lambda (x0, y0), (x1, y1): ((x0-x1), (y0-y1));
b1f_transform_invert = lambda x, y: ((x, y), (0, 0));
b1f_ground = [[0], [0]];
b1f_generator = lambda ls: [(ls[i], ls[j]) for i in range(len(ls)) for j in range(len(ls)) if i != j];
b1f_model_filter = (lambda n: len(n) == 2);

b2f = [];
b2f.append(lambda (x, y): (x*x + y*y)**0.5);
#b2f.append(lambda (x, y): 1 if abs(x) <= 1 else 0);
b2f.append(lambda (x, y): abs(y));
b2f.append(lambda (x, y): abs(x));
b2f.append(lambda (x, y): (abs(x) + .1) * (abs(y) + .1));
#b2f.append(lambda (x, y): x*x);
#b2f.append(lambda (x, y): y*y);
#b2f.append(lambda (x, y): -x*x);
b2f.append(lambda (x, y): 2.**(-x*x));
b2f.append(lambda (x, y): 2.**(-y*y));
b2f_transform = b2f_wrapper;
b2f_transform_invert = lambda x, y: ((x, y), (-B2F_REFERENCE_PT, 0), (B2F_REFERENCE_PT, 0));
b2f_ground = [[-B2F_REFERENCE_PT, B2F_REFERENCE_PT], [0, 0]];
b2f = [(lambda p0, p1, p2: b2f_wrapper(p0, p1, p2, b2fk)) for b2fk in b2f];
b2f_generator = lambda ls: [(ls[h], ls[i], ls[j]) for h in range(len(ls)) for i in range(len(ls)) for j in range(len(ls)) if i != j and h != j and h != i];
b2f_model_filter = (lambda n: len(n) == 3);



VIRTUAL_YOU = "VIRTUAL_YOU";
VIRTUAL_ME = "VIRTUAL_ME";
VIRTUAL_TABLE = "VIRTUAL_TABLE";

def load_scenes_ext():
    objs = load_scenes();
    for o in objs:
        objs[o][VIRTUAL_TABLE] = (0, 0);
        
    return objs;

def load_scenes():
    # Load the scene    
    scene = {};
    for i in "123456789ABCDEFGHIJ":
        d = {};
        f = load_data("/Scene_%s_Ground.csv" % i);
        for row in f:
            d[row[0]] = (float(row[1]), float(row[2]));
        
        scene[i] = d;
    
    return scene;

def argmaxdict(d):
     v=list(d.values())
     k=list(d.keys())
     return k[v.index(max(v))];
     
def model_scene_att(model, img):
    rv = {};    
    for p in model:
        rv[p] = [(img[ln][0], dat) for ln, dat in model[p]];
    return rv;
    
#
# Language
#
   
def node_filter((p_type, p_items)):
    return p_type not in ["IGN", "VB", "."];

def intersection(w, q):
    return set(x for x in q if x in w);
    
def simplify_prp(w):
    w = "_".join(w);
    if intersection(w, ["between", "middle_of", "center_of", "surrounded_by"]):
        return "BETWEEN";
    elif intersection(w, ["near", "close", "beside", "adjacent", "next_to" ]):
        return "NEAR";
    elif intersection(w, ["behind", "above", "beyond", "beneath"]):
        return "BEHIND";
    elif intersection(w, ["front_of", "below", "down", "under"]):
        return "IN_FRONT_OF";
    elif intersection(w, ["furthest", "far"]):
        return "FURTHEST";
    elif "left" in w:
        return "LEFT_OF";
    elif "right" in w:
        return "RIGHT_OF";
    else:
        return "PRP_UNKNOWN";

def get_nodes(g, t):
    nodes = [];
    prevNodeType = None;
    for j in range(len(g)):
        if g[j] == prevNodeType:
            (p_type, p_items) = nodes[-1];
            nodes[-1] = (p_type, p_items + [t[j]]);
        else:
            nodes += [(g[j], [t[j]])];
            prevNodeType = g[j]
    return nodes;