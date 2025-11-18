"""Small curated list of nonprofit pages per-state used by the event scraper.

This file intentionally contains a lightweight mapping used by the EventCacheManager
to discover candidate nonprofit pages for scraping. Add more entries as coverage
is required (format: state code -> list of (url, organization_name) tuples).
"""

STATE_NONPROFITS = {
    # Alabama (AL)
    "AL": [
        ("https://www.volunteermatch.org/search?l=Alabama", "VolunteerMatch Alabama"),
        ("https://www.alfoodbanks.org/volunteer", "Alabama Food Banks"),
        ("https://www.habitat.org/us-al", "Habitat for Humanity Alabama"),
    ],
    # Alaska (AK)
    "AK": [
        ("https://www.volunteermatch.org/search?l=Alaska", "VolunteerMatch Alaska"),
        ("https://www.foodbankofalaska.org/volunteer", "Food Bank of Alaska"),
        ("https://www.habitat.org/us-ak", "Habitat for Humanity Alaska"),
    ],
    # Arizona (AZ)
    "AZ": [
        ("https://www.volunteermatch.org/search?l=Arizona", "VolunteerMatch Arizona"),
        ("https://www.firstfoodbank.org/volunteer/", "St. Mary's Food Bank"),
        (
            "https://www.habitatcaz.org/volunteer",
            "Habitat for Humanity Central Arizona",
        ),
    ],
    # Arkansas (AR)
    "AR": [
        ("https://www.volunteermatch.org/search?l=Arkansas", "VolunteerMatch Arkansas"),
        ("https://www.arfoodbank.org/volunteer", "Arkansas Foodbank"),
        ("https://www.habitat.org/us-ar", "Habitat for Humanity Arkansas"),
    ],
    # California (CA)
    "CA": [
        (
            "https://www.volunteermatch.org/search?l=California",
            "VolunteerMatch California",
        ),
        ("https://www.lafoodbank.org/get-involved/volunteer/", "LA Food Bank"),
        ("https://www.sfmfoodbank.org/volunteer/", "SF-Marin Food Bank"),
        ("https://www.habitat.org/us-ca", "Habitat for Humanity California"),
        ("https://www.oneoc.org/volunteer", "OneOC Volunteer Center"),
    ],
    # Colorado (CO)
    "CO": [
        ("https://www.volunteermatch.org/search?l=Colorado", "VolunteerMatch Colorado"),
        ("https://www.foodbankrockies.org/volunteer/", "Food Bank of the Rockies"),
        (
            "https://www.habitatmetrodenver.org/volunteer",
            "Habitat for Humanity Metro Denver",
        ),
    ],
    # Connecticut (CT)
    "CT": [
        (
            "https://www.volunteermatch.org/search?l=Connecticut",
            "VolunteerMatch Connecticut",
        ),
        ("https://www.ctfoodbank.org/volunteer/", "Connecticut Food Bank"),
        ("https://www.habitat.org/us-ct", "Habitat for Humanity Connecticut"),
    ],
    # Delaware (DE)
    "DE": [
        ("https://www.volunteermatch.org/search?l=Delaware", "VolunteerMatch Delaware"),
        ("https://www.fbd.org/volunteer/", "Food Bank of Delaware"),
        ("https://www.habitatde.org/volunteer", "Habitat for Humanity Delaware"),
    ],
    # Florida (FL)
    "FL": [
        ("https://www.volunteermatch.org/search?l=Florida", "VolunteerMatch Florida"),
        ("https://www.feedingflorida.org/volunteer", "Feeding Florida"),
        (
            "https://www.habitatcfla.org/volunteer",
            "Habitat for Humanity Central Florida",
        ),
        ("https://www.volunteerflorida.org/", "Volunteer Florida"),
    ],
    # Georgia (GA)
    "GA": [
        ("https://www.volunteermatch.org/search?l=Georgia", "VolunteerMatch Georgia"),
        ("https://www.acfb.org/volunteer/", "Atlanta Community Food Bank"),
        ("https://www.habitat.org/us-ga", "Habitat for Humanity Georgia"),
        ("https://www.handsonatlanta.org/volunteer", "Hands On Atlanta"),
    ],
    # Hawaii (HI)
    "HI": [
        ("https://www.volunteermatch.org/search?l=Hawaii", "VolunteerMatch Hawaii"),
        ("https://www.hawaiifoodbank.org/volunteer", "Hawaii Foodbank"),
        ("https://www.habitat.org/us-hi", "Habitat for Humanity Hawaii"),
    ],
    # Idaho (ID)
    "ID": [
        ("https://www.volunteermatch.org/search?l=Idaho", "VolunteerMatch Idaho"),
        ("https://www.idahofoodbank.org/volunteer/", "The Idaho Foodbank"),
        ("https://www.habitat.org/us-id", "Habitat for Humanity Idaho"),
    ],
    # Illinois (IL)
    "IL": [
        ("https://www.volunteermatch.org/search?l=Illinois", "VolunteerMatch Illinois"),
        (
            "https://www.chicagosfoodbank.org/volunteer/",
            "Greater Chicago Food Depository",
        ),
        ("https://www.habitat.org/us-il", "Habitat for Humanity Illinois"),
        ("https://www.chicagocares.org/volunteer", "Chicago Cares"),
    ],
    # Indiana (IN)
    "IN": [
        ("https://www.volunteermatch.org/search?l=Indiana", "VolunteerMatch Indiana"),
        ("https://www.gleaners.org/volunteer/", "Gleaners Food Bank"),
        ("https://www.indyhabitat.org/volunteer", "Habitat for Humanity Indianapolis"),
    ],
    # Iowa (IA)
    "IA": [
        ("https://www.volunteermatch.org/search?l=Iowa", "VolunteerMatch Iowa"),
        ("https://www.foodbankiowa.org/volunteer", "Food Bank of Iowa"),
        ("https://www.habitat.org/us-ia", "Habitat for Humanity Iowa"),
    ],
    # Kansas (KS)
    "KS": [
        ("https://www.volunteermatch.org/search?l=Kansas", "VolunteerMatch Kansas"),
        ("https://www.kansasfoodbank.org/volunteer/", "Kansas Food Bank"),
        ("https://www.habitat.org/us-ks", "Habitat for Humanity Kansas"),
    ],
    # Kentucky (KY)
    "KY": [
        ("https://www.volunteermatch.org/search?l=Kentucky", "VolunteerMatch Kentucky"),
        ("https://www.daregreaterthings.org/volunteer", "Dare to Care Food Bank"),
        ("https://www.habitat.org/us-ky", "Habitat for Humanity Kentucky"),
    ],
    # Louisiana (LA)
    "LA": [
        (
            "https://www.volunteermatch.org/search?l=Louisiana",
            "VolunteerMatch Louisiana",
        ),
        ("https://www.secondharvestgno.org/volunteer", "Second Harvest Food Bank"),
        ("https://www.habitat.org/us-la", "Habitat for Humanity Louisiana"),
    ],
    # Maine (ME)
    "ME": [
        ("https://www.volunteermatch.org/search?l=Maine", "VolunteerMatch Maine"),
        ("https://www.gsfb.org/volunteer/", "Good Shepherd Food Bank"),
        ("https://www.habitat.org/us-me", "Habitat for Humanity Maine"),
    ],
    # Maryland (MD)
    "MD": [
        ("https://www.volunteermatch.org/search?l=Maryland", "VolunteerMatch Maryland"),
        ("https://www.mdfoodbank.org/volunteer/", "Maryland Food Bank"),
        (
            "https://www.habitatchesapeake.org/volunteer",
            "Habitat for Humanity Chesapeake",
        ),
    ],
    # Massachusetts (MA)
    "MA": [
        (
            "https://www.volunteermatch.org/search?l=Massachusetts",
            "VolunteerMatch Massachusetts",
        ),
        ("https://www.gbfb.org/volunteer/", "Greater Boston Food Bank"),
        ("https://www.habitat.org/us-ma", "Habitat for Humanity Massachusetts"),
        ("https://www.bostoncares.org/volunteer", "Boston Cares"),
    ],
    # Michigan (MI)
    "MI": [
        ("https://www.volunteermatch.org/search?l=Michigan", "VolunteerMatch Michigan"),
        ("https://www.fbem.org/volunteer/", "Food Bank of Eastern Michigan"),
        ("https://www.habitat.org/us-mi", "Habitat for Humanity Michigan"),
    ],
    # Minnesota (MN)
    "MN": [
        (
            "https://www.volunteermatch.org/search?l=Minnesota",
            "VolunteerMatch Minnesota",
        ),
        ("https://www.2harvest.org/volunteer", "Second Harvest Heartland"),
        ("https://www.tchabitat.org/volunteer", "Twin Cities Habitat for Humanity"),
    ],
    # Mississippi (MS)
    "MS": [
        (
            "https://www.volunteermatch.org/search?l=Mississippi",
            "VolunteerMatch Mississippi",
        ),
        ("https://www.msfoodnet.org/volunteer", "Mississippi Food Network"),
        ("https://www.habitat.org/us-ms", "Habitat for Humanity Mississippi"),
    ],
    # Missouri (MO)
    "MO": [
        ("https://www.volunteermatch.org/search?l=Missouri", "VolunteerMatch Missouri"),
        ("https://www.harvesters.org/volunteer/", "Harvesters Food Network"),
        ("https://www.stlfoodbank.org/volunteer/", "St. Louis Area Foodbank"),
        ("https://www.habitat.org/us-mo", "Habitat for Humanity Missouri"),
    ],
    # Montana (MT)
    "MT": [
        ("https://www.volunteermatch.org/search?l=Montana", "VolunteerMatch Montana"),
        ("https://www.myfoodbank.org/volunteer", "Montana Food Bank Network"),
        ("https://www.habitat.org/us-mt", "Habitat for Humanity Montana"),
    ],
    # Nebraska (NE)
    "NE": [
        ("https://www.volunteermatch.org/search?l=Nebraska", "VolunteerMatch Nebraska"),
        ("https://www.foodbankheartland.org/volunteer/", "Food Bank for the Heartland"),
        ("https://www.habitat.org/us-ne", "Habitat for Humanity Nebraska"),
    ],
    # Nevada (NV)
    "NV": [
        ("https://www.volunteermatch.org/search?l=Nevada", "VolunteerMatch Nevada"),
        ("https://www.threesquare.org/volunteer", "Three Square Food Bank"),
        ("https://www.habitat.org/us-nv", "Habitat for Humanity Nevada"),
    ],
    # New Hampshire (NH)
    "NH": [
        (
            "https://www.volunteermatch.org/search?l=New%20Hampshire",
            "VolunteerMatch New Hampshire",
        ),
        ("https://www.nhfoodbank.org/volunteer/", "New Hampshire Food Bank"),
        ("https://www.habitat.org/us-nh", "Habitat for Humanity New Hampshire"),
    ],
    # New Jersey (NJ)
    "NJ": [
        (
            "https://www.volunteermatch.org/search?l=New%20Jersey",
            "VolunteerMatch New Jersey",
        ),
        ("https://www.cfbnj.org/volunteer/", "Community FoodBank of New Jersey"),
        ("https://www.habitat.org/us-nj", "Habitat for Humanity New Jersey"),
    ],
    # New Mexico (NM)
    "NM": [
        (
            "https://www.volunteermatch.org/search?l=New%20Mexico",
            "VolunteerMatch New Mexico",
        ),
        ("https://www.rrfb.org/volunteer/", "Roadrunner Food Bank"),
        ("https://www.habitat.org/us-nm", "Habitat for Humanity New Mexico"),
    ],
    # New York (NY)
    "NY": [
        (
            "https://www.volunteermatch.org/search?l=New%20York",
            "VolunteerMatch New York",
        ),
        ("https://www.nycservice.org/volunteer", "NYC Service"),
        ("https://www.foodbanknyc.org/volunteer/", "Food Bank for New York City"),
        ("https://www.habitat.org/us-ny", "Habitat for Humanity New York"),
        ("https://www.newyorkcares.org/volunteer", "New York Cares"),
    ],
    # North Carolina (NC)
    "NC": [
        (
            "https://www.volunteermatch.org/search?l=North%20Carolina",
            "VolunteerMatch North Carolina",
        ),
        (
            "https://www.secondharvestmetrolina.org/volunteer",
            "Second Harvest Food Bank",
        ),
        ("https://www.habitat.org/us-nc", "Habitat for Humanity North Carolina"),
        ("https://www.handsoncharlotte.org/volunteer", "Hands On Charlotte"),
    ],
    # North Dakota (ND)
    "ND": [
        (
            "https://www.volunteermatch.org/search?l=North%20Dakota",
            "VolunteerMatch North Dakota",
        ),
        ("https://www.greatplainsfoodbank.org/volunteer", "Great Plains Food Bank"),
        ("https://www.habitat.org/us-nd", "Habitat for Humanity North Dakota"),
    ],
    # Ohio (OH)
    "OH": [
        ("https://www.volunteermatch.org/search?l=Ohio", "VolunteerMatch Ohio"),
        ("https://www.midohiofoodbank.org/volunteer/", "Mid-Ohio Food Collective"),
        ("https://www.gcfb.org/volunteer/", "Greater Cleveland Food Bank"),
        ("https://www.habitat.org/us-oh", "Habitat for Humanity Ohio"),
    ],
    # Oklahoma (OK)
    "OK": [
        ("https://www.volunteermatch.org/search?l=Oklahoma", "VolunteerMatch Oklahoma"),
        (
            "https://www.regionalfoodbank.org/volunteer/",
            "Regional Food Bank of Oklahoma",
        ),
        ("https://www.habitat.org/us-ok", "Habitat for Humanity Oklahoma"),
    ],
    # Oregon (OR)
    "OR": [
        ("https://www.volunteermatch.org/search?l=Oregon", "VolunteerMatch Oregon"),
        ("https://www.oregonfoodbank.org/volunteer/", "Oregon Food Bank"),
        (
            "https://www.habitatportlandmetro.org/volunteer",
            "Habitat for Humanity Portland Metro",
        ),
        ("https://www.handsonportland.org/volunteer", "Hands On Portland"),
    ],
    # Pennsylvania (PA)
    "PA": [
        (
            "https://www.volunteermatch.org/search?l=Pennsylvania",
            "VolunteerMatch Pennsylvania",
        ),
        ("https://www.philabundance.org/volunteer/", "Philabundance"),
        (
            "https://www.pittsburghfoodbank.org/volunteer/",
            "Greater Pittsburgh Food Bank",
        ),
        ("https://www.habitat.org/us-pa", "Habitat for Humanity Pennsylvania"),
    ],
    # Rhode Island (RI)
    "RI": [
        (
            "https://www.volunteermatch.org/search?l=Rhode%20Island",
            "VolunteerMatch Rhode Island",
        ),
        ("https://www.rifoodbank.org/volunteer/", "Rhode Island Community Food Bank"),
        ("https://www.habitat.org/us-ri", "Habitat for Humanity Rhode Island"),
    ],
    # South Carolina (SC)
    "SC": [
        (
            "https://www.volunteermatch.org/search?l=South%20Carolina",
            "VolunteerMatch South Carolina",
        ),
        ("https://www.harvesthopeoodbank.org/volunteer", "Harvest Hope Food Bank"),
        ("https://www.habitat.org/us-sc", "Habitat for Humanity South Carolina"),
    ],
    # South Dakota (SD)
    "SD": [
        (
            "https://www.volunteermatch.org/search?l=South%20Dakota",
            "VolunteerMatch South Dakota",
        ),
        ("https://www.feedingsouthdakota.org/volunteer", "Feeding South Dakota"),
        ("https://www.habitat.org/us-sd", "Habitat for Humanity South Dakota"),
    ],
    # Tennessee (TN)
    "TN": [
        (
            "https://www.volunteermatch.org/search?l=Tennessee",
            "VolunteerMatch Tennessee",
        ),
        (
            "https://www.secondharvestmidtn.org/volunteer",
            "Second Harvest Food Bank Middle TN",
        ),
        ("https://www.habitat.org/us-tn", "Habitat for Humanity Tennessee"),
        ("https://www.hon.org/volunteer", "Hands On Nashville"),
    ],
    # Texas (TX)
    "TX": [
        ("https://www.volunteermatch.org/search?l=Texas", "VolunteerMatch Texas"),
        ("https://www.houstonfoodbank.org/volunteer/", "Houston Food Bank"),
        ("https://www.ntfb.org/volunteer/", "North Texas Food Bank"),
        ("https://www.safoodbank.org/volunteer/", "San Antonio Food Bank"),
        ("https://www.habitat.org/us-tx", "Habitat for Humanity Texas"),
        ("https://www.volunteerhouston.org/needs", "Volunteer Houston"),
    ],
    # Utah (UT)
    "UT": [
        ("https://www.volunteermatch.org/search?l=Utah", "VolunteerMatch Utah"),
        ("https://www.slcfoodbank.org/volunteer", "Utah Food Bank"),
        ("https://www.habitat.org/us-ut", "Habitat for Humanity Utah"),
    ],
    # Vermont (VT)
    "VT": [
        ("https://www.volunteermatch.org/search?l=Vermont", "VolunteerMatch Vermont"),
        ("https://www.vtfoodbank.org/volunteer/", "Vermont Foodbank"),
        ("https://www.habitat.org/us-vt", "Habitat for Humanity Vermont"),
    ],
    # Virginia (VA)
    "VA": [
        ("https://www.volunteermatch.org/search?l=Virginia", "VolunteerMatch Virginia"),
        (
            "https://www.feedingamerica.org/find-your-local-foodbank?address=Virginia",
            "Feeding America Virginia",
        ),
        ("https://www.habitat.org/us-va", "Habitat for Humanity Virginia"),
        ("https://www.volunteerrichmond.org/volunteer", "Volunteer Richmond"),
    ],
    # Washington (WA)
    "WA": [
        (
            "https://www.volunteermatch.org/search?l=Washington",
            "VolunteerMatch Washington",
        ),
        ("https://www.seattlefoodbank.org/volunteer/", "Northwest Harvest"),
        ("https://www.habitat.org/us-wa", "Habitat for Humanity Washington"),
        ("https://www.uwkc.org/volunteer", "United Way King County"),
    ],
    # West Virginia (WV)
    "WV": [
        (
            "https://www.volunteermatch.org/search?l=West%20Virginia",
            "VolunteerMatch West Virginia",
        ),
        ("https://www.mountaineerfoodbank.org/volunteer", "Mountaineer Food Bank"),
        ("https://www.habitat.org/us-wv", "Habitat for Humanity West Virginia"),
    ],
    # Wisconsin (WI)
    "WI": [
        (
            "https://www.volunteermatch.org/search?l=Wisconsin",
            "VolunteerMatch Wisconsin",
        ),
        ("https://www.feedingwi.org/volunteer", "Feeding Wisconsin"),
        ("https://www.habitat.org/us-wi", "Habitat for Humanity Wisconsin"),
        (
            "https://www.volunteeryourtime.org/volunteer",
            "Volunteer Center of Milwaukee",
        ),
    ],
    # Wyoming (WY)
    "WY": [
        ("https://www.volunteermatch.org/search?l=Wyoming", "VolunteerMatch Wyoming"),
        ("https://www.wyomingfoodbank.org/volunteer", "Food Bank of Wyoming"),
        ("https://www.habitat.org/us-wy", "Habitat for Humanity Wyoming"),
    ],
}
