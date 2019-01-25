# MIXpanel Bayesian AB test Analysis tool (MixBABA)

This tool is intended to consume a JSON file containing details about a Mixpanel funnel and output the results of the analysis made whithin a Bayesian framework.

You can find details about the data processing [here](https://towardsdatascience.com/bayesian-a-b-testing-with-python-the-easy-guide-d638f89e0b8a).

## Installation

### From PyPi

Just easy as:

    pip install mixbaba

### From sources
To install this package you have to clone the repository:

    git clone https://github.com/NaturalCycles/MixBABA.git
    
You can run the unit tests, to ensure the tool will work:

    cd MixBABA 
    python setup.py test

And then you can install the tool via PIP:
    
    pip install .

## Usage

You can find the full documentation [here](https://mixbaba.readthedocs.io/en/latest/), 
but if you want a short guide read the following.

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

By default no output will be sent to the console. If you want a CSV file as output you can ask it with

    mixbaba -f [funnel_file.json] -k [API secret] -o csv

### Example result

This is the standard output format for the analysis of a funnel

| Group            |   Control Impressions |   Control Conversions |   test Impressions |   test Conversions |   test CR improvement |   test Probability |                                                                                                                     
|:-----------------|----------------------:|----------------------:|-------------------:|-------------------:|----------------------:|-------------------:|
| All.All          |                 34164 |                   253 |              31105 |                284 |              0.232387 |           0.992551 |
| goal.PREVENT     |                  6175 |                    25 |               6016 |                 37 |              0.500153 |           0.947624 |
| goal.PLAN        |                  1561 |                     5 |               1411 |                  5 |              0.106157 |           0.568093 |
| $country_code.US |                 16631 |                   224 |              15438 |                242 |              0.163448 |           0.95048  |
| $country_code.SE |                  8024 |                    23 |               7275 |                 35 |              0.654391 |           0.974175 |

Or, if you specify the option `-of long` at the command launch:

| Discriminant       | Cohort   | Comment                       |   Control Impressions |   Control Conversions |   test Impressions |   test Conversions |   test CR improvement |   test Probability |                                                                        
|:-------------------|:---------|:------------------------------|----------------------:|----------------------:|-------------------:|-------------------:|----------------------:|-------------------:|
| None               | All      | Result for test is OK!        |                 34164 |                   253 |              31105 |                284 |              0.232387 |           0.992551 |
| user.goal          | PREVENT  | Result for test is uncertain. |                  6175 |                    25 |               6016 |                 37 |              0.500153 |           0.947624 |
| user.goal          | PLAN     | Result for test is uncertain. |                  1561 |                     5 |               1411 |                  5 |              0.106157 |           0.568093 |
| user.$country_code | US       | Result for test is OK!        |                 16631 |                   224 |              15438 |                242 |              0.163448 |           0.95048  |
| user.$country_code | SE       | Result for test is OK!        |                  8024 |                    23 |               7275 |                 35 |              0.654391 |           0.974175 |
