import csv
import matplotlib.pyplot as plt


def readfile(filename, fields=None):
    lines = []
    with open(filename, "r", encoding="utf-8") as csvFile:
        reader = csv.DictReader(csvFile, fields)
        for row in reader:
            lines.append(row)
    return lines


COLS = [
    'Daily number of tests',
    'Daily number of people tested',
]

COL_ADV = [
    'Daily number of positive cases',
    'Cumulative number of positive cases',
    'Daily In-person (tests processed)',
    'Cumulative In-person (tests processed)',
    'Daily Delivery (tests sent out)',
    'Cumulative Delivery (tests sent out)'
]


def _print(key, date, today, pillar):
    error = 0
    try:
        tests_count = int(today["tests"][pillar][key])
    except KeyError as e:
        print("[{}] {} {} tests".format(date, pillar, e))
        error = 1

    try:
        today["caps"][pillar]
    except KeyError as e:
        error = 1
        print("unkown cap")

    if error == 0:

        if today["caps"][pillar] == "":
            print("[{}] {} n/a spec undefined".format(date, pillar))
            error = 1
        else:
            try:
                cap_count = int(today["caps"][pillar])
            except KeyError as e:
                print("[{}] {} {} cap".format(date, pillar, e))
                error = 1

        if error == 0:
            p = tests_count / cap_count * 100
            if p > 100 and "4" not in pillar:
                print("over capacity")
            print("[{}] {} {}".format(date, pillar, p))


def prettyprint(dates, date):
    today = dates[date]
    for pillar in today["tests"].keys():
        if today["tests"][pillar]['Daily number of tests'] != "":
            _print('Daily number of tests', date, today, pillar)

        elif today["tests"][pillar]['Daily number of people tested'] not in ["", "Unavailable"]:
            _print('Daily number of people tested', date, today, pillar)


        else:
            print("[{}] {} {}".format(date, pillar, "n/a"))


def get_tests(data):
    if data['Daily number of tests'] != "":
        return int(data['Daily number of tests'])

    if data['Daily number of people tested'] != "":
        return int(data['Daily number of people tested'])

    return 0


def get_int(data, key):
    if data[key] != "":
        return int(data[key])
    return 0


def try_to_int(v, pillar):
    if v.get(pillar) is None:
        return 0
    v = v[pillar]
    if v == "":
        return 0
    return int(v)


def format_dates(dates):
    temp = [k for k in dates.keys()]
    return temp


def test_lines(dates, pillar):
    plt.title(pillar)
    plt.xlabel("date")
    plt.ylabel("count")
    # int(data['Daily number of people tested'])
    plt.plot(format_dates(dates), [try_to_int(dates[k]["caps"], pillar) for k in dates.keys()],
             label="{} cap".format(pillar))
    plt.plot(format_dates(dates), [get_tests(dates[k]["tests"][pillar]) for k in dates.keys()],
             label="{} tests".format(pillar))
    plt.legend()
    plt.tight_layout()
    plt.xticks(rotation=90, fontsize=5)


def test_lines_total(dates):
    pillars = [
        # "Pillar 1",
        "Pillar 2",
        # "Pillar 3",
        "Pillar 4"
    ]

    plt.title("total no. tests and capacity for all pillars")
    plt.xlabel("date")
    plt.ylabel("count")
    # int(data['Daily number of people tested'])
    plt.plot(format_dates(dates),
             [sum([try_to_int(dates[k]["caps"], pillar) for pillar in pillars]) for k in dates.keys()], label="cap")
    plt.plot(format_dates(dates),
             [sum([get_tests(dates[k]["tests"][pillar]) for pillar in pillars]) for k in dates.keys()], label="tests")
    plt.legend()
    plt.tight_layout()
    plt.xticks(rotation=90, fontsize=5)


def save(name):
    print("saving: {}".format(f'{name}.pdf'))
    plt.savefig(f'{name}.pdf', bbox_inches='tight')
    plt.savefig(f'{name}.png', bbox_inches='tight')
    # delete the graph
    plt.clf()


