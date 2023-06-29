from collections import defaultdict
import csv
import json
import os


def load_csv_annotations(fp, row_length=7):
    lines = []
    with open(fp, 'r') as rf:
        cr = csv.reader(rf)
        for row in cr:
            if len(row) != row_length:
                continue
            if row[0] == 'observation_id':
                names = row
                continue
            lines.append({name : row[idx] for idx, name in enumerate(names)})
    return lines


def get_hist_percent_index(sorted_hist, percent):
    num_total = sum(sorted_hist)
    num_percent = int(num_total * percent)
    count = 0
    for idx, num in enumerate(sorted_hist):
        count += num
        if count >= num_percent:
            return idx


def get_statistics_on_trainval(root, file_name):
    items = load_csv_annotations(fp=os.path.join(root, file_name))
    classes = set()
    location_codes, endemics, observations = set(), set(), set()
    cls_hist = defaultdict(int)
    for it in items:
        classes.add(it['class_id'])
        endemics.add(it['endemic'])
        location_codes.add(it['code'])
        observations.add(it['observation_id'])
        cls_hist[it['class_id']] += 1
    classes = sorted(list(classes))
    endemics = sorted(list(endemics))
    observations = sorted(list(observations))
    location_codes = sorted(list(location_codes))
    class_to_idx = {name:ind for ind,name in enumerate(classes)}
    return classes, endemics, location_codes, class_to_idx, cls_hist, observations


def get_statistics_on_test(root, file_name):
    items = load_csv_annotations(fp=os.path.join(root, file_name), row_length=5)
    location_codes, endemics, observations = set(), set(), set()
    cls_hist = defaultdict(int)
    for it in items:
        endemics.add(it['endemic'])
        location_codes.add(it['code'])
        observations.add(it['observation_id'])
    endemics = sorted(list(endemics))
    observations = sorted(list(observations))
    location_codes = sorted(list(location_codes))
    return endemics, location_codes,observations


root = '/root/autodl-tmp/data'


file_name = 'SnakeCLEF2023-Train.csv'
classes, endemics, location_codes, class_to_idx, cls_hist, observations = get_statistics_on_trainval(root, file_name)
print(len(classes), len(class_to_idx), len(cls_hist))
print(len(endemics), len(location_codes), len(observations))


file_name = 'SnakeCLEF2022-Test.csv'
endemics_t, location_codes_t, observations_t = get_statistics_on_test(root, file_name)
print(len(endemics_t), len(location_codes_t), len(observations_t))


location_codes_all = sorted(list(set(location_codes_t).union(set(location_codes))))
print(len(location_codes_all))

classes_dist = []
for idx, cls_id in enumerate(classes):
    classes_dist.append(cls_hist[cls_id])

result = dict(
    classes=classes, class_to_idx=class_to_idx,
    endemics=endemics, location_codes=location_codes_all, 
    cls_hist=cls_hist, classes_dist=classes_dist,
)

for k, v in result.items():
    print(k, len(v))


output_file = os.path.join(root, 'statistics_on_train_test.json')
with open(output_file, 'w') as wf:
    wf.write(json.dumps(result))


file_path = os.path.join(root, 'statistics_on_train_test.json')
ret = json.loads(open(file_path, 'r').readline().strip())
for k, v in ret.items():
    print(k, len(v))
