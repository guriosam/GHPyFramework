import datetime

class DateUtils:

    def get_days_between_dates(self, date1, date2):
        d1 = datetime.datetime.strptime(date1, "%Y-%m-%dT%H:%M:%SZ")
        d2 = datetime.datetime.strptime(date2, "%Y-%m-%dT%H:%M:%SZ")
        #Format YYYY-MM-DD HH:MM:SS
        diff_days = d2 - d1
        return diff_days.days

    @staticmethod
    def sort_dates(dates):
        return sorted(dates)


    @staticmethod
    def days_between_date_and_now(date):
        now = datetime.datetime.utcnow()
        date = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
        result = now - date
        return result.days








