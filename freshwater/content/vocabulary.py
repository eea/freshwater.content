""" vocabulary.py """

from plone.app.vocabularies.catalog import KeywordsVocabulary as BKV
from zope.interface import implementer, provider  # alsoProvides,
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

# See https://developers.arcgis.com/javascript/3/jsapi/esri.basemaps-amd.html
layers = """
dark-gray
dark-gray-vector
gray
gray-vector
hybrid
national-geographic
oceans
osm
satellite
streets
streets-navigation-vector
streets-night-vector
streets-relief-vector
streets-vector
terrain
topo
topo-vector
""".split(
    "\n"
)

layers = [lr.strip() for lr in layers if lr.strip()]


@provider(IVocabularyFactory)
def layers_vocabulary(context):
    """ layers_vocabulary """
    return values_to_vocab(layers)


def list_values_to_vocab(values):
    """ list_values_to_vocab """
    terms = [SimpleTerm(key, value, title) for (key, value, title) in values]
    terms.sort(key=lambda t: t.title)
    vocab = SimpleVocabulary(terms)

    return vocab


def values_to_vocab(values):
    """ values_to_vocab """
    terms = [SimpleTerm(x, x, x) for x in values]
    terms.sort(key=lambda t: t.title)
    vocab = SimpleVocabulary(terms)

    return vocab


# where is this list used? There are 27 EU Member states, maybe make
# a complete list with all the member states and add into 'countries_extra'
# non EU countries?
countries = """
BE	BE	Belgium
BG	BG	Bulgaria
CY	CY	Cyprus
DE	DE	Germany
DK	DK	Denmark
EE	EE	Estonia
EL	EL	Greece
ES	ES	Spain
FI	FI	Finland
FR	FR	France
HR	HR	Croatia
IE	IE	Ireland
IT	IT	Italy
LT	LT	Lithuania
LV	LV	Latvia
MT	MT	Malta
NL	NL	Netherlands
PL	PL	Poland
PT	PT	Portugal
RO	RO	Romania
SE	SE	Sweden
SI	SI	Slovenia
UK	UK	United Kingdom
""".split(
    "\n"
)

countries = [line.strip() for line in countries if line.strip()]
countries = [line.split("\t") for line in countries]


@provider(IVocabularyFactory)
def countries_vocabulary(context):
    """countries_vocabulary"""
    vocab = list_values_to_vocab(countries)
    return vocab


countries_extra = """
AT	AT	Austria
CZ	CZ	Czechia
CH	CH	Switzerland
EU	EU	European Union
HU	HU	Hungary
IS	IS	Iceland
LU	LU	Luxembourg
NO	NO	Norway
SK	SK	Slovakia
""".split("\n")

countries_extra = [line.strip() for line in countries_extra if line.strip()]
countries_extra = [line.split("\t") for line in countries_extra]
countries_extra = countries + countries_extra
countries_extra = sorted(countries_extra, key=lambda i: i[2])


@provider(IVocabularyFactory)
def countries_complete_vocabulary(context):
    """countries_complete_vocabulary"""
    vocab = list_values_to_vocab(countries_extra)
    return vocab


types = [
    "Indicator" "Data visualization",
    "Publication/Report",
    "Spatial datasets",
    "Map (interative)",
    "Data",
]


@provider(IVocabularyFactory)
def types_vocabulary(context):
    """types_vocabulary"""
    return values_to_vocab(types)


dpsir = [
    "Pressure",
    "State",
    "Impact",
    "Response",
    "Other",
]


@provider(IVocabularyFactory)
def dpsir_vocabulary(context):
    """dpsir_vocabulary"""
    return values_to_vocab(dpsir)


report_type = [
    "Technical report",
    "Scientific report",
    "Briefing",
]


@provider(IVocabularyFactory)
def report_vocabulary(context):
    """report_vocabulary"""
    return values_to_vocab(report_type)


# legislative_reference = [
#     "Water Framework Directive",
#     "Floods Directive",
#     "Bathing Water Directive",
#     "Nitrates Directive",
#     "Urban Waste Water Treatment Directive",
#     "Drinking Water Directive",
#     "Marine Strategy Framework Directive",
#     "Habitats Directive",
#     "Birds Directive",
# ]


