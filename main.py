"""Analyze the historical Amazon Top 50 books dataset."""

from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")  # Save figures without requiring a desktop GUI.

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent
DATA_FILE = PROJECT_DIR / "books.csv"
OUTPUT_DIR = PROJECT_DIR / "output"
REQUIRED_COLUMNS = ["Name", "Author", "User_Rating", "Reviews", "Price", "Year", "Genre"]
NUMERIC_COLUMNS = ["User_Rating", "Reviews", "Price", "Year"]


def load_books(path: Path) -> pd.DataFrame:
    """Load the CSV, normalize its rating heading, and validate its data."""
    if not path.is_file():
        raise FileNotFoundError(f"Could not find the data file: {path}")

    books = pd.read_csv(path)
    # The source calls this field "User Rating"; normalize the space for analysis.
    books = books.rename(columns={"User Rating": "User_Rating"})
    missing = [column for column in REQUIRED_COLUMNS if column not in books.columns]
    if missing:
        raise ValueError("Missing required column(s): " + ", ".join(missing))
    if books.empty:
        raise ValueError("The CSV contains no book rows.")

    books = books[REQUIRED_COLUMNS].copy()
    for column in ["Name", "Author", "Genre"]:
        books[column] = books[column].astype("string").str.strip()
        if books[column].isna().any() or books[column].eq("").any():
            raise ValueError(f"Every row must have a value in the {column} column.")

    for column in NUMERIC_COLUMNS:
        books[column] = pd.to_numeric(books[column], errors="coerce")
        if books[column].isna().any() or not books[column].map(pd.notna).all():
            raise ValueError(f"The {column} column must contain a valid number in every row.")
    if (books[["Reviews", "Price"]] < 0).any().any():
        raise ValueError("Reviews and Price cannot be negative.")
    if not books["User_Rating"].between(0, 5).all():
        raise ValueError("User Rating values must be between 0 and 5.")
    if not (books["Year"] % 1 == 0).all():
        raise ValueError("Year values must be whole numbers.")
    if not books["Year"].between(2009, 2019).all():
        raise ValueError("Year values must be between 2009 and 2019 for this dataset.")

    books["Reviews"] = books["Reviews"].astype("int64")
    books["Year"] = books["Year"].astype("int64")
    return books


def genre_summary(books: pd.DataFrame) -> pd.DataFrame:
    """Summarize entries, ratings, prices, and reviews by genre."""
    return books.groupby("Genre").agg(
        Entries=("Name", "count"),
        Average_Rating=("User_Rating", "mean"),
        Average_Price=("Price", "mean"),
        Average_Reviews=("Reviews", "mean"),
    )


def yearly_summary(books: pd.DataFrame) -> pd.DataFrame:
    """Summarize annual bestseller-list entries and their metrics."""
    return books.groupby("Year").agg(
        Entries=("Name", "count"),
        Average_Rating=("User_Rating", "mean"),
        Average_Price=("Price", "mean"),
        Average_Reviews=("Reviews", "mean"),
    )


def author_summary(books: pd.DataFrame) -> pd.DataFrame:
    """Summarize each author's appearances and readership metrics."""
    return books.groupby("Author").agg(
        Entries=("Name", "count"),
        Average_Rating=("User_Rating", "mean"),
        Total_Reviews=("Reviews", "sum"),
    ).sort_values(["Entries", "Total_Reviews"], ascending=False)


