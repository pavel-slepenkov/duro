import arrow
from typing import List

events = {
    'start': 'Started',
    'connect': 'Connected to Redshift',
    'select': 'Selected data from Redshift',
    'create_temp': 'Created temporary table',
    'process': 'Processed selected data',
    'csv': 'Exported processed data to CSV',
    's3': 'Uploaded processed data to S3',
    'insert': 'Uploaded processed data to Redshift',
    'clean_csv': 'Removed CSV files',
    'tests': 'Run tests',
    'replace_old': 'Replaced old table',
    'drop_old': 'Dropped old table',
}


class Timestamps:
    __slots__ = list(events.keys()) + ['finish']

    def log(self, event: str):
        setattr(self, event, arrow.now().timestamp)
        if event in ('drop_old', 'insert'):
            self.finish = getattr(self, event)

    @property
    def events(self) -> List:
        return self.__slots__

    @property
    def values(self) -> List:
        return [getattr(self, event, None) for event in self.__slots__]

    # noinspection PyUnresolvedReferences
    @property
    def duration(self) -> int:
        return self.finish - self.start
        # if self.drop_old is not None:
        #     return self.drop_old - self.start
        # elif self.insert is not None:
        #     return self.insert - self.start
        # else:
        #     return None
