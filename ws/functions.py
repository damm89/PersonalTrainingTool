import json
from django.db import IntegrityError

def calculate_bmr(gender, weight_kg, height_cm, age):
    """
    Takes height, weight, age and gender and returns bmr as rounded float.
    """
    weight_kg = float(weight_kg)
    height_cm = float(height_cm)
    age = float(age)

    if str(gender) == "Male":
        bmr = round(10*weight_kg + 6.25*height_cm - 5*age + 5)
    else:
        bmr = round(10*weight_kg + 6.25*height_cm - 5*age - 161)

    return bmr

def calculate_kcal(protein, carbs, fats):
    """
    Takes protein, carbs and fats and returns total kcals as rounded float.
    """
    p,c,f = float(protein), float(carbs), float(fats)
    return (p + c)*4 + f*9

def str2fl(x):
        try:
            x = float(x)
        except ValueError:
            x = 0
        
        print(x, type(x))
        return x

def list_2_unordered_list(lst):
    """
    Takes a <list> and returns an unordered HTML list as <string>
    """
    core = "".join(["<li>{}</li>".format(x) for x in lst])
    return "<ul class='mx-1 px-1'>{}</ul>".format(core)

def model_unique_name(instance, obj, name, k=1, old_name=''):
    """
    This function adds a number to a name if that name already exists.
    """

    objs = list(obj.objects.filter(name=name))
    if len(objs) > 0:
        if instance.pk == objs[0].pk:
            return name
        else:
            k += 1
            if k==2:
                old_name = str(name)
                
            new_name = old_name + ' {}'.format(k)
            return model_unique_name(instance, obj, new_name, k=k, old_name=old_name)
    else:
        return name

def unique_save(obj):
    """
    This function adds a number to a name if that name already exists.
    """
    error = True
    k = 2
    old_name = str(obj.name)
    while error:
        try:
            obj.save()
            error = False
        except IntegrityError:
            obj.name = old_name + ' {}'.format(k)
            k += 1

    return obj