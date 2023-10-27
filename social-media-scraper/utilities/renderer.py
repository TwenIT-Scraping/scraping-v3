from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def render_data_to_string(data:list, sep:str) -> str:
    formated_data = sep.join([str(item) for item in data])
    formated_data.replace("'", '"')
    return formated_data


def format_linkedIn_date(date:str) -> str:
    if 'jour' in date or 'day' in date:
        date = (datetime.now() - relativedelta(hours=int(''.join(filter(str.isdigit, date))))).strftime("%d/%m/%Y")
    elif 'sem' in date or 'week' in date:
        print('semaine')
        date = (datetime.now() - relativedelta(weeks=int(''.join(filter(str.isdigit, date))))).strftime("%d/%m/%Y")
    elif 'mois' in date or 'month' in date:
        print('mois')
        date = (datetime.now() - relativedelta(months=int(''.join(filter(str.isdigit, date))))).strftime("%d/%m/%Y")
    elif 'an' in date or 'year' in date:
        print('an')
        date = (datetime.now() - relativedelta(years=int(''.join(filter(str.isdigit, date))))).strftime("%d/%m/%Y")
    return date
