"""Build the two-page first-assignment concept note from actual outputs."""
from pathlib import Path
import json
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, KeepTogether
from reportlab.graphics.shapes import Drawing, Rect, Line, Polygon, String
from matplotlib.font_manager import findfont, FontProperties

ROOT = Path(__file__).resolve().parents[1]
profile = json.loads((ROOT / 'data/sample_profile.json').read_text())
metrics = json.loads((ROOT / 'outputs/initial_metrics.json').read_text())
pdfmetrics.registerFont(TTFont('DejaVu', findfont(FontProperties(family='DejaVu Sans'))))
pdfmetrics.registerFont(TTFont('DejaVuBold', findfont(FontProperties(family='DejaVu Sans', weight='bold'))))
pdfmetrics.registerFontFamily('DejaVu', normal='DejaVu', bold='DejaVuBold', italic='DejaVu', boldItalic='DejaVuBold')

PAGE_W, PAGE_H = A4
MARGIN = 43
WIDTH = PAGE_W - 2 * MARGIN
navy = colors.HexColor('#17324d')
teal = colors.HexColor('#167d8d')
grey = colors.HexColor('#5e6873')
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='MainTitle', fontName='DejaVuBold', fontSize=22, leading=26, spaceAfter=3, textColor=colors.black))
styles.add(ParagraphStyle(name='SubtitleSmall', fontName='DejaVu', fontSize=10.3, leading=14, spaceAfter=14, textColor=grey))
styles.add(ParagraphStyle(name='SectionCustom', fontName='DejaVuBold', fontSize=11, leading=15, spaceBefore=11, spaceAfter=5, textColor=colors.black, keepWithNext=True))
styles.add(ParagraphStyle(name='SubsectionCustom', fontName='DejaVuBold', fontSize=9.8, leading=13, spaceBefore=7, spaceAfter=4, textColor=colors.black, keepWithNext=True))
styles.add(ParagraphStyle(name='BodyCustom', fontName='DejaVu', fontSize=9.45, leading=13.5, spaceAfter=7, textColor=colors.black))
styles.add(ParagraphStyle(name='SourceCustom', fontName='DejaVu', fontSize=7.6, leading=10.5, spaceAfter=3, textColor=grey))
styles.add(ParagraphStyle(name='TableCustom', fontName='DejaVu', fontSize=8.7, leading=12, textColor=colors.black))
styles.add(ParagraphStyle(name='CaptionCustom', fontName='DejaVu', fontSize=8, leading=11, spaceAfter=6, textColor=grey))

story = []
def p(text, style='BodyCustom'):
    story.append(Paragraph(text, styles[style]))
def section(text):
    p(text, 'SectionCustom')
def sub(text):
    p(text, 'SubsectionCustom')

def workflow():
    drawing = Drawing(WIDTH, 64)
    gap = 16
    box = (WIDTH - 3 * gap) / 4
    labels = [('Inventory', 'Ingredients and dates'), ('Preparation', 'Normalised names'), ('NLP retrieval', 'TF-IDF and LSA'), ('Ranked recipes', 'Matches and gaps')]
    for i, (title, detail) in enumerate(labels):
        x = i * (box + gap)
        drawing.add(Rect(x, 12, box, 42, strokeColor=colors.HexColor('#bcc8d1'), fillColor=colors.white, strokeWidth=0.8))
        drawing.add(String(x + box / 2, 38, title, fontName='DejaVuBold', fontSize=8.7, textAnchor='middle', fillColor=navy))
        drawing.add(String(x + box / 2, 24, detail, fontName='DejaVu', fontSize=7.5, textAnchor='middle', fillColor=grey))
        if i < 3:
            start, end = x + box + 2, x + box + gap - 2
            drawing.add(Line(start, 33, end, 33, strokeColor=teal, strokeWidth=1))
            drawing.add(Polygon([end, 33, end - 4, 35.5, end - 4, 30.5], strokeColor=teal, fillColor=teal))
    return drawing

p('1 Project name', 'SourceCustom')
p('FoodWise', 'MainTitle')
p('Expiry aware recipe recommendations to support food-waste prevention', 'SubtitleSmall')

section('2 Overview')
p('FoodWise will help small soup kitchens and food-service teams find recipes from available ingredients and give priority to stock with approaching user-entered use-by dates. Users enter ingredient names, stock details and dates. The tool returns ranked recipes, matched ingredients and any missing items. Its primary contribution is to <b>SDG 12 target 12.3</b>. Support for SDG 2 is indirect, through more effective use of food resources.')

section('3 Background')
p('The United Nations reports that 1.05 billion tonnes of food were wasted at retail, food-service and household levels in 2022 [1]. Choosing recipes without considering stock or approaching dates can leave usable ingredients unused. Our project investigates whether ingredient-based NLP retrieval and explicit date prioritisation can support this decision. Actual waste reduction will require later operational measurements; the recipe dataset contains no observed waste outcomes.')

section('4 Key objectives and research questions')
p('<b>Objectives.</b> Identify recipes that fit available ingredient types; make approaching dates visible in ranking; show missing ingredients; and evaluate the first retrieval approaches transparently.')
p('<b>Research questions.</b> Which approach best recovers a source recipe from a partial ingredient query? How can expiry-aware priorities be added without hiding ingredient gaps? Which source-data limitations must be resolved before portion and mass calculations?')

