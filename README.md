# FoodWise Assignment 1

Expiry aware recipe recommendations for small soup kitchens and food-service teams.

This repository contains the first assignment: a project proposal, exploratory data analysis and initial ingredient-retrieval experiments. The primary SDG connection is target 12.3. The project aims to support food-waste prevention by helping users choose recipes from stock and prioritise ingredients with approaching entered use-by dates.

## Start here

- Read report/Sunar_Tan_Acikel_Ozyakup_Group5.pdf for the two-page concept note.
- Open notebooks/FoodWise_Assignment1.ipynb for the executed EDA and experiments.
- The notebook includes saved outputs and figures. Extract the whole project before running it so the data and source modules remain available.

Install Python 3.11 or newer and the dependencies:

    python -m pip install -r requirements.txt

Open the notebook in Jupyter or VS Code and run its cells. In Google Colab, upload and extract the complete project ZIP, change the working directory to the extracted project root, and then run the notebook.

To recreate the notebook and its saved outputs without a Jupyter kernel:

    python scripts/build_notebook.py

To regenerate the proposal after running the analysis:

    python scripts/build_proposal.py

## Data

Source: https://www.kaggle.com/datasets/irkaal/foodcom-recipes-and-reviews

The analysis dataset used throughout this project contains exactly **8,000 real recipes** selected with seed 42. It retains 11 fields needed for EDA and retrieval. The filter keeps named recipes with 3-20 distinct normalised ingredient labels and positive known servings; duplicate normalised ingredient sets are removed before reservoir sampling. Original recipe IDs are retained.

The sample profile is in data/sample_profile.json. Source and sampling provenance are in data/source_metadata.json. The publisher states CC0 Public Domain. The collection contains historical general-purpose recipes rather than observed soup-kitchen inventory or waste outcomes.

The original source archive is not bundled. To recreate the 8,000-record sample and its profile, download recipes.csv from the source page and supply its downloaded ZIP:

    python scripts/prepare_data.py --source-zip path/to/recipes.csv.zip --sample-size 8000 --seed 42

If the website downloads a plain CSV, put it into a ZIP before using this command.

USDA FoodData Central is a supplementary source planned for later validated nutrient matching: https://fdc.nal.usda.gov/download-datasets/

## Methods

The baseline uses Jaccard overlap of ingredient sets. The first NLP model learns TF-IDF ingredient weights and ranks recipes by cosine similarity. A 64-dimensional latent semantic analysis model is compared using TruncatedSVD.

The illustrative inventory demo puts recipes with all ingredient types available first, then ranks within groups using 0.60 TF-IDF cosine similarity, 0.30 ingredient-type coverage and 0.10 coverage of stock due within two days. The weights are initial heuristics. Items entered as unusable or past the entered date are excluded from available stock. Missing ingredients are displayed.

Inventory quantities are stored but not used to prove that enough grams or portions are available. Within the 8,000-record sample, source quantity lists frequently differ in length from ingredient lists, and units are not consistently available. Portion scaling and nutritional claims require additional curation and validation.

## Evaluation and interpretation

The initial experiment uses 200 recipe-derived queries against the 8,000-recipe index. Each query retains 60% of a source recipe's ingredients, with 3-6 retained ingredients. Outputs report source-recipe recovery at ranks 1, 5 and 10, plus mean reciprocal rank.

This is a synthetic recovery sanity check, not independent human relevance evaluation. The query source recipe is an indexed candidate, as in document retrieval. Other recommended recipes may also be suitable. These metrics do not establish recommendation usefulness, stock sufficiency, dietary safety or actual food-waste reduction.

The initial inventory is explicitly illustrative. No operational stock records, expiry dates or waste outcomes are presented as observed data. Future evaluation needs independently specified pantries and real user judgements. Food-waste impact needs before/after measurements in a real pilot.

## Files

- data/recipes_sample.jsonl: the reproducible real recipe sample.
- data/sample_profile.json: EDA statistics for the 8,000-record sample.
- data/source_metadata.json: source and reproducible sampling metadata.
- data/example_inventory.json: clearly labelled illustrative input.
- src/foodwise.py: parsers, retrieval models, ranking and initial evaluation.
- src/analysis.py: EDA and experiment figures.
- scripts/: reproducible data preparation, notebook generation and proposal generation.
- outputs/: actual experiment results, example rankings and figures.
- report/: the first-assignment PDF proposal.

## Scope of this submission

This first assignment contains a dataset, EDA and initial model experiments. A production interface, validated mass constraints, nutritional optimisation, multilingual ingredient matching and a real food-waste impact study belong to later development stages.

The files are ready to upload to a new repository owned by the project group. Submit that repository's URL together with the PDF. The classmate's repository is a reference, not this project's submission URL. Rename the PDF to the surname-based format requested by the instructor when group details are final.

## References

1. UN SDG 12 and target 12.3: https://sdgs.un.org/goals/goal12
2. Food.com dataset: https://www.kaggle.com/datasets/irkaal/foodcom-recipes-and-reviews
3. TF-IDF documentation: https://scikit-learn.org/stable/modules/feature_extraction.html#text-feature-extraction
4. TruncatedSVD documentation: https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.TruncatedSVD.html
5. USDA FoodData Central: https://fdc.nal.usda.gov/download-datasets/

The water-potability work shared by the classmate informed the high-level EDA organisation. FoodWise code and experiments were developed for ingredient retrieval. Reference reviewed: https://github.com/yec31946/AI-Driven-Analysis-of-Water-Potability-for-Sustainable-Resource-Management
