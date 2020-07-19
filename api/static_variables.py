from django.urls import reverse_lazy

CATEGORY_DATA = {
        'meals':{
                'cols': ["Name", "Category", "Kcals", "Protein", "Carbs", "Sugars", "Fibers", "Fats", "Sat. Fats", "Unsat. Fats", "Salt"],
                'only': ["id","name", "categories", "kcals", "protein", "carbs", "sugars", "fibers", "fats", "saturated_fats", "unsaturated_fats", "salt"],
                'buttons': {'Add meal': reverse_lazy('meals:create-meal'), 'Create meal(s) from tags':reverse_lazy('meals:create-tag-meal'),'Search categories':reverse_lazy('meals:meal-categories')},
                'hidden_cols': ['sugars','fibers','saturated_fats','unsaturated_fats','salt']
                },
        'ingredients':{
                        'cols': ["Name", "Tags", "Amount", "Kcals", "Protein", "Carbs", "Sugars", "Fibers", "Fats", "Sat. Fats", "Unsat. Fats", "Salt"],
                        'only':  ["id", "name", "tags", "amount_list", "kcals", "protein", "carbs", "sugars", "fibers", "fats", "saturated_fats", "unsaturated_fats", "salt"],
                        'buttons': {'Add ingredient': reverse_lazy('ingredients:create-ingredient'), 'Mass upload ingredients':reverse_lazy('ingredients:upload-ingredients'),
                        'Search tags':reverse_lazy('ingredients:ingredients-tags')},
                        'hidden_cols': ['sugars','fibers','saturated_fats','unsaturated_fats','salt']
                        },
        'clientaccounts':{
                        'cols': ["Name","Maintenance","Activity level","Age","Gender"],
                        'only': ["id","name","maintenance","activity_level","age","gender"],
                        'buttons':{'Add client account': reverse_lazy('clientaccounts:create-client-account')}
                        },
        'meals-categories':{
                        'cols':['Category'],
                        'only':['id','name'],
                        },
        'ingredients-tags':{'cols': ["Tag", "Used"],
                        'only':["id","name","used"],
                        },
        'mealplans-templates':{
                        'cols':["Name", "Status"],
                        'only': ["id", "name", "status"],
                        'buttons': {'Add mealplan template': reverse_lazy('mealplans:create-mealplan-template')}
                        },
        'mealplans':{
                    'cols': ["Name","Client Account","Duration","Mealplan Template","Starting Weight","Target Weight"],
                    'only': ["id", "name", "client_account__name", "duration", "template", "start_weight", "end_weight"],
                    'buttons':  {'Add mealplan': reverse_lazy('mealplans:create-mealplan')}
                    }
        }