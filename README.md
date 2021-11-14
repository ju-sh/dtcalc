# dtcalc
A command line tool to find the difference between dates.

The package is self-contained and all it needs to run is a recent Python implementation.

## Why
I've known people who would've liked to have a way to quickly do basic arithmetic on datetime values. For reasons like:

 - How many days has it been since my birthday?
 - How long is it till my friend's  wedding anniversary?
 - Did the telecom company did their math right? Does my balance expire a few days *before* it should have?
 - Raised a ticket in a support portal. Issue is supposed to be resolved within 12 days. Okay, when is that?

<!--
## Installation
dtcalc can installed from PyPI.

```
pip install dtcalc
```

Python>=3.7 is needed.
-->

## Usage

### TODO Datetime values
 - The default input datetime value format is `"%Y/%m/%d"`.

## Changing datetime format
Input and output datetime formats can be changed using `--in-dtfmt` and `--out-dtfmt` respectively.

Output format is effective only if result is a datetime. If result is an offset, output format is ignored.

Most format codes mentioned [here][10] except `%Z` can be used. The format codes are mentioned at the end of this README.

### Datetime offsets
Following units can be used to create datetime offset values:

 - w: weeks
 - d: days
 - h: hours
 - m: minutes

These units together with an integer (scaling value) produces an offset value. Like:

 - `2d`: 2 days
 - `53w`: 53 weeks
 - `23w`: 23 hours
 - `351`: 351 minutes

Only integers can be used. Float values would throw error. Operators can be used to combine different units instead.

Note that there shouldn't be any space between the integer and the unit. So,

 - `2d`, `32w`, `451h` are correct.
 - `2 d`, `32  w` are wrong.

Some other units like years and months are not included as their time duration can vary (eg: due to leap years).

### Operations
Addition and subtraction of datetime values are supported.

 - `(2021/11/04 - 2021/11/05)`

Datetime offset values can be combined with operators like:

 - `3w + 2d`: 3 weeks and 2 days

There can be any number of spaces (including none) between operators (ie, `+` or `-`) and values (ie, offsets or datetime). So all of the following are okay.

 - `3w      +2d`
 - ` 3w+ 2d`
 - `3w+2d`

### Grouping operations
Operations may also be grouped together using parenthesis (as a way to specify precedence explicit).

Like:

 - `3d + (2021/11/04 - 2021/11/05)`
   + Evaluated as: `3d + (-1d)` → `2d`
   + Command: `dtcalc "3d + (2021/11/04 - 2021/11/05)"`

Evaluation happens one by one from left to right.

Needless to say, the parentheses should match. Every opening parenthesis must have a matching closing parenthesis coming after it.

### Caveats
#### Negation of datetime value
Unary negation of a datetime value would result in an error. Like:

 - `- 2021/04/28`
 - `3d - 2021/04/28`

because it doesn't make sense to have a negative time.

But subtracting a datetime from another datetime is fine:

 - `2021/05/29 - 2021/05/28  # 1 day`

#### Addtion of two datetime values
Since it doesn't make much sense to add datetimes , addition of two datetime values would throw error. Like:

## Datetime format codes
The actual value of some of the format codes are locale-dependent. Examples are as per `en_US` locale.

 - `d`: Day of month as zero padded integer (eg: 12)
 - `f`: Millisecond as zero padded integer (eg: 012345)
 - `H`: Hour (24-hour clock format) as zero padded integer (eg: 22)
 - `I`: Hour (12-hour clock format) as zero padded integer (eg: 10)
 - `j`: Day of year as zero padded integer (eg: 012)
 - `m`: Month as zero padded integer (eg: 02)
 - `M`: Minute as zero padded integer (eg: 59)
 - `S`: Second as zero padded integer (eg: 59)
 - `U`: Week number of year (with Sunday as first day) as zero padded integer (eg: 51)
 - `w`: Week day as integer (Sunday is 0)
 - `y`: Year without century as zero padded integer (eg: 21)
 - `Y`: Year with century (eg: 2021)
 - `z`: UTC offset (eg: +0530, -0200)
 - `A`: Full weekday name (locale dependent) (eg: Sunday)
 - `a`: Abbreviated weekday name (locale dependent) (eg: Sun)
 - `B`: Full month name (locale dependent) (eg: January)
 - `b`: Abbreviated month name (locale dependent) (eg: Jan)
 - `p`: AM/PM
 - `%`: literal '%'. Used as escape.

<!--
 - `G`:
 - `u`:
 - `V`:
-->

## Todo

 - Add seconds as a unit.
 - Notations for today (date only value) and now (datetime value).
 - Allow compound offsets.
   + 2w4d5h: 2 weeks 4 days 5 hours
 - Till next Friday / January.
 - Change output format.

[10]: https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
