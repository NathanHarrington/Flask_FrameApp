''' Using a default template, create a json from dict,
call http interface and add each company.
See load_example_posts.py for what it can look like direct to DB.
'''

import sys, json, requests, copy, random, datetime, uuid

if len(sys.argv) != 3:
    print('Specify total to load, server name')
    sys.exit(1)

total = int(sys.argv[1])
server_name = sys.argv[2]

comp = {'ein_number': ['12345'],
        'company_type': ['Brick and Mortar', 'Retail', 'Landscaping'],
        'certificate_type': ['LLC', 'S-CORP', 'Sole-Proprietorship'],
        'company_name': ['MyBusiness', 'Cupcakes', 'Grass Cutters'],
        'street_address': ['123 main street', '456 elm street'],
        'city': ['Holly Springs', 'Cary', 'Apex', 'Raleigh'],
        'state': ['NC', 'VA', 'MS', 'UT'],
        'zip_code': ['27540', '27513', '27709', '84321']
       }

for item in range(total):
    new_dict = copy.deepcopy(comp)

    temp_num = ('%s' % uuid.uuid4()).upper()
    new_dict['ein_number'] = [temp_num[0:8]]

    for field in new_dict:
        rnd_count = len(new_dict[field]) - 1
        rnd_sel = random.randint(0, rnd_count)

        new_value = new_dict[field][rnd_sel]
        new_dict[field] = new_value

        #print('assign %s to %s' % (field, rnd_sel))
        #print('Value: %s' % new_dict[field])

    ds = json.dumps(new_dict, indent=4, sort_keys=True)

    new_dict['crawl_date'] = '%s' % datetime.datetime.now()
    loaded = '%s at: %s' % (new_dict['ein_number'], new_dict['crawl_date'])

    server = '%s/json_new_company' % server_name
    r = requests.put(server, json=new_dict)

    print('%s result: %s' % (loaded, r.status_code))
