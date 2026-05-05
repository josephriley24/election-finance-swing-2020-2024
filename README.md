# Election Finance Changes 2020-2024
An examination of changes in campaign financing in swing states between the 2020 and 2024 presidential general elections.

## Summary
Nearly $2 billion was spent by presidential candidates in the 2024 election cycle. This study surveys party-to-party shifts in financing between the 2020 and 2024 elections, looking specifically at seven "swing states:" Pennsylvania, Wisconsin, Michigan, Georgia, Arizona, Nevada, and North Carolina. The first analysis performed was looking at campaign financing in these states solely in 2024 -- an analysis which found large advantages in individual fundraising for Democratic candidate Kamala Harris over Republican candidate Donald Trump in all seven states.

Next...

## Data Inputs:
From the FEC https://www.fec.gov/data/browse-data/?tab=bulk-data: cm24.zip, cn24.zip, and weball24.zip. 

For population data: https://api.census.gov/data/2024/acs/acs5/variables.json

There were two files which we had previously used for exercises based around 2020 FEC data. Those are contributions.zip and com_cand_info.csv, which can be found here???

The Pennsylvania zip code data came from here: https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html

I started off with some files we used for exercises based around FEC data - com_cand_info.csv, a CSV covering presidential campaign committees during the 2020 campaign cycle, as well as contributions.zip, a cleaned-up version of individual contribution data from 2020. To accomplish my goal of examining partisan swing in ZIP code-level data between the 2024 and 2020 presidential general elections, I compiled individual data on both elections, then aggregated by ZIP, candidate, and party. Going step-by-step:

1. Creating a com_cand_info equivalent for 2024. For this, I downloaded the committee master file, candidate master file and candidate summary files, as well as header files for all three, then joined them all together. This step took some work as I had difficulty finding a header file for the candidate summary file, and generally speaking those headers created significant complications in the merge process. I eventually joined the three on the candidate ID columns (for the candidate master file) and the committee ID columns (for the committee master files). Then, I filtered them down to the 2024 presidential election.
2. Pulling population data from the census API for 2024. For this, I used the link here: https://api.census.gov/data/2024/acs/acs5/variables.json to find the total population by ZIP code.
3. Pulling FEC contribution data and filtering by swing states. I downloaded the indiv24 zip file, then processed the zip file row-by-row by writing a for loop which removed and renamed a few columns to match columns in the individual data for 2020 (in the contributions.zip file), filtered to a list of the seven "swing states," and trimmed the zip code to the first five digits.
4. I noticed there was a wide discrepancy in number of rows for the indiv20 and indiv24 files. After some tinkering, I recognized that I had to strip out the donations that were for non-presidential committees in 2024, and got a number (407,654) that was much closer to the 2020 number of 331,778.
5. Aggregating by party and ZIP code. I brought party affiliation in from the com_cand_info2024 file, trimmed the ZIP codes, grouped by party and ZIP, and then used a pivot table to convert party affiliations into columns for use in later mapping.



Optimizations
(optional)

You don't have to include this section but interviewers love that you can not only deliver a final product that looks great but also functions efficiently. Did you write something then refactor it later and the result was 5x faster than the original implementation? Did you cache your assets? Things that you write in this section are GREAT to bring up in interviews and you can use this section as reference when studying for technical interviews!

Lessons Learned:
No matter what your experience level, being an engineer means continuously learning. Every time you build something you always have those whoa this is awesome or wow I actually did it! moments. This is where you should share those moments! Recruiters and interviewers love to see that you're self-aware and passionate about growing.
