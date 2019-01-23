# MIXpanel Bayesian AB test Analysis tool (MixBABA)

This tool is intended to consume a JSON file containing details about a Mixpanel funnel and output the results of the analysis made whithin a Bayesian framework.

You can find details about the data processing [here](https://towardsdatascience.com/bayesian-a-b-testing-with-python-the-easy-guide-d638f89e0b8a).

## Installation
To install this package you have to clone the repository:

    git clone https://github.com/NaturalCycles/MixBABA.git
    
You can run the unit tests, to ensure the tool will work:

    cd MixBABA 
    python setup.py test

And then you can install the tool via PIP:
    
    pip install .

## Usage
To use MixBABA you have need:
* a JSON file containing a list of the funnels together with the details about them
 (an example is in this repository) 
* the "API secret" to connect to Mixpanel; You can find your one in the settings 
dialog of the Mixpanel web application.

Then you can launch the analysis via command line:

    mixbaba -f [funnel_file.json] -k [API secret]

The tool will extract the data relative to the funnel from Mixpanel, 
and the output will be put in the same directory as CSV files, 
as many as the funnels specified in the JSON file given in input.

By default no output will be sent to the console, but if you want
to check the behavior you can specify a deeper level of verbosity:

    mixbaba -vv -f [funnel_file.json] -k [API secret]

### Example result

| Discriminant   | Cohort   |   CR improvement |   Probability | Comment                                           |
|:---------------|:---------|-----------------:|--------------:|:--------------------------------------------------|
| None           | All      |         0.649154 |      0.998485 | Result is OK!                                     |
| goal           | PREVENT  |         0.947368 |      0.99296  | Result is OK!                                     |
| goal           | PLAN     |         0.504785 |      0.894047 | Result is uncertain! Check data                   |
| goal           | PREGNANT |         0        |      0        | Not enough statistic for the two control options! |
| $country_code  | US       |         0.637771 |      0.997887 | Result is OK!                                     |
| $country_code  | UK       |         0        |      0        | Too few data!                                     |
| $country_code  | SE       |         0        |      0        | Too few data!                                     |
| $country_code  | DE       |         0        |      0        | Too few data!                                     |

(experimental)
