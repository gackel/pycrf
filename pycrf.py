#coding: utf-8
import os
from subprocess import getoutput
from tempfile import NamedTemporaryFile
# https://taku910.github.io/crfpp/

class CRF:
    def __init__(self, MODEL_NAME="model"):
        self.template_file = None
        self.model = MODEL_NAME
        
    def make_template(self, template_list):
        """
        templateの生成
            @input template_list: [((-2,0), (-1,1)), ..] --> %x[-2,0]/%x[-1,1]
            @return template_file
        """
        template_file = NamedTemporaryFile()
        with open(template_file.name, 'w') as f:
            for template_id, template_pair_list in enumerate(template_list):
                tmp_template_string = "U%02d:" % template_id
                tmp_template_string += "/".join(["%%x[%d,%d]"%(a,b) for (a,b) in template_pair_list])
                f.write(tmp_template_string)
            f.write('B')
        #template_file.flush()
        self.template_file = template_file

    def make_crf_input(self, list_of_feature_set_list):
        """
        crf format file の生成
            @input list_of_feature_set_list: [(feat1, feat2, .., label), ..]
            @return crf_input_file
        """
        crf_input = NamedTemporaryFile()
        with open(crf_input.name, 'w') as f:
            for feature_set_list in list_of_feature_set_list:
                for feature_set in feature_set_list:
                    f.write(" ".join(map(str,feature_set))+'\n')
                f.write('')
        crf_input.flush()
        return crf_input


    def train(self, list_of_train_feature_set_list):
        """
        CRFの学習
            @input list_of_feature_set_list: [(feat1, feat2, .., label), ..]
            @output self.modelを更新する  
        """
        train_file = self.make_crf_input(list_of_train_feature_set_list)
        os.system("nice -n 15 crf_learn -a CRF-L2 %s %s %s" % (self.template_file.name, train_file.name, self.model))


    def test(self, list_of_test_feature_set_list, PROB=False):
        test_file = self.make_crf_input(list_of_test_feature_set_list)
        if PROB: # -v 1, -v 2
            log = getoutput("nice -n 15 crf_test -v %d -m %s %s" % (PROB, self.model, test_file.name))
        else:
            log = getoutput("nice -n 15 crf_test -m %s %s" % (self.model, test_file.name))
        return [x.split("\t") for x in log.split("\n")]


if __name__ == "__main__":
    train_data = [
        [
        ("これ", "指示詞", "A"),
        ("は", "助詞", "A"),
        ("ペン", "名詞", "B"),
        ("です", "判定詞", "A")
        ]
            ]
    test_data = [
        [
        ("ペン", "名詞", "C"),
        ("です", "判定詞", "C")
        ],
        [
        ("これ", "指示詞", "C"),
        ("です", "判定詞", "C")
        ]
            ]
    template_list = [((0,0),), ((-1,0),), ((1,0),)]
    C = CRF()
    C.make_template(template_list)
    C.train(train_data)
    print(C.test(test_data, PROB=1))
