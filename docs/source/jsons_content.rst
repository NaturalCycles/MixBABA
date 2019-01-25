Content of the JSON file
========================

In this section we will discuss the fields (both mandatory and optional) that MixBABA expects to see in the JSON file.

Let's start with a simple example. The following JSON contains the data needed to run through a single funnel: ::

    [
        {"ID": 5397671,
            "From Date": "2018-01-28",
            "To Date": "2018-12-28",
            "Impression field name": "AB-AB025-IMPRESSION",
            "Conversion field name": "Payment",
            "By": "properties.assignment"
        }
    ]


But if you want you can specify more than one funnels.

The mandatory fields are:

* **ID** : this is the number associated to the funnel we are going to analyze (see Figure 1)
* **From/To Date** : the time range where you want to analyze the funnel
* **Impressions/Conversions field name** : the two fields are needed to point out the right data
* **by** : the name of the field in which the cohorts (e.g. *control*, *test*) are divided


.. figure:: imgs/funnel_id.png
    :width: 806px
    :align: center
    :height: 66px
    :alt: alternate text
    :figclass: align-center

    **Figure 1:** Where find the number of the funnel

By feeding MixBABA with this JSON, which we will call *simple.json*: ::

  mixbaba -k <your key> -f simple.json


you will get a result similar to this: ::

    -----------------------------------------------------
    Results for the funnel 5397671 -- AB025 Lower therm price (payment analysis)
    Control group is: control, test group is test
    Group      Control Impressions    Control Conversions    test Impressions    test Conversions    test CR improvement    test Probability
    -------  ---------------------  ---------------------  ------------------  ------------------  ---------------------  ------------------
    All.All                  34164                    253               31105                 284               0.232387            0.992551

In particular, you can read:

* The funnel name (*AB030 Old signup flow* in this example). This name is extracted from Mixpanel;
* the name of the control and test group ("control" and "test"). The names are automatically extracted from the data
  gathered from Mixpanel. If a second control group is present, it will be automatically analyzed and taken in account

Note that the names of the groups are automatically found because they follow this simple naming convention:

* the control group is called `control`; an eventual second control group can be present with the name `control2`
* the test group= are called `testX`, where `X` can be just void (`test`) or a one digit integer (ex. `test2`, `test5`)

In the table you can see the absolute numbers of impressions and conversions for the two group,
the improvement which the test option have with respect to the control one, and the probability for this
last affirmation to be true.

The very first column (Group = All.All) tells us that the data has not been further filtered.

If you specified more than one funnel in the JSON file, you will get one table for each funnel.

If instead you want to get the results as a CSV file (or many CSV files, in case you specified several funnels in the JSON),
you have to specify this in the command: ::

  mixbaba -k <your key> -f simple.json -o csv

In this case you will get a file with `funnelID-funnelname` as name (ex. 5397671-AB025 Lower therm price (payment analysis).csv).

Note that you can also have bot the console visualization and the CSV file, by specifying `-o both`.



Filters
************************

To add a filter on which divide the data, we just have to add a field to the JSON file: ::

    [ {"ID": 5397671,
          "From Date": "2018-01-28",
          "To Date": "2018-12-28",
          "Impression field name": "AB-AB025-IMPRESSION",
          "Conversion field name": "Payment",
          "By": "properties.assignment",
          "filters":
                    {"user.goal": ["PREVENT", "PLAN"],
                    "user.$country_code": ["US", 'SE']}}
    ]


The "filter" field accept a list of the filters to be used, together with a list of the values on which we are interested.

The command to be launched is exactly the same, but in this case we will get as output also the results filtered: ::

    -----------------------------------------------------
    Results for the funnel 5397671 -- AB025 Lower therm price (payment analysis)
    Control group is: control, test group is test
    Group               Control Impressions    Control Conversions    test Impressions    test Conversions    test CR improvement    test Probability
    ----------------  ---------------------  ---------------------  ------------------  ------------------  ---------------------  ------------------
    All.All                           34164                    253               31105                 284               0.232387            0.992551
    goal.PREVENT                       6175                     25                6016                  37               0.500153            0.947624
    goal.PLAN                          1561                      5                1411                   5               0.106157            0.568093
    $country_code.US                  16630                    224               15436                 242               0.163529            0.950558
    $country_code.SE                   8027                     23                7277                  35               0.654554            0.974197


Cross filtering
---------------
You may be interested in cross-filtering the results. In such case, you only have to add a `-x` option to the command: ::

      mixbaba -k <your key> -f filename.json -x

The result will be something like: ::

    -----------------------------------------------------
    Results for the funnel 5397671 -- AB025 Lower therm price (payment analysis)
    Control group is: control, test group is test
    Group                            Control Impressions    Control Conversions    test Impressions    test Conversions    test CR improvement    test Probability
    -----------------------------  ---------------------  ---------------------  ------------------  ------------------  ---------------------  ------------------
    All.All                                        34164                    253               31105                 284               0.232387            0.992551
    goal.PREVENT                                    6175                     25                6016                  37               0.500153            0.947624
    goal.PLAN                                       1561                      5                1411                   5               0.106157            0.568093
    $country_code.US                               16630                    224               15436                 242               0.163529            0.950558
    $country_code.SE                                8027                     23                7277                  35               0.654554            0.974197
    goal.PREVENT+$country_code.US                   5690                     25                5528                  37               0.504354            0.948845
    goal.PREVENT+$country_code.SE                    295                      0                 298                   0             nan                 nan
    goal.PLAN+$country_code.US                      1390                      5                1228                   3              -0.245528            0.318043
    goal.PLAN+$country_code.SE                       134                      0                 139                   0             nan                 nan

As you see, the more you filter the less data you have, and so you can end up with zeros and undefined values.

Optional fields
---------------

For ad-hoc analyses, other fields can be specified:

* Names for the groups; this can be useful in case the groups specified in the funnel
  do not follow the naming convention, or if you are maybe not interested in all the test groups' results
  In this case you can specify them manually: ::

          "AB Groups": {"Control":"controllo", "Control2":"secondo_controllo", "Test": "test"}
* a further brakedown of the data