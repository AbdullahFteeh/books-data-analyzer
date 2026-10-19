# Books Data Analyzer

A local Python project for exploring Amazon's historical Top 50 bestselling book entries from 2009 through 2019. It uses pandas for analysis and matplotlib for charts. It does not call paid APIs or send your data anywhere.

## Dataset and attribution

The project uses the 550-row **Amazon Top 50 Bestselling Books 2009–2019** CSV:

- GitHub file: [aiplanethub/Datasets](https://github.com/aiplanethub/Datasets/blob/master/Amazon%20Top%2050%20Bestselling%20Books%202009%20-%202019.csv)
- Raw CSV used for the download: [raw.githubusercontent.com](https://raw.githubusercontent.com/aiplanethub/Datasets/master/Amazon%20Top%2050%20Bestselling%20Books%202009%20-%202019.csv)
- Original dataset listing: [Kaggle, Amazon Top 50 Bestselling Books 2009–2019](https://www.kaggle.com/datasets/sootersaalu/amazon-top-50-bestselling-books-2009-2019)

Dataset attribution: **Sooter Saalu** (Kaggle dataset publisher); downloaded from the public **AI Planet `aiplanethub/Datasets` GitHub repository**. The original Kaggle dataset is reported as **CC0 / Public Domain** in published documentation about the dataset ([license reference](https://ananfito.dev/case-study_amazon-bestsellers/AmazonBestsellers.html)). The GitHub mirror does not provide a dataset-specific license file next to this CSV. Attribution is retained here; check the original dataset listing and applicable source terms before redistributing the data.

`books.csv` contains the downloaded source data with its original columns. The previous project sample is preserved separately as `sample_books.csv`.

## Setup

Requirements: Python 3.9 or newer, pandas, and matplotlib. These are free packages.

From PowerShell in the project folder, create and activate a local environment and install the dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install pandas matplotlib
```

If the project environment already exists, activate it and skip environment creation. Run the analyzer with:

```powershell
python main.py
```

The analyzer reads `books.csv` from its own folder and saves results under `output/`.

## Analysis and output

The analyzer validates required columns, missing values, numeric fields, rating range, and the dataset's 2009–2019 year range. It handles the source heading `User Rating` by normalizing it internally to `User_Rating`.

The console and `output/report.txt` summarize ratings, prices, review counts, genres, yearly trends, and the top authors by number of annual list entries. Charts are saved as:

- `average_rating_by_genre.png`
- `average_price_by_year.png`
- `average_reviews_by_year.png`
- `top_authors.png`
- `entries_by_genre.png`

## Limitations

- This is historical data for **2009–2019**. It does not contain current 2026 bestseller rankings.
- There are 550 annual list entries (50 per year), not 550 distinct titles. A book appearing in multiple years can occur in multiple rows.
- Prices and review counts are values in the historical dataset, not current Amazon prices or review totals.
- The dataset only covers books included in those annual lists; it is not a complete catalog or a representative sample of every book.
- Genre is limited to the dataset's `Fiction` and `Non Fiction` labels.
