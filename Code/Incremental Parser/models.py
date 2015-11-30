import numpy as np;
from scipy.stats import norm;
from sklearn.linear_model import LogisticRegression;
from sklearn.externals import joblib

execfile("./params.py");

class model_base(object):
    def __init__(self):
        self.name = "NONE";
        self.model = {};
        self.examples = {};

    def data_generative(self,prep, m):
        bf_ground, bf, transform, model_filter, bf_generator = self.get_features(prep);
        
        fval = np.zeros((len(m), len(bf)));
        self.examples = [[], []];
        for i in range(len(m)):
            x, y = transform(*m[i]);
            self.examples[0].append(x);
            self.examples[1].append(y);
            for j in range(len(bf)):
                fval[i, j] = bf[j](*m[i]);
                
        return fval;

    def data_regression(self, prep, m, scene, scene_ref):
        bf_ground, bf, transform, model_filter, bf_generator = self.get_features(prep);
        
        fval = [];
        yval = [];
        self.examples = [[], []];
        for i in range(len(m)):
            x, y = transform(*m[i]);
            self.examples[0].append(x);
            self.examples[1].append(y);
            
            correct_entry = np.zeros((len(bf),1));
            for j in range(len(bf)):
                correct_entry[j] = bf[j](*m[i]);
                            
            # Now we append each example in the dataset as a negative example:
            for gen_m in bf_generator(scene[scene_ref[i]].values()):
                curr_entry = np.zeros((len(bf),1));
                for j in range(len(bf)):
                    curr_entry[j] = bf[j](*gen_m);
                fval.append(curr_entry);
                yval.append(0);
                
                fval.append(correct_entry);
                yval.append(1);
        
        fval = np.transpose(np.hstack(fval));
        yval = np.transpose(np.array(yval));
        
        return (fval, yval);


    # bf_ground, bf, transform, model_filter, bf_generator
    def get_features(self, prep):
        if prep == "BETWEEN":
            return b2f_ground, b2f, b2f_transform, b2f_model_filter, b2f_generator;
        else:
            return b1f_ground, b1f, b1f_transform, b1f_model_filter, b1f_generator;

    def get_features_extended(self, prep):
        if prep == "BETWEEN":
            return b2f, b2f_transform_invert, b2f_ground;
        else:
            return b1f, b1f_transform_invert, b1f_ground;
    
    def train(self, prep, data, scene=None):
        pass;
        
    def test(self):
        pass;
    
    def load(self):
        self.model = joblib.load(GET_PATH('_%s_model.pkl' % self.name));
        
    def save(self):
        joblib.dump(self.model, GET_PATH('_%s_model.pkl' % self.name), compress=9);

    # Select landmarks that maximize the score, given prep and target.
    def generate(self, prep, scene, target):
        bf_ground, bf, transform, model_filter, bf_generator = self.get_features(prep);
        ls = [l for l in bf_generator(scene.keys()) if l[0] == target];
        ls_score = [self.test(prep, [scene[k] for k in l]) for l in ls];
        
        gnd_idx = ls_score.index(max(ls_score));
        return zip(ls, ls_score);
        
    def hasPrep(self, p):
        if p in self.model:
            return True;
        return False;


class model_logistic(model_base):
    def __init__(self):
        super(model_logistic,self).__init__()
        self.name = "logistic";
    
    def train(self, prep, data, scene):
        bf_ground, bf, transform, model_filter, bf_generator = self.get_features(prep);
        m = [mod for l,mod in data[prep] if model_filter(mod)];
        scene_ref = [l for l,mod in data[prep] if model_filter(mod)];

        if not m:
            print "No data for prep=", prep;
            return

        (fval, yval) = self.data_regression(prep, m, scene, scene_ref);
        self.model[prep] = LogisticRegression().fit(fval, yval);
        
    def test(self, prep, coords):
        if prep not in self.model:
            print "Model not trained for ", prep;
            return 0.0;
        bf, transform_invert, bf_ground = self.get_features_extended(prep);
        return self.model[prep].predict_proba([b(*coords) for b in bf])[0,1];


class model_normal(model_base):
    def __init__(self):
        super(model_normal,self).__init__()
        self.name = "gaussian";
    
    def train(self, prep, data, scene=None):
        bf_ground, bf, transform, model_filter, bf_generator = self.get_features(prep);
        m = [mod for l,mod in data[prep] if model_filter(mod)];
        
        if not m:
            print "No data!"
            return
        
        fval = self.data_generative(prep, m);
            
        normfit = [];
        for j in range(len(b1f)):
             normfit.append(norm.fit(fval[:,j]));
        self.model[prep] = normfit;
        
    def test(self, prep, coords):
        bf, transform_invert, bf_ground = self.get_features_extended(prep);

        v = 1.0;
        for l in range(len(self.model[prep])):
            (mu, sig) = self.model[prep][l];
            v *= norm.pdf(bf[l](*coords), mu, sig);
        
        return v;

