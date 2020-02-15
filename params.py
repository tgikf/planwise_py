import inspect
import holidays.countries as countries


def get_holiday_locales():
    holiday_locales = []
    for name, obj in inspect.getmembers(countries, inspect.isclass):
        if len(name) > 3 and name[0].isupper():

            holiday_locales.append({"display": name, "value": name})

            if hasattr(obj, "PROVINCES"):
                for province in obj.PROVINCES:
                    holiday_locales.append(
                        {
                            "display": name + " - " + str(province),
                            "value": name + ",P," + str(province),
                        }
                    )

            if hasattr(obj, "STATES"):
                for state in obj.STATES:
                    holiday_locales.append(
                        {
                            "display": name + " - " + str(state),
                            "value": name + ",S," + str(state),
                        }
                    )

    return holiday_locales