# @provider(IVocabularyFactory)
# def legislative_vocabulary(context):
#     """legislative_vocabulary"""
#     return values_to_vocab(legislative_reference)


# category = [
#     "Water ecological status",
#     "Water quality",
#     "Status and relevant pressure",
#     "Physico-chemical and biological status",
#     "Urban waste water generation and emission"
# ]
#
# @provider(IVocabularyFactory)
# def category_vocabulary(context):
#     return values_to_vocab(category)


@implementer(IVocabularyFactory)
class KeywordsVocabulary(BKV):
    """KeywordsVocabulary"""
    def __init__(self, index):
        self.keyword_index = index

CategoryVocabularyFactory = KeywordsVocabulary("category")
LegislativeReferenceVocabularyFactory = KeywordsVocabulary("legislation")

themes = [
    "Climate change",
    "Contaminants",
    "Ecosystem",
    "Eutrophication",
    "Extraction of species",
    "Habitats",
    "Hydrographical conditions",
    "Marine litter",
    "Marine Protected Areas",
    "Non-indigenous species",
    "Physical damage",
    "Physical disturbance",
    "Species",
    "Underwater noise",
    "Not classified",
]


@provider(IVocabularyFactory)
def themes_vocabulary(context):
    """themes_vocabulary"""
    return values_to_vocab(themes)


subthemes = [
    "Acidification",
    "Aquaculture",
    "Beach litter",
    "Benthic habitats",
    "Birds",
    "By-catch",
    "Chlorophyll-a concentration",
    "Coastline",
    "Commercially exploited fish",
    "Contaminants concentration",
    "Coverage",
    "Effects in organisms",
    "Established NIS",
    "Extent of physical Damage",
    "Fish",
    "Impulsive noise",
    "Incidental by-catch",
    "Input of contaminants",
    "Input of non-indigenous species",
    "Input of nutrients",
    "Litter in the water column",
    "Litter ingested",
    "Litter on the seafloor",
    "Macrofauna communities",
    "Mammals",
    "Microbial pathogens",
    "Nutrient concentrations",
    "Oxygen",
    "Oxygen content",
    "Permanent alterations",
    "Phytoplankton blooms",
    "Phytoplankton production",
    "Plankton diversity",
    "Predators",
    "Radionucleids",
    "Reptiles",
    "Sea ice",
    "Sea level",
    "Sea temperature",
    "Seabirds",
    "Species distribution",
    "Transparency",
    "Zooplankton",
    "Not classified",
]


@provider(IVocabularyFactory)
def subthemes_vocabulary(context):
    """subthemes_vocabulary"""
    return values_to_vocab(subthemes)


organisations = {
    "EEA": dict(
        title="European Environment Agency",
        website="https://www.eea.europa.eu/"
    ),
    "DG ENV": dict(
        title="Environment Directorate General of the European Commission ",
        website="https://ec.europa.eu/environment/index_en.htm",
    ),
    "ETC/ICM": dict(
        title="European Topic Centre on Inland, Coastal and Marine waters",
        website="https://www.eionet.europa.eu/etcs/etc-icm",
    ),
    "OSPAR": dict(
        title="OSPAR Commission-Protecting and conserving the "
        "North-East Atlantic and its resources",
        website="https://www.ospar.org/",
    ),
    "HELCOM": dict(
        title="The Baltic Marine Environment Protection Commission",
        website="https://helcom.fi/",
    ),
    "UNEP/MAP": dict(
        title="UN Environment Programme / Mediterranean Action Plan",
        website="www.unepmap.org",
    ),
    "BSC": dict(
        title="Black Sea Commission (BSC)",
        website="http://www.blacksea-commission.org/",
    ),
    "Other": dict(title="Other", website=""),
}


@provider(IVocabularyFactory)
def organisations_vocabulary(context):
    """organisations_vocabulary"""
    terms = [
        SimpleTerm(acro, acro, info["title"])
        for acro, info in organisations.items()
    ]
    terms.sort(key=lambda t: t.title)
    vocab = SimpleVocabulary(terms)
    return vocab
