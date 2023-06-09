from collections import defaultdict
import csv
import numpy as np
import os
import torch


def load_csv_annotations(fp, row_length=6):
    lines = []
    with open(fp, 'r') as rf:
        cr = csv.reader(rf)
        for row in cr:
            if len(row) < row_length:
                continue
            if row[0] == 'observation_id':
                names = row
                continue
            lines.append({name : row[idx] for idx, name in enumerate(names)})
    return lines


def get_class_and_idx_mapper():
    root = '/root/autodl-tmp/data'
    items = load_csv_annotations(fp=os.path.join(root, 'train_split.csv'))
    classes = set()
    for it in items:
        classes.add(it['class_id'])
    classes = sorted(list(classes))
    class_to_idx = {name:ind for ind,name in enumerate(classes)}
    return classes, class_to_idx


def get_items():
    root = '/root/autodl-tmp/data'
    items = load_csv_annotations(fp=os.path.join(root, 'SnakeCLEF2023-Test.csv'), row_length=5)
    return items


model_result_file = '/root/autodl-tmp/main/output/MetaFG_meta_2/OUTPUT_TAG/result_snakeclef2023test.tc'
snake_test_result = torch.load(model_result_file)
item_list = get_items()
classes, class_to_idx = get_class_and_idx_mapper()
print(len(classes), len(class_to_idx))


observation_to_classes = defaultdict(list)
print(len(snake_test_result))
for idx_st, st in enumerate(snake_test_result):
    v1, v2 = st
    data_item = item_list[int(v1.detach().cpu().numpy())]
    sm_scores = torch.nn.Softmax(dim=0)(v2).detach().cpu().numpy()
    idx_max = np.argmax(sm_scores)
    #print(classes)
    #print(idx_max)
    cls_max = classes[idx_max]
    observation_to_classes[data_item['observation_id']].append((cls_max, sm_scores[idx_max]))
print(len(observation_to_classes))


result_list = []
for obv_id, class_id_scores in observation_to_classes.items():
    sorted_scores = sorted(class_id_scores, key=lambda x: x[1], reverse=True)
    select_cls_id_according_to_max_score = sorted_scores[0][0]
    # Get most.
    dist = defaultdict(int)
    for p in class_id_scores:
        dist[p[0]] += 1
    dist_list = []
    for k, v in dist.items():
        dist_list.append((k, v))
    new_dist_list = sorted(dist_list, key=lambda x: x[1], reverse=True)
    select_cls_id_according_to_the_most = new_dist_list[0][0]
    # Deal with conflict.
    if len(new_dist_list) > 1:
        if new_dist_list[0][1] == new_dist_list[1][1]:
            selected_cls_id_final = select_cls_id_according_to_max_score
        else:
            selected_cls_id_final = select_cls_id_according_to_the_most
    else:
        assert select_cls_id_according_to_max_score == select_cls_id_according_to_the_most
        selected_cls_id_final = select_cls_id_according_to_the_most
    # print(selected_cls_id_final, class_id_scores)
    result_list.append((obv_id, selected_cls_id_final))
print(len(result_list))


output_file = model_result_file + '.result.csv'
with open(output_file, 'w') as wf:
    wf.write('observation_id,class_id\n')
    for it in result_list:
        wf.write('%s,%s\n' % (it[0], it[1]))
