import datetime

class DateUtils:

    def get_days_between_dates(self, date1, date2):
        d1 = datetime.datetime.strptime(date1, "%Y-%m-%dT%H:%M:%SZ")
        d2 = datetime.datetime.strptime(date2, "%Y-%m-%dT%H:%M:%SZ")
        #Format YYYY-MM-DD HH:MM:SS
        diff_days = d2 - d1
        return diff_days.days

    def sort_dates(self, dates):
        return sorted(dates)