def graph_delivery_inperson_pillar(dates, pillar):
    plt.title(pillar)
    plt.xlabel("date")
    plt.ylabel("count")
    # int(data['Daily number of people tested'])

    plt.plot(format_dates(dates), [try_to_int(dates[k]["caps"], pillar) for k in dates.keys()],
             label="{} cap".format(pillar))

    plt.plot(format_dates(dates), [get_tests(dates[k]["tests"][pillar]) for k in dates.keys()],
             label="old test reporting")

    plt.plot(format_dates(dates),
             [get_int(dates[k]["tests"][pillar], "Daily Delivery (tests sent out)") for k in dates.keys()],
             label="{} delivery (tests sent out)".format(pillar))
    plt.plot(format_dates(dates),
             [get_int(dates[k]["tests"][pillar], "Daily In-person (tests processed)") for k in dates.keys()],
             label="{} in person (tests processed)".format(pillar))
    plt.plot(format_dates(dates), [
        get_int(dates[k]["tests"][pillar], "Daily In-person (tests processed)") + get_int(dates[k]["tests"][pillar],
                                                                                          "Daily Delivery (tests sent out)")
        for k in dates.keys()], label="{} cumulative".format(pillar))

    plt.legend()
    plt.tight_layout()
    plt.xticks(rotation=90, fontsize=5)


def graph_pillar2_pillar4(dates):
    plt.title("tests processed delivery and in person for pillars 2 and 4")
    plt.xlabel("date")
    plt.ylabel("count")
    pillars = [
        "Pillar 2",
        "Pillar 4"
    ]
    plt.plot(format_dates(dates),
             [sum([try_to_int(dates[k]["caps"], pillar) for pillar in pillars]) for k in dates.keys()], label="cap")

    plt.plot(format_dates(dates),
             [sum([get_int(dates[k]["tests"][pillar], "Daily In-person (tests processed)") for pillar in pillars]) for k in dates.keys()], label="In person (tests processed)")

    plt.plot(format_dates(dates),
             [sum([get_int(dates[k]["tests"][pillar], "Daily Delivery (tests sent out)") for pillar in pillars]) for k in dates.keys()], label="delivery (tests sent out)")


    plt.legend()
    plt.tight_layout()
    plt.xticks(rotation=90, fontsize=5)


def main():
    tests = readfile("tests.csv")
    caps = readfile("cap.csv")
    # check(date, tests, caps)

    dates = {}
    for test in tests:
        if test["Nation"] == "UK":
            if dates.get(test["Date of reporting"]) is None:
                dates[test["Date of reporting"]] = {"tests": {}, "caps": {}}

            dates[test["Date of reporting"]]["tests"][
                test["Pillar"].replace(" (plus Pillar 2 for Wales)", "").replace(" (excluding Wales)", "")] = test

    count = 0
    for cap in caps:

        if cap["Lab capacity"] == "":
            # note: this works but can cause percentage usage to go over capacity
            # but from one quick look through the data it doesn't
            v = caps[count - 1]["Lab capacity"]
            # print("DEBUG: {} {}".format(cap["Date of reporting"], cap["Pillar"]))
            pass
        else:
            v = cap["Lab capacity"]

        dates[cap["Date of reporting"]]["caps"][cap["Pillar"]] = v
        count += 1

    pillars = ["Pillar 1", "Pillar 2", "Pillar 3", "Pillar 4"]
    for pillar in pillars:
        test_lines(dates, pillar)
        save("{}_capacity".format(pillar.replace(" ", "")))

    test_lines_total(dates)
    save("all_pillars_capacity")

    for date in dates.keys():
        prettyprint(dates, date)
        print("--------------")

    graph_delivery_inperson_pillar(dates, "Pillar 2")
    save("Pillar2_detailed_capacity")

    graph_delivery_inperson_pillar(dates, "Pillar 4")
    save("Pillar4_detailed_capacity")

    graph_pillar2_pillar4(dates)
    save("inperson_and_delivery_tests")


if __name__ == "__main__":
    main()
