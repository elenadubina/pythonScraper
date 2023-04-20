from datetime import datetime, timedelta


class BaseParser:
    def _previous_date(self, str_days_ago):
        if 'more than' in str_days_ago.lower():
            return ''

        today = datetime.now()
        arr_str_days = str_days_ago.split()
        if not arr_str_days:
            return ''

        if arr_str_days[0].lower() == 'a':
            num_days = 1
        else:
            try:
                num_days = int(arr_str_days[0])
            except ValueError:
                return ''

        str_day = arr_str_days[1].lower()
        if str_day in ['hours', 'hour']:
            return (today - timedelta(hours=num_days)).strftime('%Y-%m-%d')
        elif str_day in ['days', 'day']:
            return (today - timedelta(days=num_days)).strftime('%Y-%m-%d')
        elif 'month' in str_day:
            return (today - timedelta(days=30 * num_days)).strftime('%Y-%m-%d')
        else:
            return ''