section('5 Methods and workflow')
sub('a Datasets')
p(f'The working dataset contains exactly <b>{profile["rows"]:,} real Food.com recipe records</b> and {profile["field_count"]} retained fields, including ingredient names, source quantities, servings and instructions [2]. It was prepared with seed 42, and the publisher states CC0 Public Domain. All EDA and model experiments use the same 8,000 records. USDA FoodData Central is a supplementary source planned for later validated nutrient matching [5].')
sub('b Preparation and proposed tool flow')
p('Source lists are parsed without executing their contents. Ingredient names are normalised. The sample retains named recipes with 3-20 distinct ingredients and positive known servings, with one candidate per normalised ingredient set. Stock amounts are recorded as inputs, but this stage does not infer gram-level feasibility because source quantities and units need curation.')
story.append(workflow())

story.append(PageBreak())
p('FoodWise Assignment 1', 'SubtitleSmall')
sub('c Exploratory data analysis')
mismatch = profile['quality_flags']['quantity_ingredient_length_mismatch']
nested_missing = profile['quality_flags']['quantity_vector_has_missing_entry']
large_servings = profile['quality_flags']['servings_above_20']
p(f'Within the 8,000-record sample, ingredient and quantity lists differ in length in <b>{mismatch:,} records ({100*mismatch/profile["rows"]:.1f}%)</b>; <b>{nested_missing:,} ({100*nested_missing/profile["rows"]:.1f}%)</b> quantity vectors contain a missing entry. The median is {profile["ingredient_count"]["median"]:.0f} distinct ingredients, while {large_servings:,} records have source servings above 20 and need review. Positive known servings were a selection rule, so sample completeness must not be generalised to the original source.')
image = Image(str(ROOT / 'outputs/figures/eda_quality_and_ingredients.png'), width=WIDTH, height=WIDTH * 0.314)
story.append(image)
p('Figure 1. EDA of the 8,000-recipe working sample. Quantity flags use the source arrays; ingredient counts use distinct normalised labels.', 'CaptionCustom')

sub('d First model experiments and validation')
p('The baseline uses ingredient-set overlap. TF-IDF learns ingredient weights and ranks by cosine similarity; 64-dimensional LSA tests a compact learned representation [3,4]. In 200 reproducible recipe-derived queries, 60% of each source recipe\'s ingredients are retained, with 3-6 query ingredients, against the 8,000-recipe index.')
header = [Paragraph('<b>Approach</b>', styles['TableCustom']), Paragraph('<b>Recovery at 5</b>', styles['TableCustom']), Paragraph('<b>Recovery at 10</b>', styles['TableCustom']), Paragraph('<b>MRR</b>', styles['TableCustom'])]
table_rows = [header]
for row in metrics:
    table_rows.append([row['model'], f"{100 * row['recovery_at_5']:.1f}%", f"{100 * row['recovery_at_10']:.1f}%", f"{row['mean_reciprocal_rank']:.3f}"])
table = Table(table_rows, colWidths=[WIDTH * .40, WIDTH * .23, WIDTH * .23, WIDTH * .14], hAlign='LEFT')
table.setStyle(TableStyle([('FONTNAME',(0,0),(-1,-1),'DejaVu'),('FONTSIZE',(0,0),(-1,-1),8.7),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#eaf0f4')),('GRID',(0,0),(-1,-1),0.5,colors.HexColor('#d4dce2')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('ALIGN',(1,1),(-1,-1),'CENTER'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
story.append(table)
story.append(Spacer(1, 7))
p('Simple overlap performs best on this lexical sanity check; LSA does not improve recovery. TF-IDF remains an explainable NLP candidate for further independent testing. These are <b>source-recipe recovery results</b>, not supervised test accuracy, human relevance scores or food-waste reduction. Similar alternative recipes may also be valid. The inventory demo uses explicitly simulated dates and displays ingredient gaps.')

sub('e Ethical assessment and deliverables')
p('The tool must not infer food safety from dates alone, invent available stock or promise nutritional adequacy. Dates and usability are user inputs; entered expired or unusable stock is excluded. English ingredient vocabulary, dietary restrictions and general-recipe data limit transfer to real soup kitchens. Later validation will use independently specified pantries, user relevance judgements and curated quantity/unit mappings. Assignment 1 supplies this proposal, executed EDA notebook, initial experiments, reproducible sample and repository instructions.')

sub('Sources')
p('[1] United Nations. <link href="https://sdgs.un.org/goals/goal12" color="#167d8d">SDG 12 and target 12.3</link>. Food-waste estimate refers to 2022.', 'SourceCustom')
p('[2] irkaal. <link href="https://www.kaggle.com/datasets/irkaal/foodcom-recipes-and-reviews" color="#167d8d">Food.com Recipes and Reviews</link>, recipes.csv. Retrieved 17 October 2026; historical recipe publication dates 1999-2020.', 'SourceCustom')
p('[3] scikit-learn. <link href="https://scikit-learn.org/stable/modules/feature_extraction.html#text-feature-extraction" color="#167d8d">Text feature extraction</link>. [4] scikit-learn. <link href="https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.TruncatedSVD.html" color="#167d8d">TruncatedSVD</link>. [5] USDA. <link href="https://fdc.nal.usda.gov/download-datasets/" color="#167d8d">FoodData Central</link>.', 'SourceCustom')

def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('DejaVu', 8)
    canvas.setFillColor(grey)
    canvas.drawString(MARGIN, 25, 'Assignment 1   /   SDG 12.3')
    canvas.drawRightString(PAGE_W - MARGIN, 25, f'{doc.page} / 2')
    canvas.restoreState()

path = ROOT / 'report/FoodWise_Assignment1_Proposal.pdf'
doc = SimpleDocTemplate(str(path), pagesize=A4, rightMargin=MARGIN, leftMargin=MARGIN, topMargin=35, bottomMargin=42, title='FoodWise Assignment 1 Project Proposal', author='')
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(path)
