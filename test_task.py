import json
import datetime


def read_json_data(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data


def write_json_data(filename,data):
    with open(filename, "w") as file:
        file.write(data)


def get_data_from_list(list_name, type_data):
    try:
        if len(list_name[type_data]) > 0:
            data_list = ''
            for i in range(len(list_name[type_data])):
                if data_list == '':
                    data_list += list_name[type_data][i]['VALUE']
                else:
                    data_list += f", {list_name[type_data][i]['VALUE']}"
            return data_list
        if list_name[type_data] is list:
            return None
        else:
            return list_name[type_data]['VALUE']
    except KeyError:
        return None


def insert_leads():

    leads_from_bx = read_json_data('leads_from_bx.json') # Нужно настроить получение данных из файла leads_from_bx.json
    list_leads = []
    leads_country = []
    leads_for_insert = []

    for lead in leads_from_bx:

        if lead.get("PHONE") is None:
            continue
        lead_country = {'id': lead['ID'], 'country': lead['ADDRESS_COUNTRY'], 'city': lead['ADDRESS_PROVINCE'],
                        'region': lead['ADDRESS_PROVINCE']}
        leads_country.append(lead_country)
        lead['LANDING'] = None
        lead['EN'] = 0
        id_str = str(lead['ID'])
        if '[EN]' in lead['TITLE']:
            lead['EN'] = 1
        elif '[EX]' in lead['TITLE']:
            lead['EN'] = 3
        elif '[U]' in lead['TITLE']:
            lead['EN'] = 2
        elif '[GR]' in lead['TITLE']:
            lead['EN'] = 4
        lead['PHONE'] = get_data_from_list(lead, 'PHONE')
        lead['EMAIL'] = get_data_from_list(lead, 'EMAIL')
        lead['REJECTION_REASON'] = lead['UF_CRM_1562873021']
        if lead['SOURCE_DESCRIPTION'] is not None and "https://hwschool.online" in lead['SOURCE_DESCRIPTION']:
            landing = lead['SOURCE_DESCRIPTION'].replace("https://hwschool.online", "").split('#')[0]
            if landing[-1] == '/' and len(landing) > 1:
                lead['LANDING'] = landing[0:-1]
            else:
                lead['LANDING'] = landing

        if id_str not in list_leads:
            list_leads.append(id_str)
            leads_for_insert.append(lead)

    leads_to_bd = read_json_data('leads_to_bd.json')

    for lead in leads_for_insert:
        if any(x['ID'] == lead['ID'] for x in leads_to_bd):
            continue
        else:
            leads_to_bd.append(lead)

    with open('leads_to_bd.json', 'w') as fp:
        json.dump(leads_to_bd, fp)

    # Далее из файла leads_to_bd нужно удалить лидов которых мы получили (если такие есть) и добавить новые данные,
    # именно добавить


def delete_dead_leads():
    # from mysql_tables import table_leads
    # Удаление лидов из БД, которые были удалены в Битриксе
    list_leads = read_json_data('leads_from_bx_2.json')  # Здесь нужно получить новых лидов из файла lead_from_bx_2.json
    db_leads = read_json_data('leads_to_bd.json') # Здесь нужно получить новых лидов из файла leads_to_bd.json
    list_leads_bx = read_json_data('leads_from_bx.json')

    list_new_leads = [i['ID'] for i in list_leads]
    list_db_leads = []

    for lead in db_leads:
        list_db_leads.append(str(lead['ID']))

    # lead_to_delete = [x["ID"] for x in list_leads_bx if x not in list_new_leads]
    lead_to_delete = []
    for x in list_leads_bx:
        if x['ID'] not in list_new_leads:
            lead_to_delete.append(x['ID'])

    #for lead in db_leads:
    #    if lead["ID"] in lead_to_delete:
    #        lead_indx = next((index for (index, d) in enumerate(db_leads) if d["ID"] == lead['ID']), None)
    #        del db_leads[lead_indx]

    new_db_lead = []
    for lead in db_leads:
        if lead['ID'] not in lead_to_delete:
            new_db_lead.append(lead)

    with open("leads_to_bd.json", "w") as file:
        json.dump(new_db_lead, file)


def make_report():
    db_leads = read_json_data('leads_to_bd.json')
    list_to_report = {}

    # print(db_leads)
    for lead in db_leads:
        vals = 0
        date_obj = datetime.datetime.fromisoformat(lead['DATE_CREATE'])
        date_formatted = date_obj.date().strftime('%d.%m.%Y')

        if date_formatted in list_to_report:
            vals = list_to_report[date_formatted] + 1
            list_to_report[date_formatted] = vals
        else:
            list_to_report[date_formatted] = vals

    report = []
    for key, value in list_to_report.items():
        report_obj = []
        report_obj.append(key)
        report_obj.append(value)
        report.append(report_obj)
    print(report)


if __name__ == '__main__':
    # insert_leads()
    # delete_dead_leads()
    make_report()