def make_charts(books: pd.DataFrame) -> list[Path]:
    """Create five charts covering ratings, prices, reviews, genres, and authors."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    paths = []

    rating_by_genre = books.groupby("Genre")["User_Rating"].mean().sort_values()
    ax = rating_by_genre.plot(kind="bar", color="steelblue")
    ax.set(title="Average user rating by genre", xlabel="Genre", ylabel="Rating (out of 5)")
    ax.set_ylim(0, 5)
    plt.tight_layout()
    path = OUTPUT_DIR / "average_rating_by_genre.png"
    plt.savefig(path, dpi=150)
    plt.close()
    paths.append(path)

    yearly = yearly_summary(books)
    ax = yearly["Average_Price"].plot(marker="o", color="darkorange")
    ax.set(title="Average listed price by year", xlabel="Year", ylabel="Price (dataset units)")
    ax.set_xticks(yearly.index)
    ax.tick_params(axis="x", rotation=45)
    plt.tight_layout()
    path = OUTPUT_DIR / "average_price_by_year.png"
    plt.savefig(path, dpi=150)
    plt.close()
    paths.append(path)

    ax = yearly["Average_Reviews"].plot(marker="o", color="mediumpurple")
    ax.set(title="Average reviews per entry by year", xlabel="Year", ylabel="Average review count")
    ax.set_xticks(yearly.index)
    ax.tick_params(axis="x", rotation=45)
    plt.tight_layout()
    path = OUTPUT_DIR / "average_reviews_by_year.png"
    plt.savefig(path, dpi=150)
    plt.close()
    paths.append(path)

    top_authors = author_summary(books).head(10)["Entries"].sort_values()
    ax = top_authors.plot(kind="barh", color="seagreen")
    ax.set(title="Authors with the most bestseller-list entries", xlabel="Entries", ylabel="Author")
    plt.tight_layout()
    path = OUTPUT_DIR / "top_authors.png"
    plt.savefig(path, dpi=150)
    plt.close()
    paths.append(path)

    counts_by_genre = books["Genre"].value_counts().sort_values()
    ax = counts_by_genre.plot(kind="bar", color="slateblue")
    ax.set(title="Bestseller-list entries by genre", xlabel="Genre", ylabel="Entries")
    plt.tight_layout()
    path = OUTPUT_DIR / "entries_by_genre.png"
    plt.savefig(path, dpi=150)
    plt.close()
    paths.append(path)
    return paths


def make_report(books: pd.DataFrame) -> Path:
    """Write the analysis and historical data limitations to a text report."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    most_expensive = books.loc[books["Price"].idxmax()]
    most_reviewed = books.loc[books["Reviews"].idxmax()]
    report_lines = [
        "AMAZON TOP 50 BOOKS DATA ANALYSIS",
        "=================================",
        f"Dataset entries analyzed: {len(books)}",
        f"Unique book titles: {books['Name'].nunique()}",
        f"Years covered: {books['Year'].min()}-{books['Year'].max()}",
        f"Average user rating: {books['User_Rating'].mean():.2f} / 5",
        f"Median user rating: {books['User_Rating'].median():.2f} / 5",
        f"Average listed price: {books['Price'].mean():.2f}",
        f"Median listed price: {books['Price'].median():.2f}",
        f"Average reviews per entry: {books['Reviews'].mean():,.0f}",
        f"Median reviews per entry: {books['Reviews'].median():,.0f}",
        "",
        "Extremes in this dataset:",
        f"  Highest price: {most_expensive['Name']} by {most_expensive['Author']} ({most_expensive['Price']:.2f})",
        f"  Most reviews: {most_reviewed['Name']} by {most_reviewed['Author']} ({most_reviewed['Reviews']:,})",
        "",
        "Entries and averages by genre:",
        genre_summary(books).round(2).to_string(),
        "",
        "Yearly trends (entries and average metrics):",
        yearly_summary(books).round(2).to_string(),
        "",
        "Top 10 authors by entry count:",
        author_summary(books).head(10).round(2).to_string(),
        "",
        "Interpretation notes:",
        "- Each row is a book's appearance in a year's top-50 list; a title can appear in multiple years.",
        "- Review counts and prices are the values recorded for these historical entries, not current values.",
        "- This dataset covers 2009–2019 and does not describe current bestseller rankings.",
        "- Genre labels are the dataset's Fiction/Non Fiction categories, not an independent classification.",
        "",
    ]
    report_path = OUTPUT_DIR / "report.txt"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    return report_path


def main() -> int:
    try:
        books = load_books(DATA_FILE)
        print(f"Loaded {len(books)} entries from {DATA_FILE.name} ({books['Year'].min()}-{books['Year'].max()}).")
        print(f"Average rating: {books['User_Rating'].mean():.2f} / 5")
        print(f"Average price: {books['Price'].mean():.2f}")
        print(f"Average reviews per entry: {books['Reviews'].mean():,.0f}")
        print("\nEntries by genre:")
        print(genre_summary(books).round(2).to_string())
        print("\nYearly trends:")
        print(yearly_summary(books).round(2).to_string())
        print("\nTop authors:")
        print(author_summary(books).head(10).round(2).to_string())
        chart_paths = make_charts(books)
        report_path = make_report(books)
        print(f"\nSaved {len(chart_paths)} charts and {report_path.name} in {OUTPUT_DIR}.")
        return 0
    except (FileNotFoundError, pd.errors.EmptyDataError, pd.errors.ParserError, ValueError) as error:
        print(f"Data error: {error}", file=sys.stderr)
        return 1
    except OSError as error:
        print(f"File error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
