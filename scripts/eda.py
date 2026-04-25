import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def run_eda(data_dir: str, output_dir: str = "./eda_results") -> None:
    """Run comprehensive EDA on MovieLens 1M data."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    logger.info(f"Starting EDA on data in {data_dir}")

    # Load data
    data_path = Path(data_dir)
    movies = pd.read_csv(data_path / "movies.csv")
    ratings = pd.read_csv(data_path / "ratings.csv")
    users = pd.read_csv(data_path / "users.csv")

    logger.info("Data loaded successfully")

    # Movies EDA
    movies_report = f"""
=== MOVIES DATASET ===
Shape: {movies.shape}
Columns: {list(movies.columns)}
Data types:
{movies.dtypes}

Null values:
{movies.isnull().sum()}

Sample rows:
{movies.head(10)}

Movie ID range: {movies["movieId"].min()} to {movies["movieId"].max()}
Unique genres: {movies["genres"].nunique()}
"""
    logger.info(movies_report)

    # Ratings EDA
    ratings_report = f"""
=== RATINGS DATASET ===
Shape: {ratings.shape}
Columns: {list(ratings.columns)}
Data types:
{ratings.dtypes}

Null values:
{ratings.isnull().sum()}

Rating statistics:
{ratings["rating"].describe()}

Unique users: {ratings["userId"].nunique()}
Unique movies: {ratings["movieId"].nunique()}
User ratings range: min={ratings.groupby("userId")["movieId"].count().min()}, max={ratings.groupby("userId")["movieId"].count().max()}, mean={ratings.groupby("userId")["movieId"].count().mean():.2f}
Movie ratings range: min={ratings.groupby("movieId")["userId"].count().min()}, max={ratings.groupby("movieId")["userId"].count().max()}, mean={ratings.groupby("movieId")["userId"].count().mean():.2f}

Timestamp range: {pd.to_datetime(ratings["timestamp"], unit="s").min()} to {pd.to_datetime(ratings["timestamp"], unit="s").max()}
"""
    logger.info(ratings_report)

    # Users EDA
    users_report = f"""
=== USERS DATASET ===
Shape: {users.shape}
Columns: {list(users.columns)}
Data types:
{users.dtypes}

Null values:
{users.isnull().sum()}

Gender distribution:
{users["gender"].value_counts()}

Age distribution:
{users["age"].value_counts().sort_index()}

Occupation distribution:
{users["occupation"].value_counts().sort_index()}
"""
    logger.info(users_report)

    # Merged analysis
    merged = ratings.merge(users, on="userId").merge(movies, on="movieId")
    merged_report = f"""
=== MERGED DATASET ANALYSIS ===
Shape: {merged.shape}

Rating distribution by gender:
{merged.groupby("gender")["rating"].agg(["count", "mean", "std"]).round(3)}

Rating distribution by occupation (top 10):
{merged.groupby("occupation")["rating"].agg(["count", "mean"]).sort_values("count", ascending=False).head(10)}

Top 10 most rated movies:
{merged["movieId"].value_counts().head(10)}

Top 10 highest rated movies (min 10 ratings):
{merged.groupby("movieId")["rating"].agg(["count", "mean"]).query("count >= 10").sort_values("mean", ascending=False).head(10)}
"""
    logger.info(merged_report)

    # Save reports
    with open(output_path / "eda_report.txt", "w") as f:
        f.write(movies_report)
        f.write("\n" + ratings_report)
        f.write("\n" + users_report)
        f.write("\n" + merged_report)

    logger.info(f"EDA complete. Reports saved to {output_dir}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_eda("./data_local")
