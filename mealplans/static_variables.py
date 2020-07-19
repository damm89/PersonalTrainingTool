DURATION_CHOICES = [
    (i,i) for i in range(1,13)
]

HOUR_CHOICES = (
    ("12AM",)*2,
    ("1AM",)*2,
    ("2AM",)*2,
    ("3AM",)*2,
    ("4AM",)*2,
    ("5AM",)*2,
    ("6AM",)*2,
    ("7AM",)*2,
    ("8AM",)*2,
    ("9AM",)*2,
    ("10AM",)*2,
    ("11AM",)*2,
    ("12PM",)*2,
    ("1PM",)*2,
    ("2PM",)*2,
    ("3PM",)*2,
    ("4PM",)*2,
    ("5PM",)*2,
    ("6PM",)*2,
    ("7PM",)*2,
    ("8PM",)*2,
    ("9PM",)*2,
    ("10PM",)*2,
    ("11PM",)*2,
)

HOUR_VALUES = {_[0]:"{:02}".format(i) for i,_ in enumerate(HOUR_CHOICES)}