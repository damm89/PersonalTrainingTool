import re

ACTIVITY_LEVEL_CHOICES = (
    ("1.2", "No exercise --or-- sitting job"),
    ("1.375", "Exercises 1-3 days/week --or-- standing job"),
    ("1.55", "Exercises 3-5 days/week"),
    ("1.725", "Exercises 6-7 days/week"),
    ("1.9", "Exercises twice a day"),
    )

ACTIVITY_LEVEL_DICT = {key:value for key,value in ACTIVITY_LEVEL_CHOICES}


GENDER_CHOICES = (
    ("Female", 'Female'),
    ("Male", 'Male'),
)

MEAL_RATIO_DICT = {
    'Breakfast':0.25,
    'Lunch':0.25,
    'Dinner':0.3,
    'Snack':0.1,
}

MINUTE_CHOICES = (
    ("00",)*2,
    ("10",)*2,
    ("20",)*2,
    ("30",)*2,
    ("40",)*2,
    ("50",)*2,
)

NUMS = re.compile(r"[-+]?\d*\.?\d+([eE][-+]?\d+)?")


